<!-- version 4 -->
# marquee-shot (optional ESP-panel sidecar)

Renders Marquee's real card page to `card.jpg` and serves it, so an ESP32 panel
can display the pixel-perfect card instead of reconstructing it. **Optional** —
Nest Hub users never need it.

It is a **decoupled add-on**: it talks to Marquee only over HTTP and never
modifies it, so it runs alongside **any Marquee — including the upstream image**
(no fork of the app required, and it inherits card design changes for free).
Published image: `ghcr.io/trusselo/marquee-shot`.

## How it works

A warm headless-Chromium page stays open on `${MARQUEE_URL}/image` (the same card
the Nest Hub loads). On a play-aware loop it screenshots that page to `card.jpg`
and serves it from a tiny stdlib HTTP server. Marquee itself is untouched.

Endpoints (on `SERVE_PORT`):
- `GET /card.jpg` — the current 800×480 card image.
- `GET /state.json` — `{"ver": N, "cver": M, "playing": bool, "paused": bool}`.
  - `ver` bumps on every new frame → the panel polls this cheaply and only
    re-downloads `card.jpg` when `ver` changes.
  - `cver` bumps only when the item (title/episode) changes → the panel uses it
    to flash the backlight on a new title.
  - `paused` lets the panel brighten to 100% while paused.

## Enable it (pick your platform)

Point it at a running Marquee via `MARQUEE_URL` (with host networking that's
usually `http://127.0.0.1:8084`). Disable = stop/remove the container; Marquee is
never affected.

**Unraid (Docker tab / Community Applications):** add `unraid/marquee-shot.xml`
— Add Container → paste the template URL, or drop the file in
`/boot/config/plugins/dockerMan/templates-user/` — then set *Marquee URL* + panel
size and apply.

**Plain `docker run`:**

    docker run -d --name marquee-shot --network host --restart unless-stopped \
      -e MARQUEE_URL=http://127.0.0.1:8084 \
      -e PANEL_WIDTH=800 -e PANEL_HEIGHT=480 -e SERVE_PORT=8088 \
      ghcr.io/trusselo/marquee-shot:latest

**Docker Compose** (this repo, for dev/deploy) — opt-in via the `panel` profile,
so a plain `docker compose up -d` never starts it:

    docker compose --profile panel up -d --build

## Environment

| Var | Default | Meaning |
|-----|---------|---------|
| `MARQUEE_URL` | `http://127.0.0.1:8084` | Marquee base URL |
| `PANEL_WIDTH` / `PANEL_HEIGHT` | `800` / `480` | render size = your panel's pixels |
| `POLL_EVERY` | `1` | seconds between now-playing checks (state-change reaction) |
| `PROGRESS_EVERY` | `60` | seconds between progress-bar heartbeat re-renders |
| `SEEK_MS` | `5000` | position jump (ms) treated as a seek → immediate re-render |
| `JPEG_QUALITY` | `85` | output JPEG quality |
| `SERVE_PORT` | `8088` | port that serves `/card.jpg` |
| `SETTLE_SECONDS` | `0.8` | delay after reload before capture, so the card is fresh |

Re-renders happen on **state change** (play/pause/stop/title/seek), when enhanced
viewer/device/playback/track data changes, and whenever saved Design settings
or the custom-backdrop version changes. This keeps the ESPHome panel current
without waiting for the slower `PROGRESS_EVERY` heartbeat. Chromium is idle
when nothing is playing.

This enhanced source package tags its locally built sidecar as
`marquee-shot:esp32-enhanced-v3`. Use `--build` with the Compose command so the
metadata-aware capture code in this directory is used instead of the original
published image.

**Other displays:** set `PANEL_WIDTH`/`PANEL_HEIGHT` to your panel's resolution —
the card is responsive and reflows to it. No code changes.

## Test

    python3 shot.py --selftest      # pure logic, no browser/network needed
    python3 shot.py --once out.jpg  # one render (needs Playwright + Chromium)
