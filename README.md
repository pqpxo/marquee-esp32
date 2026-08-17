<!-- version 5 -->
# Marquee ESP32 Enhanced

![Version](https://img.shields.io/badge/version-2.2.1--esp32--enhanced.4-E5A83B)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![ESPHome](https://img.shields.io/badge/ESPHome-CrowPanel-000000?logo=esphome&logoColor=white)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Marquee turns a Google Nest Hub, ESP32 display, or browser into a configurable
now-playing screen for **Plex**, **Emby**, or **Jellyfin**. It combines artwork,
title information, playback progress, ratings, weather, viewer/device details,
stream diagnostics, and optional custom artwork in a live visual Designer.

This enhanced edition is based on
[`TRusselo/marquee-esp32`](https://github.com/TRusselo/marquee-esp32), which is
itself based on [`Jamisonfitz/marquee`](https://github.com/Jamisonfitz/marquee)
v2.2.1. It retains the optional `marquee-shot` and ESPHome/CrowPanel workflow,
then adds the expanded Designer, session-aware blocks, custom backdrops,
display-size previews, improved Street controls, and responsive logo fitting.

> [!IMPORTANT]
> Marquee is intended for a trusted local network. It has no user login and its
> now-playing data can include viewer and device names. Do not port-forward it
> directly to the internet.

## Highlights

| Area | Included features |
|---|---|
| Media servers | Plex, Emby, and Jellyfin with a common now-playing format |
| Display targets | Google Nest Hub, Nest Hub Max, Elecrow CrowPanel 7, other ESP32 panels, and ordinary browsers |
| Designer | Live preview, drag-to-position, width, scale, alignment, colour, fonts, add/remove, snap-to-grid, presets, import, and export |
| Playback blocks | Viewer, Device, Stream, Active streams, and Audio & subtitles |
| Artwork | Poster, media backdrop, fanart.tv rotation, clear-logo fitting, and persistent custom backdrop uploads |
| Street template | Live weather effects, optional rain animation, movable poster-light frame, and movable NOW PLAYING sign |
| ESP32 output | Pixel-accurate JPEG rendering through `marquee-shot`, with lightweight state/version polling for ESPHome |
| Privacy controls | User/device allow-lists, do-not-cast content words, and write-only credentials |

## Enhanced v4 features

### Target-display preview

The Design preview can match the physical display instead of assuming one
fixed browser ratio. Layout positions and sizes remain separate per template.

| Preset | Resolution | Typical use |
|---|---:|---|
| CrowPanel 7 | **800 × 480** | Default; Elecrow CrowPanel 7 ESP32-S3 |
| Google Nest Hub | 1024 × 600 | Standard Nest Hub |
| Google Nest Hub Max | 1280 × 800 | Nest Hub Max |
| HD 16:9 | 1280 × 720 | Browser, TV, or HDMI panel |
| Full HD 16:9 | 1920 × 1080 | Full-HD browser or display |
| 4:3 | 800 × 600 | Traditional 4:3 panel |
| Custom | 320 × 240 to 3840 × 2160 | Other panels and browser windows |

Changing the preview size does not change the media output resolution by
itself. For `marquee-shot`, set `PANEL_WIDTH` and `PANEL_HEIGHT` to the same
values as the physical panel.

### New session and playback blocks

The following blocks are available through **Design → + Add**. They are off by
default so an upgraded installation keeps its existing appearance.

| Block | Information displayed |
|---|---|
| **Viewer** | Active username and, when sessions rotate, the selected position such as `2 of 3` |
| **Device** | Player/device name, client application, platform, and optional **Local** or **Remote** label |
| **Stream** | Direct Play, Direct Stream, or Transcoding; source/output resolution; HDR/Dolby Vision; codecs; bitrate/bandwidth; and hardware acceleration where reported |
| **Active streams** | Server-wide count of active movie or episode streams currently in progress |
| **Audio & subtitles** | Selected language, display title, codec, channels/layout, subtitle state, and Atmos where reported |

Viewer, Device, Stream, Active streams, and Audio & subtitles use a common card
height. Each has independent **Panel background** and **Panel border** switches,
allowing the content to appear as a card or directly over the design.

Data availability depends on the media server and playback client. Plex usually
provides the most complete Local/Remote and bandwidth information; Emby and
Jellyfin fields are displayed when their Sessions APIs report them rather than
being guessed.

### Separate Category and Title blocks

Genres such as `ACTION · CRIME · COMEDY` are no longer tied to the movie/show
title. **Category** and **Title** can be independently:

- moved horizontally and vertically;
- resized and scaled;
- aligned left, centre, or right;
- recoloured;
- assigned different fonts;
- removed or restored per template.

### Improved title logos

When **Use logo art** is enabled, the title image is placed in a bounded,
centred viewport instead of relying on the source image's dimensions.

- Transparent padding is automatically detected and trimmed in the browser.
- **Contain whole logo** is the safe default.
- **Fit to width** and **Natural size** modes are also available.
- **Logo zoom** ranges from **50–200%**.
- If artwork cannot fill the available box cleanly, it remains centred.
- Each template retains an appropriate maximum logo height and width.

These controls help unusually wide, tall, or heavily padded artwork fit as
consistently as well-prepared clear logos.

### Custom backdrop uploads

Select the **Backdrop** block to upload a persistent JPEG, PNG, or WebP image up
to **15 MB**. The uploaded file is stored as
`/config/custom-backdrop.img` and can replace the playing title's normal
backdrop.

| Control | Options/range |
|---|---|
| Enable custom image | On/off without deleting the stored image |
| Fit mode | Cover, contain whole image, or stretch/fill |
| Zoom/scale | 50–300% |
| Horizontal focus | 0–100% |
| Vertical focus | 0–100% |
| Opacity | 5–100% |
| Blur | 0–20 px |
| Brightness | 25–150% |

Deleting the custom image restores the normal movie/show backdrop. Custom
image bytes are deliberately excluded from exported looks and shared presets.

### Street template controls

Street retains its animated brick-wall cinema scene and weather integration,
but its decorative artwork is no longer baked into one fixed image.

- **Poster lights** is an independent block for the bulb-lit rectangle around
  the poster. It can be moved, resized, scaled, recoloured, removed, or restored.
- **NOW PLAYING sign** is a second independent block with the same layout
  controls.
- The poster remains independently positionable inside or outside the light
  frame.
- Existing settings inherit the original Street positions automatically.
- **Rain animation** can be disabled without turning off the rest of Street's
  layout or weather support.
- Rain, snow, storm, fog, cloud, and day/night conditions can be previewed from
  the Weather editor without saving fake weather.

### Credits badge control

The content-aware **Credits badge** is now a standard removable/addable Design
block. It still appears only when credits-scene data is available, but its
location and presence are controlled like other elements.

### Expanded font selection

The theme default remains available alongside fifteen named choices:

`Bebas Neue`, `Oswald`, `Playfair Display`, `Cinzel`, `Space Grotesk`, `Roboto`,
`Montserrat`, `Lato`, `Raleway`, `Anton`, `Orbitron`, `Righteous`,
`Merriweather`, `Libre Baskerville`, and `Bangers`.

Fonts can be assigned per block and per template. If Google Fonts cannot be
reached, the card falls back to suitable local/system fonts.

## Designer reference

The settings page is also the live card editor. Open the settings page, select
**Design**, and tap a visible block or its chip below the preview.

### Common block controls

| Control | Purpose |
|---|---|
| Horizontal / Vertical | Nudge or place the selected block |
| Width | Change the block's available layout width |
| Size | Scale the complete block |
| Left / Centre / Right | Align compatible text and artwork |
| Font | Apply a font to supported text blocks |
| Colour | Override text or themed accent colours for that block |
| Snap to grid | Move the block to the nearest preview grid line |
| Remove | Hide the block from the current template |
| + Add | Restore a removed block or add an optional block |
| Reset template | Restore the selected template's default blocks and positions |

Every template stores its own block layout. Moving Title in Street therefore
does not move Title in Spotlight. Changes preview immediately but do not reach
the Hub or ESP32 image until **Save changes** is selected.

### Available Design blocks

| Block | Main purpose | Special options |
|---|---|---|
| Backdrop | Movie/show or uploaded background art | Custom image upload, fit, zoom, focus, opacity, blur, brightness |
| Clock | Current time | 12/24-hour format and optional seconds |
| Weather | Current conditions | ZIP/auto-location, °F/°C, effects, intensity, condition preview |
| Category | Genres/categories | Separate font, colour, size, and position |
| Title | Text title or clear-logo artwork | Use logo art, logo fit, logo zoom |
| Metadata | Year, runtime, media format, and content rating | Toggle individual metadata parts |
| Plot | Movie or episode summary | Standard text block controls |
| Ratings | Rotten Tomatoes/IMDb values where available | Standard block controls |
| Progress | Playback bar and elapsed/remaining time | Colour, width, scale, position |
| Poster | Poster artwork | Position, width, scale, accent colour |
| Viewer | Current media-server user | Panel background and border |
| Device | Playback device/client | Local/Remote label, panel background and border |
| Stream | Playback path and quality | Panel background and border |
| Active streams | Concurrent stream count | Panel background and border |
| Audio & subtitles | Selected tracks | Panel background and border |
| Credits badge | During/after-credits indicator | Removable and content-aware |
| Poster lights | Street's illuminated poster frame | Street only; independently movable/removable |
| NOW PLAYING sign | Street's cinema sign | Street only; independently movable/removable |

### Presets, import, and sharing

- **Save preset** stores the current look in the template carousel.
- **Share this look** exports display-only settings as a small setup file.
- **Import a look** adds a shared setup to the local preset carousel.
- Shared looks can carry author attribution.
- Credentials, server addresses, location details, and uploaded custom-image
  bytes are not included.

### Themes

Built-in themes are `Amber`, `Ice`, `Crimson`, `Emerald`, `Campaign`,
`Concrete`, `Trophy`, and `B-Sides`. A custom accent colour can override the
theme accent used by progress bars, badges, poster trim, and compatible blocks.

## Templates

Seven templates can be switched live without restarting the container.

| Template | Description |
|---|---|
| **Spotlight** | Poster beside the complete metadata, plot, ratings, and progress stack |
| **Split** | Full-height poster/art wall beside the information column |
| **Hero** | Large centred title or logo over the backdrop |
| **Lower Third** | Broadcast-style lower-third information over full-bleed artwork |
| **Big Clock** | Ambient clock with a compact title and playback progress strip |
| **Street** | Brick-wall cinema with weather, poster lights, NOW PLAYING sign, and sprayed-logo styling |
| **Fanart** | Rotating fanart.tv artwork on a deliberately minimal canvas; add only the blocks you want |

![Marquee Street template](https://github.com/Jamisonfitz/marquee/releases/download/v2.2.1/street.jpg)

## Display methods

### Google Nest Hub

Marquee uses [`catt`](https://github.com/skorokithakis/catt) to launch DashCast
on a selected Google Cast display. When playback begins, the Hub loads
`PAGE_URL`; when playback stops, Marquee releases the Hub back to ambient mode.

The settings page can scan the LAN for compatible Cast devices. `HUB_IP` remains
available as an environment-variable fallback.

### ESP32/CrowPanel screenshot mode — recommended

The optional `marquee-shot` sidecar keeps Marquee's real `/image` page open in
headless Chromium, captures it to JPEG, and serves the result to ESPHome. This
preserves the HTML Designer exactly, including all enhanced blocks.

```text
Marquee /image → marquee-shot → /card.jpg + /state.json → ESPHome panel
```

Sidecar endpoints on `SERVE_PORT` (default `8088`):

- `GET /card.jpg` — the current rendered card image.
- `GET /state.json` — lightweight `ver`, `cver`, `playing`, and `paused` state.

`ver` changes whenever a new frame is ready, so the ESP32 downloads the larger
JPEG only when needed. `cver` changes when the playing title changes and can be
used to wake or brighten the panel.

The enhanced sidecar refreshes immediately when any of the following changes:

- play, pause, stop, title, episode, or seek state;
- viewer, device, stream, audio, or subtitle data;
- saved layout, font, panel style, or block visibility;
- custom backdrop version.

See [`sidecar/README.md`](sidecar/README.md) and
[`esphome/marquee-crowpanel-shot.yaml`](esphome/marquee-crowpanel-shot.yaml).

### ESP32 on-device rendering

The examples under [`esphome/examples`](esphome/examples) reconstruct a smaller
card directly on the ESP32 from JSON and panel-sized artwork. They avoid the
Chromium sidecar but are not pixel copies of the HTML card and do not
automatically render the enhanced Designer blocks.

See [`esphome/README.md`](esphome/README.md) for the CrowPanel hardware,
ESPHome, PSRAM, display timing, touch, and first-flash requirements.

### Browser or other display

Any trusted LAN device with a modern browser can open `/image`. For screenshot
output to another physical resolution, change `PANEL_WIDTH` and `PANEL_HEIGHT`
in the sidecar.

## Requirements

- Docker Engine with Docker Compose.
- Plex, Emby, or Jellyfin reachable from the Marquee host.
- One output method:
  - Google Nest Hub/compatible Cast display; or
  - ESP32 panel using `marquee-shot`; or
  - a browser/display capable of opening `/image`.
- A media-server token/API key, entered through the settings UI or environment.
- Host networking, or equivalent routing that allows discovery and access to
  the media server, Cast display, and ESP32 panel.

For the tested ESP32 configuration:

- Elecrow CrowPanel Basic HMI 7.0 inch;
- ESP32-S3-WROOM-1-N4R8;
- 800 × 480 RGB display and GT911 touch;
- octal PSRAM enabled;
- ESPHome.

Other panels require their own ESPHome display pins and timings.

## Quick start

### 1. Configure Docker Compose

Edit `compose.yaml` and set at least:

- `PAGE_URL` to the Marquee host's LAN URL ending in `/image`;
- the desired media backend and its host/key, or enter these later in the UI;
- `PANEL_WIDTH` and `PANEL_HEIGHT` when using an ESP32 panel.

`PAGE_URL` must use an address reachable from the display. Do not use
`localhost` for a Nest Hub or another physical device.

### 2. Start Marquee

For a Nest Hub or browser without the ESP32 sidecar:

```sh
# version 5
docker compose up -d --build
docker compose logs -f marquee
```

For an ESP32/CrowPanel using the recommended screenshot workflow:

```sh
# version 5
docker compose --profile panel up -d --build
docker compose logs -f marquee marquee-shot
```

Using `--build` ensures the enhanced local `marquee-shot` code is used rather
than an older published sidecar image.

### 3. Open the settings page

- Settings and Designer: `http://SERVER-IP:8084/`
- Card page: `http://SERVER-IP:8084/image`
- Health status: `http://SERVER-IP:8084/healthz`
- ESP32 JPEG: `http://SERVER-IP:8088/card.jpg`
- ESP32 state: `http://SERVER-IP:8088/state.json`

Select a media backend, enter its server address and credential, scan for a
Cast display if required, choose a template, add any optional blocks, preview
the correct target resolution, and select **Save changes**.

### Plain Docker example

```sh
# version 5
docker build -t marquee:esp32-enhanced-v4 .

docker run -d \
  --name marquee \
  --restart unless-stopped \
  --network host \
  -e PAGE_URL=http://192.168.1.10:8084/image \
  -v marquee-config:/config \
  marquee:esp32-enhanced-v4
```

Open the settings page to select Plex, Emby, or Jellyfin and enter its
credential. Environment variables may be supplied instead if preferred.

## Media-server configuration

Plex is the default backend, but only `PAGE_URL` is required when the container
starts. A container with no media credentials can boot to the settings page.
Saved backend changes are normally picked up by the next poll without a
container restart.

| Backend | Host variable | Credential variable | Notes |
|---|---|---|---|
| Plex | `PLEX_HOST` | `PLEX_TOKEN` | Usually provides the richest session/network detail |
| Emby | `EMBY_HOST` | `EMBY_API_KEY` | Uses the normalized Emby Sessions path |
| Jellyfin | `JELLYFIN_HOST` | `JELLYFIN_API_KEY` | API-compatible session path shared with Emby |

Set `MEDIA_BACKEND` to `plex`, `emby`, or `jellyfin` to provide a container
default. The backend selected and saved through the settings page takes
precedence.

Credentials are write-only in the web application: they are stored server-side
but are never returned to a browser or included in an exported setup.

## Settings and environment reference

### Playback selection and privacy

| Setting | Default | Purpose |
|---|---:|---|
| Users / `PLEX_USERS` | Everyone | Comma-separated media-server usernames allowed to trigger Marquee |
| Devices / `PLEX_DEVICES` | Any device | Comma-separated playback device names allowed to trigger Marquee |
| Do not cast / `BLOCK_TAGS` | Empty | Blocks sessions whose genres, tags, or content rating match a listed word |
| Rotate between sessions | 30 seconds | Time given to each eligible session; `0` pins the first sorted session |
| Device Local/Remote label | On | Displays the connection location when the backend reports it |

Do-not-cast matching is case-insensitive. Words of three or more characters can
match inside a term (`adult` matches `Adult Animation`); shorter values require
an exact term match so a rating such as `R` does not match `Horror`.

### Weather and Fanart

| Setting | Default | Options |
|---|---:|---|
| Weather block | Off | Add it to any template through Design |
| Weather effects | On when weather is used | Rain, snow, storm, fog, and cloud effects on Street |
| Weather intensity | 2 | Levels 1–4 |
| Street rain animation | On | Disable rain/storm particles independently |
| Weather location | Automatic | Optional ZIP code override |
| Units | °F | °F or °C |
| Fanart rotation | 10 minutes | 5–60 minutes on a live card |
| Fanart type | Background | Background, poster, logo, clear art, banner, or thumb |

Fanart requires a free fanart.tv API key through the settings page or the
`FANART_API_KEY` environment variable.

### Core environment variables

| Variable | Default | Purpose |
|---|---:|---|
| `PAGE_URL` | Required | LAN-reachable card URL, normally `http://SERVER-IP:8084/image` |
| `HUB_IP` | Empty | Cast device fallback when none is saved through the UI |
| `MEDIA_BACKEND` | `plex` | Default backend: `plex`, `emby`, or `jellyfin` |
| `PLEX_HOST` / `PLEX_TOKEN` | Empty | Plex connection defaults |
| `EMBY_HOST` / `EMBY_API_KEY` | Empty | Emby connection defaults |
| `JELLYFIN_HOST` / `JELLYFIN_API_KEY` | Empty | Jellyfin connection defaults |
| `PLEX_USERS` | Empty | Allowed usernames; empty allows everyone |
| `PLEX_DEVICES` | Empty | Allowed devices; empty allows any device |
| `BLOCK_TAGS` | Empty | Comma-separated do-not-cast words |
| `TMDB_API_KEY` | Empty | Enables credits-scene lookup/badges |
| `FANART_API_KEY` | Empty | Container default for fanart.tv |
| `POLL_SECONDS` | `5` | Media-server polling interval |
| `SERVE_PORT` | `8084` | Marquee HTTP port |
| `DATA_DIR` | `/config` in Docker | Persistent settings and custom backdrop location |
| `REPO_DIR` | `/app` in Docker | Application/output directory |

### Environment values and saved settings

Environment variables provide defaults. A value saved in the settings page
takes precedence. Clearing a UI field returns it to its inherited environment
default. The UI shows inherited values as placeholders so an empty field does
not misleadingly appear unconfigured.

| Function | Environment default | Saved UI setting |
|---|---|---|
| Cast device | `HUB_IP` | Cast device picker wins |
| Users | `PLEX_USERS` | Typed list replaces the environment list |
| Devices | `PLEX_DEVICES` | Typed list replaces the environment list |
| Do not cast | `BLOCK_TAGS` | Typed list replaces the environment list |
| Backend/credentials | Backend-specific variables | Saved backend selection and values win |

## `marquee-shot` sidecar settings

| Variable | Default | Purpose |
|---|---:|---|
| `MARQUEE_URL` | `http://127.0.0.1:8084` | Marquee base URL |
| `PANEL_WIDTH` | `800` | Screenshot width in pixels |
| `PANEL_HEIGHT` | `480` | Screenshot height in pixels |
| `POLL_EVERY` | `1` | Seconds between lightweight state checks |
| `PROGRESS_EVERY` | `60` | Progress-bar heartbeat screenshot interval |
| `SEEK_MS` | `5000` | Position jump treated as a seek |
| `JPEG_QUALITY` | `85` | Output JPEG quality |
| `SERVE_PORT` | `8088` | Port serving `/card.jpg` and `/state.json` |
| `SETTLE_SECONDS` | `0.8` | Delay after page refresh before capture |

Chromium stays idle when nothing is playing. The sidecar fingerprints both
playback/session data and served Design settings so the ESP32 image does not
wait for the slower progress heartbeat after a layout or metadata change.

## Persistence and upgrades

Compose mounts `./data` at `/config`. Important persistent files include:

- `/config/settings.json` — saved settings, layouts, visibility, and presets;
- `/config/custom-backdrop.img` — optional uploaded custom backdrop.

Before upgrading:

1. Back up the directory mounted at `/config`.
2. Replace the source files while retaining the persistent data directory.
3. Rebuild Marquee and, if used, `marquee-shot`.
4. Open Design and confirm the selected preview resolution.
5. Add any new optional session blocks through **+ Add**.

Existing v1–v3 layouts remain compatible. New session blocks remain off until
added, while the Street poster lights and NOW PLAYING sign inherit their
original positions unless customised.

## Monitoring and troubleshooting

### Health and logs

`GET /healthz` returns service status and the running version.

```sh
# version 5
docker compose ps
docker compose logs -f marquee
docker compose logs -f marquee-shot
```

### Common issues

| Symptom | Check |
|---|---|
| Hub does not load the card | Confirm `PAGE_URL` uses the server's LAN IP, ends in `/image`, and opens from another LAN device |
| Cast scan finds nothing | Confirm host networking and that the Hub is reachable on the same LAN/VLAN |
| ESP32 shows an old layout | Rebuild `marquee-shot`, check `/state.json`, and verify `PANEL_WIDTH`/`PANEL_HEIGHT` |
| Optional block is missing | Add it in Design for the current template and select Save changes |
| Local/Remote is blank | The media backend/client did not report a location value |
| Stream details are incomplete | The backend/client omitted the relevant session or transcode fields |
| Custom backdrop is lost after recreation | Ensure `/config` is mapped to persistent storage |
| Logo still appears too large/small | Select Title, use Contain, then adjust Logo zoom or Title width |

### Silence the Nest Hub cast chime

In the Google Home app, open the Hub, select **Settings → Accessibility**, then
disable **Play sounds on start/end of casting**. This is a device setting, not a
Marquee setting.

## Development and validation

```sh
# version 5
python3 cast/cast.py --selftest
python3 sidecar/shot.py --selftest
python3 -m py_compile cast/cast.py sidecar/shot.py
docker compose config
docker build -t marquee:test .
```

Physical output should also be tested before publishing a release:

1. Open `PAGE_URL` from another device on the LAN.
2. Start a movie or episode and confirm the correct title and session blocks.
3. Pause, resume, and seek; confirm state and progress updates.
4. Change a saved Design setting; confirm the ESP32 JPEG refreshes.
5. Stop playback; confirm the Hub returns to ambient mode or the ESP32 goes
   idle/dims as configured.

## Project structure

| Path | Purpose |
|---|---|
| `cast/cast.py` | Media polling, normalisation, settings API, artwork, and Cast control |
| `cast/settings.html` | Live settings and Designer interface |
| `output/index.html` | Responsive now-playing card rendered by Hub/browser/sidecar |
| `sidecar/` | Headless-Chromium JPEG renderer for ESP32 displays |
| `esphome/` | CrowPanel screenshot configuration and direct-render examples |
| `unraid/` | Optional Unraid container template for `marquee-shot` |
| `ENHANCEMENTS.md` | Enhanced-version upgrade and validation notes |
| `CHANGELOG.md` | Version history |

## Plex token

1. Sign in to Plex Web and open an item on your server.
2. Select **More (`…`) → Get Info → View XML**.
3. Copy the value after `X-Plex-Token=` from the browser address bar.
4. Test it at `http://PLEX-IP:32400/?X-Plex-Token=YOUR_TOKEN`.

See Plex's
[authentication-token instructions](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
Never put real credentials in Compose files, screenshots, issues, or commits.

## Credits

Marquee stands on generous shoulders:

- **[Jamisonfitz](https://github.com/Jamisonfitz/marquee)** — original Marquee,
  templates, settings experience, and Google Nest Hub workflow.
- **[TRusselo](https://github.com/TRusselo/marquee-esp32)** — ESP32/ESPHome
  support, `marquee-shot`, Emby/Jellyfin work, session filtering/rotation, and
  the base used by this enhanced edition.
- **[catt](https://github.com/skorokithakis/catt)** by Stavros Korokithakis —
  the Cast/DashCast engine.
- The Street weather effects adapt techniques by sheepjs, Ivan Odintsov,
  Braeden Craig, dburrell, and Tiff Wong. See [CREDITS.md](CREDITS.md) for full
  source notes and licences.

## Licence and support

This project is provided under the [MIT License](LICENSE). Retain the licence
and upstream attribution when redistributing modified versions.

For upstream Marquee support and development, see
[`Jamisonfitz/marquee`](https://github.com/Jamisonfitz/marquee). For the ESP32
base fork, see
[`TRusselo/marquee-esp32`](https://github.com/TRusselo/marquee-esp32).
