# my_project/src/yt_video_app/video_cli.py
"""
CLI interface for YouTube video downloader.

This module contains CLI-specific functionality including argument parsing
and the CLI controller. It imports and uses the core video business logic.
"""

import argparse
import sys
import logging
from typing import Optional, Dict, Any, Callable
import yt_dlp

# Import core video business logic functions
from .video_core import (
    download_video_with_audio,
    default_video_progress_hook
)

# Import configuration utilities
from path_utils import load_config
from .video_helpers import get_default_video_settings

# Initialize logger for this module
logger = logging.getLogger("video_cli")


# --- CLI Functions -------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the YouTube video downloader CLI with config defaults.
    
    Returns:
        Parsed arguments namespace
    """
    logger.debug("Parsing command line arguments for video downloader")
    
    # Load config for defaults
    try:
        config = load_config()
        video_settings = get_default_video_settings(config)
        logger.debug("Loaded configuration successfully")
    except (FileNotFoundError, ValueError, KeyError) as e:
        logger.warning(f"Failed to load config: {e}, using fallback settings")
        # Fallback if config not available
        video_settings = {
            'ext': 'mp4',
            'quality': 'best',
            'output_template': '%(title)s.%(ext)s',
            'restrict_filenames': False
        }
    
    p = argparse.ArgumentParser(
        description='YouTube video downloader with configurable quality and format options.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.yt_video_app "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m src.yt_video_app "URL" --quality 1080p --ext mp4
  python -m src.yt_video_app "URL" --output-template "%(uploader)s - %(title)s.%(ext)s"
  python -m src.yt_video_app "URL" --ext webm --quality 720p
        """
    )
    p.add_argument('url', help='YouTube video URL to download')
    p.add_argument('--output-template', default=video_settings['output_template'], 
                   help=f'yt-dlp output template (default: {video_settings["output_template"].replace("%", "%%")})')
    p.add_argument('--restrict-filenames', action='store_true', 
                   default=video_settings['restrict_filenames'],
                   help='Safer ASCII-only filenames.')
    p.add_argument('--ext', choices=['mp4','webm'], default=video_settings['ext'], 
                   help=f'Preferred output container (default: {video_settings["ext"]}).')
    p.add_argument('--quality', choices=['best','2160p','1440p','1080p','720p','480p','360p','144p'], 
                   default=video_settings['quality'], 
                   help=f'Target video quality (cap). Default: {video_settings["quality"]}.')
    
    args = p.parse_args()
    logger.info(f"Parsed arguments: URL={args.url}, ext={args.ext}, quality={args.quality}")
    return args


class VideoCLIController:
    """Controller class for video CLI operations with dependency injection for testing."""
    
    def __init__(self, 
                 config_loader: Optional[Callable] = None,
                 video_settings_loader: Optional[Callable] = None,
                 video_downloader: Optional[Callable] = None,
                 progress_hook: Optional[Callable] = None):
        """Initialize video CLI controller with optional dependencies for testing.
        
        Args:
            config_loader: Function to load configuration (defaults to load_config)
            video_settings_loader: Function to load video settings (defaults to get_default_video_settings)
            video_downloader: Function to download video (defaults to download_video_with_audio)
            progress_hook: Progress callback function (defaults to default_video_progress_hook)
        """
        self.config_loader = config_loader or load_config
        self.video_settings_loader = video_settings_loader or get_default_video_settings
        self.video_downloader = video_downloader or download_video_with_audio
        self.progress_hook = progress_hook or default_video_progress_hook
    
    def load_configuration(self) -> tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
        """Load configuration and video settings.
        
        Returns:
            Tuple of (config, video_settings)
        """
        try:
            config = self.config_loader()
            video_settings = self.video_settings_loader(config)
            logger.debug("Loaded configuration successfully")
            return config, video_settings
        except (FileNotFoundError, ValueError, KeyError) as e:
            logger.warning(f"Failed to load config: {e}")
            return None, {'output_template': '%(title)s.%(ext)s'}
    
    def determine_output_template(self, args_output_template: str, 
                                config_output_template: str) -> Optional[str]:
        """Determine which output template to use.
        
        Args:
            args_output_template: Template from command line arguments
            config_output_template: Template from configuration
            
        Returns:
            Output template to use, or None for default
        """
        if args_output_template == config_output_template:
            return None
        return args_output_template
    
    
    def handle_video_download(self, url: str, output_template: Optional[str], 
                            restrict_filenames: bool, ext: str, quality: str,
                            config: Optional[Dict[str, Any]]) -> Optional[str]:
        """Handle video download workflow.
        
        Args:
            url: Video URL to download
            output_template: Output template for filename
            restrict_filenames: Whether to restrict filenames to ASCII
            ext: Container extension
            quality: Quality setting
            config: Configuration dictionary
            
        Returns:
            Path to downloaded video file, or None if failed
        """
        logger.info("Starting video download")
        path = self.video_downloader(
            url, 
            output_template, 
            restrict_filenames, 
            ext, 
            quality,
            progress_callback=self.progress_hook,
            config=config
        )
        logger.info(f"Video download completed: {path or 'failed'}")
        return path
    
    def handle_download_error(self, error: Exception) -> None:
        """Handle download errors with appropriate logging and output.
        
        Args:
            error: The exception that occurred
        """
        if isinstance(error, yt_dlp.utils.DownloadError):
            logger.error(f"Download error: {error}")
            print(f"Download error: {error}")
        else:
            logger.error(f"Unexpected error: {error}")
            print(f"Unexpected error: {error}")
    
    def run(self, args: argparse.Namespace) -> None:
        """Run the CLI workflow with the given arguments.
        
        Args:
            args: Parsed command line arguments
        """
        logger.info("Starting CLI workflow")
        
        # Load configuration
        config, video_settings = self.load_configuration()
        
        # Determine output template
        output_template = self.determine_output_template(
            args.output_template, 
            video_settings['output_template']
        )
        logger.debug(f"Using output template: {output_template or 'default'}")
        
        try:
            path = self.handle_video_download(
                args.url, 
                output_template, 
                args.restrict_filenames, 
                args.ext, 
                args.quality,
                config
            )
            print(f"\nVideo download completed: {path or 'failed'}")
        except Exception as e:
            self.handle_download_error(e)
            raise


def main():
    """Main CLI entry point for video downloader with error handling.
    
    This function handles the CLI workflow and error handling,
    delegating the actual download logic to the core functions.
    """
    logger.info("Starting video CLI main function")
    args = parse_args()
    
    controller = VideoCLIController()
    controller.run(args)


# --- Standalone CLI Support ----------------------------------------------------

if __name__ == '__main__':
    # Allow this module to be run as a standalone CLI script
    main()