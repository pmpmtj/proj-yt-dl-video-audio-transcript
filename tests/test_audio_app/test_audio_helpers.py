"""
Tests for audio_helpers.py

Tests the audio-specific helper functions.
"""

import pytest
from unittest.mock import patch, Mock
from pathlib import Path

# Import the functions to test
from src.yt_audio_app.audio_helpers import (
    get_audio_downloads_directory,
    get_audio_output_template,
    get_audio_settings,
    validate_audio_url
)


class TestAudioHelpers:
    """Test cases for audio helper functions."""
    
    def test_get_audio_settings(self):
        """Test getting hardcoded audio settings."""
        settings = get_audio_settings()
        
        assert settings['format'] == 'bestaudio/best'
        assert settings['codec'] == 'mp3'
        assert settings['quality'] == '192'
        assert settings['output_template'] == '%(title)s.%(ext)s'
        assert settings['restrict_filenames'] is True
    
    @patch('src.yt_audio_app.audio_helpers.get_script_directories')
    @patch('src.yt_audio_app.audio_helpers.resolve_path')
    def test_get_audio_downloads_directory_default(self, mock_resolve_path, mock_get_script_dirs):
        """Test getting default audio downloads directory."""
        mock_get_script_dirs.return_value = (Path('/script'), Path('/base'))
        mock_resolve_path.return_value = Path('/base/downloads/audio')
        
        result = get_audio_downloads_directory()
        
        assert result == Path('/base/downloads/audio')
        mock_get_script_dirs.assert_called_once()
        mock_resolve_path.assert_called_once_with('downloads/audio', Path('/base'))
    
    @patch('src.yt_audio_app.audio_helpers.get_script_directories')
    @patch('src.yt_audio_app.audio_helpers.resolve_path')
    def test_get_audio_downloads_directory_custom(self, mock_resolve_path, mock_get_script_dirs):
        """Test getting custom audio downloads directory."""
        mock_get_script_dirs.return_value = (Path('/script'), Path('/base'))
        mock_resolve_path.return_value = Path('/custom/path')
        
        result = get_audio_downloads_directory('/custom/path')
        
        assert result == Path('/custom/path')
        mock_resolve_path.assert_called_once_with('/custom/path', Path('/base'))
    
    @patch('src.yt_audio_app.audio_helpers.get_audio_downloads_directory')
    @patch('src.yt_audio_app.audio_helpers.ensure_directory')
    def test_get_audio_output_template_default(self, mock_ensure_dir, mock_get_dir):
        """Test getting default audio output template."""
        mock_get_dir.return_value = Path('/downloads/audio')
        
        result = get_audio_output_template()
        
        assert result == '/downloads/audio/%(title)s.%(ext)s'
        mock_get_dir.assert_called_once_with(None)
        mock_ensure_dir.assert_called_once_with(Path('/downloads/audio'))
    
    @patch('src.yt_audio_app.audio_helpers.get_audio_downloads_directory')
    @patch('src.yt_audio_app.audio_helpers.ensure_directory')
    def test_get_audio_output_template_custom_path(self, mock_ensure_dir, mock_get_dir):
        """Test getting audio output template with custom path."""
        mock_get_dir.return_value = Path('/custom/audio')
        
        result = get_audio_output_template(custom_path='/custom/audio')
        
        assert result == '/custom/audio/%(title)s.%(ext)s'
        mock_get_dir.assert_called_once_with('/custom/audio')
        mock_ensure_dir.assert_called_once_with(Path('/custom/audio'))
    
    @patch('src.yt_audio_app.audio_helpers.get_audio_downloads_directory')
    @patch('src.yt_audio_app.audio_helpers.ensure_directory')
    def test_get_audio_output_template_custom_template(self, mock_ensure_dir, mock_get_dir):
        """Test getting audio output template with custom template."""
        mock_get_dir.return_value = Path('/downloads/audio')
        
        result = get_audio_output_template(custom_template='%(uploader)s - %(title)s.%(ext)s')
        
        assert result == '/downloads/audio/%(uploader)s - %(title)s.%(ext)s'
        mock_get_dir.assert_called_once_with(None)
        mock_ensure_dir.assert_called_once_with(Path('/downloads/audio'))
    
    def test_validate_audio_url_valid_youtube_com(self):
        """Test URL validation with youtube.com URL."""
        url = "https://www.youtube.com/watch?v=test123"
        assert validate_audio_url(url) is True
    
    def test_validate_audio_url_valid_youtu_be(self):
        """Test URL validation with youtu.be URL."""
        url = "https://youtu.be/test123"
        assert validate_audio_url(url) is True
    
    def test_validate_audio_url_valid_m_youtube(self):
        """Test URL validation with m.youtube.com URL."""
        url = "https://m.youtube.com/watch?v=test123"
        assert validate_audio_url(url) is True
    
    def test_validate_audio_url_invalid_empty(self):
        """Test URL validation with empty string."""
        assert validate_audio_url("") is False
    
    def test_validate_audio_url_invalid_none(self):
        """Test URL validation with None."""
        assert validate_audio_url(None) is False
    
    def test_validate_audio_url_invalid_not_string(self):
        """Test URL validation with non-string input."""
        assert validate_audio_url(123) is False
    
    def test_validate_audio_url_invalid_domain(self):
        """Test URL validation with non-YouTube domain."""
        url = "https://vimeo.com/123456"
        assert validate_audio_url(url) is False
    
    def test_validate_audio_url_case_insensitive(self):
        """Test URL validation is case insensitive."""
        url = "https://WWW.YOUTUBE.COM/watch?v=test123"
        assert validate_audio_url(url) is True
