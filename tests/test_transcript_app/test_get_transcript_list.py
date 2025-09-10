"""
Unit tests for get_transcript_list.py

Tests transcript discovery, selection, and preview functionality with mocked
YouTube API dependencies to ensure isolated unit testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Import the modules under test
from src.yt_transcript_app.get_transcript_list import (
    get_transcript_list,
    list_transcript_metadata,
    print_and_select_default_transcript,
    preview_transcript,
    print_transcript_preview
)


class TestGetTranscriptList:
    """Test cases for get_transcript_list function."""
    
    def test_get_transcript_list_success_with_instance(self):
        """Test successful transcript list retrieval using instance method."""
        # Arrange
        mock_transcript_list = Mock()
        mock_api = Mock()
        mock_api.list.return_value = mock_transcript_list
        
        with patch('src.yt_transcript_app.get_transcript_list.YouTubeTranscriptApi') as mock_api_class:
            mock_api_class.return_value = mock_api
            
            # Act
            result = get_transcript_list("test_video_123")
            
            # Assert
            assert result == mock_transcript_list
            mock_api_class.assert_called_once()
            mock_api.list.assert_called_once_with("test_video_123")
    
    def test_get_transcript_list_success_with_static(self):
        """Test successful transcript list retrieval using static method fallback."""
        # Arrange
        mock_transcript_list = Mock()
        
        with patch('src.yt_transcript_app.get_transcript_list.YouTubeTranscriptApi') as mock_api_class:
            # Simulate AttributeError on instance method
            mock_api_instance = Mock()
            mock_api_instance.list.side_effect = AttributeError("No list method")
            mock_api_class.return_value = mock_api_instance
            mock_api_class.list.return_value = mock_transcript_list
            
            # Act
            result = get_transcript_list("test_video_123")
            
            # Assert
            assert result == mock_transcript_list
            mock_api_class.list.assert_called_once_with("test_video_123")
    
    def test_get_transcript_list_exception(self):
        """Test transcript list retrieval when API raises exception."""
        # Arrange
        with patch('src.yt_transcript_app.get_transcript_list.YouTubeTranscriptApi') as mock_api_class:
            mock_api_instance = Mock()
            mock_api_instance.list.side_effect = Exception("API Error")
            mock_api_class.return_value = mock_api_instance
            mock_api_class.list.side_effect = Exception("API Error")
            
            # Act & Assert
            with pytest.raises(Exception, match="API Error"):
                get_transcript_list("test_video_123")


class TestListTranscriptMetadata:
    """Test cases for list_transcript_metadata function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock transcript objects
        self.mock_transcript_1 = Mock()
        self.mock_transcript_1.is_generated = False
        self.mock_transcript_1.language_code = "en"
        self.mock_transcript_1.language = "English"
        self.mock_transcript_1.is_translatable = True
        self.mock_transcript_1.translation_languages = ["es", "fr"]
        
        self.mock_transcript_2 = Mock()
        self.mock_transcript_2.is_generated = True
        self.mock_transcript_2.language_code = "es"
        self.mock_transcript_2.language = "Spanish"
        self.mock_transcript_2.is_translatable = False
        self.mock_transcript_2.translation_languages = []
        
        self.mock_transcript_3 = Mock()
        self.mock_transcript_3.is_generated = True
        self.mock_transcript_3.language_code = "en-US"
        self.mock_transcript_3.language = "English (US)"
        self.mock_transcript_3.is_translatable = True
        self.mock_transcript_3.translation_languages = ["es"]
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    def test_list_transcript_metadata_success(self, mock_get_transcript_list):
        """Test successful metadata extraction from transcript list."""
        # Arrange
        mock_transcript_list = [self.mock_transcript_1, self.mock_transcript_2, self.mock_transcript_3]
        mock_get_transcript_list.return_value = mock_transcript_list
        
        # Act
        result = list_transcript_metadata("test_video_123")
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Check first transcript (manual, should be default)
        assert result[0]["language_code"] == "en"
        assert result[0]["language"] == "English"
        assert result[0]["is_generated"] is False
        assert result[0]["is_translatable"] is True
        assert result[0]["is_default"] is True  # Manual transcript is preferred
        assert result[0]["can_translate_to"] == ["es", "fr"]
        
        # Check second transcript (auto-generated Spanish)
        assert result[1]["language_code"] == "es"
        assert result[1]["language"] == "Spanish"
        assert result[1]["is_generated"] is True
        assert result[1]["is_translatable"] is False
        assert result[1]["is_default"] is False  # Not English
        assert result[1]["can_translate_to"] == []
        
        # Check third transcript (auto-generated English, should be default)
        assert result[2]["language_code"] == "en-US"
        assert result[2]["language"] == "English (US)"
        assert result[2]["is_generated"] is True
        assert result[2]["is_translatable"] is True
        assert result[2]["is_default"] is True  # English auto-generated is also default
        assert result[2]["can_translate_to"] == ["es"]
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    def test_list_transcript_metadata_api_error(self, mock_get_transcript_list):
        """Test metadata extraction when API raises exception."""
        # Arrange
        mock_get_transcript_list.side_effect = Exception("API Error")
        
        # Act
        result = list_transcript_metadata("test_video_123")
        
        # Assert
        assert result == []
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    def test_list_transcript_metadata_empty_list(self, mock_get_transcript_list):
        """Test metadata extraction with empty transcript list."""
        # Arrange
        mock_get_transcript_list.return_value = []
        
        # Act
        result = list_transcript_metadata("test_video_123")
        
        # Assert
        assert result == []


