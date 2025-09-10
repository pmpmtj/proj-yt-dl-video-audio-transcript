# YouTube Downloader - Audio, Video, and Transcript Apps

A modular YouTube downloader built on **yt-dlp** + **FFmpeg** with clean, production-ready architecture and multiuser support. The project consists of three focused applications:

- **Audio Downloader** (`yt_audio_app`): Simple, hardcoded MP3 downloads
- **Video Downloader** (`yt_video_app`): Configurable video downloads with quality/format options
- **Transcript Downloader** (`yt_transcript_app`): Download transcripts with multiple format support

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download audio, video, and transcript for any YouTube video
python -m src audio "https://www.youtube.com/watch?v=VIDEO_ID"
python -m src video download "https://www.youtube.com/watch?v=VIDEO_ID"
python -m src transcript "https://www.youtube.com/watch?v=VIDEO_ID"

# Or run individual apps directly
python -m src.yt_audio_app "URL"
python -m src.yt_video_app download "URL"
python -m src.yt_transcript_app "URL"
```

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

### Transcript Downloader (`yt_transcript_app`)
- **Multiple Formats**: Clean text, timestamped, and structured JSON outputs
- **Rich Metadata**: Comprehensive metadata collection and analysis
- **Chapter Detection**: Automatic chapter detection and content analysis
- **Multiple Export Formats**: JSON, CSV, and Markdown metadata exports
- **Language Support**: Auto-detect or specify transcript language
- **Preview Mode**: Preview transcript content without downloading
- **Metadata Analysis**: Rich content analysis and statistics
- **Organized Output**: Downloads to `downloads/transcripts/` directory

### Multiuser Support
- **Session-Based**: No database required - uses UUID-based sessions
- **User Isolation**: Each user gets separate download directories
- **Backward Compatible**: Existing single-user code works unchanged
- **Web-Ready**: Perfect foundation for web app development
- **Session Management**: Automatic session creation and tracking
- **Isolated Downloads**: Users can only access their own downloads

### Shared Features
- **Modular Design**: Clean separation of concerns
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Comprehensive Testing**: Full test coverage for all apps
- **Production-Ready**: Error handling, logging, and robust architecture

## Requirements

* Python 3.8+
* `pip install yt-dlp`
* `pip install youtube-transcript-api` (for transcript downloads)
* **FFmpeg** in PATH (needed for video merging/remuxing)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Main Suite (Recommended)

Run the unified YouTube Downloader Suite with a single command. This provides a consistent interface across all three applications:

```bash
# Show help for the main suite
python -m src --help

# Audio download through main suite
python -m src audio "https://www.youtube.com/watch?v=VIDEO_ID"

# Video download through main suite
python -m src video download "https://www.youtube.com/watch?v=VIDEO_ID"

# Transcript download through main suite
python -m src transcript "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Main Suite Examples

**Audio Downloads:**
```bash
# Basic audio download
python -m src audio "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom output directory
python -m src audio "URL" --output-dir ./music

# Custom filename template
python -m src audio "URL" --template "%(uploader)s - %(title)s.%(ext)s"

# Show metadata without downloading
python -m src audio "URL" --metadata

# Quiet mode
python -m src audio "URL" --quiet

# Multiuser mode
python -m src audio "URL" --session-id "user-123"
```

**Video Downloads:**
```bash
# Basic video download
python -m src video download "https://www.youtube.com/watch?v=VIDEO_ID"

# Specific quality and format
python -m src video download "URL" --quality 1080p --ext mp4

# Download with specific audio language
python -m src video download "URL" --audio-lang en --quality 720p

# Download with audio language and subtitles
python -m src video download "URL" --audio-lang en --subtitle-lang en

# Force download even if file exists
python -m src video download "URL" --force

# Get video information without downloading
python -m src video info "URL"

# Check available languages
python -m src video languages "URL"

# Check available formats and qualities
python -m src video formats "URL"

# Show configuration and feature flags
python -m src video config
```

**Transcript Downloads:**
```bash
# Basic transcript download (all formats)
python -m src transcript "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom output directory
python -m src transcript "URL" --output-dir ./transcripts

# Custom filename template
python -m src transcript "URL" --template "my_transcript"

# Specific language
python -m src transcript "URL" --language en

# Specific formats only
python -m src transcript "URL" --formats clean structured

# Skip rich metadata analysis
python -m src transcript "URL" --no-metadata-analysis

# Show transcript metadata without downloading
python -m src transcript "URL" --metadata

# Preview transcript content
python -m src transcript "URL" --preview

# List available languages
python -m src transcript "URL" --list-languages

# Quiet mode
python -m src transcript "URL" --quiet

# Multiuser mode
python -m src transcript "URL" --session-id "user-789"
```

