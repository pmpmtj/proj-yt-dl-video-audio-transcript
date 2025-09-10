"""
Application configuration module.

This module contains all application configuration settings in Python format,
replacing the previous JSON-based configuration system.
"""

from typing import Dict, Any

# Application configuration
APP_CONFIG = {
    "download": {
        "download_path": "./downloads"
    },
    "video": {
        "ext": "mp4",
        "quality": "best", 
        "output_template": "%(title)s.%(ext)s",
        "restrict_filenames": True,
        "audio_only": False
    }
}

def get_config() -> Dict[str, Any]:
    """
    Get the application configuration.
    
    Returns:
        Configuration dictionary
    """
    return APP_CONFIG.copy()

def get_download_config() -> Dict[str, Any]:
    """
    Get download-specific configuration.
    
    Returns:
        Download configuration dictionary
    """
    return APP_CONFIG["download"].copy()

def get_video_config() -> Dict[str, Any]:
    """
    Get video-specific configuration.
    
    Returns:
        Video configuration dictionary
    """
    return APP_CONFIG["video"].copy()

def get_download_path() -> str:
    """
    Get the download path from configuration.
    
    Returns:
        Download path string
    """
    return APP_CONFIG["download"]["download_path"]

def get_video_settings() -> Dict[str, Any]:
    """
    Get video settings from configuration.
    
    Returns:
        Video settings dictionary
    """
    return {
        'ext': APP_CONFIG["video"]['ext'],
        'quality': APP_CONFIG["video"]['quality'],
        'output_template': APP_CONFIG["video"]['output_template'],
        'restrict_filenames': APP_CONFIG["video"]['restrict_filenames'],
        'audio_only': APP_CONFIG["video"]['audio_only']
    }