class TestPrintAndSelectDefaultTranscript:
    """Test cases for print_and_select_default_transcript function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_transcript_metadata = [
            {
                "language_code": "en",
                "language": "English",
                "is_generated": False,
                "is_translatable": True,
                "is_default": True
            },
            {
                "language_code": "es",
                "language": "Spanish",
                "is_generated": True,
                "is_translatable": False,
                "is_default": False
            },
            {
                "language_code": "fr",
                "language": "French",
                "is_generated": True,
                "is_translatable": True,
                "is_default": False
            }
        ]
    
    @patch('src.yt_transcript_app.get_transcript_list.list_transcript_metadata')
    @patch('path_utils.path_utils.load_config')
    def test_print_and_select_default_transcript_success(self, mock_load_config, mock_list_metadata, capsys):
        """Test successful transcript selection with default preference."""
        # Arrange
        mock_load_config.return_value = {}
        mock_list_metadata.return_value = self.sample_transcript_metadata
        
        # Act
        result = print_and_select_default_transcript("test_video_123")
        
        # Assert
        assert result is not None
        assert result["language_code"] == "en"  # Should select the default (manual English)
        assert result["is_generated"] is False
        
        # Check console output
        captured = capsys.readouterr()
        assert "Transcript Info" in captured.out
        assert "English" in captured.out
        assert "Spanish" in captured.out
        assert "French" in captured.out
        assert "[DEFAULT]" in captured.out
    
    @patch('src.yt_transcript_app.get_transcript_list.list_transcript_metadata')
    @patch('path_utils.path_utils.load_config')
    def test_print_and_select_default_transcript_with_preferred_language(self, mock_load_config, mock_list_metadata, capsys):
        """Test transcript selection with specific preferred language."""
        # Arrange - Create metadata where Spanish is not marked as default
        spanish_preferred_metadata = [
            {
                "language_code": "en",
                "language": "English",
                "is_generated": False,
                "is_translatable": True,
                "is_default": False  # Not default
            },
            {
                "language_code": "es",
                "language": "Spanish",
                "is_generated": True,
                "is_translatable": False,
                "is_default": False  # Not default
            },
            {
                "language_code": "fr",
                "language": "French",
                "is_generated": True,
                "is_translatable": True,
                "is_default": False  # Not default
            }
        ]
        mock_load_config.return_value = {}
        mock_list_metadata.return_value = spanish_preferred_metadata
        
        # Act
        result = print_and_select_default_transcript("test_video_123", preferred_language="es")
        
        # Assert
        assert result is not None
        assert result["language_code"] == "es"  # Should select Spanish as preferred
        assert result["is_generated"] is True
    
    @patch('src.yt_transcript_app.get_transcript_list.list_transcript_metadata')
    @patch('path_utils.path_utils.load_config')
    def test_print_and_select_default_transcript_no_transcripts(self, mock_load_config, mock_list_metadata, capsys):
        """Test transcript selection when no transcripts are available."""
        # Arrange
        mock_load_config.return_value = {}
        mock_list_metadata.return_value = []
        
        # Act
        result = print_and_select_default_transcript("test_video_123")
        
        # Assert
        assert result is None
        
        # Check console output
        captured = capsys.readouterr()
        assert "No transcripts found" in captured.out
    
    @patch('src.yt_transcript_app.get_transcript_list.list_transcript_metadata')
    @patch('path_utils.path_utils.load_config')
    def test_print_and_select_default_transcript_fallback_to_english_auto(self, mock_load_config, mock_list_metadata, capsys):
        """Test fallback to English auto-generated when no manual transcripts."""
        # Arrange
        auto_generated_only = [
            {
                "language_code": "es",
                "language": "Spanish",
                "is_generated": True,
                "is_translatable": False,
                "is_default": False
            },
            {
                "language_code": "en",
                "language": "English",
                "is_generated": True,
                "is_translatable": True,
                "is_default": True
            }
        ]
        mock_load_config.return_value = {}
        mock_list_metadata.return_value = auto_generated_only
        
        # Act
        result = print_and_select_default_transcript("test_video_123")
        
        # Assert
        assert result is not None
        assert result["language_code"] == "en"  # Should select English auto-generated
        assert result["is_generated"] is True
    
    @patch('src.yt_transcript_app.get_transcript_list.list_transcript_metadata')
    def test_print_and_select_default_transcript_api_error(self, mock_list_metadata, capsys):
        """Test transcript selection when API raises exception."""
        # Arrange
        mock_list_metadata.side_effect = Exception("API Error")
        
        # Act
        result = print_and_select_default_transcript("test_video_123")
        
        # Assert
        assert result is None
        
        # Check console output
        captured = capsys.readouterr()
        assert "Error fetching transcript info" in captured.out


class TestPreviewTranscript:
    """Test cases for preview_transcript function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_transcript_data = [
            {"start": 0.0, "text": "Hello world."},
            {"start": 2.0, "text": "This is a test."},
            {"start": 4.0, "text": "Preview content."}
        ]
        
        self.sample_preview_data = {
            "preview_text": "[0.00s] Hello world.\n[2.00s] This is a test.\n[4.00s] Preview content.",
            "total_entries": 3,
            "language_code": "en",
            "statistics": {
                "word_count": 6,
                "character_count": 30,
                "estimated_reading_time_minutes": 0.1
            }
        }
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    @patch('src.yt_transcript_app.get_transcript_list.print_and_select_default_transcript')
    @patch('src.yt_transcript_app.transcript_processor.TranscriptProcessor')
    def test_preview_transcript_success_with_language(self, mock_processor_class, mock_select_transcript, mock_get_transcript_list):
        """Test successful transcript preview with specific language."""
        # Arrange
        mock_transcript = Mock()
        mock_transcript.language_code = "en"
        mock_transcript.fetch.return_value = self.sample_transcript_data
        mock_get_transcript_list.return_value = [mock_transcript]
        
        mock_processor = Mock()
        mock_processor.generate_preview.return_value = self.sample_preview_data
        mock_processor_class.return_value = mock_processor
        
        # Act
        result = preview_transcript("test_video_123", language_code="en")
        
        # Assert
        assert result is not None
        assert result["preview_text"] == self.sample_preview_data["preview_text"]
        assert result["total_entries"] == 3
        assert result["language_code"] == "en"
        mock_transcript.fetch.assert_called_once()
        mock_processor.generate_preview.assert_called_once_with(self.sample_transcript_data)
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    @patch('src.yt_transcript_app.get_transcript_list.print_and_select_default_transcript')
    @patch('src.yt_transcript_app.transcript_processor.TranscriptProcessor')
    def test_preview_transcript_success_auto_select(self, mock_processor_class, mock_select_transcript, mock_get_transcript_list):
        """Test successful transcript preview with automatic language selection."""
        # Arrange
        mock_select_transcript.return_value = {"language_code": "en", "language": "English"}
        
        mock_transcript = Mock()
        mock_transcript.language_code = "en"
        mock_transcript.fetch.return_value = self.sample_transcript_data
        mock_get_transcript_list.return_value = [mock_transcript]
        
        mock_processor = Mock()
        mock_processor.generate_preview.return_value = self.sample_preview_data
        mock_processor_class.return_value = mock_processor
        
        # Act
        result = preview_transcript("test_video_123")
        
        # Assert
        assert result is not None
        assert result["language_code"] == "en"
        mock_select_transcript.assert_called_once_with("test_video_123", preferred_language=None)
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    @patch('src.yt_transcript_app.get_transcript_list.print_and_select_default_transcript')
    def test_preview_transcript_no_default_transcript(self, mock_select_transcript, mock_get_transcript_list):
        """Test preview when no default transcript is found."""
        # Arrange
        mock_select_transcript.return_value = None
        
        # Act
        result = preview_transcript("test_video_123")
        
        # Assert
        assert result is None
        mock_get_transcript_list.assert_not_called()
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    @patch('src.yt_transcript_app.get_transcript_list.print_and_select_default_transcript')
    @patch('src.yt_transcript_app.transcript_processor.TranscriptProcessor')
    def test_preview_transcript_fallback_method(self, mock_processor_class, mock_select_transcript, mock_get_transcript_list):
        """Test preview with fallback to direct API call."""
        # Arrange
        mock_select_transcript.return_value = {"language_code": "en", "language": "English"}
        mock_get_transcript_list.return_value = []  # No transcripts in list
        
        mock_processor = Mock()
        mock_processor.generate_preview.return_value = self.sample_preview_data
        mock_processor_class.return_value = mock_processor
        
        # Mock the fallback API call
        with patch('youtube_transcript_api.YouTubeTranscriptApi.fetch') as mock_fetch:
            mock_fetch.return_value = self.sample_transcript_data
            
            # Act
            result = preview_transcript("test_video_123", language_code="en")
            
            # Assert
            assert result is not None
            mock_fetch.assert_called_once_with("test_video_123", languages=["en"])
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    @patch('src.yt_transcript_app.get_transcript_list.print_and_select_default_transcript')
    @patch('src.yt_transcript_app.transcript_processor.TranscriptProcessor')
    def test_preview_transcript_no_transcript_data(self, mock_processor_class, mock_select_transcript, mock_get_transcript_list):
        """Test preview when no transcript data is available."""
        # Arrange
        mock_select_transcript.return_value = {"language_code": "en", "language": "English"}
        mock_get_transcript_list.return_value = []
        
        # Mock the fallback API call to return None
        with patch('youtube_transcript_api.YouTubeTranscriptApi.fetch') as mock_fetch:
            mock_fetch.return_value = None
            
            # Act
            result = preview_transcript("test_video_123", language_code="en")
            
            # Assert
            assert result is None
    
    @patch('src.yt_transcript_app.get_transcript_list.get_transcript_list')
    @patch('src.yt_transcript_app.get_transcript_list.print_and_select_default_transcript')
    def test_preview_transcript_api_exception(self, mock_select_transcript, mock_get_transcript_list):
        """Test preview when API raises exception."""
        # Arrange
        mock_select_transcript.return_value = {"language_code": "en", "language": "English"}
        mock_get_transcript_list.side_effect = Exception("API Error")
        
        # Act
        result = preview_transcript("test_video_123", language_code="en")
        
        # Assert
        assert result is None