### Individual Apps

You can also run each application directly:

#### Audio Downloader

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

#### Video Downloader

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

#### Transcript Downloader

Download transcripts with multiple format support and rich metadata:

```bash
# Basic transcript download (all formats)
python -m src.yt_transcript_app "https://www.youtube.com/watch?v=VIDEO_ID"

# Custom output directory
python -m src.yt_transcript_app "URL" --output-dir ./transcripts

# Custom filename template
python -m src.yt_transcript_app "URL" --template "my_transcript"

# Specific language
python -m src.yt_transcript_app "URL" --language en

# Specific formats only
python -m src.yt_transcript_app "URL" --formats clean structured

# Skip rich metadata analysis
python -m src.yt_transcript_app "URL" --no-metadata

# Show transcript metadata without downloading
python -m src.yt_transcript_app "URL" --metadata

# Preview transcript content
python -m src.yt_transcript_app "URL" --preview

# Quiet mode (no progress output)
python -m src.yt_transcript_app "URL" --quiet
```

### Multiuser Mode

All apps support multiuser functionality with session isolation:

```bash
# Each user gets isolated downloads
python -m src.yt_audio_app "URL" --session-id "user-123"
python -m src.yt_video_app download "URL" --session-id "user-456"
python -m src.yt_transcript_app "URL" --session-id "user-789"

# Without session ID, creates new session automatically
python -m src.yt_audio_app "URL"  # Creates new session
```

### Command Line Options

#### Audio Downloader Options
* `url` *(positional)* — the video URL
* `--output-dir, -o` — output directory (default: ./downloads/audio)
* `--template, -t` — filename template (default: %(title)s.%(ext)s)
* `--metadata, -m` — show video metadata without downloading
* `--quiet, -q` — suppress progress output
* `--session-id` — session ID for multiuser support

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
* `--session-id` — session ID for multiuser support

**Info Command:**
* `url` *(positional)* — the video URL

**Languages Command:**
* `url` *(positional)* — the video URL

**Formats Command:**
* `url` *(positional)* — the video URL

**Config Command:**
* `--feature-flags` — show only feature flags status

#### Transcript Downloader Options
* `url` *(positional)* — the video URL
* `--output-dir, -o` — output directory (default: ./downloads/transcripts)
* `--template, -t` — filename template (default: transcript)
* `--language, -l` — language code (auto-detects if not provided)
* `--formats, -f` — formats to generate: clean, timestamped, structured (default: all)
* `--no-metadata` — skip rich metadata analysis
* `--metadata, -m` — show transcript metadata without downloading
* `--preview, -p` — preview transcript content without downloading
* `--quiet, -q` — suppress progress output
* `--session-id` — session ID for multiuser support

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
│   ├── __main__.py             # Main suite entry point
│   ├── main.py                 # Main suite application logic
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
│   ├── yt_transcript_app/      # Transcript downloader
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── trans_core.py       # Transcript download logic
│   │   ├── trans_core_cli.py   # Transcript CLI interface
│   │   ├── transcript_processor.py
│   │   ├── metadata_collector.py
│   │   ├── metadata_exporter.py
│   │   └── get_transcript_list.py
│   └── common/                 # Shared utilities
│       ├── app_config.py       # App configuration
│       ├── logging_config.py   # Centralized logging configuration
│       └── user_context.py     # Multiuser session management
├── path_utils/                 # Shared path utilities
├── downloads/                  # Download directories (multiuser structure)
│   ├── session-uuid-1/         # User session 1
│   │   └── video-uuid-1/       # Video 1
│   │       ├── audio/          # Audio downloads
│   │       ├── video/          # Video downloads
│   │       └── transcripts/    # Transcript downloads
│   └── session-uuid-2/         # User session 2
│       └── video-uuid-2/       # Video 2
│           └── audio/          # Audio downloads
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
├── test_multiuser.py          # Multiuser functionality test
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

### Transcript App Architecture
- **Rich Processing**: Multiple format outputs with metadata analysis
- **Language Support**: Auto-detection and manual language selection
- **Export Options**: JSON, CSV, and Markdown metadata exports
- **Preview Mode**: Content preview without full download

