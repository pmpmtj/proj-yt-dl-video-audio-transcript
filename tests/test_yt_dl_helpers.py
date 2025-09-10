"""
Unit tests for yt_dl_helpers module.

This module tests the helper functions for path and configuration management
with mocked dependencies to ensure fast, reliable testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any

# Import the functions we're testing
from src.yt_dl_app.yt_dl_helpers import (
    get_downloads_directory,
    get_default_video_settings,
    get_output_template_with_path
)


class TestGetDownloadsDirectory:
    """Test cases for get_downloads_directory function."""
    
    def test_get_downloads_directory_with_config(self, mocker):
        """Test that function uses provided config when available."""
        # Arrange
        config = {
            "download": {
                "download_path": "/custom/downloads"
            }
        }
        expected_path = Path("/custom/downloads")

        # Mock resolve_path to return our expected path
        mock_resolve_path = mocker.patch('src.yt_dl_app.yt_dl_helpers.resolve_path', return_value=expected_path)

        # Act
        result = get_downloads_directory(config)

        # Assert
        assert result == expected_path
        # Verify resolve_path was called with correct arguments
        mock_resolve_path.assert_called_once()
        # Check that the first argument is the download path
        call_args = mock_resolve_path.call_args[0]
        assert call_args[0] == "/custom/downloads"
    
    def test_get_downloads_directory_without_config(self, mocker):
        """Test that function loads config from module when none provided."""
        # Arrange
        expected_path = Path("/default/downloads")

        # Mock the config loading
        mock_get_download_path = mocker.patch('src.yt_dl_app.yt_dl_helpers.get_download_path', return_value="/default/downloads")
        mock_resolve_path = mocker.patch('src.yt_dl_app.yt_dl_helpers.resolve_path', return_value=expected_path)

        # Act
        result = get_downloads_directory()

        # Assert
        assert result == expected_path
        # Verify get_download_path was called
        mock_get_download_path.assert_called_once()
        # Verify resolve_path was called
        mock_resolve_path.assert_called_once()
        # Check that the first argument is the download path
        call_args = mock_resolve_path.call_args[0]
        assert call_args[0] == "/default/downloads"
    
    def test_get_downloads_directory_config_missing_download_key(self, mocker):
        """Test that function falls back to default when config missing download key."""
        # Arrange
        config = {"other": "value"}  # Missing "download" key
        expected_path = Path("/fallback/downloads")

        # Mock resolve_path to return our expected path
        mock_resolve_path = mocker.patch('src.yt_dl_app.yt_dl_helpers.resolve_path', return_value=expected_path)

        # Act
        result = get_downloads_directory(config)

        # Assert
        assert result == expected_path
        # Verify resolve_path was called
        mock_resolve_path.assert_called_once()
        # Check that the first argument is "downloads" as fallback
        call_args = mock_resolve_path.call_args[0]
        assert call_args[0] == "downloads"


class TestGetDefaultVideoSettings:
    """Test cases for get_default_video_settings function."""
    
    def test_get_default_video_settings_with_config(self, mocker):
        """Test that function uses provided config when available."""
        # Arrange
        config = {
            "video": {
                "ext": "webm",
                "quality": "1080p",
                "output_template": "%(title)s - %(uploader)s.%(ext)s",
                "restrict_filenames": True,
                "audio_only": True
            }
        }
        
        # Act
        result = get_default_video_settings(config)
        
        # Assert
        expected = {
            'ext': 'webm',
            'quality': '1080p',
            'output_template': '%(title)s - %(uploader)s.%(ext)s',
            'restrict_filenames': True,
            'audio_only': True
        }
        assert result == expected
    
    def test_get_default_video_settings_without_config(self, mocker):
        """Test that function loads config from module when none provided."""
        # Arrange
        mock_settings = {
            'ext': 'mp4',
            'quality': 'best',
            'output_template': '%(title)s.%(ext)s',
            'restrict_filenames': False,
            'audio_only': False
        }
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_video_settings', return_value=mock_settings)
        
        # Act
        result = get_default_video_settings()
        
        # Assert
        assert result == mock_settings
        # Verify get_video_settings was called
        from src.yt_dl_app.yt_dl_helpers import get_video_settings
        get_video_settings.assert_called_once()
    
    def test_get_default_video_settings_partial_config(self, mocker):
        """Test that function uses defaults for missing config values."""
        # Arrange
        config = {
            "video": {
                "ext": "webm",
                "quality": "720p"
                # Missing other keys
            }
        }
        
        # Act
        result = get_default_video_settings(config)
        
        # Assert
        expected = {
            'ext': 'webm',
            'quality': '720p',
            'output_template': '%(title)s.%(ext)s',  # Default
            'restrict_filenames': False,  # Default
            'audio_only': False  # Default
        }
        assert result == expected


class TestGetOutputTemplateWithPath:
    """Test cases for get_output_template_with_path function."""
    
    def test_get_output_template_with_path_with_custom_template(self, mocker):
        """Test that function uses custom template when provided."""
        # Arrange
        custom_template = "%(title)s - %(uploader)s.%(ext)s"
        expected_path = Path("/downloads")
        expected_result = str(expected_path / custom_template)
        
        # Mock dependencies
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_downloads_directory', return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_helpers.ensure_directory')
        
        # Act
        result = get_output_template_with_path(custom_template=custom_template)
        
        # Assert
        assert result == expected_result
        # Verify ensure_directory was called
        from src.yt_dl_app.yt_dl_helpers import ensure_directory
        ensure_directory.assert_called_once_with(expected_path)
    
    def test_get_output_template_with_path_without_custom_template(self, mocker):
        """Test that function uses config template when no custom template provided."""
        # Arrange
        config = {"video": {"output_template": "%(title)s.%(ext)s"}}
        expected_path = Path("/downloads")
        expected_result = str(expected_path / "%(title)s.%(ext)s")
        
        # Mock dependencies
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_downloads_directory', return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_default_video_settings', 
                    return_value={'output_template': '%(title)s.%(ext)s'})
        mocker.patch('src.yt_dl_app.yt_dl_helpers.ensure_directory')
        
        # Act
        result = get_output_template_with_path(config=config)
        
        # Assert
        assert result == expected_result
        # Verify get_default_video_settings was called
        from src.yt_dl_app.yt_dl_helpers import get_default_video_settings
        get_default_video_settings.assert_called_once_with(config)
        # Verify ensure_directory was called
        from src.yt_dl_app.yt_dl_helpers import ensure_directory
        ensure_directory.assert_called_once_with(expected_path)
    
    def test_get_output_template_with_path_no_config(self, mocker):
        """Test that function loads config from module when none provided."""
        # Arrange
        expected_path = Path("/downloads")
        expected_result = str(expected_path / "%(title)s.%(ext)s")
        
        # Mock dependencies
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_downloads_directory', return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_default_video_settings', 
                    return_value={'output_template': '%(title)s.%(ext)s'})
        mocker.patch('src.yt_dl_app.yt_dl_helpers.ensure_directory')
        
        # Act
        result = get_output_template_with_path()
        
        # Assert
        assert result == expected_result
        # Verify get_downloads_directory was called without config
        from src.yt_dl_app.yt_dl_helpers import get_downloads_directory
        get_downloads_directory.assert_called_once_with(None)
        # Verify get_default_video_settings was called without config
        from src.yt_dl_app.yt_dl_helpers import get_default_video_settings
        get_default_video_settings.assert_called_once_with(None)
    
    def test_get_output_template_with_path_creates_directory(self, mocker):
        """Test that function ensures download directory exists."""
        # Arrange
        expected_path = Path("/downloads")
        
        # Mock dependencies
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_downloads_directory', return_value=expected_path)
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_default_video_settings', 
                    return_value={'output_template': '%(title)s.%(ext)s'})
        mocker.patch('src.yt_dl_app.yt_dl_helpers.ensure_directory')
        
        # Act
        get_output_template_with_path()
        
        # Assert
        # Verify ensure_directory was called with the download path
        from src.yt_dl_app.yt_dl_helpers import ensure_directory
        ensure_directory.assert_called_once_with(expected_path)
    
    def test_get_output_template_with_path_combines_path_and_template(self, mocker):
        """Test that function correctly combines download path with template."""
        # Arrange
        download_path = Path("/custom/downloads")
        template = "%(title)s - %(uploader)s.%(ext)s"
        expected_result = str(download_path / template)
        
        # Mock dependencies
        mocker.patch('src.yt_dl_app.yt_dl_helpers.get_downloads_directory', return_value=download_path)
        mocker.patch('src.yt_dl_app.yt_dl_helpers.ensure_directory')
        
        # Act
        result = get_output_template_with_path(custom_template=template)
        
        # Assert
        assert result == expected_result
