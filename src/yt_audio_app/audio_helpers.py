"""
Audio-specific helper functions for the YouTube Audio Downloader.

This module contains audio-specific utilities for path management
and output template generation. Audio settings are hardcoded for simplicity.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Import generic utilities
from path_utils import resolve_path, ensure_directory, get_script_directories

# Import multiuser support
from ..common.user_context import UserContext

# Initialize logger for this module
logger = logging.getLogger("audio_helpers")

# Hardcoded audio settings - no configuration needed
AUDIO_SETTINGS = {
    'format': 'bestaudio/best',
    'codec': 'mp3',
    'quality': '192',  # 192kbps
    'output_template': '%(title)s.%(ext)s',
    'restrict_filenames': True  # Safer for audio files
}


def get_audio_downloads_directory(custom_path: Optional[str] = None) -> Path:
    """
    Get the downloads directory for audio files.
    
    Args:
        custom_path: Custom download path (defaults to ./downloads/audio)
        
    Returns:
        Resolved downloads directory path
    """
    if custom_path:
        download_path = custom_path
        logger.debug(f"Using custom download path: {download_path}")
    else:
        download_path = "downloads/audio"
        logger.debug(f"Using default audio download path: {download_path}")
    
    _, base_dir = get_script_directories()
    return resolve_path(download_path, base_dir)


def get_audio_output_template(custom_path: Optional[str] = None, 
                            custom_template: Optional[str] = None,
                            user_context: Optional[UserContext] = None,
                            video_url: Optional[str] = None) -> str:
    """
    Get complete output template for audio files including the download path.
    
    Args:
        custom_path: Custom download path
        custom_template: Custom template to use instead of default
        user_context: User context for multiuser support (optional)
        video_url: Video URL for user-specific path (required if user_context provided)
        
    Returns:
        Complete output template with path
    """
    # Use multiuser path if user context and video URL provided
    if user_context and video_url:
        download_path = user_context.get_audio_download_path(video_url)
        logger.debug(f"Using multiuser audio path: {download_path}")
    else:
        download_path = get_audio_downloads_directory(custom_path)
        logger.debug(f"Using single-user audio path: {download_path}")
    
    if custom_template:
        template = custom_template
        logger.debug(f"Using custom template: {template}")
    else:
        template = AUDIO_SETTINGS['output_template']
        logger.debug(f"Using default audio template: {template}")
    
    # Ensure download directory exists
    ensure_directory(download_path)
    
    # Combine path and template
    full_template = str(download_path / template)
    logger.debug(f"Complete audio output template: {full_template}")
    return full_template


def get_audio_settings() -> Dict[str, Any]:
    """
    Get hardcoded audio settings.
    
    Returns:
        Dictionary containing audio settings
    """
    logger.debug("Returning hardcoded audio settings")
    return AUDIO_SETTINGS.copy()


def validate_audio_url(url: str) -> bool:
    """
    Basic validation for YouTube URLs.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL appears to be a valid YouTube URL
    """
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower().strip()
    youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com']
    
    return any(domain in url_lower for domain in youtube_domains)
