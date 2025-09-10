"""
CLI interface for YouTube Audio Downloader.

This module provides a simple command-line interface for downloading
YouTube audio as MP3 files with hardcoded settings.
"""

import argparse
import sys
import logging
from typing import Optional, Callable

# Import core audio functionality
from .audio_core import (
    download_audio_mp3,
    get_audio_metadata,
    default_audio_progress_hook
)

# Import audio helpers
from .audio_helpers import get_audio_output_template

# Initialize logger for this module
logger = logging.getLogger("audio_cli")


def parse_audio_args() -> argparse.Namespace:
    """
    Parse command line arguments for the audio downloader.
    
    Returns:
        Parsed arguments namespace
    """
    logger.debug("Parsing command line arguments for audio downloader")
    
    parser = argparse.ArgumentParser(
        description='Download YouTube audio as MP3 (192kbps, hardcoded settings)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.yt_audio_app "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m src.yt_audio_app "https://youtu.be/VIDEO_ID" --output-dir ./music
  python -m src.yt_audio_app "URL" --template "%(uploader)s - %(title)s.%(ext)s"
  python -m src.yt_audio_app "URL" --metadata
        """
    )
    
    parser.add_argument(
        'url', 
        nargs='?',
        help='YouTube video URL to download audio from'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory for downloaded files (default: ./downloads/audio)'
    )
    
    parser.add_argument(
        '--template', '-t',
        help='Output filename template (default: %(title)s.%(ext)s)'
    )
    
    parser.add_argument(
        '--metadata', '-m',
        action='store_true',
        help='Show video metadata without downloading'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Check if URL is provided (unless showing help)
    if args.url is None:
        parser.error("URL is required. Use --help for usage information.")
    
    logger.info(f"Parsed arguments: URL={args.url}, output_dir={args.output_dir}, "
               f"template={args.template}, metadata={args.metadata}, quiet={args.quiet}")
    return args


class AudioCLIController:
    """
    Controller class for audio CLI operations with dependency injection for testing.
    """
    
    def __init__(self, 
                 audio_downloader: Optional[Callable] = None,
                 metadata_extractor: Optional[Callable] = None,
                 progress_hook: Optional[Callable] = None):
        """
        Initialize audio CLI controller with optional dependencies for testing.
        
        Args:
            audio_downloader: Function to download audio (defaults to download_audio_mp3)
            metadata_extractor: Function to extract metadata (defaults to get_audio_metadata)
            progress_hook: Progress callback function (defaults to default_audio_progress_hook)
        """
        self.audio_downloader = audio_downloader or download_audio_mp3
        self.metadata_extractor = metadata_extractor or get_audio_metadata
        self.progress_hook = progress_hook or default_audio_progress_hook
    
    def handle_metadata_request(self, url: str) -> None:
        """
        Handle metadata display request.
        
        Args:
            url: YouTube URL to extract metadata from
        """
        logger.info("Handling metadata request")
        try:
            metadata = self.metadata_extractor(url)
            
            print("\n" + "="*60)
            print("VIDEO METADATA")
            print("="*60)
            print(f"Title: {metadata.get('title', 'N/A')}")
            print(f"Uploader: {metadata.get('uploader', 'N/A')}")
            print(f"Channel: {metadata.get('channel', 'N/A')}")
            print(f"Duration: {metadata.get('duration', 'N/A')} seconds")
            print(f"Views: {metadata.get('view_count', 'N/A'):,}" if metadata.get('view_count') else "Views: N/A")
            print(f"Upload Date: {metadata.get('upload_date', 'N/A')}")
            print(f"Description: {metadata.get('description', 'N/A')}")
            print("="*60)
            
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            print(f"Error extracting metadata: {e}")
            raise
    
    def handle_audio_download(self, url: str, output_dir: Optional[str], 
                            template: Optional[str], quiet: bool) -> str:
        """
        Handle audio download workflow.
        
        Args:
            url: YouTube URL to download
            output_dir: Custom output directory
            template: Custom filename template
            quiet: Whether to suppress progress output
            
        Returns:
            Path to downloaded audio file
        """
        logger.info("Handling audio download request")
        
        # Determine output template
        if template:
            # If custom template provided, combine with output directory
            if output_dir:
                from pathlib import Path
                from path_utils import resolve_path, ensure_directory, get_script_directories
                _, base_dir = get_script_directories()
                download_path = resolve_path(output_dir, base_dir)
                ensure_directory(download_path)
                output_template = str(download_path / template)
            else:
                # Use default audio directory with custom template
                output_template = get_audio_output_template(template=template)
        else:
            # Use default template with custom or default directory
            output_template = get_audio_output_template(output_dir)
        
        logger.debug(f"Using output template: {output_template}")
        
        # Set up progress callback
        progress_callback = None if quiet else self.progress_hook
        
        # Perform download
        path = self.audio_downloader(
            url,
            output_template=output_template,
            progress_callback=progress_callback
        )
        
        logger.info(f"Audio download completed: {path}")
        return path
    
    def handle_download_error(self, error: Exception) -> None:
        """
        Handle download errors with appropriate logging and output.
        
        Args:
            error: The exception that occurred
        """
        if hasattr(error, '__class__') and 'DownloadError' in str(error.__class__):
            logger.error(f"Download error: {error}")
            print(f"Download error: {error}")
        else:
            logger.error(f"Unexpected error: {error}")
            print(f"Unexpected error: {error}")
    
    def run(self, args: argparse.Namespace) -> None:
        """
        Run the audio CLI workflow with the given arguments.
        
        Args:
            args: Parsed command line arguments
        """
        logger.info("Starting audio CLI workflow")
        
        try:
            if args.metadata:
                self.handle_metadata_request(args.url)
            else:
                path = self.handle_audio_download(
                    args.url,
                    args.output_dir,
                    args.template,
                    args.quiet
                )
                print(f"\nAudio download completed: {path}")
                
        except Exception as e:
            self.handle_download_error(e)
            raise


def main():
    """
    Main CLI entry point for audio downloader.
    
    This function handles the CLI workflow and error handling,
    delegating the actual download logic to the core functions.
    """
    logger.info("Starting audio CLI main function")
    args = parse_audio_args()
    
    controller = AudioCLIController()
    controller.run(args)


# --- Standalone CLI Support ----------------------------------------------------

if __name__ == '__main__':
    # Allow this module to be run as a standalone CLI script
    main()
