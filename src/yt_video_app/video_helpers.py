# my_project/src/yt_video_app/video_helpers.py
"""
video_helpers.py

YouTube video downloader specific helper functions for path and configuration management.
"""

import logging
from pathlib import Path
from typing import Union, Optional, Dict, Any

# Import generic utilities
from path_utils import resolve_path, ensure_directory, get_script_directories

# Import the new Python configuration
from ..common.app_config import get_config, get_download_config, get_video_config, get_download_path, get_video_settings

# Initialize logger for this module
logger = logging.getLogger("video_helpers")


def get_downloads_directory(config: Optional[Dict[str, Any]] = None) -> Path:
    """
    Get the configured downloads directory.

    Args:
        config: Configuration dictionary (loads from Python module if None)

    Returns:
        Resolved downloads directory path
    """
    if config is None:
        download_path = get_download_path()
    else:
        download_path = config.get("download", {}).get("download_path", "downloads")
    
    logger.debug(f"Using download path: {download_path}")
    _, base_dir = get_script_directories()
    return resolve_path(download_path, base_dir)


def get_default_video_settings(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get default video settings from configuration.
    
    Args:
        config: Configuration dictionary (loads from Python module if None)
        
    Returns:
        Dictionary containing default video settings
    """
    if config is None:
        logger.debug("Loading video settings from Python module")
        return get_video_settings()
    
    logger.debug("Loading video settings from provided config")
    video_config = config.get("video", {})
    return {
        'ext': video_config.get('ext', 'mp4'),
        'quality': video_config.get('quality', 'best'),
        'output_template': video_config.get('output_template', '%(title)s.%(ext)s'),
        'restrict_filenames': video_config.get('restrict_filenames', False)
    }


def get_output_template_with_path(config: Optional[Dict[str, Any]] = None, 
                                 custom_template: Optional[str] = None) -> str:
    """
    Get complete output template including the download path.
    
    Args:
        config: Configuration dictionary (loads from Python module if None)
        custom_template: Custom template to use instead of config default
        
    Returns:
        Complete output template with path
    """
    download_path = get_downloads_directory(config)
    
    if custom_template:
        template = custom_template
        logger.debug(f"Using custom template: {template}")
    else:
        video_settings = get_default_video_settings(config)
        template = video_settings['output_template']
        logger.debug(f"Using config template: {template}")
    
    # Ensure download directory exists
    ensure_directory(download_path)
    
    # Combine path and template
    full_template = str(download_path / template)
    logger.debug(f"Complete output template: {full_template}")
    return full_template
