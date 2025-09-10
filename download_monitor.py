# src/yt_dl_app/download_monitor.py
"""
Download monitoring utilities for tracking download status and file existence.

This module provides common functionality for monitoring downloads that can be used
by both CLI and web interfaces.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path

# Initialize logger
logger = logging.getLogger("yt_dl_app.download_monitor")


class DownloadResult:
    """Result object for download operations with detailed status information."""
    
    def __init__(self, path: str, status: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        self.path = path
        self.status = status  # 'downloaded', 'already_exists', 'failed'
        self.message = message
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization."""
        return {
            'path': self.path,
            'status': self.status,
            'message': self.message,
            'metadata': self.metadata
        }


def monitor_download(download_func: Callable, *args, **kwargs) -> DownloadResult:
    """
    Monitor a download function and return detailed status information.
    
    Args:
        download_func: The download function to monitor (e.g., download_audio_mp3)
        *args: Arguments to pass to download_func
        **kwargs: Keyword arguments to pass to download_func
        
    Returns:
        DownloadResult object with status information
    """
    logger.info(f"Starting download monitoring for {download_func.__name__}")
    
    try:
        # Record start time
        start_time = time.time()
        
        # Call the download function
        result_path = download_func(*args, **kwargs)
        
        if not result_path or not os.path.exists(result_path):
            return DownloadResult(
                path=result_path or "unknown",
                status="failed",
                message="Download failed - file not found",
                metadata={'error': 'file_not_found'}
            )
        
        # Check if file was actually downloaded by comparing timestamps
        file_mtime = os.path.getmtime(result_path)
        download_duration = file_mtime - start_time
        
        if download_duration > 1:  # File was modified more than 1 second after start
            logger.info(f"Download completed successfully: {result_path}")
            return DownloadResult(
                path=result_path,
                status="downloaded",
                message=f"Downloaded successfully: {os.path.basename(result_path)}",
                metadata={
                    'download_duration': download_duration,
                    'file_size': os.path.getsize(result_path)
                }
            )
        else:
            # File wasn't actually downloaded (was already there)
            logger.info(f"File already existed, no download performed: {result_path}")
            return DownloadResult(
                path=result_path,
                status="already_exists",
                message=f"File already exists: {os.path.basename(result_path)}",
                metadata={
                    'file_size': os.path.getsize(result_path),
                    'file_age': time.time() - file_mtime
                }
            )
            
    except Exception as e:
        logger.error(f"Download monitoring failed: {e}")
        return DownloadResult(
            path="unknown",
            status="failed",
            message=f"Download failed: {str(e)}",
            metadata={'error': str(e)}
        )


def check_file_exists(url: str, audio_only: bool = False, ext: str = "mp4") -> Optional[str]:
    """
    Check if a file already exists for the given URL and parameters.
    
    Args:
        url: YouTube URL
        audio_only: Whether checking for audio file
        ext: Container extension for video files
        
    Returns:
        Path to existing file if found, None otherwise
    """
    try:
        import yt_dlp
        
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            expected_filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(expected_filename)
            expected_ext = 'mp3' if audio_only else (ext if ext in ('mp4', 'webm') else 'mp4')
            expected_path = base + f'.{expected_ext}'
            
            if os.path.exists(expected_path):
                logger.debug(f"File already exists: {expected_path}")
                return expected_path
            else:
                logger.debug(f"File does not exist: {expected_path}")
                return None
                
    except Exception as e:
        logger.error(f"Error checking file existence: {e}")
        return None


def force_download_if_exists(url: str, audio_only: bool = False, ext: str = "mp4") -> bool:
    """
    Force download by removing existing file if it exists.
    
    Args:
        url: YouTube URL
        audio_only: Whether checking for audio file
        ext: Container extension for video files
        
    Returns:
        True if file was removed, False if no file existed
    """
    existing_file = check_file_exists(url, audio_only, ext)
    
    if existing_file and os.path.exists(existing_file):
        try:
            os.remove(existing_file)
            logger.info(f"Removed existing file for force download: {existing_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove existing file: {e}")
            return False
    
    return False
