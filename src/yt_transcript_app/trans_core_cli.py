"""
CLI interface for YouTube Transcript Downloader.

This module provides a comprehensive command-line interface for downloading
YouTube transcripts with multiple format support, metadata collection, and
content analysis features.
"""

import argparse
import sys
import logging
import os
from typing import Optional, Callable, List, Dict

# Import core transcript functionality
from .trans_core import (
    download_transcript,
    get_transcript_metadata,
    preview_transcript,
    default_transcript_progress_hook
)

# Import transcript utilities
from .get_transcript_list import print_and_select_default_transcript, print_transcript_preview

# Initialize logger for this module
logger = logging.getLogger("trans_cli")


def parse_transcript_args() -> argparse.Namespace:
    """
    Parse command line arguments for the transcript downloader.
    
    Returns:
        Parsed arguments namespace
    """
    logger.debug("Parsing command line arguments for transcript downloader")
    
    parser = argparse.ArgumentParser(
        description='Download YouTube transcripts with multiple format support and rich metadata analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m yt_transcript_app "https://www.youtube.com/watch?v=VIDEO_ID"
  python -m yt_transcript_app "https://youtu.be/VIDEO_ID" --output-dir ./transcripts
  python -m yt_transcript_app "URL" --formats clean timestamped structured
  python -m yt_transcript_app "URL" --language en --metadata
  python -m yt_transcript_app "URL" --preview
  python -m yt_transcript_app "URL" --list-languages
        """
    )
    
    parser.add_argument(
        'url', 
        nargs='?',
        help='YouTube video URL to download transcript from'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory for downloaded files (default: ./downloads/transcripts)'
    )
    
    parser.add_argument(
        '--template', '-t',
        help='Output filename template (default: transcript)'
    )
    
    parser.add_argument(
        '--language', '-l',
        help='Language code for transcript (e.g., en, es, fr). Auto-detects if not specified.'
    )
    
    parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['clean', 'timestamped', 'structured'],
        default=['clean', 'timestamped', 'structured'],
        help='Output formats to generate (default: all formats)'
    )
    
    parser.add_argument(
        '--metadata', '-m',
        action='store_true',
        help='Show transcript metadata without downloading'
    )
    
    parser.add_argument(
        '--preview', '-p',
        action='store_true',
        help='Preview transcript content without downloading'
    )
    
    parser.add_argument(
        '--list-languages', '--list',
        action='store_true',
        help='List available transcript languages for the video'
    )
    
    parser.add_argument(
        '--no-metadata-analysis',
        action='store_true',
        help='Disable rich metadata collection and analysis'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Check if URL is provided (unless showing help or listing languages)
    if args.url is None and not args.list_languages:
        parser.error("URL is required. Use --help for usage information.")
    
    logger.info(f"Parsed arguments: URL={args.url}, output_dir={args.output_dir}, "
               f"template={args.template}, language={args.language}, formats={args.formats}, "
               f"metadata={args.metadata}, preview={args.preview}, list_languages={args.list_languages}")
    return args


class TranscriptCLIController:
    """
    Controller class for transcript CLI operations with dependency injection for testing.
    """
    
    def __init__(self, 
                 transcript_downloader: Optional[Callable] = None,
                 metadata_extractor: Optional[Callable] = None,
                 preview_generator: Optional[Callable] = None,
                 progress_hook: Optional[Callable] = None):
        """
        Initialize transcript CLI controller with optional dependencies for testing.
        
        Args:
            transcript_downloader: Function to download transcripts (defaults to download_transcript)
            metadata_extractor: Function to extract metadata (defaults to get_transcript_metadata)
            preview_generator: Function to generate preview (defaults to preview_transcript)
            progress_hook: Progress callback function (defaults to default_transcript_progress_hook)
        """
        self.transcript_downloader = transcript_downloader or download_transcript
        self.metadata_extractor = metadata_extractor or get_transcript_metadata
        self.preview_generator = preview_generator or preview_transcript
        self.progress_hook = progress_hook or default_transcript_progress_hook
    
    def handle_metadata_request(self, url: str) -> None:
        """
        Handle metadata display request.
        
        Args:
            url: YouTube URL to extract metadata from
        """
        logger.info("Handling transcript metadata request")
        try:
            metadata = self.metadata_extractor(url)
            
            print("\n" + "="*80)
            print("TRANSCRIPT METADATA")
            print("="*80)
            
            # Video information
            video_meta = metadata.get('video_metadata', {})
            print(f"Title: {video_meta.get('title', 'N/A')}")
            print(f"Uploader: {video_meta.get('uploader', 'N/A')}")
            print(f"Channel: {video_meta.get('channel', 'N/A')}")
            print(f"Duration: {video_meta.get('duration', 'N/A')} seconds")
            print(f"Views: {video_meta.get('view_count', 'N/A'):,}" if video_meta.get('view_count') else "Views: N/A")
            print(f"Upload Date: {video_meta.get('upload_date', 'N/A')}")
            print()
            
            # Transcript information
            transcript_meta = metadata.get('transcript_metadata', [])
            print(f"Total Transcripts Available: {metadata.get('total_transcripts', 0)}")
            print(f"Available Languages: {', '.join(metadata.get('available_languages', []))}")
            print()
            
            if transcript_meta:
                print("Transcript Details:")
                print("-" * 60)
                print(f"{'Language':<8} | {'Name':<24} | {'Generated':<10} | {'Translatable':<12}")
                print("-" * 60)
                
                for t in transcript_meta:
                    generated = "Yes" if t.get('is_generated') else "No"
                    translatable = "Yes" if t.get('is_translatable') else "No"
                    print(f"{t.get('language_code', '-'):<8} | "
                          f"{t.get('language', '-'):<24} | "
                          f"{generated:<10} | "
                          f"{translatable:<12}")
                
                # Show manual vs auto-generated counts
                manual_count = len(metadata.get('manual_transcripts', []))
                auto_count = len(metadata.get('auto_generated_transcripts', []))
                print(f"\nManual Transcripts: {manual_count}")
                print(f"Auto-generated Transcripts: {auto_count}")
            
            print("="*80)
            
        except Exception as e:
            logger.error(f"Failed to extract transcript metadata: {e}")
            print(f"Error extracting transcript metadata: {e}")
            raise
    
    def handle_preview_request(self, url: str, language_code: Optional[str] = None) -> None:
        """
        Handle transcript preview request.
        
        Args:
            url: YouTube URL to preview transcript from
            language_code: Specific language code for preview
        """
        logger.info("Handling transcript preview request")
        try:
            preview_data = self.preview_generator(url, language_code)
            
            if not preview_data:
                print("❌ No transcript preview available")
                return
            
            # Use the enhanced preview display from get_transcript_list
            from .get_transcript_list import print_transcript_preview
            video_id = preview_data.get('video_id', 'unknown')
            print_transcript_preview(video_id, language_code)
            
        except Exception as e:
            logger.error(f"Failed to generate transcript preview: {e}")
            print(f"Error generating transcript preview: {e}")
            raise
    
    def handle_list_languages_request(self, url: str) -> None:
        """
        Handle list languages request.
        
        Args:
            url: YouTube URL to list languages for
        """
        logger.info("Handling list languages request")
        try:
            from .trans_core import extract_video_id
            video_id = extract_video_id(url)
            if not video_id:
                print("❌ Could not extract video ID from URL")
                return
            
            # Use the existing function to display transcript info
            print_and_select_default_transcript(video_id)
            
        except Exception as e:
            logger.error(f"Failed to list transcript languages: {e}")
            print(f"Error listing transcript languages: {e}")
            raise
    
    def handle_transcript_download(self, url: str, language_code: Optional[str], 
                                 output_dir: Optional[str], template: Optional[str],
                                 formats: List[str], include_metadata: bool, 
                                 quiet: bool) -> Dict[str, str]:
        """
        Handle transcript download workflow.
        
        Args:
            url: YouTube URL to download
            language_code: Language code for transcript
            output_dir: Custom output directory
            template: Custom filename template
            formats: List of formats to generate
            include_metadata: Whether to include metadata analysis
            quiet: Whether to suppress progress output
            
        Returns:
            Dictionary with format names as keys and file paths as values
        """
        logger.info("Handling transcript download request")
        
        # Determine output template
        if template:
            # If custom template provided, combine with output directory
            if output_dir:
                from path_utils.path_utils import resolve_path, ensure_directory, get_script_directories
                _, base_dir = get_script_directories()
                download_path = resolve_path(output_dir, base_dir)
                ensure_directory(download_path)
                output_template = str(download_path / template)
            else:
                # Use default transcript directory with custom template
                from .trans_core import get_transcript_output_template
                output_template = get_transcript_output_template(template=template)
        else:
            # Use default template with custom or default directory
            from .trans_core import get_transcript_output_template
            output_template = get_transcript_output_template(custom_path=output_dir)
        
        logger.debug(f"Using output template: {output_template}")
        
        # Set up progress callback
        progress_callback = None if quiet else self.progress_hook
        
        # Perform download
        saved_files = self.transcript_downloader(
            url,
            language_code=language_code,
            output_template=output_template,
            custom_download_path=output_dir,
            formats=formats,
            include_metadata=include_metadata,
            progress_callback=progress_callback
        )
        
        logger.info(f"Transcript download completed: {len(saved_files)} files saved")
        return saved_files
    
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
        Run the transcript CLI workflow with the given arguments.
        
        Args:
            args: Parsed command line arguments
        """
        logger.info("Starting transcript CLI workflow")
        
        try:
            if args.list_languages:
                self.handle_list_languages_request(args.url)
            elif args.metadata:
                self.handle_metadata_request(args.url)
            elif args.preview:
                self.handle_preview_request(args.url, args.language)
            else:
                saved_files = self.handle_transcript_download(
                    args.url,
                    args.language,
                    args.output_dir,
                    args.template,
                    args.formats,
                    not args.no_metadata_analysis,
                    args.quiet
                )
                
                print(f"\n✅ Transcript download completed successfully!")
                print(f"📁 Files saved:")
                for format_name, file_path in saved_files.items():
                    print(f"   • {format_name}: {file_path}")
                
                # Show additional files if metadata was included
                if not args.no_metadata_analysis and 'structured' in saved_files:
                    base_name = saved_files['structured'].replace('_structured.json', '')
                    metadata_files = [
                        f"{base_name}_metadata.json",
                        f"{base_name}_metadata.csv", 
                        f"{base_name}_report.md"
                    ]
                    
                    existing_metadata = [f for f in metadata_files if os.path.exists(f)]
                    if existing_metadata:
                        print(f"\n📊 Metadata files:")
                        for file_path in existing_metadata:
                            print(f"   • {file_path}")
                
        except Exception as e:
            self.handle_download_error(e)
            raise


def main():
    """
    Main CLI entry point for transcript downloader.
    
    This function handles the CLI workflow and error handling,
    delegating the actual download logic to the core functions.
    """
    logger.info("Starting transcript CLI main function")
    args = parse_transcript_args()
    
    controller = TranscriptCLIController()
    controller.run(args)


# --- Standalone CLI Support ----------------------------------------------------

if __name__ == '__main__':
    # Allow this module to be run as a standalone CLI script
    main()
