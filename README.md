# YouTube Downloader - Separated Audio and Video Apps

A modular YouTube downloader built on **yt-dlp** + **FFmpeg** with clean, production-ready architecture. The project has been separated into two focused applications:

- **Audio Downloader** (`yt_audio_app`): Simple, hardcoded MP3 downloads
- **Video Downloader** (`yt_video_app`): Configurable video downloads with quality/format options

## Features

### Audio Downloader (`yt_audio_app`)
- **Hardcoded Settings**: MP3, 192kbps, no configuration needed
- **Simple CLI**: Just URL and basic options
- **Fast & Reliable**: Minimal dependencies, focused functionality
- **No Config Files**: Everything is hardcoded for simplicity
- **Organized Output**: Downloads to `downloads/audio/` directory

### Video Downloader (`yt_video_app`)
- **Configurable Quality**: Choose from best, 2160p, 1440p, 1080p, 720p, 480p, 360p, 144p
- **Multiple Formats**: MP4 and WebM container support
- **Container Compatibility**: Enforces container-compatible tracks to avoid FFmpeg errors
- **Configuration-Driven**: Python-based configuration for easy customization
- **Comprehensive Logging**: Centralized logging with hybrid approach
- **Organized Output**: Downloads to `downloads/video/` directory

### Shared Features
- **Modular Design**: Clean separation of concerns
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Comprehensive Testing**: Full test coverage for both apps
- **Production-Ready**: Error handling, logging, and robust architecture

## Requirements

* Python 3.8+
* `pip install yt-dlp`
* **FFmpeg** in PATH (needed for video merging/remuxing)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Audio Downloader

Download audio only as MP3 with hardcoded settings (192kbps):

```bash
# Basic audio download
python -m src.yt_audio_app "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom output directory
python -m src.yt_audio_app "URL" --output-dir ./music

# Custom filename template
python -m src.yt_audio_app "URL" --template "%(uploader)s - %(title)s.%(ext)s"

# Show metadata without downloading
python -m src.yt_audio_app "URL" --metadata

# Quiet mode (no progress output)
python -m src.yt_audio_app "URL" --quiet
```

### Video Downloader

Download video with configurable quality and format:

```bash
# Basic video download (using config defaults)
python -m src.yt_video_app "https://www.youtube.com/watch?v=VIDEO_ID"

# Specific quality and format
python -m src.yt_video_app "URL" --quality 1080p --ext mp4

# Custom filename template
python -m src.yt_video_app "URL" --output-template "%(uploader)s - %(title)s.%(ext)s"

# WebM format at 720p
python -m src.yt_video_app "URL" --ext webm --quality 720p

# ASCII-only filenames (safer)
python -m src.yt_video_app "URL" --restrict-filenames
```

### Command Line Options

#### Audio Downloader Options
* `url` *(positional)* — the video URL
* `--output-dir, -o` — output directory (default: ./downloads/audio)
* `--template, -t` — filename template (default: %(title)s.%(ext)s)
* `--metadata, -m` — show video metadata without downloading
* `--quiet, -q` — suppress progress output

#### Video Downloader Options
* `url` *(positional)* — the video URL
* `--output-template` — yt-dlp output template (default: from config)
* `--restrict-filenames` — ASCII-only safe filenames
* `--ext {mp4,webm}` — preferred output container (default: from config)
* `--quality {best,2160p,1440p,1080p,720p,480p,360p,144p}` — video quality cap (default: from config)

## Configuration

### Video Downloader Configuration

The video downloader uses Python configuration in `src/common/app_config.py`:

```python
APP_CONFIG = {
    "download": {
        "download_path": "./downloads"
    },
    "video": {
        "ext": "mp4",
        "quality": "best", 
        "output_template": "%(title)s.%(ext)s",
        "restrict_filenames": True
    }
}
```

### Audio Downloader Configuration

The audio downloader has **hardcoded settings** for simplicity:
- Format: `bestaudio/best`
- Codec: `MP3`
- Quality: `192kbps`
- Filename restriction: `enabled`

## Project Structure

```
my_project/
├── src/
│   ├── yt_audio_app/           # Audio downloader (hardcoded settings)
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── audio_core.py       # Audio download logic
│   │   ├── audio_cli.py        # Audio CLI interface
│   │   └── audio_helpers.py    # Audio-specific helpers
│   ├── yt_video_app/           # Video downloader (configurable)
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── video_core.py       # Video download logic
│   │   ├── video_cli.py        # Video CLI interface
│   │   └── video_helpers.py    # Video-specific helpers
│   └── common/                 # Shared utilities
│       ├── app_config.py       # Video app configuration
│       └── logging_config.py   # Shared logging configuration
├── path_utils/                 # Shared path utilities
├── downloads/                  # Download directories
│   ├── audio/                  # Audio downloads (MP3 files)
│   └── video/                  # Video downloads (MP4/WebM files)
├── tests/
│   ├── test_audio_app/         # Audio app tests
│   │   ├── test_audio_core.py
│   │   ├── test_audio_cli.py
│   │   └── test_audio_helpers.py
│   ├── test_video_app/         # Video app tests
│   │   ├── test_video_core.py
│   │   ├── test_video_cli.py
│   │   └── test_video_helpers.py
│   └── test_path_utils.py      # Shared utility tests
├── requirements.txt
└── README.md
```

