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
    GET /status/<code>           any status code from 200 to 599, with the headers and body a real
                                 server sends with that code, for seeing what a client does with it
    GET /echo                    the query the request arrived with, as sent and decoded, for
                                 seeing what a server receives

The stations are reference data, and read-only. Any other method on these endpoints gets
405 Method Not Allowed, with an Allow header naming the method that is allowed. Endpoints
added later for POST, PUT and DELETE use other paths, so what these return never changes.

The OpenAPI document describes the stations endpoints. The old /v0 addresses, /status, /echo
and the recording are left out of it.

OPEN-METEO. Public services have outages. open_meteo() sends every request the recording holds
to Open-Meteo's archive at once, and returns the archive's address if every response comes back
as JSON within 10 seconds. If one does not, it prints why and returns the address of the
recording instead, which answers the requests this guide makes exactly as Open-Meteo did.
Setting the environment variable OPEN_METEO_RECORDING to 1 skips the live service, which is how
to test that path.

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
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlencode

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

# /status/<code> sends the phrases RFC 9110 gives. Python 3.13 renamed four in its own table, so
# they are fixed here, and a response reads the same on every Python version.
PHRASES = {status.value: status.phrase for status in HTTPStatus} | {
    413: "Content Too Large", 414: "URI Too Long", 416: "Range Not Satisfiable",
    422: "Unprocessable Content",
}

# What an API says went wrong, for the codes a client meets most. Other codes give their phrase.
STATUS_ERRORS = {
    400: "the request is malformed",
    401: "the request needs a valid API key",
    403: "the API key does not allow this request",
    404: "the resource does not exist",
    405: "that method is not allowed here",
    409: "the request conflicts with the resource's current state",
    410: "the resource has been removed, permanently",
    422: "a value in the request is invalid",
    429: "too many requests: wait 30 seconds before sending another",
    500: "the server failed while handling the request",
    503: "the service is down for maintenance: try again in 120 seconds",
}

# The headers a real server sends with these codes.
STATUS_HEADERS = {
    401: {"WWW-Authenticate": "Bearer"},
    405: {"Allow": "GET"},
    429: {"Retry-After": "30"},
    503: {"Retry-After": "120"},
}

# A 502 or 504 comes from a gateway in front of an API, so its body is the gateway's HTML page.
GATEWAY_FAILURES = {
    502: "The server in front of the API received an invalid response from it.",
    504: "The server in front of the API received no response from it in time.",
}

LIVE_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"

# The part of every request this guide makes to Open-Meteo that never changes.
RECORDED_QUERY = {"start_date": "2025-01-15", "end_date": "2025-01-17", "models": "era5"}

# Daily variables Open-Meteo's archive accepts. The recording answers a request naming any other
# with the 400 Open-Meteo sends, and a request for these that it does not hold with a 404.
DAILY_VARIABLES = {
    "apparent_temperature_max", "apparent_temperature_mean", "apparent_temperature_min",
    "daylight_duration", "et0_fao_evapotranspiration", "precipitation_hours", "precipitation_sum",
    "rain_sum", "shortwave_radiation_sum", "snowfall_sum", "sunrise", "sunset",
    "sunshine_duration", "temperature_2m_max", "temperature_2m_mean", "temperature_2m_min",
    "weather_code", "wind_direction_10m_dominant", "wind_gusts_10m_max", "wind_speed_10m_max",
}

