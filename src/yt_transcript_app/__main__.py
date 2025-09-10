"""
Main entry point for the YouTube Transcript Downloader.

This module provides the main entry point for the transcript downloader application.
It can be run in multiple ways:

1. As a package module: python -m yt_transcript_app
2. As a standalone script: python src/yt_transcript_app/__main__.py
3. Direct execution: python -m yt_transcript_app

The transcript downloader provides comprehensive features:
- Multiple output formats (clean, timestamped, structured)
- Rich metadata collection and analysis
- Chapter detection and content analysis
- Multiple export formats (JSON, CSV, Markdown)
- Auto-language detection and selection
- Content quality assessment
- LLM suitability analysis

Usage:
    python -m yt_transcript_app "https://www.youtube.com/watch?v=VIDEO_ID"
    python -m yt_transcript_app "URL" --formats clean structured --metadata
    python -m yt_transcript_app "URL" --preview --language en
    python -m yt_transcript_app "URL" --list-languages
"""

import sys
from pathlib import Path

# Add the current directory and project root to Python path for standalone execution
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the CLI main function
from .trans_core_cli import main

# Import logging configuration
from ..common.logging_config import setup_logging
import logging

# Initialize centralized logging
setup_logging()
logger = logging.getLogger("transcript_app")


if __name__ == "__main__":
    logger.info("Starting YouTube Transcript Downloader application")
    try:
        main()
        logger.info("YouTube Transcript Downloader application completed successfully")
    except KeyboardInterrupt:
        logger.info("Transcript downloader interrupted by user")
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"YouTube Transcript Downloader application failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
