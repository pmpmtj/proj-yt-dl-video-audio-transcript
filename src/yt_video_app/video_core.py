"""
Core business logic for YouTube video downloader.

This module contains the core video download functionality and metadata parsing.
It's designed to be independent of CLI or web interface concerns.
Focuses solely on video downloads with configurable quality and format options.
"""

import os
import logging
from typing import Optional, Dict, Any, List, Set, Tuple, Callable
import yt_dlp

# Import configuration utilities
from path_utils import load_config
from .video_helpers import (
    get_default_video_settings, 
    get_output_template_with_path,
    get_downloads_directory
)

# Initialize logger for this module
logger = logging.getLogger("video_core")


# --- Progress Hook (Callback Interface) ----------------------------------------

def default_video_progress_hook(d):
    """Default progress hook for video downloads."""
    if d.get('status') == 'downloading':
        pct = (d.get('_percent_str') or '').strip()
        print(f"\rDownloading video: {pct}", end='', flush=True)
    elif d.get('status') == 'finished':
        print("\rVideo download: 100%    ")


# --- Format Selection Logic ---------------------------------------------------

def _fmt_for(ext: str, quality: Optional[str]) -> str:
    """Build a strict yt-dlp format string so merges don't fail.
    
    - For webm: pick VP9/AV1 + Opus/Vorbis (both *.webm).
    - For mp4:  pick H.264/AV1 in MP4 + AAC (m4a) (both *.mp4/*.m4a).
    No cross-container mixing, so remux is trivial.
    
    Args:
        ext: Container extension ('mp4' or 'webm')
        quality: Quality setting ('best' or height like '1080p')
        
    Returns:
        yt-dlp format string
    """
    q = (quality or 'best').lower()
    if q != 'best':
        h = int(q.rstrip('p'))  # e.g. '1080p' -> 1080
        height = f"[height<={h}]"
    else:
        height = ''

    if ext == 'webm':
        # Prefer separate A/V in webm, else progressive webm — no other fallback
        return f"bestvideo[ext=webm]{height}+bestaudio[ext=webm]/best[ext=webm]{height}"
    # mp4 path
    return f"bestvideo[ext=mp4]{height}+bestaudio[ext=m4a]/best[ext=mp4]{height}"


# --- Configuration and Setup Functions ----------------------------------------

