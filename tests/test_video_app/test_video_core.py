"""
Unit tests for video_core module.

This module tests the core YouTube video downloader functionality with mocked dependencies
to ensure fast, reliable testing without actual network calls or file operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path

# Import the functions we're testing
from src.yt_video_app.video_core import (
    download_video_with_audio,
    _load_download_config,
    _get_video_download_settings,
    _create_video_ydl_options,
    _extract_expected_filename,
    _check_file_exists,
    _perform_download,
    extract_basic_meta,
    extract_containers_and_qualities,
    extract_audio_languages,
    extract_subtitle_languages
)


class TestDownloadVideoWithAudio:
    """Test cases for download_video_with_audio function."""
    
    def test_download_video_with_audio_file_already_exists(self, mocker):
        """Test that function returns existing file path when file already exists."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp4"
        
        # Mock the dependencies
        mock_file_checker = Mock(return_value=True)  # File exists
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/downloads/test_video.webm"
        
        # Create a proper context manager mock
        mock_downloader = Mock()
        mock_downloader.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_downloader.return_value.__exit__ = Mock(return_value=None)
        
        # Mock the helper functions
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False, "ext": "mp4", "quality": "best"}}
        mocker.patch('src.yt_video_app.video_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_video_app.video_core._get_video_download_settings', return_value=("/downloads/%(title)s.%(ext)s", False, "mp4", "best"))
        mocker.patch('src.yt_video_app.video_core._create_video_ydl_options', return_value={"format": "best"})
        mocker.patch('src.yt_video_app.video_core._extract_expected_filename', return_value=expected_path)
        mocker.patch('src.yt_video_app.video_core._check_file_exists', return_value=True)
        
        # Act
        result = download_video_with_audio(url, downloader=mock_downloader, file_checker=mock_file_checker)
        
        # Assert
        assert result == expected_path
        mock_ydl_instance.extract_info.assert_called_once_with(url, download=False)
    
    def test_download_video_with_audio_successful_download(self, mocker):
        """Test successful video download."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp4"
        
        # Mock the dependencies
        mock_file_checker = Mock(side_effect=[False, True])  # File doesn't exist, then exists after download
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/downloads/test_video.webm"
        
        # Create a proper context manager mock
        mock_downloader = Mock()
        mock_downloader.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_downloader.return_value.__exit__ = Mock(return_value=None)
        
        # Mock the helper functions
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False, "ext": "mp4", "quality": "best"}}
        mocker.patch('src.yt_video_app.video_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_video_app.video_core._get_video_download_settings', return_value=("/downloads/%(title)s.%(ext)s", False, "mp4", "best"))
        mocker.patch('src.yt_video_app.video_core._create_video_ydl_options', return_value={"format": "best"})
        mocker.patch('src.yt_video_app.video_core._extract_expected_filename', return_value=expected_path)
        mocker.patch('src.yt_video_app.video_core._check_file_exists', side_effect=[False, True])
        mocker.patch('src.yt_video_app.video_core._perform_download', return_value=True)
        
        # Act
        result = download_video_with_audio(url, downloader=mock_downloader, file_checker=mock_file_checker)
        
        # Assert
        assert result == expected_path
        # The download is handled by _perform_download, which is mocked to return True
        # So we don't need to check ydl.download directly
    
    def test_download_video_with_audio_download_failure(self, mocker):
        """Test video download failure."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp4"
        
        # Mock the dependencies
        mock_file_checker = Mock(return_value=False)  # File doesn't exist
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/downloads/test_video.webm"
        
        # Create a proper context manager mock
        mock_downloader = Mock()
        mock_downloader.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_downloader.return_value.__exit__ = Mock(return_value=None)
        
        # Mock the helper functions
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False, "ext": "mp4", "quality": "best"}}
        mocker.patch('src.yt_video_app.video_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_video_app.video_core._get_video_download_settings', return_value=("/downloads/%(title)s.%(ext)s", False, "mp4", "best"))
        mocker.patch('src.yt_video_app.video_core._create_video_ydl_options', return_value={"format": "best"})
        mocker.patch('src.yt_video_app.video_core._extract_expected_filename', return_value=expected_path)
        mocker.patch('src.yt_video_app.video_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_video_app.video_core._perform_download', return_value=False)
        
        # Act
        result = download_video_with_audio(url, downloader=mock_downloader, file_checker=mock_file_checker)
        
        # Assert
        assert result is None


