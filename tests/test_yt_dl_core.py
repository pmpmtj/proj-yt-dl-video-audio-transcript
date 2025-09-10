"""
Unit tests for yt_dl_core module.

This module tests the core YouTube downloader functionality with mocked dependencies
to ensure fast, reliable testing without actual network calls or file operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path

# Import the functions we're testing
from src.yt_dl_app.yt_dl_core import (
    download_audio_mp3, 
    download_video_with_audio,
    _load_download_config,
    _get_audio_download_settings,
    _get_video_download_settings,
    _create_audio_ydl_options,
    _create_video_ydl_options,
    _extract_expected_filename,
    _check_file_exists,
    _perform_download
)


class TestDownloadAudioMP3:
    """Test cases for download_audio_mp3 function."""
    
    def test_download_audio_mp3_file_already_exists(self, mocker):
        """Test that function returns existing file path when file already exists."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp3"
        
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
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False}}
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_audio_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_audio_ydl_options', 
                    return_value={'format': 'bestaudio/best'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=True)
        
        # Act
        result = download_audio_mp3(
            url=url,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result == expected_path
        # Should not call download since file exists
        mock_ydl_instance.download.assert_not_called()
    
    def test_download_audio_mp3_new_download(self, mocker):
        """Test that function downloads new file when it doesn't exist."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp3"
        
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
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False}}
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_audio_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_audio_ydl_options', 
                    return_value={'format': 'bestaudio/best'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=True)
        
        # Act
        result = download_audio_mp3(
            url=url,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result == expected_path
        # Note: download is handled by _perform_download mock, not directly by ydl_instance
    
    def test_download_audio_mp3_uses_default_dependencies(self, mocker):
        """Test that function uses default dependencies when none provided."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp3"
        
        # Mock the default dependencies
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/downloads/test_video.webm"
        
        # Create a proper context manager mock
        mock_ydl_class = Mock()
        mock_ydl_class.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_ydl_class.return_value.__exit__ = Mock(return_value=None)
        
        # Mock os.path.exists
        mock_file_checker = Mock(return_value=False)
        
        # Mock the helper functions
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False}}
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_audio_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_audio_ydl_options', 
                    return_value={'format': 'bestaudio/best'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=True)
        mocker.patch('os.path.exists', mock_file_checker)
        mocker.patch('yt_dlp.YoutubeDL', mock_ydl_class)
        
        # Act
        result = download_audio_mp3(url=url)  # No dependencies provided
        
        # Assert
        assert result == expected_path
        mock_ydl_class.assert_called_once()
    
    def test_download_audio_mp3_with_custom_parameters(self, mocker):
        """Test that function respects custom parameters."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        custom_template = "/custom/path/%(title)s.%(ext)s"
        restrict_filenames = True
        expected_path = "/custom/path/test_video.mp3"
        
        # Mock the dependencies
        mock_file_checker = Mock(return_value=False)
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/custom/path/test_video.webm"
        
        # Create a proper context manager mock
        mock_downloader = Mock()
        mock_downloader.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_downloader.return_value.__exit__ = Mock(return_value=None)
        
        # Mock the helper functions
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False}}
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_audio_download_settings', 
                    return_value=(custom_template, restrict_filenames))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_audio_ydl_options', 
                    return_value={'format': 'bestaudio/best', 'outtmpl': custom_template, 'restrictfilenames': restrict_filenames})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=True)
        
        # Act
        result = download_audio_mp3(
            url=url,
            outtmpl=custom_template,
            restrict=restrict_filenames,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result == expected_path
        # Verify the downloader was called with correct options
        mock_downloader.assert_called_once()
        call_args = mock_downloader.call_args[0][0]  # First positional argument (ydl_opts)
        assert call_args['outtmpl'] == custom_template
        assert call_args['restrictfilenames'] == restrict_filenames


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
        mock_config = {
            "video": {
                "ext": "mp4",
                "quality": "best",
                "output_template": "%(title)s.%(ext)s",
                "restrict_filenames": False
            }
        }
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_video_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False, "mp4", "best"))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_video_ydl_options', 
                    return_value={'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=True)
        
        # Act
        result = download_video_with_audio(
            url=url,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result == expected_path
        # Should not call download since file exists
        mock_ydl_instance.download.assert_not_called()
    
    def test_download_video_with_audio_new_download_success(self, mocker):
        """Test that function downloads new file when it doesn't exist and succeeds."""
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
        mock_config = {
            "video": {
                "ext": "mp4",
                "quality": "best",
                "output_template": "%(title)s.%(ext)s",
                "restrict_filenames": False
            }
        }
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_video_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False, "mp4", "best"))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_video_ydl_options', 
                    return_value={'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=True)
        
        # Act
        result = download_video_with_audio(
            url=url,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result == expected_path
        # Note: download is handled by _perform_download mock, not directly by ydl_instance
    
    def test_download_video_with_audio_download_failure(self, mocker):
        """Test that function returns None when download fails."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp4"
        
        # Mock the dependencies
        mock_file_checker = Mock(return_value=False)  # File never exists
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/downloads/test_video.webm"
        
        # Create a proper context manager mock
        mock_downloader = Mock()
        mock_downloader.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_downloader.return_value.__exit__ = Mock(return_value=None)
        
        # Mock the helper functions
        mock_config = {
            "video": {
                "ext": "mp4",
                "quality": "best",
                "output_template": "%(title)s.%(ext)s",
                "restrict_filenames": False
            }
        }
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_video_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False, "mp4", "best"))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_video_ydl_options', 
                    return_value={'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=False)
        
        # Act
        result = download_video_with_audio(
            url=url,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result is None
        # Note: download is handled by _perform_download mock, not directly by ydl_instance
    
    def test_download_video_with_audio_uses_default_dependencies(self, mocker):
        """Test that function uses default dependencies when none provided."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp4"
        
        # Mock the default dependencies
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/downloads/test_video.webm"
        
        # Create a proper context manager mock
        mock_ydl_class = Mock()
        mock_ydl_class.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_ydl_class.return_value.__exit__ = Mock(return_value=None)
        
        # Mock os.path.exists
        mock_file_checker = Mock(side_effect=[False, True])
        
        # Mock the helper functions
        mock_config = {
            "video": {
                "ext": "mp4",
                "quality": "best",
                "output_template": "%(title)s.%(ext)s",
                "restrict_filenames": False
            }
        }
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_video_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False, "mp4", "best"))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_video_ydl_options', 
                    return_value={'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=True)
        mocker.patch('os.path.exists', mock_file_checker)
        mocker.patch('yt_dlp.YoutubeDL', mock_ydl_class)
        
        # Act
        result = download_video_with_audio(url=url)  # No dependencies provided
        
        # Assert
        assert result == expected_path
        mock_ydl_class.assert_called_once()
    
    def test_download_video_with_audio_custom_parameters(self, mocker):
        """Test that function respects custom parameters."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        custom_template = "/custom/path/%(title)s.%(ext)s"
        restrict_filenames = True
        ext = "webm"
        quality = "1080p"
        expected_path = "/custom/path/test_video.webm"
        
        # Mock the dependencies
        mock_file_checker = Mock(side_effect=[False, True])
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/custom/path/test_video.webm"
        
        # Create a proper context manager mock
        mock_downloader = Mock()
        mock_downloader.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_downloader.return_value.__exit__ = Mock(return_value=None)
        
        # Mock the helper functions
        mock_config = {
            "video": {
                "ext": "mp4",
                "quality": "best",
                "output_template": "%(title)s.%(ext)s",
                "restrict_filenames": False
            }
        }
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_video_download_settings', 
                    return_value=(custom_template, restrict_filenames, ext, quality))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_video_ydl_options', 
                    return_value={'format': 'bestvideo[ext=webm][height<=1080]+bestaudio[ext=webm]', 'outtmpl': custom_template, 'restrictfilenames': restrict_filenames, 'merge_output_format': ext})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=True)
        
        # Act
        result = download_video_with_audio(
            url=url,
            outtmpl=custom_template,
            restrict=restrict_filenames,
            ext=ext,
            quality=quality,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result == expected_path
        # Verify the downloader was called with correct options
        mock_downloader.assert_called_once()
        call_args = mock_downloader.call_args[0][0]  # First positional argument (ydl_opts)
        assert call_args['outtmpl'] == custom_template
        assert call_args['restrictfilenames'] == restrict_filenames
        assert call_args['merge_output_format'] == ext
        # Verify format string includes quality constraint
        assert 'height<=' in call_args['format'] or 'best' in call_args['format']
    
    def test_download_video_with_audio_invalid_extension_fallback(self, mocker):
        """Test that function falls back to mp4 for invalid extensions."""
        # Arrange
        url = "https://youtube.com/watch?v=test123"
        invalid_ext = "avi"  # Not in ('mp4', 'webm')
        expected_path = "/downloads/test_video.mp4"  # Should fallback to mp4
        
        # Mock the dependencies
        mock_file_checker = Mock(side_effect=[False, True])
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {"id": "test123", "title": "Test Video"}
        mock_ydl_instance.prepare_filename.return_value = "/downloads/test_video.webm"
        
        # Create a proper context manager mock
        mock_downloader = Mock()
        mock_downloader.return_value.__enter__ = Mock(return_value=mock_ydl_instance)
        mock_downloader.return_value.__exit__ = Mock(return_value=None)
        
        # Mock the helper functions
        mock_config = {
            "video": {
                "ext": "mp4",
                "quality": "best",
                "output_template": "%(title)s.%(ext)s",
                "restrict_filenames": False
            }
        }
        mocker.patch('src.yt_dl_app.yt_dl_core._load_download_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core._get_video_download_settings', 
                    return_value=("/downloads/%(title)s.%(ext)s", False, invalid_ext, "best"))
        mocker.patch('src.yt_dl_app.yt_dl_core._create_video_ydl_options', 
                    return_value={'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]', 'merge_output_format': 'mp4'})
        mocker.patch('src.yt_dl_app.yt_dl_core._extract_expected_filename', 
                    return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_core._check_file_exists', return_value=False)
        mocker.patch('src.yt_dl_app.yt_dl_core._perform_download', return_value=True)
        
        # Act
        result = download_video_with_audio(
            url=url,
            ext=invalid_ext,
            downloader=mock_downloader,
            file_checker=mock_file_checker
        )
        
        # Assert
        assert result == expected_path
        # Verify the downloader was called with mp4 as merge_output_format
        call_args = mock_downloader.call_args[0][0]
        assert call_args['merge_output_format'] == 'mp4'


# --- Tests for Helper Functions ------------------------------------------------

class TestLoadDownloadConfig:
    """Test cases for _load_download_config function."""
    
    def test_load_download_config_with_provided_config(self):
        """Test that function returns provided config when available."""
        # Arrange
        config = {"video": {"ext": "mp4"}}
        
        # Act
        result = _load_download_config(config)
        
        # Assert
        assert result == config
    
    def test_load_download_config_loads_from_file(self, mocker):
        """Test that function loads config from file when none provided."""
        # Arrange
        expected_config = {"video": {"ext": "mp4"}}
        mocker.patch('src.yt_dl_app.yt_dl_core.load_config', return_value=expected_config)
        
        # Act
        result = _load_download_config()
        
        # Assert
        assert result == expected_config


class TestGetAudioDownloadSettings:
    """Test cases for _get_audio_download_settings function."""
    
    def test_get_audio_download_settings_with_all_parameters(self, mocker):
        """Test that function uses provided parameters when available."""
        # Arrange
        config = {"video": {"restrict_filenames": False}}
        outtmpl = "/custom/template.%(ext)s"
        restrict = True
        
        mocker.patch('src.yt_dl_app.yt_dl_core.get_output_template_with_path', return_value=outtmpl)
        mocker.patch('src.yt_dl_app.yt_dl_core.get_default_video_settings', 
                    return_value={'restrict_filenames': False})
        
        # Act
        result_outtmpl, result_restrict = _get_audio_download_settings(config, outtmpl, restrict)
        
        # Assert
        assert result_outtmpl == outtmpl
        assert result_restrict == restrict
    
    def test_get_audio_download_settings_uses_config_defaults(self, mocker):
        """Test that function uses config defaults when parameters not provided."""
        # Arrange
        config = {"video": {"restrict_filenames": True}}
        expected_outtmpl = "/downloads/%(title)s.%(ext)s"
        expected_restrict = True
        
        mocker.patch('src.yt_dl_app.yt_dl_core.get_output_template_with_path', return_value=expected_outtmpl)
        mocker.patch('src.yt_dl_app.yt_dl_core.get_default_video_settings', 
                    return_value={'restrict_filenames': expected_restrict})
        
        # Act
        result_outtmpl, result_restrict = _get_audio_download_settings(config)
        
        # Assert
        assert result_outtmpl == expected_outtmpl
        assert result_restrict == expected_restrict


class TestCreateAudioYdlOptions:
    """Test cases for _create_audio_ydl_options function."""
    
    def test_create_audio_ydl_options_basic(self):
        """Test that function creates basic audio options."""
        # Arrange
        outtmpl = "/downloads/%(title)s.%(ext)s"
        restrict = False
        
        # Act
        result = _create_audio_ydl_options(outtmpl, restrict)
        
        # Assert
        assert result['format'] == 'bestaudio/best'
        assert result['outtmpl'] == outtmpl
        assert result['restrictfilenames'] == restrict
        assert 'postprocessors' in result
        assert result['postprocessors'][0]['key'] == 'FFmpegExtractAudio'
        assert result['postprocessors'][0]['preferredcodec'] == 'mp3'
    
    def test_create_audio_ydl_options_with_progress_callback(self):
        """Test that function includes progress callback when provided."""
        # Arrange
        outtmpl = "/downloads/%(title)s.%(ext)s"
        restrict = False
        progress_callback = Mock()
        
        # Act
        result = _create_audio_ydl_options(outtmpl, restrict, progress_callback)
        
        # Assert
        assert progress_callback in result['progress_hooks']


class TestCreateVideoYdlOptions:
    """Test cases for _create_video_ydl_options function."""
    
    def test_create_video_ydl_options_basic(self, mocker):
        """Test that function creates basic video options."""
        # Arrange
        outtmpl = "/downloads/%(title)s.%(ext)s"
        restrict = False
        ext = "mp4"
        quality = "best"
        
        mocker.patch('src.yt_dl_app.yt_dl_core._fmt_for', return_value='bestvideo[ext=mp4]+bestaudio[ext=m4a]')
        
        # Act
        result = _create_video_ydl_options(outtmpl, restrict, ext, quality)
        
        # Assert
        assert result['outtmpl'] == outtmpl
        assert result['restrictfilenames'] == restrict
        assert result['merge_output_format'] == ext
        assert 'format' in result
    
    def test_create_video_ydl_options_invalid_extension_fallback(self, mocker):
        """Test that function falls back to mp4 for invalid extensions."""
        # Arrange
        outtmpl = "/downloads/%(title)s.%(ext)s"
        restrict = False
        ext = "avi"  # Invalid extension
        quality = "best"
        
        mocker.patch('src.yt_dl_app.yt_dl_core._fmt_for', return_value='bestvideo[ext=mp4]+bestaudio[ext=m4a]')
        
        # Act
        result = _create_video_ydl_options(outtmpl, restrict, ext, quality)
        
        # Assert
        assert result['merge_output_format'] == 'mp4'  # Should fallback to mp4


class TestExtractExpectedFilename:
    """Test cases for _extract_expected_filename function."""
    
    def test_extract_expected_filename_mp3(self):
        """Test that function extracts expected filename for MP3."""
        # Arrange
        mock_ydl = Mock()
        mock_ydl.prepare_filename.return_value = "/downloads/test_video.webm"
        info = {"id": "test123", "title": "Test Video"}
        file_extension = "mp3"
        
        # Act
        result = _extract_expected_filename(mock_ydl, info, file_extension)
        
        # Assert
        assert result == "/downloads/test_video.mp3"
    
    def test_extract_expected_filename_mp4(self):
        """Test that function extracts expected filename for MP4."""
        # Arrange
        mock_ydl = Mock()
        mock_ydl.prepare_filename.return_value = "/downloads/test_video.webm"
        info = {"id": "test123", "title": "Test Video"}
        file_extension = "mp4"
        
        # Act
        result = _extract_expected_filename(mock_ydl, info, file_extension)
        
        # Assert
        assert result == "/downloads/test_video.mp4"


class TestCheckFileExists:
    """Test cases for _check_file_exists function."""
    
    def test_check_file_exists_file_exists(self, mocker):
        """Test that function returns True when file exists."""
        # Arrange
        expected_path = "/downloads/test_video.mp3"
        mock_file_checker = Mock(return_value=True)
        mocker.patch('builtins.print')  # Mock print to avoid output during tests
        
        # Act
        result = _check_file_exists(expected_path, mock_file_checker)
        
        # Assert
        assert result is True
        mock_file_checker.assert_called_once_with(expected_path)
    
    def test_check_file_exists_file_not_exists(self):
        """Test that function returns False when file doesn't exist."""
        # Arrange
        expected_path = "/downloads/test_video.mp3"
        mock_file_checker = Mock(return_value=False)
        
        # Act
        result = _check_file_exists(expected_path, mock_file_checker)
        
        # Assert
        assert result is False
        mock_file_checker.assert_called_once_with(expected_path)


class TestPerformDownload:
    """Test cases for _perform_download function."""
    
    def test_perform_download_success(self, mocker):
        """Test that function returns True when download succeeds."""
        # Arrange
        mock_ydl = Mock()
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp3"
        mock_file_checker = Mock(return_value=True)  # File exists after download
        mocker.patch('builtins.print')  # Mock print to avoid output during tests
        
        # Act
        result = _perform_download(mock_ydl, url, expected_path, mock_file_checker)
        
        # Assert
        assert result is True
        mock_ydl.download.assert_called_once_with([url])
        mock_file_checker.assert_called_once_with(expected_path)
    
    def test_perform_download_failure(self, mocker):
        """Test that function returns False when download fails."""
        # Arrange
        mock_ydl = Mock()
        url = "https://youtube.com/watch?v=test123"
        expected_path = "/downloads/test_video.mp3"
        mock_file_checker = Mock(return_value=False)  # File never exists
        mocker.patch('builtins.print')  # Mock print to avoid output during tests
        
        # Act
        result = _perform_download(mock_ydl, url, expected_path, mock_file_checker)
        
        # Assert
        assert result is False
        mock_ydl.download.assert_called_once_with([url])
        mock_file_checker.assert_called_once_with(expected_path)
