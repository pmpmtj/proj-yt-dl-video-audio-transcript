# my_project/src/yt_video_app/__main__.py
"""
Main entry point for the yt_video_app package.

This module provides the main entry point for the YouTube video downloader application.
It can be run in multiple ways:

1. As a package module: python -m src.yt_video_app
2. As a standalone script: python src/yt_video_app/__main__.py
3. Direct execution: python -m src.yt_video_app

The core functionality is organized as:
- video_core.py: Core business logic (video download functions, metadata extraction)
- video_cli.py: CLI interface and user interaction logic
- video_helpers.py: Helper functions for path and configuration management

This script is focused solely on video downloads. For audio-only downloads, use yt_audio_app.
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
from .video_cli import main

# Import logging configuration
from ..common.logging_config import setup_logging
import logging

# Initialize centralized logging
setup_logging()
logger = logging.getLogger("run")


if __name__ == "__main__":
    logger.info("Starting YouTube Video Downloader application")
    try:
        main()
        logger.info("YouTube Video Downloader application completed successfully")
    except KeyboardInterrupt:
        logger.info("Video downloader interrupted by user")
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"YouTube Video Downloader application failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)