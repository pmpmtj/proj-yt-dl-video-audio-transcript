"""
Application configuration module.

This module contains all application configuration settings in Python format,
replacing the previous JSON-based configuration system.
"""

from typing import Dict, Any

# Application configuration for video downloader
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
        'restrict_filenames': APP_CONFIG["video"]['restrict_filenames']
    }

def get_feature_flags() -> Dict[str, Any]:
    """
    Get feature flags configuration.
    
    Returns:
        Feature flags dictionary
    """
    return APP_CONFIG["features"].copy()

def is_database_source_enabled() -> bool:
    """
    Check if database is configured as the single source of truth.
    
    Returns:
        True if database should be used as source of truth, False otherwise
    """
    return APP_CONFIG["features"]["use_database_as_source"]

def is_file_check_enabled() -> bool:
    """
    Check if file existence check should be performed.
    
    Returns:
        True if file existence check should be performed, False otherwise
    """
    return APP_CONFIG["features"]["enable_file_existence_check"]

def is_metadata_caching_enabled() -> bool:
    """
    Check if metadata caching is enabled.
    
    Returns:
        True if metadata caching is enabled, False otherwise
    """
    return APP_CONFIG["features"]["enable_metadata_caching"]

def is_download_history_enabled() -> bool:
    """
    Check if download history tracking is enabled.
    
    Returns:
        True if download history is enabled, False otherwise
    """
    return APP_CONFIG["features"]["enable_download_history"]
