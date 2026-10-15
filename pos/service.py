"""Application controller for sale and return use cases."""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from .domain import BusinessError, Sale, SaleLine, CashPayment, money, quantity


class POSService:
    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    def _lines(items):
        if not isinstance(items, list) or not 1 <= len(items) <= 100:
            raise BusinessError("Select at least one item, up to 100 lines.")
        merged = {}
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("sku"), str):
                raise BusinessError("Each item needs a product code and quantity.")
            sku = item["sku"]
            merged[sku] = quantity(merged.get(sku, 0) + quantity(item.get("quantity")))
        return merged

    @staticmethod
    def _request(conn, payload, kind):
        token = payload.get("token")
        if not isinstance(token, str) or not 8 <= len(token) <= 100:
            raise BusinessError("A valid request token is required.")
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        old = conn.execute("SELECT * FROM requests WHERE token=?", (token,)).fetchone()
        if old and (old["kind"] != kind or old["fingerprint"] != fingerprint):
            raise BusinessError("This request token was already used for different data.")
        return token, fingerprint, old["result_id"] if old else None

    def checkout(self, payload):
        items = self._lines(payload.get("items"))
        payment = CashPayment(money(payload.get("cash")))
        with self.repository.transaction() as conn:
            token, fingerprint, old_id = self._request(conn, payload, "sale")
            if old_id:
                return self.repository.sale(conn, old_id)
            lines = []
            for sku, count in items.items():
                product = conn.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()
                if product is None:
                    raise BusinessError(f"Unknown product code: {sku}.")
                if count > product["stock"]:
                    raise BusinessError(f"Not enough stock for {product['name']}.")
                lines.append(SaleLine(sku, product["name"], product["price"], count))
            sale = Sale(tuple(lines))
            change = payment.change_for(sale.total)
            sale_id = "S-" + uuid.uuid4().hex[:12].upper()
            conn.execute("INSERT INTO sales VALUES (?,?,?,?,?)", (sale_id, datetime.now(timezone.utc).isoformat(), sale.total, payment.tendered, change))
            for line in sale.lines:
                conn.execute("INSERT INTO sale_lines VALUES (?,?,?,?,?,0)", (sale_id, line.sku, line.name, line.unit_price, line.quantity))
                conn.execute("UPDATE products SET stock=stock-? WHERE sku=?", (line.quantity, line.sku))
            conn.execute("INSERT INTO requests VALUES (?,?,?,?)", (token, "sale", fingerprint, sale_id))
            return self.repository.sale(conn, sale_id)

    def find_sale(self, sale_id):
        with self.repository.transaction() as conn:
            result = self.repository.sale(conn, sale_id)
            if not result:
                raise BusinessError("Receipt not found. Check the sale ID.")
            return result

    def return_items(self, payload):
        items = self._lines(payload.get("items"))
        sale_id = payload.get("sale_id")
        reason = payload.get("reason", "")
        if not isinstance(sale_id, str) or not isinstance(reason, str) or not 3 <= len(reason.strip()) <= 200:
            raise BusinessError("Provide a sale ID and a return reason of 3 to 200 characters.")
        with self.repository.transaction() as conn:
            token, fingerprint, old_id = self._request(conn, payload, "return")
            if old_id:
                return self.repository.refund(conn, old_id)
            sale = self.repository.sale(conn, sale_id)
            if not sale:
                raise BusinessError("Receipt not found. Check the sale ID.")
            original = {line["sku"]: line for line in sale["lines"]}
            total = 0
            for sku, count in items.items():
                if sku not in original:
                    raise BusinessError("This product is not on the original receipt.")
                line = original[sku]
                if count > line["quantity"] - line["returned"]:
                    raise BusinessError(f"Return quantity exceeds the remaining quantity for {line['name']}.")
                total += count * line["unit_price"]
            return_id = "R-" + uuid.uuid4().hex[:12].upper()
            conn.execute("INSERT INTO returns VALUES (?,?,?,?,?)", (return_id, sale_id, datetime.now(timezone.utc).isoformat(), total, reason.strip()))
            for sku, count in items.items():
                conn.execute("INSERT INTO return_lines VALUES (?,?,?,?)", (return_id, sku, count, original[sku]["unit_price"]))
                conn.execute("UPDATE sale_lines SET returned=returned+? WHERE sale_id=? AND sku=?", (count, sale_id, sku))
                conn.execute("UPDATE products SET stock=stock+? WHERE sku=?", (count, sku))
            conn.execute("INSERT INTO requests VALUES (?,?,?,?)", (token, "return", fingerprint, return_id))
            return self.repository.refund(conn, return_id)

    def history(self):
        with self.repository.transaction() as conn:
            return {
                "sales": [dict(r) for r in conn.execute("SELECT * FROM sales ORDER BY created_at DESC LIMIT 100")],
                "returns": [dict(r) for r in conn.execute("SELECT * FROM returns ORDER BY created_at DESC LIMIT 100")],
                "summary": dict(conn.execute("SELECT (SELECT COUNT(*) FROM sales) AS sale_count, (SELECT COALESCE(SUM(total),0) FROM sales) AS gross, (SELECT COALESCE(SUM(total),0) FROM returns) AS refunds").fetchone()),
            }