### Multiuser Architecture
- **Session-Based**: UUID-based user sessions without database
- **User Isolation**: Separate directories for each user session
- **Backward Compatible**: Existing code works unchanged
- **Web-Ready**: Perfect foundation for web application development

### Shared Architecture
- **Modular Design**: Clean separation between core logic, CLI, and helpers
- **Dependency Injection**: Easy testing with mocked dependencies
- **Cross-Platform**: Handles Windows/Unix path differences
- **Logging**: Centralized logging with appropriate levels

## Testing

All apps include comprehensive unit tests:

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run audio app tests only
python -m pytest tests/test_audio_app/ -v

# Run video app tests only
python -m pytest tests/test_video_app/ -v

# Run transcript app tests only
python -m pytest tests/test_transcript_app/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

* **Audio App**: Core download functions, CLI interface, helper functions
* **Video App**: Core download functions, CLI interface, helper functions, metadata extraction
* **Transcript App**: Core download functions, CLI interface, helper functions, metadata processing
* **Multiuser Support**: Session management, user isolation, directory structure
* **Shared Utilities**: Path handling, configuration management
* **Error Scenarios**: Download failures, invalid URLs, missing files
* **Fast Execution**: All tests run with mocked dependencies (no network calls)

### Multiuser Testing

Test multiuser functionality with the provided test script:

```bash
# Test multiuser functionality
python test_multiuser.py
```

This will demonstrate:
- Session-based user isolation
- Directory structure creation
- Multiple users downloading different content types
- File organization and access control

## Logging

The YouTube Downloader Suite includes comprehensive centralized logging across all applications.

### Log Files

* **`app.log`** - Main application log (all modules, INFO level and above)
* **`error.log`** - Error-specific log entries (ERROR level only)

### Log Locations

```
logs/
├── app.log             # Main application log (rotating, 1MB max)
└── error.log           # Error-specific entries (rotating, 512KB max)
```

### Logging Features

- **Centralized Configuration**: Single logging setup across all applications
- **Multiple Outputs**: Console output + rotating log files
- **Module-Specific Loggers**: Each module has its own logger with descriptive names
- **Appropriate Levels**: DEBUG, INFO, WARNING, ERROR levels used throughout
- **Automatic Setup**: Logging is initialized when running any application
- **File Rotation**: Log files rotate automatically to prevent disk space issues

### Log Levels

- **DEBUG**: Detailed information for debugging (file operations, configuration loading)
- **INFO**: General information about application flow (downloads, user actions)
- **WARNING**: Warning messages (fallback operations, missing optional features)
- **ERROR**: Error messages (download failures, invalid inputs)

### Viewing Logs

```bash
# View main application log
cat logs/app.log

# View error log only
cat logs/error.log

# Follow logs in real-time
tail -f logs/app.log

# Search for specific errors
grep ERROR logs/app.log
```

## Examples

### Main Suite Examples

**Quick Start:**
```bash
# Download audio, video, and transcript for the same video
python -m src audio "https://youtu.be/dQw4w9WgXcQ"
python -m src video download "https://youtu.be/dQw4w9WgXcQ"
python -m src transcript "https://youtu.be/dQw4w9WgXcQ"
```

**Advanced Usage:**
```bash
# Download 1080p video with English audio and subtitles
python -m src video download "URL" --quality 1080p --audio-lang en --subtitle-lang en

# Download transcript in specific language with custom output
python -m src transcript "URL" --language es --output-dir ./spanish_transcripts

# Preview transcript before downloading
python -m src transcript "URL" --preview

# Get video information without downloading
python -m src video info "URL"
```

### Individual App Examples

#### Audio Download Examples

```bash
# Download a song as MP3 (saves to downloads/audio/)
python -m src.yt_audio_app "https://youtu.be/dQw4w9WgXcQ"

# Download to custom directory
python -m src.yt_audio_app "URL" --output-dir ./music

# Custom filename format
python -m src.yt_audio_app "URL" --template "%(uploader)s - %(title)s.%(ext)s"

# Show video info without downloading
python -m src.yt_audio_app "URL" --metadata

# Multiuser mode with session ID
python -m src.yt_audio_app "URL" --session-id "user-123"
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

# Multiuser mode with session ID
python -m src.yt_video_app download "URL" --session-id "user-456"
```

