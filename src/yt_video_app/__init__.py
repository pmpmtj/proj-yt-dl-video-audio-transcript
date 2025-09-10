"""
YouTube Video Downloader Package

A modular YouTube video downloader built on yt-dlp + FFmpeg with a clean, production-ready architecture.

Features:
- Modular Design: Separated core logic, CLI interface, and configuration
- Container Compatibility: Enforces container-compatible tracks to avoid FFmpeg errors
- Quality Control: Configurable quality caps and format selection
- Video Support: Download video with audio in various formats (MP4, WebM)
- Language Support: Extract available audio and subtitle languages
- Metadata Extraction: Get video information without downloading
- Configuration-Driven: Python-based configuration for easy customization
- Comprehensive Logging: Centralized logging with hybrid approach (main log + specialized logs)
- Cross-Platform: Works on Windows, macOS, and Linux

The core functionality is organized as:
- video_core.py: Core business logic (video download functions, metadata extraction)
- video_cli.py: CLI interface and user interaction logic
- video_helpers.py: Helper functions for path and configuration management

This package is focused solely on video downloads. For audio-only downloads, use yt_audio_app.
"""

# Import core functions for easy access
from .video_core import (
    download_video_with_audio,
    get_video_info,
    get_video_metadata,
    get_video_languages,
    get_video_formats,
    extract_audio_languages,
    extract_subtitle_languages,
    extract_containers_and_qualities,
    extract_basic_meta
)

# Import CLI functions
from .video_cli import main, parse_args, VideoCLIController

__version__ = "1.0.0"
__author__ = "YouTube Video Downloader"

# Define what gets imported with "from yt_video_app import *"
__all__ = [
    # Core download functions
    'download_video_with_audio',
    
    # Information extraction functions
    'get_video_info',
    'get_video_metadata', 
    'get_video_languages',
    'get_video_formats',
    
    # Metadata parsing functions
    'extract_audio_languages',
    'extract_subtitle_languages',
    'extract_containers_and_qualities',
    'extract_basic_meta',
    
    # CLI functions
    'main',
    'parse_args',
    'VideoCLIController'
]