# RECORDING BEGINS
# Recorded from Open-Meteo's archive on 14 September 2026: the requests this guide makes, keyed
# by latitude, longitude, temperature unit and daily variables, with each body exactly as
# Open-Meteo sent it. Weather data by Open-Meteo.com, under CC BY 4.0, from the ERA5
# reanalysis. Generated using Copernicus Climate Change Service information 2026.
RECORDING = {
    (59.91, 10.75, 'celsius', 'temperature_2m_mean'): '{"latitude":60.0,"longitude":10.75,"generationtime_ms":11423.548936843872,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[0.0,2.3,3.0]}}',
    (60.39, 5.32, 'celsius', 'temperature_2m_mean'): '{"latitude":60.5,"longitude":5.25,"generationtime_ms":0.032067298889160156,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":17.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[7.8,8.0,8.0]}}',
    (60.39, 5.32, 'fahrenheit', 'temperature_2m_mean'): '{"latitude":60.5,"longitude":5.25,"generationtime_ms":0.06628036499023438,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":17.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°F"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[46.0,46.3,46.4]}}',
    (69.65, 18.96, 'celsius', 'temperature_2m_mean'): '{"latitude":69.75,"longitude":19.0,"generationtime_ms":22564.093947410583,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[4.6,6.4,7.1]}}',
    (69.65, 18.96, 'fahrenheit', 'temperature_2m_mean'): '{"latitude":69.75,"longitude":19.0,"generationtime_ms":0.042557716369628906,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°F"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[40.3,43.5,44.8]}}',
    (78.22, 15.65, 'celsius', 'temperature_2m_mean'): '{"latitude":78.25,"longitude":15.75,"generationtime_ms":21258.768439292908,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":21.0,"daily_units":{"time":"iso8601","temperature_2m_mean":"°C"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_mean":[-12.9,-12.8,-13.8]}}',
    (60.39, 5.32, 'celsius', 'temperature_2m_max,temperature_2m_min,precipitation_sum'): '{"latitude":60.5,"longitude":5.25,"generationtime_ms":0.14603137969970703,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":17.0,"daily_units":{"time":"iso8601","temperature_2m_max":"°C","temperature_2m_min":"°C","precipitation_sum":"mm"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_max":[8.3,8.2,8.9],"temperature_2m_min":[6.9,7.6,6.4],"precipitation_sum":[13.20,5.60,4.00]}}',
    (59.91, 10.75, 'celsius', 'temperature_2m_max,temperature_2m_min,precipitation_sum'): '{"latitude":60.0,"longitude":10.75,"generationtime_ms":0.3198385238647461,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_max":"°C","temperature_2m_min":"°C","precipitation_sum":"mm"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_max":[2.8,3.2,4.8],"temperature_2m_min":[-3.6,1.3,1.4],"precipitation_sum":[0.10,0.00,0.30]}}',
    (78.22, 15.65, 'celsius', 'temperature_2m_max,temperature_2m_min,precipitation_sum'): '{"latitude":78.25,"longitude":15.75,"generationtime_ms":0.22172927856445312,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":21.0,"daily_units":{"time":"iso8601","temperature_2m_max":"°C","temperature_2m_min":"°C","precipitation_sum":"mm"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_max":[-11.0,-12.3,-12.1],"temperature_2m_min":[-13.6,-13.1,-15.1],"precipitation_sum":[0.40,5.70,4.70]}}',
    (69.65, 18.96, 'celsius', 'temperature_2m_max,temperature_2m_min,precipitation_sum'): '{"latitude":69.75,"longitude":19.0,"generationtime_ms":0.18298625946044922,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":9.0,"daily_units":{"time":"iso8601","temperature_2m_max":"°C","temperature_2m_min":"°C","precipitation_sum":"mm"},"daily":{"time":["2025-01-15","2025-01-16","2025-01-17"],"temperature_2m_max":[6.5,7.1,8.6],"temperature_2m_min":[2.7,5.8,6.2],"precipitation_sum":[23.70,21.10,18.80]}}',
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
            station_id = unquote(parts[1])          # a path parameter arrives percent-encoded
            if station_id in STATIONS:
                self.reply_json(200, STATIONS[station_id])
            else:
                self.reply_json(404, {"error": f"no station with id {station_id!r}"})
        elif parts == ["echo"]:
            query = self.path.partition("?")[2]
            self.reply_json(200, {"query": query, "args": parse_qs(query, keep_blank_values=True)})
        elif len(parts) == 2 and parts[0] == "status":
            self.status(parts[1])
        else:
            self.reply_json(404, {"error": f"nothing at {path}"})

    def status(self, value):
        """Respond with the status code the path names, as a real server sends that code.

        For seeing what a client does with a status code, without waiting for a server to fail.
        Each response carries what a real one usually does: Retry-After on 429 and 503,
        WWW-Authenticate on 401, Allow on 405, no body on 204 and 304, a Location on the other
        3xx codes, and on 502 and 504 an HTML page, because those come from a gateway in front
        of an API rather than from the API itself.
        """
        if not (value.isascii() and value.isdigit() and 200 <= int(value) <= 599):
            self.reply_json(400, {"error": f"the status must be a number from 200 to 599, not {value!r}"})
            return
        code = int(value)
        phrase = PHRASES.get(code, "")
        if code in (204, 304):                  # these never carry a body
            self.send_response(code, phrase)
            self.end_headers()
        elif code // 100 == 3:
            self.send_response(code, phrase)
            self.send_header("Location", "/status/200")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif code in GATEWAY_FAILURES:
            page = (f"<!doctype html>\n<html>\n<head><title>{code} {phrase}</title></head>\n"
                    f"<body><h1>{code} {phrase}</h1><p>{GATEWAY_FAILURES[code]}</p></body>\n</html>\n")
            self.reply(code, page, "text/html; charset=utf-8", reason=phrase)
        elif code // 100 == 2:
            self.reply_json(code, {"status": code, "reason": phrase}, reason=phrase)
        else:
            error = STATUS_ERRORS.get(code) or phrase or f"status {code}"
            self.reply_json(code, {"error": error}, reason=phrase, **STATUS_HEADERS.get(code, {}))

    def recorded_archive(self):
        """Answer a request as Open-Meteo's archive answered it, from the recording.

        Three behaviors of the real service are copied because notebooks show them: a parameter it
        does not recognize is ignored, several daily variables can be asked for at once, as a
        comma-separated value or a repeated name, and a daily value naming a variable it does not
        have gets a 400 with a reason. A request the guide does not make gets a 404 saying so.
        """
        values = parse_qs(self.path.partition("?")[2])
        query = {name: found[-1] for name, found in values.items()}
        daily = ",".join(values["daily"]) if "daily" in values else None
        if daily is not None and not set(daily.split(",")) <= DAILY_VARIABLES:
            reason = ("Invalid value: Cannot initialize ForecastVariableDaily from invalid String "
                      f"value {daily}")
            body = json.dumps({"error": True, "reason": reason}, separators=(",", ":"))
            self.reply(400, body, "application/json; charset=utf-8")
            return
        try:
            key = (float(query["latitude"]), float(query["longitude"]),
                   query.get("temperature_unit", "celsius"), daily)
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

    def reply_json(self, status, body, reason=None, **headers):
        self.reply(status, json.dumps(body), "application/json", reason, **headers)

    def reply(self, status, text, content_type, reason=None, **headers):
        """Send a response. Without a reason, the status line takes Python's phrase for the code."""
        data = text.encode("utf-8")
        self.send_response(status, reason)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(data)


class Server(ThreadingHTTPServer):
    allow_reuse_port = False       # never share a port with another server, even where allowed
    daemon_threads = True


# Kept when Setup reloads this module, so the reloaded copy can find the server already running.
_server = globals().get("_server")


def start():
    """Start the practice API, once per Python process, and return its address.

    Setup reloads this module every time it runs, so that a newer copy of the file takes effect in
    a session that imported an older one. A server started by an earlier copy is then still
    answering with the earlier code, so it is stopped and replaced, on the same port.
    """
    global _server
    ports = list(PORTS)
    if _server is not None and _server.RequestHandlerClass is not Handler:
        ports.insert(0, _server.server_address[1])
        _server.shutdown()
        _server.server_close()
        _server = None
    if _server is None:
        for port in ports:
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
        latitude, longitude, unit, daily = key
        query = {"latitude": latitude, "longitude": longitude, **RECORDED_QUERY, "daily": daily}
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