class TestHelperFunctions:
    """Test cases for helper functions."""
    
    def test_load_download_config_with_config(self):
        """Test loading config when config is provided."""
        config = {"video": {"ext": "mp4"}}
        result = _load_download_config(config)
        assert result == config
    
    def test_load_download_config_without_config(self, mocker):
        """Test loading config when no config is provided."""
        mock_config = {"video": {"ext": "mp4"}}
        mocker.patch('src.yt_video_app.video_core.load_config', return_value=mock_config)
        
        result = _load_download_config(None)
        assert result == mock_config
    
    def test_get_video_download_settings(self, mocker):
        """Test getting video download settings."""
        config = {"video": {"ext": "webm", "quality": "720p", "output_template": "%(title)s.%(ext)s", "restrict_filenames": True}}
        mocker.patch('src.yt_video_app.video_core.get_default_video_settings', return_value=config["video"])
        
        result = _get_video_download_settings(config)
        
        # The first element should be a full path, not just a template
        assert result[0].endswith("%(title)s.%(ext)s")
        assert result[1] == True
        assert result[2] == "webm"
        assert result[3] == "720p"
    
    def test_create_video_ydl_options(self):
        """Test creating video yt-dlp options."""
        options = _create_video_ydl_options("/path/%(title)s.%(ext)s", True, "mp4", "1080p")
        
        assert options["outtmpl"] == "/path/%(title)s.%(ext)s"
        assert options["restrictfilenames"] is True
        assert options["merge_output_format"] == "mp4"
        assert "format" in options
        assert "progress_hooks" in options
    
    def test_extract_expected_filename(self):
        """Test extracting expected filename."""
        mock_ydl = Mock()
        mock_ydl.prepare_filename.return_value = "/path/video.webm"
        
        result = _extract_expected_filename(mock_ydl, {}, "mp4")
        
        assert result == "/path/video.mp4"
        mock_ydl.prepare_filename.assert_called_once_with({})
    
    def test_check_file_exists_true(self):
        """Test file existence check when file exists."""
        mock_file_checker = Mock(return_value=True)
        
        result = _check_file_exists("/path/file.mp4", mock_file_checker)
        
        assert result is True
        mock_file_checker.assert_called_once_with("/path/file.mp4")
    
    def test_check_file_exists_false(self):
        """Test file existence check when file doesn't exist."""
        mock_file_checker = Mock(return_value=False)
        
        result = _check_file_exists("/path/file.mp4", mock_file_checker)
        
        assert result is False
        mock_file_checker.assert_called_once_with("/path/file.mp4")
    
    def test_perform_download_success(self):
        """Test successful download."""
        mock_ydl = Mock()
        mock_file_checker = Mock(return_value=True)
        
        result = _perform_download(mock_ydl, "https://youtube.com/watch?v=test", "/path/file.mp4", mock_file_checker)
        
        assert result is True
        mock_ydl.download.assert_called_once_with(["https://youtube.com/watch?v=test"])
        mock_file_checker.assert_called_once_with("/path/file.mp4")
    
    def test_perform_download_failure(self):
        """Test failed download."""
        mock_ydl = Mock()
        mock_file_checker = Mock(return_value=False)
        
        result = _perform_download(mock_ydl, "https://youtube.com/watch?v=test", "/path/file.mp4", mock_file_checker)
        
        assert result is False
        mock_ydl.download.assert_called_once_with(["https://youtube.com/watch?v=test"])
        mock_file_checker.assert_called_once_with("/path/file.mp4")


class TestMetadataFunctions:
    """Test cases for metadata extraction functions."""
    
    def test_extract_basic_meta(self):
        """Test extracting basic metadata."""
        info = {
            "id": "test123",
            "title": "Test Video",
            "duration": 120,
            "uploader": "Test Channel",
            "channel": "Test Channel"
        }
        
        result = extract_basic_meta(info)
        
        assert result["video_id"] == "test123"
        assert result["title"] == "Test Video"
        assert result["duration"] == 120
        assert result["uploader"] == "Test Channel"
        assert result["channel"] == "Test Channel"
    
    def test_extract_containers_and_qualities(self):
        """Test extracting containers and qualities."""
        info = {
            "formats": [
                {"ext": "mp4", "vcodec": "avc1", "height": 1080},
                {"ext": "webm", "vcodec": "vp9", "height": 720},
                {"ext": "mp4", "vcodec": "avc1", "height": 480},
                {"ext": "mp3", "acodec": "mp3", "height": None}
            ]
        }
        
        containers, qualities = extract_containers_and_qualities(info)
        
        assert "mp4" in containers
        assert "webm" in containers
        assert 480 in qualities
        assert 720 in qualities
        assert 1080 in qualities
    
    def test_extract_audio_languages(self):
        """Test extracting audio languages."""
        info = {
            "formats": [
                {"acodec": "mp3", "language": "en"},
                {"acodec": "aac", "language": "es"},
                {"acodec": "opus", "language": "fr"},
                {"acodec": "none", "language": "en"}  # Should be ignored
            ]
        }
        
        result = extract_audio_languages(info)
        
        assert len(result) >= 3  # At least original + found languages
        language_codes = [lang["code"] for lang in result]
        assert "original" in language_codes
        assert "en" in language_codes
        assert "es" in language_codes
        assert "fr" in language_codes
    
    def test_extract_subtitle_languages(self):
        """Test extracting subtitle languages."""
        info = {
            "subtitles": {"en": [], "es": []},
            "automatic_captions": {"fr": [], "de": []}
        }
        
        result = extract_subtitle_languages(info)
        
        assert len(result) == 4
        language_codes = [lang["code"] for lang in result]
        assert "en" in language_codes
        assert "es" in language_codes
        assert "fr" in language_codes
        assert "de" in language_codes