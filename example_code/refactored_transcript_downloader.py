"""
Refactored transcript downloader with dependency injection.

This demonstrates how dependency injection improves testability and maintainability
compared to the tightly coupled original implementation.
"""

from typing import Optional, Dict, Any, List, Protocol
from abc import ABC, abstractmethod
import logging

# Setup logger
logger = logging.getLogger("refactored_downloader")


class TranscriptAPI(Protocol):
    """Protocol for transcript API operations."""
    
    def list_transcripts(self, video_id: str) -> List[Any]:
        """List available transcripts for a video."""
        ...
    
    def fetch_transcript(self, video_id: str, language_code: str) -> List[Dict[str, Any]]:
        """Fetch transcript data for a video and language."""
        ...


class TranscriptProcessor(Protocol):
    """Protocol for transcript processing operations."""
    
    def process_transcript(self, transcript_data: List[Dict[str, Any]], 
                          formats: List[str]) -> Dict[str, str]:
        """Process transcript data into various formats."""
        ...


class MetadataCollector(Protocol):
    """Protocol for metadata collection operations."""
    
    def collect_metadata(self, video_info: Optional[Dict[str, Any]], 
                        transcript_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect comprehensive metadata."""
        ...


class FileManager(Protocol):
    """Protocol for file operations."""
    
    def ensure_directory(self, path: str) -> None:
        """Ensure directory exists."""
        ...
    
    def write_file(self, path: str, content: str) -> None:
        """Write content to file."""
        ...


class RefactoredTranscriptDownloader:
    """
    Refactored transcript downloader with dependency injection.
    
    This class demonstrates how dependency injection makes the code:
    - Easier to test (no complex mocking required)
    - More flexible (easy to swap implementations)
    - More maintainable (clear dependencies)
    - More configurable (inject different behaviors)
    """
    
    def __init__(self, 
                 api_provider: TranscriptAPI,
                 processor: TranscriptProcessor,
                 metadata_collector: Optional[MetadataCollector] = None,
                 file_manager: Optional[FileManager] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize with injected dependencies.
        
        Args:
            api_provider: Handles transcript API operations
            processor: Handles transcript processing
            metadata_collector: Handles metadata collection (optional)
            file_manager: Handles file operations (optional)
            config: Configuration dictionary (optional)
        """
        self.api = api_provider
        self.processor = processor
        self.metadata_collector = metadata_collector
        self.file_manager = file_manager
        self.config = config or {}
        
        logger.debug("RefactoredTranscriptDownloader initialized with injected dependencies")
    
    def download_transcript(self, 
                           video_id: str, 
                           language_code: str = "en",
                           output_path: str = "transcript",
                           formats: List[str] = None,
                           include_metadata: bool = False) -> Dict[str, Any]:
        """
        Download and process transcript with clean, testable logic.
        
        Args:
            video_id: YouTube video ID
            language_code: Preferred language code
            output_path: Base path for output files
            formats: List of output formats
            include_metadata: Whether to collect metadata
            
        Returns:
            Dictionary with results and file paths
        """
        if formats is None:
            formats = ["clean", "timestamped", "structured"]
        
        logger.info(f"Starting transcript download for video {video_id}")
        
        try:
            # Step 1: Get transcript data
            transcript_data = self._fetch_transcript_data(video_id, language_code)
            
            # Step 2: Process transcript
            processed_data = self.processor.process_transcript(transcript_data, formats)
            
            # Step 3: Save files
            file_paths = self._save_processed_data(processed_data, output_path)
            
            # Step 4: Collect metadata (if requested)
            metadata = {}
            if include_metadata and self.metadata_collector:
                metadata = self.metadata_collector.collect_metadata(None, transcript_data)
            
            # Step 5: Return results
            result = {
                "success": True,
                "video_id": video_id,
                "language_code": language_code,
                "file_paths": file_paths,
                "metadata": metadata,
                "transcript_entries": len(transcript_data)
            }
            
            logger.info(f"Successfully downloaded transcript for video {video_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to download transcript for video {video_id}: {e}")
            return {
                "success": False,
                "video_id": video_id,
                "error": str(e),
                "file_paths": {},
                "metadata": {}
            }
    
    def _fetch_transcript_data(self, video_id: str, language_code: str) -> List[Dict[str, Any]]:
        """Fetch transcript data using the injected API provider."""
        try:
            # Try to get transcript list first
            transcript_list = self.api.list_transcripts(video_id)
            
            # Find matching language
            for transcript in transcript_list:
                if hasattr(transcript, 'language_code') and transcript.language_code == language_code:
                    return transcript.fetch()
            
            # Fallback to direct fetch
            return self.api.fetch_transcript(video_id, language_code)
            
        except Exception as e:
            logger.warning(f"Primary method failed, trying fallback: {e}")
            return self.api.fetch_transcript(video_id, language_code)
    
    def _save_processed_data(self, processed_data: Dict[str, str], output_path: str) -> Dict[str, str]:
        """Save processed data to files using the injected file manager."""
        file_paths = {}
        
        if not self.file_manager:
            logger.warning("No file manager provided, skipping file save")
            return file_paths
        
        try:
            # Ensure output directory exists
            self.file_manager.ensure_directory(output_path)
            
            # Save each format
            for format_name, content in processed_data.items():
                file_path = f"{output_path}_{format_name}.txt"
                self.file_manager.write_file(file_path, content)
                file_paths[format_name] = file_path
                logger.debug(f"Saved {format_name} format to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save processed data: {e}")
            raise
        
        return file_paths


# Example implementations for testing and demonstration

class MockTranscriptAPI:
    """Mock implementation for testing."""
    
    def __init__(self, transcript_data: List[Dict[str, Any]] = None):
        self.transcript_data = transcript_data or [
            {"start": 0.0, "text": "Hello world."},
            {"start": 2.0, "text": "This is a test."}
        ]
    
    def list_transcripts(self, video_id: str) -> List[Any]:
        mock_transcript = MockTranscript()
        mock_transcript.language_code = "en"
        mock_transcript.fetch = lambda: self.transcript_data
        return [mock_transcript]
    
    def fetch_transcript(self, video_id: str, language_code: str) -> List[Dict[str, Any]]:
        return self.transcript_data


class MockTranscript:
    """Mock transcript object."""
    def __init__(self):
        self.language_code = "en"
        self.fetch = lambda: []


class MockTranscriptProcessor:
    """Mock implementation for testing."""
    
    def process_transcript(self, transcript_data: List[Dict[str, Any]], 
                          formats: List[str]) -> Dict[str, str]:
        # Return only the requested formats
        all_formats = {
            "clean": "Hello world. This is a test.",
            "timestamped": "[0.00s] Hello world.\n[2.00s] This is a test.",
            "structured": '{"transcript": "data"}'
        }
        return {fmt: all_formats[fmt] for fmt in formats if fmt in all_formats}


class MockMetadataCollector:
    """Mock implementation for testing."""
    
    def collect_metadata(self, video_info: Optional[Dict[str, Any]], 
                        transcript_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "word_count": len(" ".join(entry["text"] for entry in transcript_data).split()),
            "quality_score": 85.0,
            "language": "English"
        }


class MockFileManager:
    """Mock implementation for testing."""
    
    def __init__(self):
        self.saved_files = {}
        self.created_dirs = set()
    
    def ensure_directory(self, path: str) -> None:
        self.created_dirs.add(path)
    
    def write_file(self, path: str, content: str) -> None:
        self.saved_files[path] = content


# Factory function for easy creation
def create_downloader(api_provider: TranscriptAPI = None,
                     processor: TranscriptProcessor = None,
                     metadata_collector: MetadataCollector = None,
                     file_manager: FileManager = None,
                     config: Dict[str, Any] = None) -> RefactoredTranscriptDownloader:
    """Factory function to create a downloader with default implementations."""
    
    return RefactoredTranscriptDownloader(
        api_provider=api_provider or MockTranscriptAPI(),
        processor=processor or MockTranscriptProcessor(),
        metadata_collector=metadata_collector,
        file_manager=file_manager or MockFileManager(),
        config=config
    )
