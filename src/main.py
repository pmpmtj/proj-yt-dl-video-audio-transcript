"""
Main entry point for YouTube Downloader Suite.

This module provides a unified interface to all three applications:
- Audio Downloader (yt_audio_app)
- Video Downloader (yt_video_app) 
- Transcript Downloader (yt_transcript_app)

All applications share centralized logging and configuration.
"""

import sys
import logging
import argparse
from pathlib import Path

# Import centralized logging setup
from .common.logging_config import setup_logging

# Initialize logger for this module
logger = logging.getLogger("main")


def setup_application_logging():
    """Set up centralized logging for the entire application."""
    logger.info("Setting up centralized logging system")
    setup_logging()
    logger.info("Logging system initialized successfully")


def create_main_parser():
    """Create the main argument parser for the application suite."""
    parser = argparse.ArgumentParser(
        description='YouTube Downloader Suite - Audio, Video, and Transcript Downloader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Applications:
  audio      Download YouTube audio as MP3 files
  video      Download YouTube videos with configurable quality
  transcript Download YouTube transcripts with multiple formats

Examples:
  python -m src audio "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m src video download "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m src transcript "https://www.youtube.com/watch?v=VIDEO_ID"
        """
    )
    
    # Add subcommands for each app
    subparsers = parser.add_subparsers(dest='app', help='Available applications')
    
    # Audio app subcommand
    audio_parser = subparsers.add_parser('audio', help='Audio downloader')
    audio_parser.add_argument('url', nargs='?', help='YouTube video URL')
    audio_parser.add_argument('--output-dir', '-o', help='Output directory')
    audio_parser.add_argument('--template', '-t', help='Output filename template')
    audio_parser.add_argument('--metadata', '-m', action='store_true', help='Show metadata only')
    audio_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output')
    audio_parser.add_argument('--session-id', help='Session ID for multiuser support')
    
    # Video app subcommand
    video_parser = subparsers.add_parser('video', help='Video downloader')
    video_subparsers = video_parser.add_subparsers(dest='command', help='Video commands')
    
    # Video download subcommand
    video_download = video_subparsers.add_parser('download', help='Download video')
    video_download.add_argument('url', help='YouTube video URL')
    video_download.add_argument('--quality', help='Video quality (e.g., 1080p, 720p)')
    video_download.add_argument('--ext', choices=['mp4', 'webm'], help='Container format')
    video_download.add_argument('--audio-lang', help='Audio language code')
    video_download.add_argument('--subtitle-lang', help='Subtitle language code')
    video_download.add_argument('--force', action='store_true', help='Force download')
    video_download.add_argument('--session-id', help='Session ID for multiuser support')
    
    # Video info subcommand
    video_info = video_subparsers.add_parser('info', help='Get video information')
    video_info.add_argument('url', help='YouTube video URL')
    
    # Video languages subcommand
    video_langs = video_subparsers.add_parser('languages', help='Get available languages')
    video_langs.add_argument('url', help='YouTube video URL')
    
    # Video formats subcommand
    video_formats = video_subparsers.add_parser('formats', help='Get available formats')
    video_formats.add_argument('url', help='YouTube video URL')
    
    # Transcript app subcommand
    transcript_parser = subparsers.add_parser('transcript', help='Transcript downloader')
    transcript_parser.add_argument('url', nargs='?', help='YouTube video URL')
    transcript_parser.add_argument('--output-dir', '-o', help='Output directory')
    transcript_parser.add_argument('--template', '-t', help='Output filename template')
    transcript_parser.add_argument('--language', '-l', help='Language code')
    transcript_parser.add_argument('--formats', '-f', nargs='+', 
                                 choices=['clean', 'timestamped', 'structured'],
                                 help='Output formats')
    transcript_parser.add_argument('--metadata', '-m', action='store_true', help='Show metadata only')
    transcript_parser.add_argument('--preview', '-p', action='store_true', help='Preview transcript')
    transcript_parser.add_argument('--list-languages', '--list', action='store_true', 
                                 help='List available languages')
    transcript_parser.add_argument('--no-metadata-analysis', action='store_true',
                                 help='Disable metadata analysis')
    transcript_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output')
    transcript_parser.add_argument('--session-id', help='Session ID for multiuser support')
    
    return parser


def route_to_audio_app(args):
    """Route arguments to the audio application."""
    logger.info("Routing to audio application")
    
    # Import and run audio CLI
    from .yt_audio_app.audio_cli import main as audio_main
    
    # Reconstruct sys.argv for audio app
    audio_args = ['audio']
    if args.url:
        audio_args.append(args.url)
    if args.output_dir:
        audio_args.extend(['--output-dir', args.output_dir])
    if args.template:
        audio_args.extend(['--template', args.template])
    if args.metadata:
        audio_args.append('--metadata')
    if args.quiet:
        audio_args.append('--quiet')
    if args.session_id:
        audio_args.extend(['--session-id', args.session_id])
    
    # Temporarily modify sys.argv
    original_argv = sys.argv.copy()
    sys.argv = audio_args
    
    try:
        audio_main()
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def route_to_video_app(args):
    """Route arguments to the video application."""
    logger.info(f"Routing to video application: {args.command}")
    
    # Import and run video CLI
    from .yt_video_app.video_cli import main as video_main
    
    # Reconstruct sys.argv for video app
    video_args = ['video', args.command]
    if hasattr(args, 'url') and args.url:
        video_args.append(args.url)
    if hasattr(args, 'quality') and args.quality:
        video_args.extend(['--quality', args.quality])
    if hasattr(args, 'ext') and args.ext:
        video_args.extend(['--ext', args.ext])
    if hasattr(args, 'audio_lang') and args.audio_lang:
        video_args.extend(['--audio-lang', args.audio_lang])
    if hasattr(args, 'subtitle_lang') and args.subtitle_lang:
        video_args.extend(['--subtitle-lang', args.subtitle_lang])
    if hasattr(args, 'force') and args.force:
        video_args.append('--force')
    if hasattr(args, 'session_id') and args.session_id:
        video_args.extend(['--session-id', args.session_id])
    
    # Temporarily modify sys.argv
    original_argv = sys.argv.copy()
    sys.argv = video_args
    
    try:
        video_main()
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def route_to_transcript_app(args):
    """Route arguments to the transcript application."""
    logger.info("Routing to transcript application")
    
    # Import and run transcript CLI
    from .yt_transcript_app.trans_core_cli import main as transcript_main
    
    # Reconstruct sys.argv for transcript app
    transcript_args = ['transcript']
    if args.url:
        transcript_args.append(args.url)
    if args.output_dir:
        transcript_args.extend(['--output-dir', args.output_dir])
    if args.template:
        transcript_args.extend(['--template', args.template])
    if args.language:
        transcript_args.extend(['--language', args.language])
    if args.formats:
        transcript_args.extend(['--formats'] + args.formats)
    if args.metadata:
        transcript_args.append('--metadata')
    if args.preview:
        transcript_args.append('--preview')
    if args.list_languages:
        transcript_args.append('--list-languages')
    if args.no_metadata_analysis:
        transcript_args.append('--no-metadata-analysis')
    if args.quiet:
        transcript_args.append('--quiet')
    if args.session_id:
        transcript_args.extend(['--session-id', args.session_id])
    
    # Temporarily modify sys.argv
    original_argv = sys.argv.copy()
    sys.argv = transcript_args
    
    try:
        transcript_main()
    finally:
        # Restore original sys.argv
        sys.argv = original_argv


def main():
    """Main entry point for the YouTube Downloader Suite."""
    logger.info("Starting YouTube Downloader Suite")
    
    # Set up logging first
    setup_application_logging()
    
    # Parse command line arguments
    parser = create_main_parser()
    args = parser.parse_args()
    
    # Check if no arguments provided
    if not args.app:
        parser.print_help()
        logger.warning("No application specified")
        return 1
    
    try:
        # Route to appropriate application
        if args.app == 'audio':
            route_to_audio_app(args)
        elif args.app == 'video':
            route_to_video_app(args)
        elif args.app == 'transcript':
            route_to_transcript_app(args)
        else:
            logger.error(f"Unknown application: {args.app}")
            parser.print_help()
            return 1
        
        logger.info("Application completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Application failed with error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
