<!-- version 4 -->
# Package information

- Package: Marquee ESP32 Enhanced v4
- Enhanced version: `2.2.1-esp32-enhanced.4`
- Base project: `TRusselo/marquee-esp32`
- Base commit: `3e02ddc268d6317aefd808caf078d0baa3737c6d`
- Included upstream release: `Jamisonfitz/marquee` v2.2.1
- Prepared: 17 August 2026

## Included enhancements

- Viewer, Device, Stream, Active streams, and Audio & subtitles Designer blocks
- Common Plex, Emby, and Jellyfin session/playback payload
- Eligible-session rotation position and count
- Enhanced `marquee-shot` metadata-change capture trigger
- Equal-height session cards with background and border switches
- 800 × 480 default Design viewport plus Nest Hub, 16:9, 4:3, and custom sizes
- Optional Local/Remote label on the Device block
- Server-wide Active streams Designer block
- Separate Street rain-animation switch
- Removable and addable Credits Badge block
- Independently movable Street poster-light frame and NOW PLAYING sign
- Centered, bounded title-logo fitting with transparent-padding trim,
  contain/width/natural modes, and 50–200% zoom
- Separate Category and Title blocks
- Fifteen named per-block fonts plus theme default
- Persistent custom-backdrop upload and image-adjustment controls
- Immediate screenshot refresh after saved design or custom-art changes
- Existing Elecrow CrowPanel 7 screenshot-mode ESPHome configuration
- Existing panel-sized artwork and direct-render ESPHome examples
- Demonstration data for designing blocks while playback is idle
- Backward-compatible settings and presets

## Validation targets

- Core Python self-tests
- `marquee-shot` Python self-tests
- Python byte-code compilation
- Card and settings JavaScript syntax checks
- HTTP smoke tests for `/healthz`, `/image`, and `/settings`
- Git whitespace validation
