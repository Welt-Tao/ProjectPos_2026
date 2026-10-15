# Market POS

An individual Software Engineering Practice project by Taoliyuan. The system supports cash checkout and receipt-based returns. It uses Python's standard library, SQLite and a browser interface, with no pip dependencies.

## Run

Install Python 3.10 or newer from https://www.python.org/downloads/ if needed. Open a terminal in this folder:

```powershell
python app.py
```

Then open http://127.0.0.1:8765 in Edge or Chrome. Windows users can also double-click `START_POS.cmd`. If the browser opens before the server is ready, refresh once. Keep the server terminal open. Ctrl+C stops it.

Data persists in `data/pos.sqlite3`. The first run seeds eight products. The application creates a fresh demonstration database if you supply a new path:

```powershell
python app.py --port 8766 --db data/rehearsal.sqlite3
```

Open http://127.0.0.1:8766 for that instance. This leaves the original database untouched.

## Demonstration

1. Add Whole Milk 1L twice and Sourdough Bread once. The total is EUR 8.20.
2. Enter EUR 5.00 and try completing the sale. The application rejects insufficient cash without changing stock.
3. Enter EUR 10.00 and complete the sale. Change is EUR 1.80. Keep the generated sale ID.
4. Open Returns and find that sale ID. Return one milk unit with reason `Unopened item no longer needed`.
5. Confirm the EUR 2.50 cash refund. Milk stock is 39 from an initial 40. Bread stock is 24 from an initial 25.
6. Try returning two more milk units from that receipt. The application rejects the request because only one remains returnable.
7. Open Transactions. For this isolated scenario the gross total is EUR 8.20, refunds EUR 2.50 and net sales EUR 5.70.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests use temporary databases and never modify live or demonstration data. They cover receipts, precision, validation, transaction rollback, original-price refunds, persistence, idempotency, concurrent sale/return requests and HTTP validation.

## Structure

| Location | Responsibility |
|---|---|
| `app.py` | Local HTTP server and JSON boundary |
| `pos/domain.py` | Sale values, payment and validation |
| `pos/service.py` | Sale and return use-case controller |
| `pos/repository.py` | SQLite schema and transaction lifecycle |
| `static/` | English interface and basket previews |
| `tests/` | Repeatable automated verification |
| `docs/uml/` | Editable SVG diagrams and vector PDF copies |
| `docs/screenshots/` | Actual browser demonstration evidence |
| `PROJECT_PLAN.md` | Scope, timeboxes and acceptance criteria |

## Business rules and boundaries

Amounts are integer cents. Prices are tax-inclusive EUR demonstration prices. The server is authoritative for sale prices, stock and returnable quantities. Cash returns use the stored original unit price and restock goods assumed suitable for resale. Each transaction uses `BEGIN IMMEDIATE` and commits or rolls back as a unit. Request tokens make retries of the same payload idempotent. Changing the payload requires a new token.

The cart is a browser draft, lost on refresh. A stock check at checkout protects against stale catalogues. A failed or uncertain network response can be retried without changing the basket or cash amount. There is no user login, card payment, stock adjustment screen, receipt-less return, damaged-goods processing, tax reporting or public deployment. The development HTTP server binds only to `127.0.0.1`.

## Git workflow and authorship

The individual development branch is `taoliyuan/development`. Merge it to `main` when an increment is ready, and preserve both branches. Local commits use the supplied project owner's identity. Implementation and document preparation used AI assistance, with the student responsible for review, comprehension, demonstration and submission. Commit timestamps are actual execution timestamps, not evidence of elapsed three-day sprints.

Published repository: https://github.com/Welt-Tao/ProjectPos_2026 . Both `main` and `taoliyuan/development` were verified remotely on 15 October 2026. Final report, slides and workbook are in `docs/submission/`. The student demonstration video is still pending.
