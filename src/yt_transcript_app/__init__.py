"""
YouTube Transcript Downloader Application.

This package provides comprehensive transcript downloading capabilities for YouTube videos
with multiple format support, rich metadata collection, and content analysis features.

Main Components:
- trans_core: Core transcript download and processing functionality
- trans_core_cli: Command-line interface for transcript downloads
- transcript_processor: Enhanced transcript processing and formatting
- metadata_collector: Rich metadata collection and content analysis
- metadata_exporter: Export metadata in multiple formats (JSON, CSV, Markdown)
- _get_transcript_list: Transcript discovery and language selection utilities

Features:
- Multiple output formats (clean, timestamped, structured)
- Rich metadata collection and analysis
- Chapter detection and content analysis
- Multiple export formats (JSON, CSV, Markdown)
- Auto-language detection and selection
- Content quality assessment
- LLM suitability analysis
- Batch processing support

Usage:
    python -m yt_transcript_app "https://www.youtube.com/watch?v=VIDEO_ID"
    python -m yt_transcript_app "URL" --formats clean structured --metadata
    python -m yt_transcript_app "URL" --preview --language en
"""

# Version information
__version__ = "1.0.0"
__author__ = "YouTube Transcript Downloader"
__description__ = "Comprehensive YouTube transcript downloader with rich metadata analysis"

# Import main functionality for easy access
from .trans_core import (
    download_transcript,
    get_transcript_metadata,
    preview_transcript,
    validate_transcript_url,
    extract_video_id
)

from .trans_core_cli import main as cli_main

# Export main functions
__all__ = [
    'download_transcript',
    'get_transcript_metadata', 
    'preview_transcript',
    'validate_transcript_url',
    'extract_video_id',
    'cli_main'
]
