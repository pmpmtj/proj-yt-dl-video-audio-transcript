"""
Refactored CLI interface with dependency injection.

This demonstrates how dependency injection improves CLI testing and maintainability
by separating concerns and making dependencies explicit.
"""

import argparse
import sys
import logging
from typing import Optional, Callable, List, Dict, Any, Protocol
from pathlib import Path

# Setup logger
logger = logging.getLogger("refactored_trans_cli")


class TranscriptDownloader(Protocol):
    """Protocol for transcript download operations."""
    
    def download_transcript(self, url: str, language_code: str = "en", 
                          output_dir: str = "./downloads/transcripts",
                          filename_template: str = "transcript",
                          formats: List[str] = None) -> Dict[str, Any]:
        """Download transcript with specified parameters."""
        ...


class MetadataExtractor(Protocol):
    """Protocol for metadata extraction operations."""
    
    def get_transcript_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from video URL."""
        ...


class PreviewGenerator(Protocol):
    """Protocol for preview generation operations."""
    
    def preview_transcript(self, url: str, language_code: str = "en") -> Dict[str, Any]:
        """Generate transcript preview."""
        ...


class LanguageLister(Protocol):
    """Protocol for language listing operations."""
    
    def list_available_languages(self, url: str) -> List[Dict[str, Any]]:
        """List available transcript languages."""
        ...


class ProgressReporter(Protocol):
    """Protocol for progress reporting."""
    
    def report_progress(self, message: str, percentage: Optional[float] = None) -> None:
        """Report progress to user."""
        ...


class OutputHandler(Protocol):
    """Protocol for output operations."""
    
    def print_info(self, message: str) -> None:
        """Print informational message."""
        ...
    
    def print_error(self, message: str) -> None:
        """Print error message."""
        ...
    
    def print_success(self, message: str) -> None:
        """Print success message."""
        ...


class RefactoredTranscriptCLI:
    """
    Refactored CLI with dependency injection.
    
    This class demonstrates how dependency injection makes CLI testing:
    - Easy to test (no complex mocking required)
    - More flexible (easy to swap implementations)
    - More maintainable (clear separation of concerns)
    - More configurable (inject different behaviors)
    """
    
    def __init__(self,
                 transcript_downloader: TranscriptDownloader,
                 metadata_extractor: MetadataExtractor,
                 preview_generator: PreviewGenerator,
                 language_lister: LanguageLister,
                 progress_reporter: ProgressReporter,
                 output_handler: OutputHandler,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize with injected dependencies.
        
        Args:
            transcript_downloader: Handles transcript downloads
            metadata_extractor: Handles metadata extraction
            preview_generator: Handles preview generation
            language_lister: Handles language listing
            progress_reporter: Handles progress reporting
            output_handler: Handles output operations
            config: Configuration dictionary (optional)
        """
        self.downloader = transcript_downloader
        self.metadata_extractor = metadata_extractor
        self.preview_generator = preview_generator
        self.language_lister = language_lister
        self.progress_reporter = progress_reporter
        self.output_handler = output_handler
        self.config = config or {}
        
        logger.debug("RefactoredTranscriptCLI initialized with injected dependencies")
    
    def handle_metadata_request(self, url: str) -> None:
        """Handle metadata extraction request."""
        try:
            self.output_handler.print_info(f"Extracting metadata for: {url}")
            self.progress_reporter.report_progress("Extracting metadata...", 0.0)
            
            metadata = self.metadata_extractor.get_transcript_metadata(url)
            
            if metadata and metadata.get('success'):
                self.output_handler.print_success("✅ Metadata extracted successfully!")
                self._display_metadata(metadata)
            else:
                self.output_handler.print_error("❌ Failed to extract metadata")
                
        except Exception as e:
            self.output_handler.print_error(f"❌ Error extracting metadata: {str(e)}")
    
    def handle_preview_request(self, url: str, language_code: Optional[str] = None) -> None:
        """Handle transcript preview request."""
        try:
            self.output_handler.print_info(f"Generating preview for: {url}")
            self.progress_reporter.report_progress("Generating preview...", 0.0)
            
            preview = self.preview_generator.preview_transcript(url, language_code or "en")
            
            if preview and preview.get('success'):
                self.output_handler.print_success("✅ Preview generated successfully!")
                self._display_preview(preview)
            else:
                self.output_handler.print_error("❌ Failed to generate preview")
                
        except Exception as e:
            self.output_handler.print_error(f"❌ Error generating preview: {str(e)}")
    
    def handle_list_languages_request(self, url: str) -> None:
        """Handle language listing request."""
        try:
            self.output_handler.print_info(f"Listing available languages for: {url}")
            self.progress_reporter.report_progress("Fetching language list...", 0.0)
            
            languages = self.language_lister.list_available_languages(url)
            
            if languages:
                self.output_handler.print_success("✅ Available languages:")
                self._display_languages(languages)
            else:
                self.output_handler.print_error("❌ No languages found")
                
        except Exception as e:
            self.output_handler.print_error(f"❌ Error listing languages: {str(e)}")
    
    def handle_transcript_download(self, url: str, language_code: Optional[str], 
                                 output_dir: str, filename_template: str, 
                                 formats: List[str]) -> None:
        """Handle transcript download request."""
        try:
            self.output_handler.print_info(f"Downloading transcript for: {url}")
            self.progress_reporter.report_progress("Starting download...", 0.0)
            
            result = self.downloader.download_transcript(
                url=url,
                language_code=language_code or "en",
                output_dir=output_dir,
                filename_template=filename_template,
                formats=formats
            )
            
            if result.get('success'):
                self.output_handler.print_success("✅ Transcript downloaded successfully!")
                self._display_download_results(result)
            else:
                self.output_handler.print_error(f"❌ Download failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.output_handler.print_error(f"❌ Error downloading transcript: {str(e)}")
    
    def run(self, args: argparse.Namespace) -> None:
        """Run the CLI with parsed arguments."""
        try:
            # Handle different request types
            if args.metadata:
                self.handle_metadata_request(args.url)
            elif args.preview:
                self.handle_preview_request(args.url, args.language)
            elif args.list_languages:
                self.handle_list_languages_request(args.url)
            else:
                # Default: download transcript
                self.handle_transcript_download(
                    url=args.url,
                    language_code=args.language,
                    output_dir=args.output_dir,
                    filename_template=args.filename_template,
                    formats=args.formats
                )
                
        except KeyboardInterrupt:
            self.output_handler.print_info("\n⚠️ Operation cancelled by user")
            sys.exit(1)
        except Exception as e:
            self.output_handler.print_error(f"❌ Unexpected error: {str(e)}")
            sys.exit(1)
    
    def _display_metadata(self, metadata: Dict[str, Any]) -> None:
        """Display metadata in a formatted way."""
        if 'video_info' in metadata:
            video_info = metadata['video_info']
            self.output_handler.print_info(f"Title: {video_info.get('title', 'N/A')}")
            self.output_handler.print_info(f"Duration: {video_info.get('duration', 'N/A')}")
            self.output_handler.print_info(f"Uploader: {video_info.get('uploader', 'N/A')}")
    
    def _display_preview(self, preview: Dict[str, Any]) -> None:
        """Display preview in a formatted way."""
        if 'preview_text' in preview:
            self.output_handler.print_info("Preview:")
            self.output_handler.print_info(preview['preview_text'])
    
    def _display_languages(self, languages: List[Dict[str, Any]]) -> None:
        """Display available languages."""
        for lang in languages:
            name = lang.get('name', 'Unknown')
            code = lang.get('language_code', 'Unknown')
            is_default = " (default)" if lang.get('is_default') else ""
            self.output_handler.print_info(f"  {name} ({code}){is_default}")
    
    def _display_download_results(self, result: Dict[str, Any]) -> None:
        """Display download results."""
        if 'file_paths' in result:
            self.output_handler.print_info("Downloaded files:")
            for format_name, file_path in result['file_paths'].items():
                self.output_handler.print_info(f"  {format_name}: {file_path}")


# Example implementations for testing and demonstration

class MockTranscriptDownloader:
    """Mock implementation for testing."""
    
    def __init__(self, should_succeed: bool = True, result_data: Dict[str, Any] = None):
        self.should_succeed = should_succeed
        self.result_data = result_data or {
            'success': True,
            'file_paths': {
                'clean': '/test/transcript_clean.txt',
                'timestamped': '/test/transcript_timestamped.txt'
            },
            'video_id': 'test123'
        }
        self.download_calls = []
    
    def download_transcript(self, url: str, language_code: str = "en", 
                          output_dir: str = "./downloads/transcripts",
                          filename_template: str = "transcript",
                          formats: List[str] = None) -> Dict[str, Any]:
        self.download_calls.append({
            'url': url,
            'language_code': language_code,
            'output_dir': output_dir,
            'filename_template': filename_template,
            'formats': formats
        })
        
        if self.should_succeed:
            return self.result_data
        else:
            return {'success': False, 'error': 'Mock download failed'}


class MockMetadataExtractor:
    """Mock implementation for testing."""
    
    def __init__(self, should_succeed: bool = True, metadata: Dict[str, Any] = None):
        self.should_succeed = should_succeed
        self.metadata = metadata or {
            'success': True,
            'video_info': {
                'title': 'Test Video',
                'duration': 300,
                'uploader': 'Test Channel'
            }
        }
        self.extract_calls = []
    
    def get_transcript_metadata(self, url: str) -> Dict[str, Any]:
        self.extract_calls.append({'url': url})
        
        if self.should_succeed:
            return self.metadata
        else:
            return {'success': False, 'error': 'Mock extraction failed'}


class MockPreviewGenerator:
    """Mock implementation for testing."""
    
    def __init__(self, should_succeed: bool = True, preview: Dict[str, Any] = None):
        self.should_succeed = should_succeed
        self.preview = preview or {
            'success': True,
            'preview_text': 'This is a test preview of the transcript content.'
        }
        self.preview_calls = []
    
    def preview_transcript(self, url: str, language_code: str = "en") -> Dict[str, Any]:
        self.preview_calls.append({'url': url, 'language_code': language_code})
        
        if self.should_succeed:
            return self.preview
        else:
            return {'success': False, 'error': 'Mock preview failed'}


class MockLanguageLister:
    """Mock implementation for testing."""
    
    def __init__(self, languages: List[Dict[str, Any]] = None):
        self.languages = languages or [
            {'name': 'English', 'language_code': 'en', 'is_default': True},
            {'name': 'Spanish', 'language_code': 'es', 'is_default': False},
            {'name': 'French', 'language_code': 'fr', 'is_default': False}
        ]
        self.list_calls = []
    
    def list_available_languages(self, url: str) -> List[Dict[str, Any]]:
        self.list_calls.append({'url': url})
        return self.languages


class MockProgressReporter:
    """Mock implementation for testing."""
    
    def __init__(self):
        self.progress_calls = []
    
    def report_progress(self, message: str, percentage: Optional[float] = None) -> None:
        self.progress_calls.append({'message': message, 'percentage': percentage})


class MockOutputHandler:
    """Mock implementation for testing."""
    
    def __init__(self):
        self.info_messages = []
        self.error_messages = []
        self.success_messages = []
    
    def print_info(self, message: str) -> None:
        self.info_messages.append(message)
    
    def print_error(self, message: str) -> None:
        self.error_messages.append(message)
    
    def print_success(self, message: str) -> None:
        self.success_messages.append(message)


# Real implementations for production use

class RealOutputHandler:
    """Real output handler implementation."""
    
    def print_info(self, message: str) -> None:
        print(f"ℹ️  {message}")
    
    def print_error(self, message: str) -> None:
        print(f"❌ {message}", file=sys.stderr)
    
    def print_success(self, message: str) -> None:
        print(f"✅ {message}")


class RealProgressReporter:
    """Real progress reporter implementation."""
    
    def report_progress(self, message: str, percentage: Optional[float] = None) -> None:
        if percentage is not None:
            print(f"🔄 {message} ({percentage:.1f}%)")
        else:
            print(f"🔄 {message}")


# Factory function for easy creation
def create_cli(transcript_downloader: TranscriptDownloader = None,
              metadata_extractor: MetadataExtractor = None,
              preview_generator: PreviewGenerator = None,
              language_lister: LanguageLister = None,
              progress_reporter: ProgressReporter = None,
              output_handler: OutputHandler = None,
              config: Dict[str, Any] = None) -> RefactoredTranscriptCLI:
    """Factory function to create a CLI with default implementations."""
    
    return RefactoredTranscriptCLI(
        transcript_downloader=transcript_downloader or MockTranscriptDownloader(),
        metadata_extractor=metadata_extractor or MockMetadataExtractor(),
        preview_generator=preview_generator or MockPreviewGenerator(),
        language_lister=language_lister or MockLanguageLister(),
        progress_reporter=progress_reporter or MockProgressReporter(),
        output_handler=output_handler or MockOutputHandler(),
        config=config
    )


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
    
    # Required positional argument
    parser.add_argument(
        'url',
        help='YouTube video URL or video ID'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output-dir', '-o',
        default='./downloads/transcripts',
        help='Output directory for downloaded files (default: ./downloads/transcripts)'
    )
    
    parser.add_argument(
        '--filename-template', '-f',
        default='transcript',
        help='Output filename template (default: transcript)'
    )
    
    parser.add_argument(
        '--language', '-l',
        help='Preferred language code (e.g., en, es, fr)'
    )
    
    parser.add_argument(
        '--formats',
        nargs='+',
        default=['clean', 'timestamped', 'structured'],
        help='Output formats to generate (default: all formats)'
    )
    
    # Action flags
    parser.add_argument(
        '--metadata', '-m',
        action='store_true',
        help='Extract and display video metadata only'
    )
    
    parser.add_argument(
        '--preview', '-p',
        action='store_true',
        help='Generate and display transcript preview only'
    )
    
    parser.add_argument(
        '--list-languages',
        action='store_true',
        help='List available transcript languages'
    )
    
    # Verbosity
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the refactored CLI."""
    try:
        # Parse arguments
        args = parse_transcript_args()
        
        # Create CLI with real implementations
        cli = create_cli(
            output_handler=RealOutputHandler(),
            progress_reporter=RealProgressReporter()
        )
        
        # Run CLI
        cli.run(args)
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
