"""
Unit tests for trans_core.py

Tests the core transcript download functionality with mocked external dependencies
to ensure isolated unit testing of the main business logic.
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path

# Import the modules under test
from src.yt_transcript_app.trans_core import (
    validate_transcript_url,
    extract_video_id,
    get_transcript_output_template,
    check_transcript_file_exists,
    perform_transcript_download,
    download_transcript,
    get_transcript_metadata,
    preview_transcript,
    default_transcript_progress_hook
)


class TestURLValidation:
    """Test cases for URL validation functions."""
    
    def test_validate_transcript_url_valid_urls(self):
        """Test validation of valid YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=VIDEO_ID",
            "https://youtu.be/VIDEO_ID",
            "https://youtube.com/embed/VIDEO_ID",
            "https://youtube.com/v/VIDEO_ID",
            "http://www.youtube.com/watch?v=VIDEO_ID",
            "https://m.youtube.com/watch?v=VIDEO_ID"
        ]
        
        for url in valid_urls:
            assert validate_transcript_url(url) is True, f"URL should be valid: {url}"
    
    def test_validate_transcript_url_invalid_urls(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            "https://www.google.com",
            "https://vimeo.com/123456",
            "not_a_url",
            "https://youtube.com/playlist?list=PL123",
            "https://youtube.com/channel/UC123",
            "",
            None
        ]
        
        for url in invalid_urls:
            if url is not None:  # Skip None as it would cause TypeError
                assert validate_transcript_url(url) is False, f"URL should be invalid: {url}"
    
    def test_extract_video_id_valid_urls(self):
        """Test video ID extraction from valid URLs."""
        test_cases = [
            ("https://www.youtube.com/watch?v=ABC123DEF45", "ABC123DEF45"),  # 11 chars
            ("https://youtu.be/ABC123DEF45", "ABC123DEF45"),
            ("https://youtube.com/embed/ABC123DEF45", "ABC123DEF45"),
            ("https://youtube.com/v/ABC123DEF45", "ABC123DEF45"),
            ("https://www.youtube.com/watch?v=ABC123DEF45&t=30s", "ABC123DEF45"),
            ("https://youtu.be/ABC123DEF45?t=30s", "ABC123DEF45")
        ]
        
        for url, expected_id in test_cases:
            result = extract_video_id(url)
            assert result == expected_id, f"Expected {expected_id}, got {result} for URL: {url}"
    
    def test_extract_video_id_invalid_urls(self):
        """Test video ID extraction from invalid URLs."""
        invalid_urls = [
            "https://www.google.com",
            "not_a_url",
            "https://youtube.com/playlist?list=PL123",
            "",
            None
        ]
        
        for url in invalid_urls:
            if url is not None:
                result = extract_video_id(url)
                assert result is None, f"Expected None, got {result} for URL: {url}"


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    @patch('src.yt_transcript_app.trans_core.get_script_directories')
    @patch('src.yt_transcript_app.trans_core.ensure_directory')
    def test_get_transcript_output_template_default(self, mock_ensure_dir, mock_get_dirs):
        """Test getting default output template."""
        # Arrange
        mock_get_dirs.return_value = (Path("/script"), Path("/base"))
        mock_ensure_dir.return_value = Path("/base/downloads/transcripts")
        
        # Act
        result = get_transcript_output_template()
        
        # Assert
        # Use Path for cross-platform compatibility
        expected = str(Path("/base/downloads/transcripts/transcript"))
        assert result == expected
        mock_get_dirs.assert_called_once()
        mock_ensure_dir.assert_called_once()
    
    @patch('src.yt_transcript_app.trans_core.get_script_directories')
    @patch('src.yt_transcript_app.trans_core.resolve_path')
    @patch('src.yt_transcript_app.trans_core.ensure_directory')
    def test_get_transcript_output_template_custom(self, mock_ensure_dir, mock_resolve, mock_get_dirs):
        """Test getting custom output template."""
        # Arrange
        mock_get_dirs.return_value = (Path("/script"), Path("/base"))
        mock_resolve.return_value = Path("/custom/path")
        mock_ensure_dir.return_value = Path("/custom/path")
        
        # Act
        result = get_transcript_output_template(custom_path="/custom/path", template="custom_name")
        
        # Assert
        # Use Path for cross-platform compatibility
        expected = str(Path("/custom/path/custom_name"))
        assert result == expected
        mock_resolve.assert_called_once_with("/custom/path", Path("/base"))
    
    def test_check_transcript_file_exists_file_exists(self):
        """Test file existence check when file exists."""
        # Arrange
        mock_file_checker = Mock(return_value=True)
        
        # Act
        result = check_transcript_file_exists("/path/to/file.txt", mock_file_checker)
        
        # Assert
        assert result is True
        mock_file_checker.assert_called_once_with("/path/to/file.txt")
    
    def test_check_transcript_file_exists_file_not_exists(self):
        """Test file existence check when file doesn't exist."""
        # Arrange
        mock_file_checker = Mock(return_value=False)
        
        # Act
        result = check_transcript_file_exists("/path/to/file.txt", mock_file_checker)
        
        # Assert
        assert result is False
        mock_file_checker.assert_called_once_with("/path/to/file.txt")
    
    def test_default_transcript_progress_hook_downloading(self, capsys):
        """Test progress hook during download."""
        # Arrange
        progress_data = {'status': 'downloading', '_percent_str': '50%'}
        
        # Act
        default_transcript_progress_hook(progress_data)
        
        # Assert
        captured = capsys.readouterr()
        assert "Downloading transcript: 50%" in captured.out
    
    def test_default_transcript_progress_hook_finished(self, capsys):
        """Test progress hook when finished."""
        # Arrange
        progress_data = {'status': 'finished'}
        
        # Act
        default_transcript_progress_hook(progress_data)
        
        # Assert
        captured = capsys.readouterr()
        assert "Transcript download: 100%" in captured.out


