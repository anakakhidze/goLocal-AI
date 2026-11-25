"""Local tool demonstration endpoint; this is not the full GoLocal HTTP backend."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .act import act
from .llm import ModelUnavailable
from .tools import tools_for


def handle_turn(payload, *, llm=None):
    if not isinstance(payload, dict) or set(payload) != {"question"}:
        return 400, {"ok": False, "error": "Send only a question field; identity is never accepted in the body."}
    try:
        return 200, act(payload["question"], os.environ.get("GOLOCAL_CALLER") or None, llm=llm)
    except ValueError:
        return 400, {"ok": False, "error": "Question must contain 1 to 2000 nonblank characters."}
    except ModelUnavailable as exc:
        return 503, {"ok": False, "error": str(exc)}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/tools":
            self.respond(200, {"tools": [t.schema() for t in tools_for(None).values()]})
        else:
            self.respond(404, {"ok": False, "error": "Use GET /tools or POST /act."})

    def do_POST(self):
        if self.path != "/act":
            self.respond(404, {"ok": False, "error": "Use POST /act."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                self.respond(413, {"ok": False, "error": "Send a JSON body of 1 to 8192 bytes."})
                return
            payload = json.loads(self.rfile.read(size))
        except (ValueError, UnicodeError):
            self.respond(400, {"ok": False, "error": "Send valid JSON."})
            return
        self.respond(*handle_turn(payload))

    def log_message(self, *_):
        pass  # Request paths and bodies do not enter tool/usage logs.


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
