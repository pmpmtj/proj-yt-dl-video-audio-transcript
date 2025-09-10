# my_project/src/yt_dl_app/__main__.py
"""
Main entry point for the yt_dl_app package.

This module provides the main entry point for the YouTube downloader application.
It can be run in multiple ways:

1. As a package module: python -m yt_dl_app
2. As a standalone script: python src/yt_dl_app/__main__.py
3. Direct execution: python -m src.yt_dl_app

The core functionality is organized as:
- yt_dl_core.py: Core business logic (download functions, metadata extraction)
- yt_dl_core_CLI.py: CLI interface and user interaction logic
- yt_dl_helpers.py: Helper functions for path and configuration management

This script maintains backward compatibility while using the new modular architecture.
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
from src.yt_dl_app.yt_dl_core_CLI import main

# Import logging configuration
from src.common.logging_config import setup_logging
import logging

# Initialize centralized logging
setup_logging()
logger = logging.getLogger("run")


if __name__ == "__main__":
    logger.info("Starting YouTube downloader application")
    try:
        main()
        logger.info("YouTube downloader application completed successfully")
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"YouTube downloader application failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)