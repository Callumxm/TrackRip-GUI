# TrackRip

Graphical interface for downloading YouTube videos and playlists.
Intended for downloading music off YouTube easily

## Features

- Download individual YouTube tracks
- Download YouTube playlists
- Add individual tracks to a download queue
- Add playlists to a download queue
- Download the entire queue
- Cancel active downloads
- Configure download location
- Configure audio quality
- Configure a default album name

## Requirements

- Python 3.11+
- FFmpeg
- `uv` recommended for dependency management

TrackRip uses:

- Python
- PySide6
- yt-dlp
- FFmpeg

## Installation

### Clone the repository

```bash
git clone <repository-url>
cd TrackRip-2.0
```

## Building

TrackRip can be packaged using PyInstaller.

Install the development dependencies:

```bash
uv sync
```

Build the application:

```bash
uv run pyinstaller TrackRip.spec
```

The packaged application will be placed in:

dist/TrackRip/

Run the packaged Linux application with:

./dist/TrackRip/TrackRip
Configuration

TrackRip allows you to configure:

Download location
Audio quality
Default album name

These settings can be changed from the Settings tab.
