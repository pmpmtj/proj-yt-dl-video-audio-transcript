# YouTube Downloader - Modular Python Package

A modular YouTube downloader built on **yt-dlp** + **FFmpeg** with a clean, production-ready architecture.

## Features

* **Modular Design**: Separated core logic, CLI interface, and configuration
* **Container Compatibility**: Enforces container-compatible tracks to avoid FFmpeg errors
* **Quality Control**: Configurable quality caps and format selection
* **Audio Support**: Download audio-only as MP3
* **Configuration-Driven**: JSON-based configuration for easy customization
* **Comprehensive Logging**: Centralized logging with hybrid approach (main log + specialized logs)
* **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

* Python 3.8+
* `pip install yt-dlp`
* **FFmpeg** in PATH (needed for merging/remuxing)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### As a Python Module (Recommended)

```bash
python -m src.yt_dl_app "https://www.youtube.com/watch?v=VIDEO_ID" [options]
```

### As a Standalone Script (Alternative)

```bash
python src/yt_dl_app/__main__.py "https://www.youtube.com/watch?v=VIDEO_ID" [options]
```

### Direct CLI Module Execution

```bash
python src/yt_dl_app/yt_dl_core_CLI.py "https://www.youtube.com/watch?v=VIDEO_ID" [options]
```

### Command Line Options

* `url` *(positional)* — the video URL
* `--audio-only` — download audio only (MP3)
* `--output-template TEMPLATE` — yt-dlp output template (default: from config)
* `--restrict-filenames` — ASCII-only safe filenames
* `--ext {mp4,webm}` — preferred output container (default: from config)
* `--quality {best,2160p,1440p,1080p,720p,480p,360p,144p}` — video quality cap (default: from config)

### Examples

```bash
# Best available MP4 (using config defaults)
python -m src.yt_dl_app https://youtu.be/VIDEO_ID

# MP4 at most 1080p
python -m src.yt_dl_app https://youtu.be/VIDEO_ID --quality 1080p

# WEBM at most 720p
python -m src.yt_dl_app https://youtu.be/VIDEO_ID --ext webm --quality 720p

# Audio only (best → MP3)
python -m src.yt_dl_app https://youtu.be/VIDEO_ID --audio-only

# Show help and available options
python -m src.yt_dl_app --help

# Alternative: Direct script execution
python src/yt_dl_app/__main__.py https://youtu.be/VIDEO_ID --quality 720p

# Alternative: Direct CLI module execution
python src/yt_dl_app/yt_dl_core_CLI.py https://youtu.be/VIDEO_ID --audio-only
```

## Configuration

The application uses Python configuration modules:

* `src/common/app_config.py` - Main application settings (Python-based)
* `src/common/logging_config.py` - Logging configuration (Python-based)

### Default Configuration

#### Application Settings (`app_config.py`)
```python
APP_CONFIG = {
    "download": {
        "download_path": "./download"
    },
    "video": {
        "ext": "mp4",
        "quality": "best",
        "output_template": "%(title)s.%(ext)s",
        "restrict_filenames": True,
        "audio_only": False
    }
}
```

#### Logging Configuration (`logging_config.py`)
The logging configuration is now handled by a Python module that provides centralized logging setup:

```python
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'rotating_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'app.log'),
            'maxBytes': 1024 * 1024,  # 1MB
            'backupCount': 5,
            'formatter': 'standard',
            'mode': 'a',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'error.log'),
            'maxBytes': 512 * 1024,  # 512KB
            'backupCount': 3,
            'formatter': 'standard',
            'mode': 'a',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console', 'rotating_file', 'error_file'],
        'level': 'INFO',
    },
}
```

## Project Structure

```
my_project/
├── src/
│   ├── yt_dl_app/
│   │   ├── __init__.py          # Package initialization
│   │   ├── __main__.py          # Package entry point
│   │   ├── yt_dl_core.py        # Core business logic
│   │   ├── yt_dl_core_CLI.py    # CLI interface
│   │   └── yt_dl_helpers.py     # YTDL-specific helper functions
│   └── common/
│       ├── app_config.py        # Application configuration (Python)
│       └── logging_config.py    # Logging configuration (Python)
├── path_utils/
│   ├── __init__.py              # Package initialization with clean exports
│   └── path_utils.py            # Generic path and file utilities
├── logs/                        # Log files directory
├── requirements.txt
└── README.md
```

## Architecture

The application follows a clean, modular architecture designed for both CLI and server use:

* **Core Logic** (`yt_dl_core.py`): Contains all business logic for downloading and metadata extraction
* **CLI Interface** (`yt_dl_core_CLI.py`): Handles command-line argument parsing and user interaction
* **YTDL Helpers** (`yt_dl_helpers.py`): YTDL-specific helper functions for path and configuration management
* **Configuration** (`src/common/`): Python-based configuration management
* **Path Utilities** (`path_utils/`): Generic cross-platform path handling and file operations
* **Logging** (`logs/`): Centralized logging with hybrid approach

### Server-Ready Design

The modular architecture supports both CLI and server environments:

* **CLI Usage**: `python -m src.yt_dl_app "URL" [options]`
* **Server Usage**: Import core functions directly in Django/Flask applications
* **API Integration**: Core functions accept parameters directly (no CLI parsing needed)
* **Dynamic Options**: Extract available formats/qualities from video metadata

### Recent Improvements

The codebase has been optimized for better maintainability and server readiness:

* **Streamlined Entry Point**: Simplified `__main__.py` with direct CLI integration
* **Modular Architecture**: Separated generic utilities from YTDL-specific helpers
* **Descriptive Naming**: Renamed `utils/` to `path_utils/` for better clarity
* **Clean Imports**: Simplified import statements with package-level exports
* **Self-Contained Modules**: YTDL app is more cohesive with local helper functions
* **Improved Error Handling**: Specific exception handling instead of bare `except` clauses
* **Code Deduplication**: Eliminated redundant functions and imports
* **Optimized Logging**: Hybrid approach with main log file and specialized logs for high-volume operations
* **Server-Ready Architecture**: Core functions designed for both CLI and web API integration

## Logging

### Log Files

* **`app.log`** - Main application log (all modules)
* **`error.log`** - Error-specific log entries
* **`downloads.log`** - Download operations (high volume, when implemented)
* **`api.log`** - API requests/responses (when web interface added)

### Log Locations

```
logs/
├── app.log             # Main application log
├── error.log           # Error-specific entries
├── downloads.log       # Download operations
└── api.log            # API operations
```

## Testing

The project includes comprehensive unit tests for all core functionality:

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_yt_dl_core.py -v
python -m pytest tests/test_yt_dl_helpers.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

* **Core Download Functions**: Audio and video download with mocked dependencies
* **Helper Functions**: Path and configuration management
* **Error Scenarios**: Download failures, missing files, invalid parameters
* **Cross-Platform**: Windows/Unix path handling
* **Fast Execution**: All tests run in under 0.2 seconds with no network calls

### Test Structure

```
tests/
├── test_yt_dl_core.py      # Core download function tests
└── test_yt_dl_helpers.py   # Helper function tests
```

## Troubleshooting

* **"No suitable formats"** → The chosen `--ext` or `--quality` isn't available for this video. Try another container or different quality cap.
* **"Conversion failed!"** → This is prevented by enforcing container compatibility. Ensure you're using the correct `--ext` option.
* **"Missing FFmpeg"** → Install FFmpeg and ensure it's in your system PATH.
* **Logging Issues** → Check `logs/` directory for log files and verify `src/common/logging_config.py` settings.
* **Import Errors** → Ensure you're running from the project root directory and all dependencies are installed.

## License

MIT
