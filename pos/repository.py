"""SQLite persistence. Each use case owns one atomic transaction."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
 sku TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
 price INTEGER NOT NULL CHECK(price>0), stock INTEGER NOT NULL CHECK(stock>=0));
CREATE TABLE IF NOT EXISTS sales (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, total INTEGER NOT NULL,
 tendered INTEGER NOT NULL, change_due INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sale_lines (
 sale_id TEXT NOT NULL REFERENCES sales(id), sku TEXT NOT NULL REFERENCES products(sku),
 name TEXT NOT NULL, unit_price INTEGER NOT NULL, quantity INTEGER NOT NULL CHECK(quantity>0),
 returned INTEGER NOT NULL DEFAULT 0 CHECK(returned>=0 AND returned<=quantity),
 PRIMARY KEY(sale_id,sku));
CREATE TABLE IF NOT EXISTS returns (
 id TEXT PRIMARY KEY, sale_id TEXT NOT NULL REFERENCES sales(id),
 created_at TEXT NOT NULL, total INTEGER NOT NULL, reason TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS return_lines (
 return_id TEXT NOT NULL REFERENCES returns(id), sku TEXT NOT NULL REFERENCES products(sku),
 quantity INTEGER NOT NULL CHECK(quantity>0), unit_price INTEGER NOT NULL,
 PRIMARY KEY(return_id,sku));
CREATE TABLE IF NOT EXISTS requests (
 token TEXT PRIMARY KEY, kind TEXT NOT NULL, fingerprint TEXT NOT NULL, result_id TEXT NOT NULL);
"""
PRODUCTS = [
    ("1001", "Whole Milk 1L", "Dairy", 250, 40),
    ("1002", "Sourdough Bread", "Bakery", 320, 25),
    ("1003", "Free Range Eggs 6pk", "Dairy", 420, 30),
    ("1004", "Gala Apples 1kg", "Produce", 360, 35),
    ("1005", "Pasta 500g", "Pantry", 180, 50),
    ("1006", "Orange Juice 1L", "Drinks", 300, 20),
    ("1007", "Coffee 250g", "Pantry", 650, 18),
    ("1008", "Dark Chocolate", "Snacks", 220, 45),
]


class SQLiteRepository:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as conn:
            conn.executescript(SCHEMA)
            conn.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)", PRODUCTS)

    @contextmanager
    def transaction(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def products(self):
        with self.transaction() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM products ORDER BY sku")]

    def sale(self, conn, sale_id):
        row = conn.execute("SELECT * FROM sales WHERE id=?", (sale_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["lines"] = [dict(r) for r in conn.execute("SELECT * FROM sale_lines WHERE sale_id=? ORDER BY sku", (sale_id,))]
        return result

    def refund(self, conn, return_id):
        row = dict(conn.execute("SELECT * FROM returns WHERE id=?", (return_id,)).fetchone())
        row["lines"] = [dict(r) for r in conn.execute("SELECT * FROM return_lines WHERE return_id=?", (return_id,))]
        return row
