"""
Core business logic for YouTube transcript downloader.

This module contains the core transcript download and processing functionality.
It's designed to be simple, reliable, and focused on transcript downloads with
multiple format support and rich metadata collection.
"""

import os
import logging
import time
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Import transcript processing components
from .transcript_processor import TranscriptProcessor, process_transcript_data
from .metadata_collector import MetadataCollector, collect_comprehensive_metadata
from .metadata_exporter import export_metadata
from .get_transcript_list import get_transcript_list, list_transcript_metadata, print_and_select_default_transcript

# Import centralized utilities
from ..common.logging_config import setup_logging
from path_utils.path_utils import resolve_path, ensure_directory, get_script_directories

# Import multiuser support
from ..common.user_context import UserContext

# Initialize logger for this module
logger = logging.getLogger("trans_core")


def default_transcript_progress_hook(d):
    """Default progress hook for transcript downloads."""
    if d.get('status') == 'downloading':
        pct = (d.get('_percent_str') or '').strip()
        print(f"\rDownloading transcript: {pct}", end='', flush=True)
    elif d.get('status') == 'finished':
        print("\rTranscript download: 100%    ")


def validate_transcript_url(url: str) -> bool:
    """
    Validate if URL is a valid YouTube URL for transcript download.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    youtube_patterns = [
        'youtube.com/watch',
        'youtu.be/',
        'youtube.com/embed/',
        'youtube.com/v/'
    ]
    return any(pattern in url.lower() for pattern in youtube_patterns)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID if found, None otherwise
    """
    import re
    
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_transcript_output_template(custom_path: Optional[str] = None, 
                                 template: Optional[str] = None,
                                 user_context: Optional[UserContext] = None,
                                 video_url: Optional[str] = None) -> str:
    """
    Get output template for transcript files.
    
    Args:
        custom_path: Custom download directory
        template: Custom filename template
        user_context: User context for multiuser support (optional)
        video_url: Video URL for user-specific path (required if user_context provided)
        
    Returns:
        Output template string
    """
    # Use multiuser path if user context and video URL provided
    if user_context and video_url:
        download_path = user_context.get_transcript_download_path(video_url)
        logger.debug(f"Using multiuser transcript path: {download_path}")
    else:
        # Get script directories
        _, base_dir = get_script_directories()
        
        # Determine download directory
        if custom_path:
            download_path = resolve_path(custom_path, base_dir)
        else:
            download_path = base_dir / "downloads" / "transcripts"
        
        logger.debug(f"Using single-user transcript path: {download_path}")
    
    ensure_directory(download_path)
    
    # Determine filename template
    if template:
        return str(download_path / template)
    else:
        return str(download_path / "transcript")


def check_transcript_file_exists(expected_path: str, file_checker: Callable) -> bool:
    """
    Check if transcript file already exists.
    
    Args:
        expected_path: Path to check
        file_checker: Function to check file existence
        
    Returns:
        True if file exists, False otherwise
    """
    exists = file_checker(expected_path)
    if exists:
        logger.info(f"Transcript file already present: {expected_path}")
        print(f"Transcript file already present: {expected_path}")
    return exists


