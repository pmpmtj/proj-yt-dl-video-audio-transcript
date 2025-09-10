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
    default_video_progress_hook,
    get_video_metadata,
    get_video_languages,
    get_video_formats
)

# Import feature flag functions
from ..common.app_config import (
    get_feature_flags,
    is_database_source_enabled,
    is_file_check_enabled,
    is_metadata_caching_enabled,
    is_download_history_enabled
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
    
    # Create main parser with subcommands
    parser = argparse.ArgumentParser(
        description='YouTube video downloader with configurable quality and format options.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download video
  python -m src.yt_video_app download "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m src.yt_video_app download "URL" --quality 1080p --ext mp4
  
  # Get video information
  python -m src.yt_video_app info "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m src.yt_video_app languages "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m src.yt_video_app formats "https://www.youtube.com/watch?v=VIDEO_ID"
        """
    )
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Download subcommand
    download_parser = subparsers.add_parser('download', help='Download video with audio')
    download_parser.add_argument('url', help='YouTube video URL to download')
    download_parser.add_argument('--output-template', default=video_settings['output_template'], 
                               help=f'yt-dlp output template (default: {video_settings["output_template"].replace("%", "%%")})')
    download_parser.add_argument('--restrict-filenames', action='store_true', 
                               default=video_settings['restrict_filenames'],
                               help='Safer ASCII-only filenames.')
    download_parser.add_argument('--ext', choices=['mp4','webm'], default=video_settings['ext'], 
                               help=f'Preferred output container (default: {video_settings["ext"]}).')
    download_parser.add_argument('--quality', choices=['best','2160p','1440p','1080p','720p','480p','360p','144p'], 
                               default=video_settings['quality'], 
                               help=f'Target video quality (cap). Default: {video_settings["quality"]}.')
    download_parser.add_argument('--audio-lang', type=str, default='original',
                               help='Audio language code (use "languages" command to see available options). Default: original.')
    download_parser.add_argument('--subtitle-lang', type=str, default=None,
                               help='Subtitle language code to embed (use "languages" command to see available options). Default: none.')
    download_parser.add_argument('--force', action='store_true',
                               help='Force download even if file already exists. Skips file existence check.')
    
    # Info subcommand
    info_parser = subparsers.add_parser('info', help='Get video metadata information')
    info_parser.add_argument('url', help='YouTube video URL to get information from')
    
    # Languages subcommand
    languages_parser = subparsers.add_parser('languages', help='Get available audio and subtitle languages')
    languages_parser.add_argument('url', help='YouTube video URL to get language information from')
    
    # Formats subcommand
    formats_parser = subparsers.add_parser('formats', help='Get available video formats and qualities')
    formats_parser.add_argument('url', help='YouTube video URL to get format information from')
    
    # Config subcommand
    config_parser = subparsers.add_parser('config', help='Show current configuration and feature flags')
    config_parser.add_argument('--feature-flags', action='store_true', 
                              help='Show only feature flags status')
    
    # For backward compatibility, if no subcommand is provided, treat as download
    args = parser.parse_args()
    
    # Handle backward compatibility - if no command specified, assume download
    if args.command is None:
        # Re-parse with download as default command
        import sys
        if len(sys.argv) > 1 and not sys.argv[1] in ['download', 'info', 'languages', 'formats']:
            # Insert 'download' as the first argument
            sys.argv.insert(1, 'download')
            args = parser.parse_args()
    
    logger.info(f"Parsed arguments: command={args.command}, URL={getattr(args, 'url', 'N/A')}")
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
                            audio_lang: str, subtitle_lang: Optional[str],
                            force: bool, config: Optional[Dict[str, Any]]) -> Optional[str]:
        """Handle video download workflow.
        
        Args:
            url: Video URL to download
            output_template: Output template for filename
            restrict_filenames: Whether to restrict filenames to ASCII
            ext: Container extension
            quality: Quality setting
            audio_lang: Audio language code
            subtitle_lang: Subtitle language code (optional)
            force: Whether to force download even if file exists
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
            audio_lang,
            subtitle_lang,
            force,
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
    
    def handle_info_command(self, url: str) -> None:
        """Handle the info command to display video metadata.
        
        Args:
            url: Video URL to get information from
        """
        logger.info(f"Getting video metadata for: {url}")
        try:
            metadata = get_video_metadata(url)
            print("\n=== Video Information ===")
            print(f"Title: {metadata.get('title', 'Unknown')}")
            print(f"Video ID: {metadata.get('video_id', 'Unknown')}")
            print(f"Duration: {metadata.get('duration', 'Unknown')} seconds")
            print(f"Uploader: {metadata.get('uploader', 'Unknown')}")
            print(f"Channel: {metadata.get('channel', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to get video metadata: {e}")
            print(f"Error getting video metadata: {e}")
            raise
    
    def handle_languages_command(self, url: str) -> None:
        """Handle the languages command to display available languages.
        
        Args:
            url: Video URL to get language information from
        """
        logger.info(f"Getting video languages for: {url}")
        try:
            languages = get_video_languages(url)
            
            print("\n=== Available Audio Languages ===")
            for lang in languages['audio_languages']:
                print(f"  {lang['code']}: {lang['label']}")
            
            print("\n=== Available Subtitle Languages ===")
            for lang in languages['subtitle_languages']:
                print(f"  {lang['code']}: {lang['label']}")
                
        except Exception as e:
            logger.error(f"Failed to get video languages: {e}")
            print(f"Error getting video languages: {e}")
            raise
    
    def handle_formats_command(self, url: str) -> None:
        """Handle the formats command to display available formats.
        
        Args:
            url: Video URL to get format information from
        """
        logger.info(f"Getting video formats for: {url}")
        try:
            formats = get_video_formats(url)
            
            print("\n=== Available Container Formats ===")
            for container in formats['containers']:
                print(f"  {container.upper()}")
            
            print("\n=== Available Video Qualities ===")
            for quality in formats['qualities']:
                print(f"  {quality}p")
                
        except Exception as e:
            logger.error(f"Failed to get video formats: {e}")
            print(f"Error getting video formats: {e}")
            raise
    
    def handle_config_command(self, show_feature_flags_only: bool = False) -> None:
        """Handle the config command to display configuration and feature flags.
        
        Args:
            show_feature_flags_only: Whether to show only feature flags
        """
        logger.info("Displaying configuration")
        try:
            if show_feature_flags_only:
                print("\n=== Feature Flags Status ===")
                flags = get_feature_flags()
                for flag, value in flags.items():
                    status = "✅ ENABLED" if value else "❌ DISABLED"
                    print(f"  {flag}: {status}")
            else:
                print("\n=== Application Configuration ===")
                
                # Show feature flags
                print("\n--- Feature Flags ---")
                flags = get_feature_flags()
                for flag, value in flags.items():
                    status = "✅ ENABLED" if value else "❌ DISABLED"
                    print(f"  {flag}: {status}")
                
                # Show current behavior
                print("\n--- Current Behavior ---")
                if is_database_source_enabled():
                    print("  📊 Database is the single source of truth")
                    print("  🔄 File existence check: SKIPPED (always force download)")
                elif not is_file_check_enabled():
                    print("  📁 File system is the source of truth")
                    print("  🔄 File existence check: DISABLED (always force download)")
                else:
                    print("  📁 File system is the source of truth")
                    print("  🔄 File existence check: ENABLED (normal behavior)")
                
        except Exception as e:
            logger.error(f"Failed to get configuration: {e}")
            print(f"Error getting configuration: {e}")
            raise

    def run(self, args: argparse.Namespace) -> None:
        """Run the CLI workflow with the given arguments.
        
        Args:
            args: Parsed command line arguments
        """
        logger.info(f"Starting CLI workflow for command: {args.command}")
        
        try:
            if args.command == 'download':
                # Load configuration for download
                config, video_settings = self.load_configuration()
                
                # Determine output template
                output_template = self.determine_output_template(
                    args.output_template, 
                    video_settings['output_template']
                )
                logger.debug(f"Using output template: {output_template or 'default'}")
                
                path = self.handle_video_download(
                    args.url, 
                    output_template, 
                    args.restrict_filenames, 
                    args.ext, 
                    args.quality,
                    args.audio_lang,
                    args.subtitle_lang,
                    args.force,
                    config
                )
                print(f"\nVideo download completed: {path or 'failed'}")
                
            elif args.command == 'info':
                self.handle_info_command(args.url)
                
            elif args.command == 'languages':
                self.handle_languages_command(args.url)
                
            elif args.command == 'formats':
                self.handle_formats_command(args.url)
                
            elif args.command == 'config':
                self.handle_config_command(args.feature_flags)
                
            else:
                print(f"Unknown command: {args.command}")
                sys.exit(1)
                
        except Exception as e:
            if args.command == 'download':
                self.handle_download_error(e)
            else:
                logger.error(f"Command failed: {e}")
                print(f"Error: {e}")
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