class TestPerformTranscriptDownload:
    """Test cases for perform_transcript_download function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_transcript_data = [
            {"start": 0.0, "text": "Hello world."},
            {"start": 2.0, "text": "This is a test."}
        ]
        
        self.sample_video_metadata = {
            "id": "test_video_123",
            "title": "Test Video",
            "duration": 30
        }
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', mock_open())
    @patch('src.yt_transcript_app.trans_core.load_config')
    @patch('src.yt_transcript_app.trans_core.process_transcript_data')
    @patch('src.yt_transcript_app.trans_core.get_transcript_list')
    def test_perform_transcript_download_success(self, mock_get_transcript_list, mock_process_data, 
                                                mock_load_config, mock_open_file, mock_mkdir):
        """Test successful transcript download."""
        # Arrange
        mock_load_config.return_value = {}
        mock_transcript = Mock()
        mock_transcript.language_code = "en"
        mock_transcript.fetch.return_value = self.sample_transcript_data
        mock_get_transcript_list.return_value = [mock_transcript]
        
        mock_process_data.return_value = {
            'clean': 'Hello world. This is a test.',
            'timestamped': '[0.00s] Hello world.\n[2.00s] This is a test.',
            'structured': {'metadata': {}, 'transcript': {}}
        }
        
        # Act
        result = perform_transcript_download(
            video_id="test_video_123",
            language_code="en",
            output_template="/output/transcript",
            formats=['clean', 'timestamped', 'structured'],
            video_metadata=self.sample_video_metadata
        )
        
        # Assert
        assert isinstance(result, dict)
        assert 'clean' in result
        assert 'timestamped' in result
        assert 'structured' in result
        assert result['clean'].endswith('_clean.txt')
        assert result['timestamped'].endswith('_timestamped.txt')
        assert result['structured'].endswith('_structured.json')
        
        mock_get_transcript_list.assert_called_once_with("test_video_123")
        mock_transcript.fetch.assert_called_once()
        mock_process_data.assert_called_once()
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', mock_open())
    @patch('src.yt_transcript_app.trans_core.load_config')
    @patch('src.yt_transcript_app.trans_core.process_transcript_data')
    @patch('src.yt_transcript_app.trans_core.get_transcript_list')
    def test_perform_transcript_download_fallback(self, mock_get_transcript_list, mock_process_data,
                                                 mock_load_config, mock_open_file, mock_mkdir):
        """Test transcript download with fallback method."""
        # Arrange
        mock_load_config.return_value = {}
        mock_get_transcript_list.return_value = []  # No transcripts found in list
        
        # Mock the YouTube API fallback
        with patch('youtube_transcript_api.YouTubeTranscriptApi.fetch') as mock_fetch:
            mock_fetch.return_value = self.sample_transcript_data
            
            mock_process_data.return_value = {
                'clean': 'Hello world. This is a test.',
                'timestamped': '[0.00s] Hello world.\n[2.00s] This is a test.',
                'structured': {'metadata': {}, 'transcript': {}}
            }
            
            # Act
            result = perform_transcript_download(
                video_id="test_video_123",
                language_code="en",
                output_template="/output/transcript",
                formats=['clean'],
                video_metadata=self.sample_video_metadata
            )
            
            # Assert
            assert isinstance(result, dict)
            assert 'clean' in result
            mock_fetch.assert_called_once_with("test_video_123", languages=["en"])
    
    @patch('src.yt_transcript_app.trans_core.get_transcript_list')
    def test_perform_transcript_download_no_transcript_found(self, mock_get_transcript_list):
        """Test transcript download when no transcript is found."""
        # Arrange
        mock_get_transcript_list.return_value = []
        
        # Mock the YouTube API fallback to raise an exception
        with patch('youtube_transcript_api.YouTubeTranscriptApi.fetch') as mock_fetch:
            mock_fetch.side_effect = Exception("No transcript found")
            
            # Act & Assert
            with pytest.raises(Exception, match="No transcript found for language: en"):
                perform_transcript_download(
                    video_id="test_video_123",
                    language_code="en",
                    output_template="/output/transcript",
                    formats=['clean']
                )


class TestDownloadTranscript:
    """Test cases for main download_transcript function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_video_metadata = {
            "id": "test_video_123",
            "title": "Test Video",
            "duration": 30,
            "uploader": "Test Channel"
        }
    
    @patch('src.yt_transcript_app.trans_core.perform_transcript_download')
    @patch('src.yt_transcript_app.trans_core.print_and_select_default_transcript')
    @patch('src.yt_transcript_app.trans_core.get_transcript_output_template')
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    @patch('src.yt_transcript_app.trans_core.validate_transcript_url')
    def test_download_transcript_success(self, mock_validate, mock_extract, mock_get_template, 
                                       mock_select_transcript, mock_perform_download):
        """Test successful transcript download."""
        # Arrange
        mock_validate.return_value = True
        mock_extract.return_value = "test_video_123"
        mock_get_template.return_value = "/output/transcript"
        mock_select_transcript.return_value = {"language_code": "en", "language": "English"}
        mock_perform_download.return_value = {
            'clean': '/output/transcript_clean.txt',
            'timestamped': '/output/transcript_timestamped.txt',
            'structured': '/output/transcript_structured.json'
        }
        
        # Act
        result = download_transcript("https://youtube.com/watch?v=test_video_123")
        
        # Assert
        assert isinstance(result, dict)
        assert 'clean' in result
        assert 'timestamped' in result
        assert 'structured' in result
        mock_validate.assert_called_once()
        mock_extract.assert_called_once()
        mock_perform_download.assert_called_once()
    
    def test_download_transcript_invalid_url(self):
        """Test download with invalid URL."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            download_transcript("https://invalid-url.com")
    
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    @patch('src.yt_transcript_app.trans_core.validate_transcript_url')
    def test_download_transcript_no_video_id(self, mock_validate, mock_extract):
        """Test download when video ID cannot be extracted."""
        # Arrange
        mock_validate.return_value = True
        mock_extract.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Could not extract video ID"):
            download_transcript("https://youtube.com/invalid")
    
    @patch('src.yt_transcript_app.trans_core.perform_transcript_download')
    @patch('src.yt_transcript_app.trans_core.print_and_select_default_transcript')
    @patch('src.yt_transcript_app.trans_core.get_transcript_output_template')
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    @patch('src.yt_transcript_app.trans_core.validate_transcript_url')
    def test_download_transcript_no_suitable_transcript(self, mock_validate, mock_extract, 
                                                      mock_get_template, mock_select_transcript, 
                                                      mock_perform_download):
        """Test download when no suitable transcript is found."""
        # Arrange
        mock_validate.return_value = True
        mock_extract.return_value = "test_video_123"
        mock_get_template.return_value = "/output/transcript"
        mock_select_transcript.return_value = None  # No suitable transcript
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="No suitable transcript found"):
            download_transcript("https://youtube.com/watch?v=test_video_123")
    
    @patch('src.yt_transcript_app.trans_core.perform_transcript_download')
    @patch('src.yt_transcript_app.trans_core.print_and_select_default_transcript')
    @patch('src.yt_transcript_app.trans_core.get_transcript_output_template')
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    @patch('src.yt_transcript_app.trans_core.validate_transcript_url')
    def test_download_transcript_with_metadata(self, mock_validate, mock_extract, mock_get_template,
                                             mock_select_transcript, mock_perform_download):
        """Test download with metadata collection enabled."""
        # Arrange
        mock_validate.return_value = True
        mock_extract.return_value = "test_video_123"
        mock_get_template.return_value = "/output/transcript"
        mock_select_transcript.return_value = {"language_code": "en", "language": "English"}
        mock_perform_download.return_value = {
            'structured': '/output/transcript_structured.json'
        }
        
        # Mock yt-dlp for metadata extraction
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl_instance = Mock()
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
            mock_ydl_instance.extract_info.return_value = self.sample_video_metadata
            
            # Act
            result = download_transcript(
                "https://youtube.com/watch?v=test_video_123",
                include_metadata=True
            )
            
            # Assert
            assert isinstance(result, dict)
            mock_ydl_instance.extract_info.assert_called_once()


class TestGetTranscriptMetadata:
    """Test cases for get_transcript_metadata function."""
    
    @patch('src.yt_transcript_app.trans_core.list_transcript_metadata')
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    @patch('src.yt_transcript_app.trans_core.validate_transcript_url')
    def test_get_transcript_metadata_success(self, mock_validate, mock_extract, mock_list_metadata):
        """Test successful metadata extraction."""
        # Arrange
        mock_validate.return_value = True
        mock_extract.return_value = "test_video_123"
        mock_list_metadata.return_value = [
            {"language_code": "en", "language": "English", "is_generated": False},
            {"language_code": "es", "language": "Spanish", "is_generated": True}
        ]
        
        # Mock yt-dlp for video metadata
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl_instance = Mock()
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
            mock_ydl_instance.extract_info.return_value = {
                "id": "test_video_123",
                "title": "Test Video",
                "duration": 30,
                "uploader": "Test Channel",
                "view_count": 1000
            }
            
            # Act
            result = get_transcript_metadata("https://youtube.com/watch?v=test_video_123")
            
            # Assert
            assert isinstance(result, dict)
            assert "video_metadata" in result
            assert "transcript_metadata" in result
            assert "total_transcripts" in result
            assert "available_languages" in result
            assert result["total_transcripts"] == 2
            assert "en" in result["available_languages"]
            assert "es" in result["available_languages"]
    
    def test_get_transcript_metadata_invalid_url(self):
        """Test metadata extraction with invalid URL."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid YouTube URL"):
            get_transcript_metadata("https://invalid-url.com")
    
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    @patch('src.yt_transcript_app.trans_core.validate_transcript_url')
    def test_get_transcript_metadata_no_video_id(self, mock_validate, mock_extract):
        """Test metadata extraction when video ID cannot be extracted."""
        # Arrange
        mock_validate.return_value = True
        mock_extract.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Could not extract video ID"):
            get_transcript_metadata("https://youtube.com/invalid")


class TestPreviewTranscript:
    """Test cases for preview_transcript function."""
    
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    def test_preview_transcript_success(self, mock_extract):
        """Test successful transcript preview."""
        # Arrange
        mock_extract.return_value = "test_video_123"
        
        # Mock the preview function from get_transcript_list module
        with patch('src.yt_transcript_app.get_transcript_list.preview_transcript') as mock_preview:
            mock_preview.return_value = {
                "preview_text": "[0.00s] Hello world.\n[2.00s] This is a test.",
                "total_entries": 2,
                "language_code": "en"
            }
            
            # Act
            result = preview_transcript("https://youtube.com/watch?v=test_video_123")
            
            # Assert
            assert isinstance(result, dict)
            assert "preview_text" in result
            assert "total_entries" in result
            assert result["total_entries"] == 2
    
    @patch('src.yt_transcript_app.trans_core.extract_video_id')
    def test_preview_transcript_no_video_id(self, mock_extract):
        """Test preview when video ID cannot be extracted."""
        # Arrange
        mock_extract.return_value = None
        
        # Act
        result = preview_transcript("https://youtube.com/invalid")
        
        # Assert
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__])
