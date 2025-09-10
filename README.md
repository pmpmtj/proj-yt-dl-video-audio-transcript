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
- **Language Support**: Download with specific audio languages and embedded subtitles
- **Multi-Language Downloads**: Download same video in different languages with unique filenames
- **Force Downloads**: Bypass file existence checks with `--force` option
- **Feature Flags**: Database-ready configuration for future scalability
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

Download video with configurable quality, format, and language options:

```bash
# Basic video download (using config defaults)
python -m src.yt_video_app download "https://www.youtube.com/watch?v=VIDEO_ID"

# Specific quality and format
python -m src.yt_video_app download "URL" --quality 1080p --ext mp4

# Download with specific audio language
python -m src.yt_video_app download "URL" --audio-lang en --quality 720p

# Download with audio language and subtitles
python -m src.yt_video_app download "URL" --audio-lang en --subtitle-lang en

# Force download even if file exists
python -m src.yt_video_app download "URL" --force

# Custom filename template
python -m src.yt_video_app download "URL" --output-template "%(uploader)s - %(title)s.%(ext)s"

# WebM format at 720p
python -m src.yt_video_app download "URL" --ext webm --quality 720p

# ASCII-only filenames (safer)
python -m src.yt_video_app download "URL" --restrict-filenames

# Get video information without downloading
python -m src.yt_video_app info "URL"

# Check available languages
python -m src.yt_video_app languages "URL"

# Check available formats and qualities
python -m src.yt_video_app formats "URL"

# Show configuration and feature flags
python -m src.yt_video_app config
```

### Command Line Options

#### Audio Downloader Options
* `url` *(positional)* — the video URL
* `--output-dir, -o` — output directory (default: ./downloads/audio)
* `--template, -t` — filename template (default: %(title)s.%(ext)s)
* `--metadata, -m` — show video metadata without downloading
* `--quiet, -q` — suppress progress output

#### Video Downloader Commands

**Download Command:**
* `url` *(positional)* — the video URL
* `--output-template` — yt-dlp output template (default: from config)
* `--restrict-filenames` — ASCII-only safe filenames
* `--ext {mp4,webm}` — preferred output container (default: from config)
* `--quality {best,2160p,1440p,1080p,720p,480p,360p,144p}` — video quality cap (default: from config)
* `--audio-lang` — audio language code (default: original)
* `--subtitle-lang` — subtitle language code to embed (optional)
* `--force` — force download even if file exists

**Info Command:**
* `url` *(positional)* — the video URL

**Languages Command:**
* `url` *(positional)* — the video URL

**Formats Command:**
* `url` *(positional)* — the video URL

**Config Command:**
* `--feature-flags` — show only feature flags status

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
    },
    "features": {
        "use_database_as_source": False,
        "enable_file_existence_check": True,
        "enable_metadata_caching": False,
        "enable_download_history": False
    }
}
```

### Feature Flags

The video downloader includes feature flags for future database integration:

- **`use_database_as_source`**: When `True`, database becomes the single source of truth (always force downloads)
- **`enable_file_existence_check`**: When `False`, skips file existence checks (always force downloads)
- **`enable_metadata_caching`**: Future feature for metadata caching
- **`enable_download_history`**: Future feature for download history tracking

### Multi-Language Downloads

The system automatically generates unique filenames for different language combinations:

- **Original language**: `Video_Title.mp4`
- **English audio**: `Video_Title_audio-en.mp4`
- **Spanish audio**: `Video_Title_audio-es.mp4`
- **English audio + subtitles**: `Video_Title_audio-en_sub-en.mp4`

### Download Behavior Matrix

The following table shows how different feature flags and CLI options determine download behavior:

| `use_database_as_source` | `enable_file_existence_check` | `--force` CLI | File Exists | **Result** |
|-------------------------|------------------------------|---------------|-------------|------------|
| `True` | `True` | Not specified | Yes | **Force Download** (DB overrides) |
| `True` | `True` | `--force` | Yes | **Force Download** (DB overrides) |
| `True` | `True` | `--no-force` | Yes | **Force Download** (DB overrides) |
| `True` | `False` | Not specified | Yes | **Force Download** (DB overrides) |
| `False` | `True` | Not specified | Yes | **Skip Download** (file exists) |
| `False` | `True` | `--force` | Yes | **Force Download** (CLI overrides) |
| `False` | `True` | `--no-force` | Yes | **Skip Download** (explicit no-force) |
| `False` | `False` | Not specified | Yes | **Force Download** (check disabled) |
| `False` | `False` | `--force` | Yes | **Force Download** (check disabled) |
| `False` | `False` | `--no-force` | Yes | **Skip Download** (explicit no-force) |
| Any | Any | Any | No | **Download** (file doesn't exist) |

**Key Behaviors:**
- **Database Source (`use_database_as_source: True`)**: Always forces download regardless of file existence or CLI options
- **File Check Disabled (`enable_file_existence_check: False`)**: Always forces download unless `--no-force` is explicitly used
- **Normal Mode**: Respects file existence check and `--force` CLI option
- **CLI Override**: `--force` always overrides file existence check in normal mode
- **Explicit No-Force**: `--no-force` always skips download even when checks are disabled

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
python -m src.yt_video_app download "https://youtu.be/dQw4w9WgXcQ"

# Download 1080p MP4
python -m src.yt_video_app download "URL" --quality 1080p --ext mp4

# Download with English audio
python -m src.yt_video_app download "URL" --audio-lang en --quality 720p

# Download with English audio and subtitles
python -m src.yt_video_app download "URL" --audio-lang en --subtitle-lang en

# Download same video in multiple languages
python -m src.yt_video_app download "URL" --audio-lang en
python -m src.yt_video_app download "URL" --audio-lang es
python -m src.yt_video_app download "URL" --audio-lang fr

# Force re-download even if file exists
python -m src.yt_video_app download "URL" --force

# Download 720p WebM
python -m src.yt_video_app download "URL" --quality 720p --ext webm

# Custom filename with uploader
python -m src.yt_video_app download "URL" --output-template "%(uploader)s - %(title)s.%(ext)s"

# Safe ASCII-only filenames
python -m src.yt_video_app download "URL" --restrict-filenames

# Check what languages are available
python -m src.yt_video_app languages "URL"

# Check what formats are available
python -m src.yt_video_app formats "URL"

# Get video information without downloading
python -m src.yt_video_app info "URL"

# Show current configuration
python -m src.yt_video_app config
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
* **Language options** → Use `--audio-lang` and `--subtitle-lang` flags for language selection
* **Force downloads** → Use `--force` flag to bypass file existence checks
* **Feature flags** → Configure database integration and other features in `app_config.py`
* **Multi-language** → System automatically creates unique filenames for different language combinations

## Migration from Unified App

If you were using the previous unified app:

1. **For audio downloads**: Use `yt_audio_app` instead of `--audio-only` flag
2. **For video downloads**: Use `yt_video_app download` instead of the unified app
3. **Configuration**: Video settings moved to `src/common/app_config.py`
4. **CLI options**: Audio and video apps have separate, focused option sets
5. **New features**: Language selection, force downloads, and feature flags are now available
6. **Subcommands**: Video app now uses subcommands (`download`, `info`, `languages`, `formats`, `config`)

## License

MIT