import concurrent.futures
import json
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import uuid
from pathlib import Path
from http.server import ThreadingHTTPServer
from app import make_handler
from pos.domain import BusinessError, money
from pos.repository import SQLiteRepository
from pos.service import POSService


class POSTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.sqlite3'
        self.repo = SQLiteRepository(self.path)
        self.service = POSService(self.repo)

    def tearDown(self):
        self.temp.cleanup()

    def sale_payload(self, items=None, cash='10.00'):
        return {'token': str(uuid.uuid4()), 'cash': cash, 'items': items if items is not None else [{'sku':'1001','quantity':2},{'sku':'1002','quantity':1}]}

    def return_payload(self, sale, count=1):
        return {'token':str(uuid.uuid4()), 'sale_id':sale['id'], 'reason':'Unopened item', 'items':[{'sku':'1001','quantity':count}]}

    def stock(self, sku='1001'):
        return next(p['stock'] for p in self.repo.products() if p['sku']==sku)

    def test_cash_sale_totals_receipt_and_stock(self):
        s=self.service.checkout(self.sale_payload())
        self.assertEqual((s['total'],s['tendered'],s['change_due']),(820,1000,180))
        self.assertEqual((self.stock(),self.stock('1002')),(38,24))
        self.assertEqual(len(s['lines']),2)

    def test_insufficient_cash_is_atomic(self):
        with self.assertRaises(BusinessError): self.service.checkout(self.sale_payload(cash='8.19'))
        self.assertEqual(self.stock(),40)
        self.assertEqual(self.service.history()['summary']['sale_count'],0)

    def test_unknown_product_rolls_back_all_lines(self):
        with self.assertRaises(BusinessError): self.service.checkout(self.sale_payload([{'sku':'1001','quantity':1},{'sku':'BAD','quantity':1}]))
        self.assertEqual(self.stock(),40)

    def test_insufficient_stock(self):
        with self.assertRaises(BusinessError): self.service.checkout(self.sale_payload([{'sku':'1001','quantity':41}],'1000'))
        self.assertEqual(self.stock(),40)

    def test_invalid_quantities(self):
        for q in (0,-1,1.5,True,'2',1000,None):
            with self.subTest(q=q), self.assertRaises(BusinessError):
                self.service.checkout(self.sale_payload([{'sku':'1001','quantity':q}]))

    def test_empty_sale(self):
        with self.assertRaises(BusinessError): self.service.checkout(self.sale_payload([]))

    def test_duplicate_product_lines_merge(self):
        s=self.service.checkout(self.sale_payload([{'sku':'1001','quantity':1},{'sku':'1001','quantity':2}]))
        self.assertEqual((s['total'],len(s['lines'])),(750,1))
        self.assertEqual(self.stock(),37)

    def test_money_rejects_nonfinite_and_extra_decimals(self):
        for value in ('NaN','Infinity','-1','1.001','1000001','abc',None,10):
            with self.subTest(value=value), self.assertRaises(BusinessError): money(value)
        self.assertEqual(money('0.10'),10)

    def test_sale_retry_is_idempotent(self):
        p=self.sale_payload(); a=self.service.checkout(p); b=self.service.checkout(p)
        self.assertEqual(a['id'],b['id']);self.assertEqual(self.stock(),38)

    def test_token_reuse_with_changed_payload_rejected(self):
        p=self.sale_payload();self.service.checkout(p);p['cash']='20.00'
        with self.assertRaises(BusinessError):self.service.checkout(p)

    def test_partial_return_and_net_total(self):
        sale=self.service.checkout(self.sale_payload());r=self.service.return_items(self.return_payload(sale))
        self.assertEqual(r['total'],250);self.assertEqual(self.stock(),39)
        self.assertEqual(self.service.find_sale(sale['id'])['lines'][0]['returned'],1)
        h=self.service.history()['summary'];self.assertEqual(h['gross']-h['refunds'],570)

    def test_full_return_then_excess_return_rejected(self):
        sale=self.service.checkout(self.sale_payload());self.service.return_items(self.return_payload(sale,2))
        with self.assertRaises(BusinessError):self.service.return_items(self.return_payload(sale))
        self.assertEqual(self.stock(),40)

    def test_refund_uses_original_price(self):
        sale=self.service.checkout(self.sale_payload())
        with self.repo.transaction() as c:c.execute("UPDATE products SET price=999 WHERE sku='1001'")
        self.assertEqual(self.service.return_items(self.return_payload(sale))['total'],250)

    def test_missing_receipt(self):
        with self.assertRaises(BusinessError): self.service.find_sale('missing')
        with self.assertRaises(BusinessError): self.service.return_items(self.return_payload({'id':'missing'}))

    def test_return_nonpurchased_item(self):
        s=self.service.checkout(self.sale_payload());p=self.return_payload(s);p['items'][0]['sku']='1008'
        with self.assertRaises(BusinessError): self.service.return_items(p)
        self.assertEqual(self.stock('1008'),45)

    def test_mixed_return_is_atomic(self):
        s=self.service.checkout(self.sale_payload());p=self.return_payload(s);p['items'].append({'sku':'1002','quantity':2})
        with self.assertRaises(BusinessError):self.service.return_items(p)
        self.assertEqual(self.stock(),38);self.assertEqual(len(self.service.history()['returns']),0)

    def test_return_retry_is_idempotent(self):
        s=self.service.checkout(self.sale_payload());p=self.return_payload(s)
        a=self.service.return_items(p);b=self.service.return_items(p)
        self.assertEqual(a['id'],b['id']);self.assertEqual(self.stock(),39)

    def test_return_reason_required(self):
        s=self.service.checkout(self.sale_payload());p=self.return_payload(s);p['reason']=' '
        with self.assertRaises(BusinessError):self.service.return_items(p)

    def test_persistence_after_repository_restart(self):
        s=self.service.checkout(self.sale_payload());other=POSService(SQLiteRepository(self.path))
        self.assertEqual(other.find_sale(s['id'])['total'],820)
        self.assertEqual(next(p['stock'] for p in other.repository.products() if p['sku']=='1001'),38)

    def test_concurrent_sales_cannot_oversell(self):
        with self.repo.transaction() as c:c.execute("UPDATE products SET stock=1 WHERE sku='1001'")
        def buy(_):
            try:self.service.checkout(self.sale_payload([{'sku':'1001','quantity':1}]));return True
            except BusinessError:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool: results=list(pool.map(buy,range(2)))
        self.assertEqual(sorted(results),[False,True]);self.assertEqual(self.stock(),0)

    def test_concurrent_returns_cannot_overrefund(self):
        s=self.service.checkout(self.sale_payload([{'sku':'1001','quantity':1}]))
        def refund(_):
            try:self.service.return_items(self.return_payload(s));return True
            except BusinessError:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool: results=list(pool.map(refund,range(2)))
        self.assertEqual(sorted(results),[False,True]);self.assertEqual(self.stock(),40)

    def test_http_endpoints_and_bad_request(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.service))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            with urllib.request.urlopen(base+'/api/products') as r:self.assertEqual(len(json.load(r)),8)
            req=urllib.request.Request(base+'/api/sales',json.dumps(self.sale_payload()).encode(),{'Content-Type':'application/json'})
            with urllib.request.urlopen(req) as r:self.assertEqual(json.load(r)['total'],820)
            bad=urllib.request.Request(base+'/api/sales',b'[]',{'Content-Type':'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as exc:urllib.request.urlopen(bad)
            self.assertEqual(exc.exception.code,400)
            cross=urllib.request.Request(base+'/api/sales',b'{}',{'Origin':'https://example.com'})
            with self.assertRaises(urllib.error.HTTPError) as exc:urllib.request.urlopen(cross)
            self.assertEqual(exc.exception.code,403)
        finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