class TestPrintTranscriptPreview:
    """Test cases for print_transcript_preview function."""
    
    @patch('src.yt_transcript_app.get_transcript_list.preview_transcript')
    def test_print_transcript_preview_success(self, mock_preview, capsys):
        """Test successful preview printing."""
        # Arrange
        mock_preview.return_value = {
            "preview_text": "[0.00s] Hello world.\n[2.00s] This is a test.",
            "total_entries": 2,
            "language_code": "en",
            "statistics": {
                "word_count": 4,
                "character_count": 20,
                "estimated_reading_time_minutes": 0.1
            },
            "quality_indicators": {
                "quality_estimate": "High",
                "average_entry_length": 10.0,
                "has_timestamps": True
            }
        }
        
        # Act
        print_transcript_preview("test_video_123", "en")
        
        # Assert
        captured = capsys.readouterr()
        assert "Transcript Preview (en)" in captured.out
        assert "Hello world" in captured.out
        assert "This is a test" in captured.out
        assert "Word count: 4" in captured.out
        assert "Quality estimate: High" in captured.out
        assert "Total entries available: 2" in captured.out
    
    @patch('src.yt_transcript_app.get_transcript_list.preview_transcript')
    def test_print_transcript_preview_no_preview(self, mock_preview, capsys):
        """Test preview printing when no preview is available."""
        # Arrange
        mock_preview.return_value = None
        
        # Act
        print_transcript_preview("test_video_123", "en")
        
        # Assert
        captured = capsys.readouterr()
        assert "No transcript preview available" in captured.out
    
    @patch('src.yt_transcript_app.get_transcript_list.preview_transcript')
    def test_print_transcript_preview_with_insights(self, mock_preview, capsys):
        """Test preview printing with content insights."""
        # Arrange
        mock_preview.return_value = {
            "preview_text": "[0.00s] Hello world.",
            "total_entries": 1,
            "language_code": "en",
            "statistics": {
                "word_count": 2,
                "character_count": 10,
                "estimated_reading_time_minutes": 0.1
            },
            "content_insights": {
                "content_category": "Educational",
                "language_detected": "English",
                "keywords": ["hello", "world"],
                "topics": ["greeting", "introduction"]
            },
            "quality_insights": {
                "quality_score": 85.0,
                "quality_category": "Very Good",
                "artifact_ratio": 0.05
            },
            "content_metrics": {
                "speaking_rate_wpm": 120.0,
                "readability": "Easy",
                "lexical_diversity": 0.8
            }
        }
        
        # Act
        print_transcript_preview("test_video_123", "en")
        
        # Assert
        captured = capsys.readouterr()
        assert "Content Insights:" in captured.out
        assert "Category: Educational" in captured.out
        assert "Language: English" in captured.out
        assert "Key topics: hello, world" in captured.out
        assert "Quality Assessment:" in captured.out
        assert "Overall quality: Very Good (85.0/100)" in captured.out
        assert "Content Metrics:" in captured.out
        assert "Speaking rate: 120.0 words/minute" in captured.out


if __name__ == '__main__':
    pytest.main([__file__])
