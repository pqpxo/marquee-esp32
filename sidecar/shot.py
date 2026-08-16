#!/usr/bin/env python3
# version 4
"""marquee-shot: screenshot Marquee's card page and serve it as card.jpg.

Pure logic + stdlib only at import time. Playwright is imported lazily inside
the renderer so `--selftest` runs anywhere with just Python 3.

Cadence: poll now-playing.json fast (POLL_EVERY); re-render only when the state
meaningfully changes (play/pause/stop/title/EPISODE/viewer/device/stream/tracks/
design/custom backdrop/seek) so those show quickly, plus a slow PROGRESS_EVERY
heartbeat for the creeping progress bar. Idle -> one frame, then Chromium sleeps.

Serves two routes:
  /card.jpg    the current 800x480 card image
  /state.json  {"ver": N, "cver": M, "playing": bool, "paused": bool}
               ver  bumps on every new frame (client re-fetches card.jpg on change)
               cver bumps only when the item (title/episode) changes (client can
                    use it to flash the backlight on a new title)
"""
import os
import sys
import json
import time
import threading
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def cfg():
    """Read all knobs from the environment, with defaults."""
    return {
        "url": os.environ.get("MARQUEE_URL", "http://127.0.0.1:8084").rstrip("/"),
        "width": int(os.environ.get("PANEL_WIDTH", "800")),
        "height": int(os.environ.get("PANEL_HEIGHT", "480")),
        "quality": int(os.environ.get("JPEG_QUALITY", "85")),
        "port": int(os.environ.get("SERVE_PORT", "8088")),
        "settle": float(os.environ.get("SETTLE_SECONDS", "0.8")),
        "poll_every": float(os.environ.get("POLL_EVERY", "1")),        # now-playing check
        "progress_every": float(os.environ.get("PROGRESS_EVERY", "60")),  # progress heartbeat
        "seek_ms": int(os.environ.get("SEEK_MS", "5000")),             # jump = seek
    }


