"""
Core business logic for YouTube audio downloader.

This module contains the core audio download functionality with hardcoded settings.
It's designed to be simple, reliable, and focused solely on audio downloads.
"""

import os
import logging
from typing import Optional, Dict, Any, Callable
import yt_dlp

# Import audio-specific helpers
from .audio_helpers import (
    get_audio_output_template,
    get_audio_settings,
    validate_audio_url
)

# Initialize logger for this module
logger = logging.getLogger("audio_core")


def default_audio_progress_hook(d):
    """Default progress hook for audio downloads."""
    if d.get('status') == 'downloading':
        pct = (d.get('_percent_str') or '').strip()
        print(f"\rDownloading audio: {pct}", end='', flush=True)
    elif d.get('status') == 'finished':
        print("\rAudio download: 100%    ")


def create_audio_ydl_options(output_template: str, 
                            progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Create yt-dlp options for audio download with hardcoded settings.
    
    Args:
        output_template: Output template for filename
        progress_callback: Optional progress callback function
        
    Returns:
        yt-dlp options dictionary
    """
    progress_hooks = [progress_callback] if progress_callback else [default_audio_progress_hook]
    audio_settings = get_audio_settings()
    
    return {
        'format': audio_settings['format'],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio', 
            'preferredcodec': audio_settings['codec'], 
            'preferredquality': audio_settings['quality'],
        }],
        'outtmpl': output_template,
        'restrictfilenames': audio_settings['restrict_filenames'],
        'progress_hooks': progress_hooks,
        'quiet': False,
        'no_warnings': False,
    }


def extract_expected_audio_filename(ydl, info: Dict[str, Any]) -> str:
    """
    Extract expected filename for audio download.
    
    Args:
        ydl: yt-dlp instance
        info: Video information dictionary
        
    Returns:
        Expected audio file path
    """
    base, _ = os.path.splitext(ydl.prepare_filename(info))
    return base + '.mp3'


def check_audio_file_exists(expected_path: str, file_checker: Callable) -> bool:
    """
    Check if audio file already exists.
    
    Args:
        expected_path: Path to check
        file_checker: Function to check file existence
        
    Returns:
        True if file exists, False otherwise
    """
    exists = file_checker(expected_path)
    if exists:
        logger.info(f"Audio file already present: {expected_path}")
        print(f"Audio file already present: {expected_path}")
    return exists


def perform_audio_download(ydl, url: str, expected_path: str, file_checker: Callable) -> bool:
    """
    Perform the actual audio download and verify success.
    
    Args:
        ydl: yt-dlp instance
        url: URL to download
        expected_path: Expected output path
        file_checker: Function to check file existence
        
    Returns:
        True if download successful, False otherwise
    """
    logger.info("Starting audio download...")
    ydl.download([url])
    
    if file_checker(expected_path):
        logger.info(f"Audio download completed: {expected_path}")
        return True
    else:
        logger.error(f"Audio download failed - file not found: {expected_path}")
        return False


def download_audio_mp3(url: str, 
                      output_template: Optional[str] = None,
                      custom_download_path: Optional[str] = None,
                      progress_callback: Optional[Callable] = None,
                      downloader=None, 
                      file_checker=None) -> str:
    """
    Download best audio from YouTube URL as MP3.
    
    This is the main function for audio downloads with hardcoded settings:
    - Format: bestaudio/best
    - Codec: MP3
    - Quality: 192kbps
    - Filename restriction: enabled for safety
    
    Args:
        url: YouTube URL to download
        output_template: Output template for filename (uses default if None)
        custom_download_path: Custom download directory (uses default if None)
        progress_callback: Optional progress callback function
        downloader: yt-dlp downloader class (defaults to yt_dlp.YoutubeDL)
        file_checker: Function to check if file exists (defaults to os.path.exists)
        
    Returns:
        Path to downloaded MP3 file
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If download fails
    """
    logger.info(f"Starting audio download for URL: {url}")
    
    # Validate URL
    if not validate_audio_url(url):
        error_msg = f"Invalid YouTube URL: {url}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Get output template
    if output_template is None:
        output_template = get_audio_output_template(custom_download_path)
        logger.debug(f"Using output template: {output_template}")
    
    # Set up dependencies
    if downloader is None:
        downloader = yt_dlp.YoutubeDL
    if file_checker is None:
        file_checker = os.path.exists
    
    # Create yt-dlp options
    ydl_opts = create_audio_ydl_options(output_template, progress_callback)
    logger.debug(f"yt-dlp options: {ydl_opts}")
    
    with downloader(ydl_opts) as ydl:
        logger.info("Extracting video information...")
        info = ydl.extract_info(url, download=False)
        expected_path = extract_expected_audio_filename(ydl, info)
        
        # Check if file already exists
        if check_audio_file_exists(expected_path, file_checker):
            return expected_path
        
        # Perform download
        if perform_audio_download(ydl, url, expected_path, file_checker):
            return expected_path
        else:
            raise RuntimeError(f"Audio download failed - file not found: {expected_path}")


def get_audio_metadata(url: str, downloader=None) -> Dict[str, Any]:
    """
    Extract basic metadata from YouTube URL without downloading.
    
    Args:
        url: YouTube URL to extract metadata from
        downloader: yt-dlp downloader class (defaults to yt_dlp.YoutubeDL)
        
    Returns:
        Dictionary containing basic video metadata
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If metadata extraction fails
    """
    logger.info(f"Extracting metadata for URL: {url}")
    
    # Validate URL
    if not validate_audio_url(url):
        error_msg = f"Invalid YouTube URL: {url}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Set up dependencies
    if downloader is None:
        downloader = yt_dlp.YoutubeDL
    
    # Create minimal options for metadata extraction
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with downloader(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            metadata = {
                'video_id': info.get('id') or info.get('display_id'),
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader') or info.get('uploader_id'),
                'channel': info.get('channel'),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date')
            }
            logger.debug(f"Extracted metadata: {metadata}")
            return metadata
        except Exception as e:
            error_msg = f"Failed to extract metadata: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