def perform_transcript_download(video_id: str, language_code: str, 
                               output_template: str, formats: List[str],
                               video_metadata: Optional[Dict[str, Any]] = None,
                               file_checker: Callable = None) -> Dict[str, str]:
    """
    Perform the actual transcript download and processing.
    
    Args:
        video_id: YouTube video ID
        language_code: Language code for transcript
        output_template: Output template for files
        formats: List of formats to generate
        video_metadata: Video metadata for enhanced processing
        file_checker: Function to check file existence
        
    Returns:
        Dictionary with format names as keys and file paths as values
    """
    logger.info(f"Starting transcript download: video_id={video_id}, language={language_code}")
    
    if file_checker is None:
        file_checker = os.path.exists
    
    # Get transcript data
    transcript_list = get_transcript_list(video_id)
    transcript_data = None
    
    # Find the transcript for our language
    for transcript in transcript_list:
        if hasattr(transcript, 'language_code') and transcript.language_code == language_code:
            transcript_data = transcript.fetch()
            logger.debug(f"✅ Found transcript using transcript list method")
            break
    
    if not transcript_data:
        # Fallback: try direct fetch
        try:
            transcript_data = YouTubeTranscriptApi.fetch(video_id, languages=[language_code])
            logger.debug(f"✅ Found transcript using fetch fallback method")
        except Exception as fallback_error:
            logger.warning(f"Fallback method also failed: {fallback_error}")
            raise Exception(f"No transcript found for language: {language_code}")
    
    if not transcript_data:
        raise Exception(f"No transcript data found for language: {language_code}")
    
    # Process transcript with enhanced processor
    try:
        from path_utils.path_utils import load_config
        config = load_config()
    except Exception as e:
        logger.warning(f"Could not load config for transcript processing: {e}")
        config = {}
    
    processed_results = process_transcript_data(transcript_data, video_metadata, formats, config)
    
    # Save files and collect paths
    saved_files = {}
    
    for format_name, content in processed_results.items():
        # Determine filename
        base_name = output_template
        if base_name.endswith('.txt') or base_name.endswith('.json'):
            base_name = base_name.rsplit('.', 1)[0]  # Remove extension
        
        if format_name == 'structured':
            filename = f"{base_name}_structured.json"
        elif format_name == 'clean':
            filename = f"{base_name}_clean.txt"
        else:  # timestamped
            filename = f"{base_name}_timestamped.txt"
        
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        if format_name == 'structured':
            import json
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2, ensure_ascii=False, default=str)
        else:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
        
        saved_files[format_name] = filename
        logger.debug(f"✅ Saved {format_name} format to: {filename}")
    
    logger.info(f"✅ Transcript download successful: {len(saved_files)} formats saved")
    return saved_files


