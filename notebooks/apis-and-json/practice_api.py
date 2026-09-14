"""A practice web API for the APIs and JSON guide.

Every notebook in the guide starts this in its Setup cell:

    import practice_api
    BASE = practice_api.start()            # "http://127.0.0.1:8765"
    OPEN_METEO = practice_api.open_meteo()

It runs inside the notebook's own Python process, listening on 127.0.0.1, the address a
computer uses to reach itself. In Colab that computer is Colab's, so nothing runs on yours.
It serves the weather stations used throughout this library, and it responds to every reader
the same way, which is what lets a notebook show an error on purpose.

Endpoints:

    GET /                        a short HTML page, the kind a person would read
    GET /stations                every station, as a list of {"id", "name"}
    GET /stations/<id>           one station, or 404 if no station has that id
    GET /openapi.json            this API's own documentation, as an OpenAPI document
    GET /v0/<path>               an old address: 301 Moved Permanently, to the path without /v0
    GET /open-meteo/v1/archive   a recording of Open-Meteo's archive, for when the real one is down

The stations are reference data, and read-only. Any other method on these endpoints gets
405 Method Not Allowed, with an Allow header naming the method that is allowed. Endpoints
added later for POST, PUT and DELETE use other paths, so what these return never changes.

The OpenAPI document describes the stations endpoints. The old /v0 addresses and the recording
are left out of it.

OPEN-METEO. Public services have outages. open_meteo() sends a request the guide makes to
Open-Meteo's archive, once, and returns the archive's address if the answer comes back. If it
does not, it prints why and returns the address of the recording instead, which answers the
requests this guide makes exactly as Open-Meteo did. Setting the environment variable
OPEN_METEO_RECORDING to 1 skips the live service, which is how to test that path.

To use a tool such as Postman, which cannot reach a server running inside Colab, run this
file on your own computer instead:

    python practice_api.py

Two details differ from a real server, both so that the output printed in a notebook matches
what you see when you run it: the Date header always reports the same moment, and the Server
header does not name a Python version.

Standard library only, so it runs wherever Python does.
"""

import json
import os
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode

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

LIVE_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"

# The part of every request this guide makes to Open-Meteo that never changes.
RECORDED_QUERY = {"start_date": "2025-01-15", "end_date": "2025-01-17",
                  "daily": "temperature_2m_mean", "models": "era5"}

# RECORDING BEGINS
# Recorded from Open-Meteo's archive on 14 September 2026: the requests this guide makes, keyed
# by latitude, longitude and temperature unit, with each body exactly as Open-Meteo sent it.
# Weather data by Open-Meteo.com, under CC BY 4.0, from the ERA5 reanalysis. Generated using
# Copernicus Climate Change Service information 2026.
RECORDING = {
    (59.91, 10.75, 'celsius'): '{"latitude":60.0,"longitude":10.75,"generationtime_ms":11423.548936843872,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[0.0,2.3,3.0]}}',
    (60.39, 5.32, 'celsius'): '{"latitude":60.5,"longitude":5.25,"generationtime_ms":0.032067298889160156,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":17.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[7.8,8.0,8.0]}}',
    (60.39, 5.32, 'fahrenheit'): '{"latitude":60.5,"longitude":5.25,"generationtime_ms":0.06628036499023438,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":17.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°F"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[46.0,46.3,46.4]}}',
    (69.65, 18.96, 'celsius'): '{"latitude":69.75,"longitude":19.0,"generationtime_ms":22564.093947410583,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[4.6,6.4,7.1]}}',
    (69.65, 18.96, 'fahrenheit'): '{"latitude":69.75,"longitude":19.0,"generationtime_ms":0.042557716369628906,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°F"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[40.3,43.5,44.8]}}',
    (78.22, 15.65, 'celsius'): '{"latitude":78.25,"longitude":15.75,"generationtime_ms":21258.768439292908,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":21.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[-12.9,-12.8,-13.8]}}',
}
# RECORDING ENDS


