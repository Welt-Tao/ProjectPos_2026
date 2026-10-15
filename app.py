"""Local-only POS server. Run: python app.py, then open http://127.0.0.1:8765."""
import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote
from pos.domain import BusinessError
from pos.repository import SQLiteRepository
from pos.service import POSService

ROOT = Path(__file__).resolve().parent


def make_handler(service):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, code, content, content_type="application/json"):
            data = json.dumps(content).encode() if content_type == "application/json" else content
            self.send_response(code)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = urlparse(self.path).path
            try:
                if path in ("/", "/index.html"):
                    return self.respond(200, (ROOT / "static/index.html").read_bytes(), "text/html")
                if path in ("/style.css", "/app.js"):
                    return self.respond(200, (ROOT / "static" / path[1:]).read_bytes(), "text/css" if path.endswith("css") else "text/javascript")
                if path == "/api/products":
                    return self.respond(200, service.repository.products())
                if path == "/api/history":
                    return self.respond(200, service.history())
                if path.startswith("/api/sales/"):
                    return self.respond(200, service.find_sale(unquote(path.split("/")[-1])))
                self.respond(404, {"error": "Not found"})
            except BusinessError as exc:
                self.respond(400, {"error": str(exc)})
            except Exception:
                logging.exception("GET failed")
                self.respond(500, {"error": "Storage is unavailable. Try again."})

        def do_POST(self):
            # Browser requests must originate from this local application.
            if self.headers.get("Origin") not in (None, f"http://{self.headers.get('Host')}"):
                return self.respond(403, {"error": "Origin is not allowed."})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 65536:
                    return self.respond(400, {"error": "Invalid request size."})
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise BusinessError("Expected a JSON object.")
                path = urlparse(self.path).path
                if path == "/api/sales":
                    return self.respond(200, service.checkout(payload))
                if path == "/api/returns":
                    return self.respond(200, service.return_items(payload))
                self.respond(404, {"error": "Not found"})
            except (BusinessError, ValueError, TypeError) as exc:
                self.respond(400, {"error": str(exc)})
            except Exception:
                logging.exception("Transaction failed")
                self.respond(500, {"error": "Transaction could not be completed. Retry the same request."})

    return Handler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default=str(ROOT / "data/pos.sqlite3"))
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(POSService(SQLiteRepository(args.db))))
    print(f"POS is running at http://127.0.0.1:{args.port}. Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
