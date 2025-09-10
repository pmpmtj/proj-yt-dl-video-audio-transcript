"""
Unit tests for video_helpers module.

This module tests the video-specific helper functions.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# Import the functions we're testing
from src.yt_video_app.video_helpers import (
    get_downloads_directory,
    get_default_video_settings,
    get_output_template_with_path
)


class TestVideoHelpers:
    """Test cases for video helper functions."""
    
    def test_get_downloads_directory_with_config(self):
        """Test getting downloads directory with config."""
        config = {"download": {"download_path": "/custom/downloads"}}
        
        with patch('src.yt_video_app.video_helpers.get_script_directories', return_value=(Path('/script'), Path('/base'))):
            with patch('src.yt_video_app.video_helpers.resolve_path', return_value=Path('/custom/downloads')) as mock_resolve:
                result = get_downloads_directory(config)
                
                assert result == Path('/custom/downloads')
                mock_resolve.assert_called_once_with('/custom/downloads/video', Path('/base'))
    
    def test_get_downloads_directory_without_config(self):
        """Test getting downloads directory without config."""
        with patch('src.yt_video_app.video_helpers.get_download_path', return_value='./downloads'):
            with patch('src.yt_video_app.video_helpers.get_script_directories', return_value=(Path('/script'), Path('/base'))):
                with patch('src.yt_video_app.video_helpers.resolve_path', return_value=Path('/base/downloads')) as mock_resolve:
                    result = get_downloads_directory(None)
                    
                    assert result == Path('/base/downloads')
                    mock_resolve.assert_called_once_with('./downloads/video', Path('/base'))
    
    def test_get_default_video_settings_with_config(self):
        """Test getting default video settings with config."""
        config = {
            "video": {
                "ext": "webm",
                "quality": "720p",
                "output_template": "%(uploader)s - %(title)s.%(ext)s",
                "restrict_filenames": True
            }
        }
        
        result = get_default_video_settings(config)
        
        assert result["ext"] == "webm"
        assert result["quality"] == "720p"
        assert result["output_template"] == "%(uploader)s - %(title)s.%(ext)s"
        assert result["restrict_filenames"] is True
    
    def test_get_default_video_settings_without_config(self):
        """Test getting default video settings without config."""
        with patch('src.yt_video_app.video_helpers.get_video_settings', return_value={
            "ext": "mp4",
            "quality": "best",
            "output_template": "%(title)s.%(ext)s",
            "restrict_filenames": False
        }) as mock_get_settings:
            result = get_default_video_settings(None)
            
            assert result["ext"] == "mp4"
            assert result["quality"] == "best"
            assert result["output_template"] == "%(title)s.%(ext)s"
            assert result["restrict_filenames"] is False
            mock_get_settings.assert_called_once()
    
    def test_get_default_video_settings_partial_config(self):
        """Test getting default video settings with partial config."""
        config = {
            "video": {
                "ext": "webm"
                # Missing other fields
            }
        }
        
        result = get_default_video_settings(config)
        
        assert result["ext"] == "webm"
        assert result["quality"] == "best"  # Default
        assert result["output_template"] == "%(title)s.%(ext)s"  # Default
        assert result["restrict_filenames"] is False  # Default
    
    def test_get_output_template_with_path_with_config(self):
        """Test getting output template with path using config."""
        config = {"download": {"download_path": "/custom/downloads"}}
        
        with patch('src.yt_video_app.video_helpers.get_downloads_directory', return_value=Path('/custom/downloads')):
            with patch('src.yt_video_app.video_helpers.get_default_video_settings', return_value={"output_template": "%(title)s.%(ext)s"}):
                with patch('src.yt_video_app.video_helpers.ensure_directory') as mock_ensure:
                    result = get_output_template_with_path(config)
                    
                    assert result.replace('\\', '/') == '/custom/downloads/%(title)s.%(ext)s'
                    mock_ensure.assert_called_once_with(Path('/custom/downloads'))
    
    def test_get_output_template_with_path_without_config(self):
        """Test getting output template with path without config."""
        with patch('src.yt_video_app.video_helpers.get_downloads_directory', return_value=Path('/default/downloads')):
            with patch('src.yt_video_app.video_helpers.get_default_video_settings', return_value={"output_template": "%(title)s.%(ext)s"}):
                with patch('src.yt_video_app.video_helpers.ensure_directory') as mock_ensure:
                    result = get_output_template_with_path(None)
                    
                    assert result.replace('\\', '/') == '/default/downloads/%(title)s.%(ext)s'
                    mock_ensure.assert_called_once_with(Path('/default/downloads'))
    
    def test_get_output_template_with_path_custom_template(self):
        """Test getting output template with custom template."""
        config = {"download": {"download_path": "/custom/downloads"}}
        custom_template = "%(uploader)s - %(title)s.%(ext)s"
        
        with patch('src.yt_video_app.video_helpers.get_downloads_directory', return_value=Path('/custom/downloads')):
            with patch('src.yt_video_app.video_helpers.ensure_directory') as mock_ensure:
                result = get_output_template_with_path(config, custom_template)
                
                assert result.replace('\\', '/') == '/custom/downloads/%(uploader)s - %(title)s.%(ext)s'
                mock_ensure.assert_called_once_with(Path('/custom/downloads'))
    
    def test_get_output_template_with_path_ensure_directory_called(self):
        """Test that ensure_directory is called with the correct path."""
        config = {"download": {"download_path": "/test/downloads"}}
        
        with patch('src.yt_video_app.video_helpers.get_downloads_directory', return_value=Path('/test/downloads')):
            with patch('src.yt_video_app.video_helpers.get_default_video_settings', return_value={"output_template": "%(title)s.%(ext)s"}):
                with patch('src.yt_video_app.video_helpers.ensure_directory') as mock_ensure:
                    get_output_template_with_path(config)
                    
                    mock_ensure.assert_called_once_with(Path('/test/downloads'))