def download_transcript(url: str, 
                       language_code: Optional[str] = None,
                       output_template: Optional[str] = None,
                       custom_download_path: Optional[str] = None,
                       formats: Optional[List[str]] = None,
                       include_metadata: bool = True,
                       progress_callback: Optional[Callable] = None,
                       file_checker: Callable = None,
                       user_context: Optional[UserContext] = None) -> Dict[str, str]:
    """
    Download transcript from YouTube URL with multiple format support.
    
    This is the main function for transcript downloads with comprehensive features:
    - Multiple output formats (clean, timestamped, structured)
    - Rich metadata collection and analysis
    - Chapter detection and content analysis
    - Multiple export formats (JSON, CSV, Markdown)
    
    Args:
        url: YouTube URL to download transcript from
        language_code: Language code for transcript (auto-detects if None)
        output_template: Output template for filename (uses default if None)
        custom_download_path: Custom download directory (uses default if None)
        formats: List of formats to generate ('clean', 'timestamped', 'structured')
        include_metadata: Whether to include rich metadata analysis
        progress_callback: Optional progress callback function
        file_checker: Function to check if file exists (defaults to os.path.exists)
        user_context: User context for multiuser support (optional)
        
    Returns:
        Dictionary with format names as keys and file paths as values
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If download fails
    """
    logger.info(f"Starting transcript download for URL: {url}")
    
    # Validate URL
    if not validate_transcript_url(url):
        error_msg = f"Invalid YouTube URL: {url}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        error_msg = f"Could not extract video ID from URL: {url}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"Extracted video ID: {video_id}")
    
    # Set up dependencies
    if file_checker is None:
        file_checker = os.path.exists
    
    # Get output template
    if output_template is None:
        output_template = get_transcript_output_template(
            custom_download_path, 
            user_context=user_context, 
            video_url=url
        )
        logger.debug(f"Using output template: {output_template}")
    
    # Set default formats
    if formats is None:
        formats = ['clean', 'timestamped', 'structured']
    
    # Auto-detect language if not provided
    if language_code is None:
        logger.info("Auto-detecting transcript language...")
        default_transcript = print_and_select_default_transcript(video_id)
        if not default_transcript:
            raise RuntimeError("No suitable transcript found for this video")
        language_code = default_transcript['language_code']
        logger.info(f"Selected language: {default_transcript['language']} ({language_code})")
    
    # Get video metadata if metadata collection is enabled
    video_metadata = None
    if include_metadata:
        try:
            import yt_dlp
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_metadata = ydl.extract_info(url, download=False)
                logger.debug("Extracted video metadata for enhanced processing")
        except Exception as e:
            logger.warning(f"Could not extract video metadata: {e}")
            # Continue without metadata - basic transcript is still useful
    
    # Perform download
    try:
        saved_files = perform_transcript_download(
            video_id, language_code, output_template, formats, 
            video_metadata, file_checker
        )
        
        # Export metadata if enabled and available
        if include_metadata and 'structured' in saved_files:
            try:
                # Load the structured file to get comprehensive metadata
                import json
                with open(saved_files['structured'], 'r', encoding='utf-8') as f:
                    structured_data = json.load(f)
                
                if 'comprehensive_metadata' in structured_data:
                    # Export metadata in multiple formats
                    base_name = output_template.rsplit('.', 1)[0] if '.' in output_template else output_template
                    
                    # Export JSON metadata
                    metadata_file = f"{base_name}_metadata.json"
                    export_metadata(structured_data['comprehensive_metadata'], 'json', metadata_file)
                    
                    # Export CSV metadata
                    csv_file = f"{base_name}_metadata.csv"
                    export_metadata(structured_data['comprehensive_metadata'], 'csv', csv_file)
                    
                    # Export Markdown report
                    md_file = f"{base_name}_report.md"
                    export_metadata(structured_data['comprehensive_metadata'], 'markdown', md_file)
                    
                    logger.info(f"✅ Metadata exported in multiple formats")
                    
            except Exception as e:
                logger.warning(f"Could not export metadata: {e}")
                # Continue - transcript files are still available
        
        return saved_files
        
    except Exception as e:
        error_msg = f"Transcript download failed: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def get_transcript_metadata(url: str) -> Dict[str, Any]:
    """
    Extract transcript metadata from YouTube URL without downloading.
    
    Args:
        url: YouTube URL to extract metadata from
        
    Returns:
        Dictionary containing transcript metadata
        
    Raises:
        ValueError: If URL is invalid
        RuntimeError: If metadata extraction fails
    """
    logger.info(f"Extracting transcript metadata for URL: {url}")
    
    # Validate URL
    if not validate_transcript_url(url):
        error_msg = f"Invalid YouTube URL: {url}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        error_msg = f"Could not extract video ID from URL: {url}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Get transcript metadata
        transcript_metadata = list_transcript_metadata(video_id)
        
        # Get basic video metadata
        try:
            import yt_dlp
            ydl_opts = {'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_info = ydl.extract_info(url, download=False)
                basic_metadata = {
                    'video_id': video_info.get('id') or video_info.get('display_id'),
                    'title': video_info.get('title'),
                    'duration': video_info.get('duration'),
                    'uploader': video_info.get('uploader') or video_info.get('uploader_id'),
                    'channel': video_info.get('channel'),
                    'description': video_info.get('description', '')[:200] + '...' if video_info.get('description') else '',
                    'view_count': video_info.get('view_count'),
                    'upload_date': video_info.get('upload_date')
                }
        except Exception as e:
            logger.warning(f"Could not extract video metadata: {e}")
            basic_metadata = {'video_id': video_id}
        
        metadata = {
            'video_metadata': basic_metadata,
            'transcript_metadata': transcript_metadata,
            'total_transcripts': len(transcript_metadata),
            'available_languages': [t['language_code'] for t in transcript_metadata if t['language_code']],
            'manual_transcripts': [t for t in transcript_metadata if not t['is_generated']],
            'auto_generated_transcripts': [t for t in transcript_metadata if t['is_generated']]
        }
        
        logger.debug(f"Extracted transcript metadata: {len(transcript_metadata)} transcripts found")
        return metadata
        
    except Exception as e:
        error_msg = f"Failed to extract transcript metadata: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def preview_transcript(url: str, language_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Generate a preview of transcript content without downloading.
    
    Args:
        url: YouTube URL
        language_code: Specific language code, or None to use default selection
        
    Returns:
        Dictionary with preview information, or None if not available
    """
    logger.info(f"Generating transcript preview for URL: {url}")
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        logger.error(f"Could not extract video ID from URL: {url}")
        return None
    
    try:
        from .get_transcript_list import preview_transcript as _preview_transcript
        return _preview_transcript(video_id, language_code, include_metadata=True)
    except Exception as e:
        logger.error(f"Failed to generate transcript preview: {e}")
        return None
