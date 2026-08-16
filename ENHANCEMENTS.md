<!-- version 4 -->
# Marquee ESP32 Enhanced v4

This package is based on `TRusselo/marquee-esp32` at commit
`3e02ddc268d6317aefd808caf078d0baa3737c6d`. The fork already incorporates
upstream Marquee v2.2.1 and adds the optional `marquee-shot` plus ESPHome panel
workflow. This edition includes the session-aware Design blocks from v1, then
adds the expanded Designer, custom backdrop, target-display previews, and ESP32
refresh improvements.

## Version 4 Street and logo improvements

- Street's rectangle of poster lights and its **NOW PLAYING** sign are now
  independent Design blocks. Select either in the block chips to move, resize,
  scale, recolour, remove, or restore it without moving the poster.
- Title logo art now lives in a bounded, centered viewport. Marquee trims
  transparent padding from clear-logo images in the browser, uses whole-image
  contain by default, and offers fit-to-width, natural-size, and 50–200% zoom
  controls in the Title editor.
- Existing saved layouts need no conversion. With no v4 overrides, both Street
  decorations occupy the exact positions used by the previous baked scene.

## New Design blocks

- **Viewer** — active username and `position of total` when more than one
  eligible session is rotating.
- **Device** — playback device, client application, platform, and Local/Remote
  status when supplied by the backend.
- **Stream** — Direct Play, Direct Stream, or Transcoding; source/output
  resolution; HDR/Dolby Vision; codecs; bitrate/bandwidth; hardware acceleration.
- **Active streams** — server-wide count of movie/episode streams currently in
  progress, independent of the selected session's rotation position.
- **Audio & subtitles** — selected audio and subtitle tracks with language,
  codec, channel layout, display title, and Atmos where reported.

All five are available under **Design → + Add** and support the existing drag,
position, width, scale, alignment, font, colour, preset, import, and export
features. They are off by default, so existing `settings.json` files and
template appearances remain compatible.

## Version 3 Designer improvements

- The target preview defaults to **800 × 480** for the Elecrow CrowPanel 7.
  Presets cover Google Nest Hub (1024 × 600), Nest Hub Max (1280 × 800),
  HD/Full HD 16:9, 800 × 600 4:3, and custom dimensions from 320 × 240 through
  3840 × 2160.
- Device can show or hide its live **Local / Remote** status label.
- The new **Active streams** block displays the server-wide concurrent count.
- Street's rain/storm particle animation has its own switch, without disabling
  the rest of the Street layout.
- **Credits badge** is now a normal removable/addable Design block. It remains
  content-aware and only appears when a credits-scene tag exists.

## Version 2 Designer improvements

- Viewer, Device, Stream, and Audio & subtitles cards share the same height.
- Every session card has independent **Panel background** and **Panel border**
  switches. Turning both off leaves its content directly on the card.
- **Category** is now separate from **Title**, so genres and the movie/show
  title can be positioned, sized, coloured, and styled independently.
- The font list now offers Bebas Neue, Oswald, Playfair Display, Cinzel, Space
  Grotesk, Roboto, Montserrat, Lato, Raleway, Anton, Orbitron, Righteous,
  Merriweather, Libre Baskerville, and Bangers, plus the theme default.

## Custom backdrop

Select **Backdrop** in Design to upload or replace a JPEG, PNG, or WebP image
up to 15 MB. The image is stored as `/config/custom-backdrop.img`, alongside
the existing persistent settings. Controls include:

- Cover, contain, or stretch fit
- 50–300% zoom/scale
- Horizontal and vertical focus
- Opacity, blur, and brightness

Deleting the custom image restores the normal movie/show backdrop. The custom
file is intentionally not embedded in shared presets or exported look files.

## Why marquee-shot was updated

The original sidecar captures quickly for title and playback-state changes,
then relies on a slower progress heartbeat. The enhanced fields can change
without the title changing—for example, a subtitle is enabled or playback
switches from Direct Play to Transcoding. `sidecar/shot.py` now fingerprints
the `session`, `stream`, and `tracks` objects (excluding ordinary progress) and
the served design settings. It publishes a fresh `card.jpg` as soon as playback,
layout, font, panel style, or custom-art version changes. ESPHome's existing
`ver` polling then downloads the new frame without a firmware change.

The primary `esphome/marquee-crowpanel-shot.yaml` remains compatible. The
on-device examples that reconstruct a card instead of displaying `card.jpg`
do not automatically render the new HTML Designer blocks.

## Upgrade using Docker Compose

1. Back up the persistent directory mounted at `/config`.
2. Extract this package and edit `compose.yaml`, especially `PAGE_URL`, media
   backend address, credentials/defaults, and panel size.
3. Build both the application and the enhanced sidecar:

```sh
# version 4
docker compose --profile panel up -d --build
docker compose logs -f marquee marquee-shot
```

4. Open the Marquee settings page and add the desired blocks from
   **Design → + Add** for each template that should display them.

If the panel profile is not required, start only Marquee with:

```sh
# version 4
docker compose up -d --build
```

## Backend notes

- Plex normally supplies the most complete Local/Remote and bandwidth data.
- Emby and Jellyfin use the same normalized shape. Missing `/Sessions` fields
  are omitted rather than guessed.
- Track labels depend on metadata reported by the playback server and client.
- Viewer details are exposed through the LAN-hosted `now-playing.json`. Marquee
  remains intended for a trusted LAN and should not be port-forwarded.

## Validation commands

```sh
# version 4
python3 cast/cast.py --selftest
python3 sidecar/shot.py --selftest
docker compose config
```