## Architecture

### Audio App Architecture
- **Simple & Focused**: Hardcoded settings, minimal configuration
- **Fast Execution**: No complex format selection or configuration loading
- **Reliable**: Fewer moving parts, less chance of errors
- **Easy to Use**: Just provide URL and optional output directory

### Video App Architecture
- **Configurable**: Full control over quality, format, and output options
- **Flexible**: Supports multiple containers and quality settings
- **Production-Ready**: Comprehensive error handling and logging
- **Extensible**: Easy to add new features and options

### Shared Architecture
- **Modular Design**: Clean separation between core logic, CLI, and helpers
- **Dependency Injection**: Easy testing with mocked dependencies
- **Cross-Platform**: Handles Windows/Unix path differences
- **Logging**: Centralized logging with appropriate levels

## Testing

Both apps include comprehensive unit tests:

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run audio app tests only
python -m pytest tests/test_audio_app/ -v

# Run video app tests only
python -m pytest tests/test_video_app/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

* **Audio App**: Core download functions, CLI interface, helper functions
* **Video App**: Core download functions, CLI interface, helper functions, metadata extraction
* **Shared Utilities**: Path handling, configuration management
* **Error Scenarios**: Download failures, invalid URLs, missing files
* **Fast Execution**: All tests run with mocked dependencies (no network calls)

## Logging

### Log Files

* **`app.log`** - Main application log (all modules)
* **`error.log`** - Error-specific log entries
* **`downloads.log`** - Download operations (when implemented)
* **`api.log`** - API requests/responses (when web interface added)

### Log Locations

```
logs/
├── app.log             # Main application log
├── error.log           # Error-specific entries
├── downloads.log       # Download operations
└── api.log            # API operations
```

## Examples

### Audio Download Examples

```bash
# Download a song as MP3 (saves to downloads/audio/)
python -m src.yt_audio_app "https://youtu.be/dQw4w9WgXcQ"

# Download to custom directory
python -m src.yt_audio_app "URL" --output-dir ./music

# Custom filename format
python -m src.yt_audio_app "URL" --template "%(uploader)s - %(title)s.%(ext)s"

# Show video info without downloading
python -m src.yt_audio_app "URL" --metadata
```

### Video Download Examples

```bash
# Download best available quality (saves to downloads/video/)
python -m src.yt_video_app "https://youtu.be/dQw4w9WgXcQ"

# Download 1080p MP4
python -m src.yt_video_app "URL" --quality 1080p --ext mp4

# Download 720p WebM
python -m src.yt_video_app "URL" --quality 720p --ext webm

# Custom filename with uploader
python -m src.yt_video_app "URL" --output-template "%(uploader)s - %(title)s.%(ext)s"

# Safe ASCII-only filenames
python -m src.yt_video_app "URL" --restrict-filenames
```

## Troubleshooting

### Common Issues

* **"No suitable formats"** → The chosen `--ext` or `--quality` isn't available for this video. Try another container or different quality cap.
* **"Conversion failed!"** → This is prevented by enforcing container compatibility. Ensure you're using the correct `--ext` option.
* **"Missing FFmpeg"** → Install FFmpeg and ensure it's in your system PATH.
* **Logging Issues** → Check `logs/` directory for log files and verify `src/common/logging_config.py` settings.
* **Import Errors** → Ensure you're running from the project root directory and all dependencies are installed.

### Audio App Specific

* **Audio quality** → Fixed at 192kbps MP3 (by design)
* **Configuration** → No config files needed (hardcoded settings)
* **Dependencies** → Only requires yt-dlp (no FFmpeg needed)

### Video App Specific

* **Configuration** → Edit `src/common/app_config.py` for default settings
* **Quality options** → Use `--quality` flag to override config defaults
* **Format options** → Use `--ext` flag to choose MP4 or WebM

## Migration from Unified App

If you were using the previous unified app:

1. **For audio downloads**: Use `yt_audio_app` instead of `--audio-only` flag
2. **For video downloads**: Use `yt_video_app` instead of the unified app
3. **Configuration**: Video settings moved to `src/common/app_config.py`
4. **CLI options**: Audio and video apps have separate, focused option sets

## License

MIT