"""
Unit tests for refactored_transcript_downloader.py

Demonstrates how dependency injection makes unit testing simple and clean.
No complex mocking required - just inject test doubles!
"""

import pytest
from unittest.mock import Mock
from typing import List, Dict, Any

# Import the refactored module
from src.yt_transcript_app.refactored_transcript_downloader import (
    RefactoredTranscriptDownloader,
    MockTranscriptAPI,
    MockTranscriptProcessor,
    MockMetadataCollector,
    MockFileManager,
    create_downloader
)


class TestRefactoredTranscriptDownloader:
    """Test cases for the refactored downloader with dependency injection."""
    
    def test_initialization_with_dependencies(self):
        """Test initialization with injected dependencies."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        mock_metadata = MockMetadataCollector()
        mock_files = MockFileManager()
        config = {"test": "value"}
        
        # Act
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            metadata_collector=mock_metadata,
            file_manager=mock_files,
            config=config
        )
        
        # Assert
        assert downloader.api == mock_api
        assert downloader.processor == mock_processor
        assert downloader.metadata_collector == mock_metadata
        assert downloader.file_manager == mock_files
        assert downloader.config == config
    
    def test_download_transcript_success(self):
        """Test successful transcript download."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        mock_files = MockFileManager()
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            file_manager=mock_files
        )
        
        # Act
        result = downloader.download_transcript("test_video_123", "en")
        
        # Assert
        assert result["success"] is True
        assert result["video_id"] == "test_video_123"
        assert result["language_code"] == "en"
        assert "file_paths" in result
        assert result["transcript_entries"] == 2
        
        # Check that files were saved
        assert len(mock_files.saved_files) == 3  # clean, timestamped, structured
        assert "transcript_clean.txt" in mock_files.saved_files
        assert "transcript_timestamped.txt" in mock_files.saved_files
        assert "transcript_structured.txt" in mock_files.saved_files
    
    def test_download_transcript_with_metadata(self):
        """Test transcript download with metadata collection."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        mock_metadata = MockMetadataCollector()
        mock_files = MockFileManager()
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            metadata_collector=mock_metadata,
            file_manager=mock_files
        )
        
        # Act
        result = downloader.download_transcript("test_video_123", include_metadata=True)
        
        # Assert
        assert result["success"] is True
        assert "metadata" in result
        assert result["metadata"]["word_count"] == 6  # "Hello world. This is a test." (6 words)
        assert result["metadata"]["quality_score"] == 85.0
    
    def test_download_transcript_api_failure(self):
        """Test handling of API failures."""
        # Arrange
        mock_api = MockTranscriptAPI()
        # Make both methods fail
        mock_api.list_transcripts = Mock(side_effect=Exception("List Error"))
        mock_api.fetch_transcript = Mock(side_effect=Exception("Fetch Error"))
        mock_processor = MockTranscriptProcessor()
        mock_files = MockFileManager()
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            file_manager=mock_files
        )
        
        # Act
        result = downloader.download_transcript("test_video_123")
        
        # Assert
        assert result["success"] is False
        assert result["video_id"] == "test_video_123"
        assert "Fetch Error" in result["error"]
        assert result["file_paths"] == {}
    
    def test_download_transcript_processor_failure(self):
        """Test handling of processor failures."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        mock_processor.process_transcript = Mock(side_effect=Exception("Processing Error"))
        mock_files = MockFileManager()
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            file_manager=mock_files
        )
        
        # Act
        result = downloader.download_transcript("test_video_123")
        
        # Assert
        assert result["success"] is False
        assert "Processing Error" in result["error"]
    
    def test_download_transcript_file_save_failure(self):
        """Test handling of file save failures."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        mock_files = MockFileManager()
        mock_files.write_file = Mock(side_effect=Exception("File Error"))
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            file_manager=mock_files
        )
        
        # Act
        result = downloader.download_transcript("test_video_123")
        
        # Assert
        assert result["success"] is False
        assert "File Error" in result["error"]
    
    def test_download_transcript_no_file_manager(self):
        """Test behavior when no file manager is provided."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            file_manager=None  # No file manager
        )
        
        # Act
        result = downloader.download_transcript("test_video_123")
        
        # Assert
        assert result["success"] is True
        assert result["file_paths"] == {}  # No files saved
    
    def test_download_transcript_no_metadata_collector(self):
        """Test behavior when no metadata collector is provided."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        mock_files = MockFileManager()
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            file_manager=mock_files,
            metadata_collector=None  # No metadata collector
        )
        
        # Act
        result = downloader.download_transcript("test_video_123", include_metadata=True)
        
        # Assert
        assert result["success"] is True
        assert result["metadata"] == {}  # No metadata collected
    
    def test_custom_formats(self):
        """Test download with custom formats."""
        # Arrange
        mock_api = MockTranscriptAPI()
        mock_processor = MockTranscriptProcessor()
        mock_files = MockFileManager()
        
        downloader = RefactoredTranscriptDownloader(
            api_provider=mock_api,
            processor=mock_processor,
            file_manager=mock_files
        )
        
        # Act
        result = downloader.download_transcript(
            "test_video_123", 
            formats=["clean", "structured"]  # Only 2 formats
        )
        
        # Assert
        assert result["success"] is True
        assert len(mock_files.saved_files) == 2  # Only 2 files saved
        assert "transcript_clean.txt" in mock_files.saved_files
        assert "transcript_structured.txt" in mock_files.saved_files
        assert "transcript_timestamped.txt" not in mock_files.saved_files


class TestFactoryFunction:
    """Test cases for the factory function."""
    
    def test_create_downloader_with_defaults(self):
        """Test creating downloader with default implementations."""
        # Act
        downloader = create_downloader()
        
        # Assert
        assert isinstance(downloader.api, MockTranscriptAPI)
        assert isinstance(downloader.processor, MockTranscriptProcessor)
        assert isinstance(downloader.file_manager, MockFileManager)
        assert downloader.metadata_collector is None
    
    def test_create_downloader_with_custom_dependencies(self):
        """Test creating downloader with custom dependencies."""
        # Arrange
        custom_api = MockTranscriptAPI()
        custom_processor = MockTranscriptProcessor()
        custom_metadata = MockMetadataCollector()
        custom_files = MockFileManager()
        custom_config = {"custom": "value"}
        
        # Act
        downloader = create_downloader(
            api_provider=custom_api,
            processor=custom_processor,
            metadata_collector=custom_metadata,
            file_manager=custom_files,
            config=custom_config
        )
        
        # Assert
        assert downloader.api == custom_api
        assert downloader.processor == custom_processor
        assert downloader.metadata_collector == custom_metadata
        assert downloader.file_manager == custom_files
        assert downloader.config == custom_config


class TestMockImplementations:
    """Test cases for the mock implementations."""
    
    def test_mock_transcript_api(self):
        """Test mock transcript API."""
        # Arrange
        mock_api = MockTranscriptAPI()
        
        # Act
        transcript_list = mock_api.list_transcripts("test_video")
        transcript_data = mock_api.fetch_transcript("test_video", "en")
        
        # Assert
        assert len(transcript_list) == 1
        assert transcript_list[0].language_code == "en"
        assert len(transcript_data) == 2
        assert transcript_data[0]["text"] == "Hello world."
    
    def test_mock_transcript_processor(self):
        """Test mock transcript processor."""
        # Arrange
        mock_processor = MockTranscriptProcessor()
        transcript_data = [{"start": 0.0, "text": "Hello world."}]
        
        # Act
        result = mock_processor.process_transcript(transcript_data, ["clean"])
        
        # Assert
        assert "clean" in result
        assert result["clean"] == "Hello world. This is a test."
    
    def test_mock_metadata_collector(self):
        """Test mock metadata collector."""
        # Arrange
        mock_metadata = MockMetadataCollector()
        transcript_data = [{"start": 0.0, "text": "Hello world."}]
        
        # Act
        result = mock_metadata.collect_metadata(None, transcript_data)
        
        # Assert
        assert result["word_count"] == 2  # "Hello world."
        assert result["quality_score"] == 85.0
        assert result["language"] == "English"
    
    def test_mock_file_manager(self):
        """Test mock file manager."""
        # Arrange
        mock_files = MockFileManager()
        
        # Act
        mock_files.ensure_directory("/test/path")
        mock_files.write_file("/test/file.txt", "test content")
        
        # Assert
        assert "/test/path" in mock_files.created_dirs
        assert "/test/file.txt" in mock_files.saved_files
        assert mock_files.saved_files["/test/file.txt"] == "test content"


if __name__ == '__main__':
    pytest.main([__file__])