def openapi(base):
    """This API's documentation, as an OpenAPI 3.1 document, for a server at `base`."""
    def ref(name):
        return {"$ref": f"#/components/schemas/{name}"}

    def json_response(description, schema):
        return {"description": description, "content": {"application/json": {"schema": schema}}}

    return {
        "openapi": "3.1.0",
        "info": {"title": "Practice API", "version": "1.0",
                 "description": "Weather stations, for the APIs and JSON guide."},
        "servers": [{"url": base}],
        "paths": {
            "/stations": {"get": {
                "operationId": "listStations",
                "summary": "List every station",
                "responses": {
                    "200": json_response("A summary of every station",
                                         {"type": "array", "items": ref("StationSummary")}),
                },
            }},
            "/stations/{id}": {"get": {
                "operationId": "getStation",
                "summary": "Get one station",
                "parameters": [{"name": "id", "in": "path", "required": True,
                                "description": "The station's id, in lowercase",
                                "schema": {"type": "string"}, "example": "tromso"}],
                "responses": {
                    "200": json_response("The station", ref("Station")),
                    "404": json_response("No station has that id", ref("Error")),
                },
            }},
        },
        "components": {"schemas": {
            "StationSummary": {"type": "object", "required": ["id", "name"],
                               "properties": {"id": {"type": "string"},
                                              "name": {"type": "string"}}},
            "Station": {"type": "object", "required": ["id", "name", "latitude", "longitude"],
                        "properties": {"id": {"type": "string"}, "name": {"type": "string"},
                                       "latitude": {"type": "number"},
                                       "longitude": {"type": "number"}}},
            "Error": {"type": "object", "required": ["error"],
                      "properties": {"error": {"type": "string"}}},
        }},
    }


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
        if parts[:1] == ["v0"]:
            self.moved("/" + "/".join(parts[1:]))
        elif not parts:
            self.reply(200, HOME, "text/html; charset=utf-8")
        elif parts == ["openapi.json"]:
            host, port = self.server.server_address[:2]
            self.reply_json(200, openapi(f"http://{host}:{port}"))
        elif parts == ["open-meteo", "v1", "archive"]:
            self.recorded_archive()
        elif parts == ["stations"]:
            self.reply_json(200, [{"id": s["id"], "name": s["name"]} for s in STATIONS.values()])
        elif len(parts) == 2 and parts[0] == "stations":
            if parts[1] in STATIONS:
                self.reply_json(200, STATIONS[parts[1]])
            else:
                self.reply_json(404, {"error": f"no station with id {parts[1]!r}"})
        else:
            self.reply_json(404, {"error": f"nothing at {path}"})

    def recorded_archive(self):
        """Answer a request as Open-Meteo's archive answered it, from the recording.

        Two behaviors of the real service are copied because notebooks show them: a parameter
        it does not recognize is ignored, and a daily variable it does not recognize gets a 400
        with a reason. A request the guide does not make gets a 404 saying so.
        """
        query = {name: values[-1] for name, values in parse_qs(self.path.partition("?")[2]).items()}
        daily = query.get("daily")
        if daily is not None and daily != RECORDED_QUERY["daily"]:
            reason = ("Invalid value: Cannot initialize ForecastVariableDaily from invalid String "
                      f"value {daily}")
            body = json.dumps({"error": True, "reason": reason}, separators=(",", ":"))
            self.reply(400, body, "application/json; charset=utf-8")
            return
        try:
            key = (float(query["latitude"]), float(query["longitude"]),
                   query.get("temperature_unit", "celsius"))
        except (KeyError, ValueError):
            key = None
        same = all(query.get(name) == value for name, value in RECORDED_QUERY.items())
        if same and key in RECORDING:
            self.reply(200, RECORDING[key], "application/json; charset=utf-8")
        else:
            self.reply_json(404, {"error": True,
                                  "reason": "this recording holds only the requests the guide makes"})

    def refuse(self):
        """Every method but GET. The endpoints above are read-only, and nothing else exists yet."""
        self.discard_body()
        path, parts = self.route()
        if parts[:1] == ["v0"]:
            self.moved("/" + "/".join(parts[1:]))
        elif not parts or parts == ["openapi.json"] or (parts[0] == "stations" and len(parts) <= 2):
            self.reply_json(405, {"error": f"{self.command} not allowed: the stations are read-only"},
                            Allow="GET")
        else:
            self.reply_json(404, {"error": f"nothing at {path}"})

    do_POST = do_PUT = do_PATCH = do_DELETE = refuse

    def moved(self, location):
        """301 Moved Permanently: the resource now lives at `location`."""
        self.send_response(301)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

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


def open_meteo(timeout=10):
    """The address to send Open-Meteo requests to: its archive, or this API's recording of it.

    Sends Open-Meteo every request the recording holds, all at once, and returns the archive's
    address if every answer comes back as JSON within `timeout` seconds. A request Open-Meteo has
    just answered comes back quickly the next time, so this also readies the requests a notebook
    goes on to make. If any answer fails, prints why and returns the recording's address.

    Checking every request, not one, matters: while Open-Meteo is struggling, a request it answered
    recently can come back in half a second while another takes half a minute and fails.
    """
    from concurrent.futures import ThreadPoolExecutor

    def attempt(key):
        latitude, longitude, unit = key
        query = {"latitude": latitude, "longitude": longitude, **RECORDED_QUERY}
        if unit != "celsius":
            query["temperature_unit"] = unit
        try:
            with urllib.request.urlopen(f"{LIVE_ARCHIVE}?{urlencode(query)}", timeout=timeout) as response:
                json.loads(response.read())
        except urllib.error.HTTPError as error:
            return f"Open-Meteo responded with status {error.code}"
        except (TimeoutError, urllib.error.URLError) as error:
            if isinstance(error, TimeoutError) or isinstance(getattr(error, "reason", None), TimeoutError):
                return f"Open-Meteo did not respond within {timeout} seconds"
            return "Open-Meteo could not be reached"
        except ValueError:
            return "Open-Meteo sent something other than JSON"
        return None

    if os.environ.get("OPEN_METEO_RECORDING") == "1":
        why = "OPEN_METEO_RECORDING is set"
    else:
        with ThreadPoolExecutor(max_workers=max(1, len(RECORDING))) as pool:
            failures = [result for result in pool.map(attempt, RECORDING) if result]
        if not failures:
            return LIVE_ARCHIVE
        why = failures[0]
    print(f"{why}, so the Open-Meteo cells in this notebook use the practice API's recording of "
          "its responses.")
    return f"{start()}/open-meteo/v1/archive"


if __name__ == "__main__":
    print(f"The practice API is running at {start()}. Press Ctrl+C to stop it.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("Stopped.")