def _load_download_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load configuration for download operations.
    
    Args:
        config: Configuration dictionary (loads from file if None)
        
    Returns:
        Configuration dictionary
    """
    if config is None:
        config = load_config()
        logger.debug("Loaded configuration from file")
    return config


def _get_video_download_settings(config: Dict[str, Any], outtmpl: Optional[str] = None, 
                                restrict: Optional[bool] = None, ext: Optional[str] = None, 
                                quality: Optional[str] = None) -> Tuple[str, bool, str, str]:
    """Get video download settings from config and parameters.
    
    Args:
        config: Configuration dictionary
        outtmpl: Output template for filename (uses config default if None)
        restrict: Whether to restrict filenames to ASCII (uses config default if None)
        ext: Container extension (uses config default if None)
        quality: Quality setting (uses config default if None)
        
    Returns:
        Tuple of (output_template, restrict_filenames, extension, quality)
    """
    video_settings = get_default_video_settings(config)
    
    if outtmpl is None:
        outtmpl = get_output_template_with_path(config)
        logger.debug(f"Using output template: {outtmpl}")
    
    if restrict is None:
        restrict = video_settings['restrict_filenames']
        logger.debug(f"Using restrict filenames: {restrict}")
        
    if ext is None:
        ext = video_settings['ext']
        logger.debug(f"Using container extension: {ext}")
        
    if quality is None:
        quality = video_settings['quality']
        logger.debug(f"Using quality setting: {quality}")
    
    return outtmpl, restrict, ext, quality


def _create_video_ydl_options(outtmpl: str, restrict: bool, ext: str, quality: str,
                             progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """Create yt-dlp options for video download.
    
    Args:
        outtmpl: Output template for filename
        restrict: Whether to restrict filenames to ASCII
        ext: Container extension
        quality: Quality setting
        progress_callback: Optional progress callback function
        
    Returns:
        yt-dlp options dictionary
    """
    progress_hooks = [progress_callback] if progress_callback else [default_video_progress_hook]
    
    merge_ext = ext if ext in ('mp4', 'webm') else 'mp4'
    format_string = _fmt_for(merge_ext, quality)
    logger.debug(f"Using format string: {format_string}")
    
    return {
        'format': format_string,
        'merge_output_format': merge_ext,
        'outtmpl': outtmpl,
        'restrictfilenames': restrict,
        'progress_hooks': progress_hooks,
        'quiet': False,
        'no_warnings': False,
    }


def _extract_expected_filename(ydl, info: Dict[str, Any], file_extension: str) -> str:
    """Extract expected filename from yt-dlp info.
    
    Args:
        ydl: yt-dlp instance
        info: Video information dictionary
        file_extension: Expected file extension (e.g., 'mp4', 'webm')
        
    Returns:
        Expected file path
    """
    base, _ = os.path.splitext(ydl.prepare_filename(info))
    return base + f'.{file_extension}'


def _check_file_exists(expected_path: str, file_checker: Callable) -> bool:
    """Check if file already exists.
    
    Args:
        expected_path: Path to check
        file_checker: Function to check file existence
        
    Returns:
        True if file exists, False otherwise
    """
    exists = file_checker(expected_path)
    if exists:
        logger.info(f"Video file already present: {expected_path}")
        print(f"Video file already present: {expected_path}")
    return exists


def _perform_download(ydl, url: str, expected_path: str, file_checker: Callable) -> bool:
    """Perform the actual download and verify success.
    
    Args:
        ydl: yt-dlp instance
        url: URL to download
        expected_path: Expected output path
        file_checker: Function to check file existence
        
    Returns:
        True if download successful, False otherwise
    """
    logger.info("Starting video download...")
    ydl.download([url])
    
    if file_checker(expected_path):
        logger.info(f"Video download completed: {expected_path}")
        return True
    else:
        logger.error(f"Video download failed - file not found: {expected_path}")
        return False


# --- Core Download Functions --------------------------------------------------

def download_video_with_audio(url: str, outtmpl: Optional[str] = None, 
                            restrict: Optional[bool] = None, ext: Optional[str] = None, 
                            quality: Optional[str] = None,
                            progress_callback: Optional[Callable] = None,
                            config: Optional[Dict[str, Any]] = None,
                            downloader=None, file_checker=None) -> Optional[str]:
    """Download video+audio and merge to the chosen container without re-encoding.
    
    Args:
        url: YouTube URL to download
        outtmpl: Output template for filename (uses config default if None)
        restrict: Whether to restrict filenames to ASCII (uses config default if None)
        ext: Container extension ('mp4' or 'webm') (uses config default if None)
        quality: Quality setting ('best' or height like '1080p') (uses config default if None)
        progress_callback: Optional progress callback function
        config: Configuration dictionary (loads from file if None)
        downloader: yt-dlp downloader class (defaults to yt_dlp.YoutubeDL)
        file_checker: Function to check if file exists (defaults to os.path.exists)
        
    Returns:
        Path to downloaded video file, or None if failed
    """
    logger.info(f"Starting video download for URL: {url}")
    
    # Load configuration
    config = _load_download_config(config)
    
    # Get download settings
    outtmpl, restrict, ext, quality = _get_video_download_settings(config, outtmpl, restrict, ext, quality)
    
    # Set up dependencies
    if downloader is None:
        downloader = yt_dlp.YoutubeDL
    if file_checker is None:
        file_checker = os.path.exists
    
    # Create yt-dlp options
    ydl_opts = _create_video_ydl_options(outtmpl, restrict, ext, quality, progress_callback)
    logger.debug(f"yt-dlp options: {ydl_opts}")
    
    # Get video information using shared function
    try:
        info = get_video_info(url, downloader)
    except Exception as e:
        logger.error(f"Failed to extract video information: {e}")
        return None
    
    with downloader(ydl_opts) as ydl:
        # Determine expected file extension
        merge_ext = ext if ext in ('mp4', 'webm') else 'mp4'
        expected_path = _extract_expected_filename(ydl, info, merge_ext)
        
        # Check if file already exists
        if _check_file_exists(expected_path, file_checker):
            return expected_path
        
        # Perform download
        if _perform_download(ydl, url, expected_path, file_checker):
            return expected_path
        else:
            logger.error(f"Video download failed - file not found: {expected_path}")
            return None


# --- Metadata Parsing Functions -----------------------------------------------

LANG_LABELS = {
    'en': 'English', 'en-US': 'English (US)', 'en-GB': 'English (UK)',
    'pt': 'Português', 'pt-PT': 'Português (PT)', 'pt-BR': 'Português (BR)',
    'es': 'Español', 'fr': 'Français', 'de': 'Deutsch', 'it': 'Italiano',
    'ja': '日本語', 'zh': '中文', 'ru': 'Русский'
}


def _label_for_lang(code: str) -> str:
    """Get human-readable label for language code."""
    if not code:
        return 'Original'
    return LANG_LABELS.get(code, code)


def extract_basic_meta(info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract basic metadata from yt-dlp info dict."""
    return {
        'video_id': info.get('id') or info.get('display_id'),
        'title': info.get('title'),
        'duration': info.get('duration'),
        'uploader': info.get('uploader') or info.get('uploader_id'),
        'channel': info.get('channel')
    }


def extract_containers_and_qualities(info: Dict[str, Any]) -> Tuple[List[str], List[int]]:
    """Extract available containers and video qualities from yt-dlp info dict."""
    formats = info.get('formats') or []
    containers: Set[str] = set()
    heights: Set[int] = set()
    for f in formats:
        ext = (f.get('ext') or '').lower()
        vcodec = (f.get('vcodec') or '').lower()
        acodec = (f.get('acodec') or '').lower()
        if ext:
            containers.add(ext)
        if vcodec and vcodec != 'none':
            h = f.get('height')
            if isinstance(h, int) and h > 0:
                heights.add(h)
        # Some progressive formats (video+audio) are listed without vcodec height; try resolution fallback
        if (not f.get('height')) and f.get('resolution'):
            try:
                # resolution like "1280x720"
                parts = str(f['resolution']).lower().split('x')
                if len(parts) == 2:
                    heights.add(int(parts[1]))
            except Exception:
                pass
    # only offer mp4/webm in UI
    ui_containers = [c for c in ['mp4', 'webm'] if c in containers]
    return ui_containers, sorted(heights)