def content_signature(np, design=None):
    """Stable signature of display metadata or saved design changes.

    Progress is deliberately excluded: it is handled by the slower heartbeat
    and seek detector. The enhanced Designer blocks are sourced from these
    three objects. The settings document covers block layout, fonts, panel
    styling, and the custom-backdrop version, so any visible design change also
    bumps the screenshot version consumed by the ESPHome panel.
    """
    return json.dumps({
        "design": design or {},
        "session": np.get("session") or {},
        "stream": np.get("stream") or {},
        "tracks": np.get("tracks") or {},
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def card_state(np, design=None):
    """Extract the fields that decide when to re-render, from now-playing.json.

    `key` is Marquee's unique item Id, so a new EPISODE (same show title, new key)
    is detected. `paused` is derived from `state` ("paused"/"playing").
    """
    prog = np.get("progress") or {}
    state = str(np.get("state", ""))
    return {
        "playing": bool(np.get("playing", False)),
        "state": state,
        "paused": "paus" in state.lower(),
        "title": str(np.get("title", "")),
        "key": str(np.get("key", "")),
        "offset": int(prog.get("offsetMs", 0) or 0),
        "content_sig": content_signature(np, design),
    }


def hard_change(prev, cur):
    """True for playback or displayed metadata changes that must show fast."""
    return (prev["playing"] != cur["playing"]
            or prev["state"] != cur["state"]
            or prev["title"] != cur["title"]
            or prev["key"] != cur["key"]
            or prev["content_sig"] != cur["content_sig"])


def is_seek(prev, cur, elapsed_s, seek_ms):
    """True when position jumped more than normal playback would explain.

    Frozen offset (paused/buffering) is NOT a seek, even after a long gap.
    """
    if not (prev["playing"] and cur["playing"]):
        return False
    if cur["offset"] == prev["offset"]:
        return False
    expected = prev["offset"] + int(elapsed_s * 1000)
    return abs(cur["offset"] - expected) > seek_ms


def fetch_json(url, timeout=5):
    """GET url and parse JSON. Raises on network/parse error (caller handles)."""
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


_latest = {"jpg": None, "ver": 0, "cver": 0, "playing": False, "paused": False, "key": ""}
_latest_lock = threading.Lock()


def publish(jpg, playing, paused, key):
    """Publish a frame: bump ver always, and cver only when the item changes."""
    with _latest_lock:
        _latest["jpg"] = jpg
        _latest["ver"] += 1
        _latest["playing"] = bool(playing)
        _latest["paused"] = bool(paused)
        if key and key != _latest["key"]:      # new title/episode
            _latest["cver"] += 1
            _latest["key"] = key


class CardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/state.json":
            with _latest_lock:
                body = json.dumps({
                    "ver": _latest["ver"],
                    "cver": _latest["cver"],
                    "playing": _latest["playing"],
                    "paused": _latest["paused"],
                }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if path != "/card.jpg":
            self.send_error(404, "only /card.jpg or /state.json")
            return
        with _latest_lock:
            jpg = _latest["jpg"]
        if jpg is None:
            self.send_error(503, "no frame captured yet")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(jpg)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(jpg)

    def log_message(self, *a):
        pass


def serve(port):
    ThreadingHTTPServer(("", port), CardHandler).serve_forever()


class Renderer:
    """One warm headless-Chromium page held open on the card URL."""

    def __init__(self, url, width, height, quality):
        self.url = f"{url}/image"
        self.width = width
        self.height = height
        self.quality = quality
        self._pw = self._browser = self._page = None

    def start(self):
        from playwright.sync_api import sync_playwright  # lazy: keeps --selftest dep-free
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=True, channel="chromium-headless-shell",
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        self._page = self._browser.new_page(
            viewport={"width": self.width, "height": self.height},
            device_scale_factor=1,
        )
        self._page.goto(self.url, wait_until="networkidle", timeout=30000)

    def reload(self):
        """Force the card to re-fetch now-playing + re-render (fresh capture)."""
        self._page.reload(wait_until="networkidle", timeout=30000)

    def capture(self):
        return self._page.screenshot(type="jpeg", quality=self.quality)

    def alive(self):
        try:
            return self._page is not None and not self._page.is_closed()
        except Exception:
            return False

    def stop(self):
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._pw:
                self._pw.stop()
        except Exception:
            pass


def run():
    c = cfg()
    print(f"marquee-shot: {c['url']}/image -> :{c['port']}/card.jpg @ "
          f"{c['width']}x{c['height']}  poll {c['poll_every']}s  "
          f"progress {c['progress_every']}s", flush=True)
    threading.Thread(target=serve, args=(c["port"],), daemon=True).start()

    r = Renderer(c["url"], c["width"], c["height"], c["quality"])
    r.start()

    def do_capture(st):
        r.reload()
        time.sleep(c["settle"])
        publish(r.capture(), st["playing"], st["paused"], st["key"])

    prev = None
    prev_mono = time.monotonic()
    last_capture = 0.0
    idle_captured = False
    while True:
        try:
            if not r.alive():
                print("renderer died; relaunching", flush=True)
                r.stop()
                r = Renderer(c["url"], c["width"], c["height"], c["quality"])
                r.start()
                prev = None  # force a fresh capture after relaunch

            playing_doc = fetch_json(f"{c['url']}/now-playing.json")
            design_doc = fetch_json(f"{c['url']}/settings.json")
            cur = card_state(playing_doc, design_doc)
            now = time.monotonic()
            elapsed = now - prev_mono

            reason = None
            if prev is None or hard_change(prev, cur):
                reason = "state"
            elif is_seek(prev, cur, elapsed, c["seek_ms"]):
                reason = "seek"
            elif cur["playing"] and (now - last_capture) >= c["progress_every"]:
                reason = "progress"
            elif (not cur["playing"]) and not idle_captured:
                reason = "idle"

            if reason:
                do_capture(cur)
                last_capture = now
                idle_captured = not cur["playing"]
                print(f"captured ({reason})", flush=True)
            prev, prev_mono = cur, now
        except Exception as e:
            print(f"loop error: {e}", flush=True)
        time.sleep(c["poll_every"])


def _selftest():
    # card_state extracts exactly the fields we key on, including enhanced
    # viewer/stream/track metadata but excluding normal progress movement.
    s = card_state({"playing": True, "state": "playing", "title": "X", "key": "k1",
                    "progress": {"offsetMs": 12000},
                    "session": {"user": "Sam", "device": "CrowPanel"},
                    "stream": {"decision": "Direct Play"},
                    "tracks": {"audio": {"codec": "EAC3"}}},
                   {"template": "spotlight", "customBackdropVersion": "7"})
    assert s == {"playing": True, "state": "playing", "paused": False, "title": "X",
                 "key": "k1", "offset": 12000,
                 "content_sig": ('{"design":{"customBackdropVersion":"7",'
                                 '"template":"spotlight"},'
                                 '"session":{"device":"CrowPanel","user":"Sam"},'
                                 '"stream":{"decision":"Direct Play"},'
                                 '"tracks":{"audio":{"codec":"EAC3"}}}')}, s
    assert card_state({}) == {"playing": False, "state": "", "paused": False,
                              "title": "", "key": "", "offset": 0,
                              "content_sig": ('{"design":{},"session":{},"stream":{},'
                                              '"tracks":{}}')}
    assert card_state({"playing": True, "state": "paused"})["paused"] is True

    # hard_change: play/pause/stop/title/EPISODE flip true; advancing offset does not.
    base = card_state({"playing": True, "state": "playing", "title": "X", "key": "k1",
                       "progress": {"offsetMs": 1000}})
    assert hard_change(base, card_state({"playing": True, "state": "paused",
                       "title": "X", "key": "k1", "progress": {"offsetMs": 1000}})) is True
    assert hard_change(base, card_state({"playing": False})) is True
    assert hard_change(base, card_state({"playing": True, "state": "playing",
                       "title": "Y", "key": "k2", "progress": {"offsetMs": 1000}})) is True
    assert hard_change(base, card_state({"playing": True, "state": "playing",
                       "title": "X", "key": "k2", "progress": {"offsetMs": 1000}})) is True, \
        "same show, new episode (new key) is a hard change"
    assert hard_change(base, card_state({"playing": True, "state": "playing",
                       "title": "X", "key": "k1", "progress": {"offsetMs": 4000}})) is False, \
        "advancing offset is not a hard change"
    assert hard_change(base, card_state({
        "playing": True, "state": "playing", "title": "X", "key": "k1",
        "progress": {"offsetMs": 1000},
        "session": {"user": "Sam", "device": "CrowPanel"}})) is True, \
        "viewer/device change must refresh the panel immediately"
    stream_base = card_state({
        "playing": True, "state": "playing", "title": "X", "key": "k1",
        "stream": {"decision": "Direct Play"},
        "tracks": {"audio": {"codec": "EAC3"}}})
    assert hard_change(stream_base, card_state({
        "playing": True, "state": "playing", "title": "X", "key": "k1",
        "stream": {"decision": "Transcoding"},
        "tracks": {"audio": {"codec": "EAC3"}}})) is True
    assert hard_change(stream_base, card_state({
        "playing": True, "state": "playing", "title": "X", "key": "k1",
        "stream": {"decision": "Direct Play"},
        "tracks": {"audio": {"codec": "AAC"}}})) is True
    assert hard_change(base, card_state({
        "playing": True, "state": "playing", "title": "X", "key": "k1",
        "progress": {"offsetMs": 1000}},
        {"customBackdropVersion": "new", "template": "spotlight"})) is True, \
        "saved layout or custom-art change must refresh the panel immediately"

    # is_seek: normal advance = no; big jump = yes; frozen (paused) = no.
    p = card_state({"playing": True, "state": "playing", "title": "X", "key": "k1",
                    "progress": {"offsetMs": 10000}})
    normal = card_state({"playing": True, "state": "playing", "title": "X", "key": "k1",
                         "progress": {"offsetMs": 12000}})
    assert is_seek(p, normal, 2.0, 5000) is False, "advanced ~2s over 2s"
    jump = card_state({"playing": True, "state": "playing", "title": "X", "key": "k1",
                       "progress": {"offsetMs": 300000}})
    assert is_seek(p, jump, 2.0, 5000) is True, "jumped ~5min"
    frozen = card_state({"playing": True, "state": "playing", "title": "X", "key": "k1",
                         "progress": {"offsetMs": 10000}})
    assert is_seek(p, frozen, 30.0, 5000) is False, "frozen 30s = paused, not seek"

    # fetch_json round-trips JSON from a local ephemeral server.
    class _H(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b'{"playing": true, "title": "Family Guy", "key": "42", "progress": {"offsetMs": 42}}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *a):
            pass
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    got = card_state(fetch_json(f"http://127.0.0.1:{port}/now-playing.json"))
    assert got["playing"] is True and got["title"] == "Family Guy" and got["key"] == "42", got
    srv.shutdown()

    # File server + versioning: 503 before a frame; ver bumps per publish; cver
    # only on a new key; paused reflected.
    with _latest_lock:
        _latest.update({"jpg": None, "ver": 0, "cver": 0, "playing": False,
                        "paused": False, "key": ""})
    csrv = ThreadingHTTPServer(("127.0.0.1", 0), CardHandler)
    threading.Thread(target=csrv.serve_forever, daemon=True).start()
    cport = csrv.server_address[1]

    def _state():
        with urllib.request.urlopen(f"http://127.0.0.1:{cport}/state.json", timeout=5) as r:
            return json.loads(r.read())

    try:
        urllib.request.urlopen(f"http://127.0.0.1:{cport}/card.jpg", timeout=5)
        assert False, "expected 503 before first frame"
    except urllib.error.HTTPError as e:
        assert e.code == 503, e.code
    assert _state() == {"ver": 0, "cver": 0, "playing": False, "paused": False}
    publish(b"\xff\xd8\xff-frame1", True, False, "k1")     # new item
    assert _state() == {"ver": 1, "cver": 1, "playing": True, "paused": False}
    publish(b"\xff\xd8\xff-frame2", True, True, "k1")      # same item, now paused
    assert _state() == {"ver": 2, "cver": 1, "playing": True, "paused": True}
    publish(b"\xff\xd8\xff-frame3", True, False, "k2")     # new episode -> cver++
    assert _state() == {"ver": 3, "cver": 2, "playing": True, "paused": False}
    with urllib.request.urlopen(f"http://127.0.0.1:{cport}/card.jpg", timeout=5) as r:
        assert r.headers["Content-Type"] == "image/jpeg"
        assert r.read() == b"\xff\xd8\xff-frame3"
    csrv.shutdown()
    with _latest_lock:
        _latest.update({"jpg": None, "ver": 0, "cver": 0, "playing": False,
                        "paused": False, "key": ""})

    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
        sys.exit(0)
    c = cfg()
    if "--once" in sys.argv:
        idx = sys.argv.index("--once")
        out = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else "card.jpg"
        r = Renderer(c["url"], c["width"], c["height"], c["quality"])
        r.start()
        time.sleep(c["settle"])
        with open(out, "wb") as f:
            f.write(r.capture())
        r.stop()
        print(f"wrote {out} ({c['width']}x{c['height']})")
        sys.exit(0)
    run()
