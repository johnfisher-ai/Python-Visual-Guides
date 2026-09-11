"""A practice web API for the APIs and JSON guide.

Every notebook in the guide starts this in its Setup cell:

    import practice_api
    BASE = practice_api.start()        # "http://127.0.0.1:8765"

It runs inside the notebook's own Python process, listening on 127.0.0.1, the address a
computer uses to reach itself. In Colab that computer is Colab's, so nothing runs on yours.
It serves the weather stations used throughout this library, and it responds to every reader
the same way, which is what lets a notebook show an error on purpose.

Endpoints:

    GET /                  a short HTML page, the kind a person would read
    GET /stations          every station, as a list of {"id", "name"}
    GET /stations/<id>     one station, or 404 if no station has that id

The stations are reference data, and read-only. Any other method on these endpoints gets
405 Method Not Allowed, with an Allow header naming the method that is allowed. Endpoints
added later for POST, PUT and DELETE use other paths, so what these return never changes.

Two details differ from a real server, both so that the output printed in a notebook matches
what you see when you run it: the Date header always reports the same moment, and the Server
header does not name a Python version.

Standard library only, so it runs wherever Python does.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORTS = range(8765, 8785)          # the first free port in this range is used
DATE = "Sun, 01 Mar 2026 09:00:00 GMT"

STATIONS = {
    "bergen":   {"id": "bergen",   "name": "Bergen",   "latitude": 60.39, "longitude": 5.32},
    "oslo":     {"id": "oslo",     "name": "Oslo",     "latitude": 59.91, "longitude": 10.75},
    "svalbard": {"id": "svalbard", "name": "Svalbard", "latitude": 78.22, "longitude": 15.65},
    "tromso":   {"id": "tromso",   "name": "Tromso",   "latitude": 69.65, "longitude": 18.96},
}

HOME = """<!doctype html>
<html>
<head><title>Practice API</title></head>
<body><h1>Practice API</h1><p>The stations are at <a href="/stations">/stations</a>.</p></body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    """Answers requests. The server creates a Handler for every connection it accepts."""

    protocol_version = "HTTP/1.1"

    def version_string(self):
        return "PracticeAPI/1.0"

    def date_time_string(self, timestamp=None):
        return DATE

    def log_message(self, format, *args):
        """Say nothing. A real server logs every request; here that would clutter the notebook."""

    def route(self):
        """The path without its query, and the path split into its segments."""
        path = self.path.split("?", 1)[0]
        return path, [p for p in path.split("/") if p]

    def do_GET(self):
        path, parts = self.route()
        if not parts:
            self.reply(200, HOME, "text/html; charset=utf-8")
        elif parts == ["stations"]:
            self.reply_json(200, [{"id": s["id"], "name": s["name"]} for s in STATIONS.values()])
        elif len(parts) == 2 and parts[0] == "stations":
            if parts[1] in STATIONS:
                self.reply_json(200, STATIONS[parts[1]])
            else:
                self.reply_json(404, {"error": f"no station with id {parts[1]!r}"})
        else:
            self.reply_json(404, {"error": f"nothing at {path}"})

    def refuse(self):
        """Every method but GET. The endpoints above are read-only, and nothing else exists yet."""
        self.discard_body()
        path, parts = self.route()
        if not parts or (parts[0] == "stations" and len(parts) <= 2):
            self.reply_json(405, {"error": f"{self.command} not allowed: the stations are read-only"},
                            Allow="GET")
        else:
            self.reply_json(404, {"error": f"nothing at {path}"})

    do_POST = do_PUT = do_PATCH = do_DELETE = refuse

    def discard_body(self):
        """Read and drop a request body, so it cannot be mistaken for the next request."""
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)

    def reply_json(self, status, body, **headers):
        self.reply(status, json.dumps(body), "application/json", **headers)

    def reply(self, status, text, content_type, **headers):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)


class Server(ThreadingHTTPServer):
    allow_reuse_port = False       # never share a port with another server, even where allowed
    daemon_threads = True


_server = None


def start():
    """Start the practice API, once per Python process, and return its address."""
    global _server
    if _server is None:
        for port in PORTS:
            try:
                _server = Server((HOST, port), Handler)
                break
            except OSError:        # the port is taken, perhaps by another notebook's practice API
                continue
        else:
            raise RuntimeError(f"no free port for the practice API in {PORTS}")
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    host, port = _server.server_address[:2]
    return f"http://{host}:{port}"