def extract_audio_languages(info: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract available audio languages from yt-dlp info dict."""
    formats = info.get('formats') or []
    langs: Set[str] = set()
    for f in formats:
        acodec = (f.get('acodec') or '').lower()
        if not acodec or acodec == 'none':
            continue
        # Try multiple fields that may carry lang info
        lang = (
            f.get('language')
            or (f.get('audio_track') or {}).get('language')
            or (f.get('audio_track') or {}).get('id')
        )
        if isinstance(lang, str):
            lang = lang.strip()
        if lang:
            langs.add(lang)
    if not langs:
        return [{ 'code': 'original', 'label': 'Original' }]
    out = [{ 'code': 'original', 'label': 'Original' }]
    out.extend({ 'code': l, 'label': _label_for_lang(l) } for l in sorted(langs))
    return out


def extract_subtitle_languages(info: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract available subtitle languages from yt-dlp info dict."""
    subs = info.get('subtitles') or {}
    autos = info.get('automatic_captions') or {}
    keys = set()
    for d in (subs, autos):
        for k in d.keys():
            if isinstance(k, str):
                keys.add(k.strip())
    return [{ 'code': k, 'label': _label_for_lang(k) } for k in sorted(keys)]


# --- Shared Video Information Functions -----------------------------------------

def get_video_info(url: str, downloader=None) -> Dict[str, Any]:
    """Extract video information from YouTube URL without downloading.
    
    This is the shared function that eliminates duplication of ydl.extract_info calls.
    All other functions that need video metadata should use this function.
    
    Args:
        url: YouTube URL to extract information from
        downloader: yt-dlp downloader class (defaults to yt_dlp.YoutubeDL)
        
    Returns:
        Dictionary containing complete video information from yt-dlp
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If information extraction fails
    """
    logger.info(f"Extracting video information for URL: {url}")
    
    # Set up dependencies
    if downloader is None:
        downloader = yt_dlp.YoutubeDL
    
    # Create minimal options for information extraction
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with downloader(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            logger.debug(f"Successfully extracted video information for: {info.get('title', 'Unknown')}")
            return info
        except Exception as e:
            error_msg = f"Failed to extract video information: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)


def get_video_metadata(url: str, downloader=None) -> Dict[str, Any]:
    """Get basic video metadata from YouTube URL without downloading.
    
    Args:
        url: YouTube URL to extract metadata from
        downloader: yt-dlp downloader class (defaults to yt_dlp.YoutubeDL)
        
    Returns:
        Dictionary containing basic video metadata
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If metadata extraction fails
    """
    logger.info(f"Getting video metadata for URL: {url}")
    
    try:
        info = get_video_info(url, downloader)
        metadata = extract_basic_meta(info)
        logger.debug(f"Extracted metadata: {metadata}")
        return metadata
    except Exception as e:
        error_msg = f"Failed to get video metadata: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def get_video_languages(url: str, downloader=None) -> Dict[str, List[Dict[str, str]]]:
    """Get available audio and subtitle languages from YouTube URL without downloading.
    
    Args:
        url: YouTube URL to extract language information from
        downloader: yt-dlp downloader class (defaults to yt_dlp.YoutubeDL)
        
    Returns:
        Dictionary containing:
        - 'audio_languages': List of available audio languages
        - 'subtitle_languages': List of available subtitle languages
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If language extraction fails
    """
    logger.info(f"Getting video languages for URL: {url}")
    
    try:
        info = get_video_info(url, downloader)
        audio_langs = extract_audio_languages(info)
        subtitle_langs = extract_subtitle_languages(info)
        
        result = {
            'audio_languages': audio_langs,
            'subtitle_languages': subtitle_langs
        }
        
        logger.debug(f"Found {len(audio_langs)} audio languages and {len(subtitle_langs)} subtitle languages")
        return result
    except Exception as e:
        error_msg = f"Failed to get video languages: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def get_video_formats(url: str, downloader=None) -> Dict[str, Any]:
    """Get available video formats and qualities from YouTube URL without downloading.
    
    Args:
        url: YouTube URL to extract format information from
        downloader: yt-dlp downloader class (defaults to yt_dlp.YoutubeDL)
        
    Returns:
        Dictionary containing:
        - 'containers': List of available container formats
        - 'qualities': List of available video qualities (heights)
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If format extraction fails
    """
    logger.info(f"Getting video formats for URL: {url}")
    
    try:
        info = get_video_info(url, downloader)
        containers, qualities = extract_containers_and_qualities(info)
        
        result = {
            'containers': containers,
            'qualities': qualities
        }
        
        logger.debug(f"Found containers: {containers}, qualities: {qualities}")
        return result
    except Exception as e:
        error_msg = f"Failed to get video formats: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)