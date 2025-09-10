"""
Main entry point for the YouTube Audio Downloader.

This module provides the main entry point for the audio downloader application.
It can be run in multiple ways:

1. As a package module: python -m src.yt_audio_app
2. As a standalone script: python src/yt_audio_app/__main__.py
3. Direct execution: python -m src.yt_audio_app

The audio downloader is designed to be simple and focused:
- Downloads audio only as MP3 (192kbps)
- No configuration files needed
- Hardcoded settings for reliability
- Simple CLI interface

Usage:
    python -m src.yt_audio_app "https://www.youtube.com/watch?v=VIDEO_ID"
    python -m src.yt_audio_app "URL" --output-dir ./music
    python -m src.yt_audio_app "URL" --metadata
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
from .audio_cli import main

# Import logging configuration
from ..common.logging_config import setup_logging
import logging

# Initialize centralized logging
setup_logging()
logger = logging.getLogger("audio_app")


if __name__ == "__main__":
    logger.info("Starting YouTube Audio Downloader application")
    try:
        main()
        logger.info("YouTube Audio Downloader application completed successfully")
    except KeyboardInterrupt:
        logger.info("Audio downloader interrupted by user")
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"YouTube Audio Downloader application failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