### Transcript Download Examples

```bash
# Download all transcript formats
python -m src.yt_transcript_app "https://youtu.be/dQw4w9WgXcQ"

# Download specific formats only
python -m src.yt_transcript_app "URL" --formats clean structured

# Download with specific language
python -m src.yt_transcript_app "URL" --language en

# Preview transcript without downloading
python -m src.yt_transcript_app "URL" --preview

# Show transcript metadata
python -m src.yt_transcript_app "URL" --metadata

# Custom output directory
python -m src.yt_transcript_app "URL" --output-dir ./my_transcripts

# Skip rich metadata analysis
python -m src.yt_transcript_app "URL" --no-metadata

# Multiuser mode with session ID
python -m src.yt_transcript_app "URL" --session-id "user-789"
```

### Multiuser Examples

```bash
# Different users downloading same video
python -m src.yt_audio_app "URL" --session-id "alice"
python -m src.yt_video_app download "URL" --session-id "bob"
python -m src.yt_transcript_app "URL" --session-id "charlie"

# Same user downloading different content types
python -m src.yt_audio_app "URL1" --session-id "user-123"
python -m src.yt_video_app download "URL1" --session-id "user-123"
python -m src.yt_transcript_app "URL1" --session-id "user-123"
```

## Troubleshooting

### Common Issues

* **"No suitable formats"** → The chosen `--ext` or `--quality` isn't available for this video. Try another container or different quality cap.
* **"Conversion failed!"** → This is prevented by enforcing container compatibility. Ensure you're using the correct `--ext` option.
* **"Missing FFmpeg"** → Install FFmpeg and ensure it's in your system PATH.
* **"No module named src"** → Ensure you're running from the project root directory and using `python -m src` command.
* **Logging Issues** → Check `logs/` directory for log files and verify `src/common/logging_config.py` settings.
* **Import Errors** → Ensure you're running from the project root directory and all dependencies are installed.
* **Main Suite Not Working** → Try running individual apps directly: `python -m src.yt_audio_app --help`

### Audio App Specific

* **Audio quality** → Fixed at 192kbps MP3 (by design)
* **Configuration** → No config files needed (hardcoded settings)
* **Dependencies** → Only requires yt-dlp (no FFmpeg needed)
* **Multiuser** → Use `--session-id` for user isolation

### Video App Specific

* **Configuration** → Edit `src/common/app_config.py` for default settings
* **Quality options** → Use `--quality` flag to override config defaults
* **Format options** → Use `--ext` flag to choose MP4 or WebM
* **Language options** → Use `--audio-lang` and `--subtitle-lang` flags for language selection
* **Force downloads** → Use `--force` flag to bypass file existence checks
* **Feature flags** → Configure database integration and other features in `app_config.py`
* **Multi-language** → System automatically creates unique filenames for different language combinations
* **Multiuser** → Use `--session-id` for user isolation

### Transcript App Specific

* **Dependencies** → Requires `youtube-transcript-api` package
* **Formats** → Choose from clean, timestamped, structured outputs
* **Language detection** → Auto-detects available languages or specify with `--language`
* **Metadata analysis** → Rich content analysis (disable with `--no-metadata`)
* **Preview mode** → Use `--preview` to see content without downloading
* **Multiuser** → Use `--session-id` for user isolation

### Multiuser Specific

* **Session management** → Each `--session-id` creates isolated user space
* **Directory structure** → Downloads organized by session and video UUIDs
* **Backward compatibility** → Works without `--session-id` (creates new session)
* **Web integration** → Perfect for web app development
* **No database** → Pure session-based approach

## Migration from Unified App

If you were using the previous unified app:

1. **For audio downloads**: Use `yt_audio_app` instead of `--audio-only` flag
2. **For video downloads**: Use `yt_video_app download` instead of the unified app
3. **For transcript downloads**: Use `yt_transcript_app` (new feature)
4. **Configuration**: Video settings moved to `src/common/app_config.py`
5. **CLI options**: Audio, video, and transcript apps have separate, focused option sets
6. **New features**: Language selection, force downloads, multiuser support, and feature flags
7. **Subcommands**: Video app uses subcommands (`download`, `info`, `languages`, `formats`, `config`)
8. **Multiuser support**: All apps now support `--session-id` for user isolation
9. **Transcript support**: New transcript downloader with multiple format outputs

## License

MIT