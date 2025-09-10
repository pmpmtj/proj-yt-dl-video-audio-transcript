"""
Tests for audio_core.py

Tests the core audio download functionality with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

# Import the functions to test
from src.yt_audio_app.audio_core import (
    download_audio_mp3,
    get_audio_metadata,
    create_audio_ydl_options,
    extract_expected_audio_filename,
    check_audio_file_exists,
    perform_audio_download,
    default_audio_progress_hook
)


class TestAudioCore:
    """Test cases for audio core functionality."""
    
    def test_create_audio_ydl_options(self):
        """Test creation of yt-dlp options for audio download."""
        output_template = "/path/to/%(title)s.%(ext)s"
        
        options = create_audio_ydl_options(output_template)
        
        assert options['format'] == 'bestaudio/best'
        assert options['outtmpl'] == output_template
        assert options['restrictfilenames'] is True
        assert 'postprocessors' in options
        assert options['postprocessors'][0]['key'] == 'FFmpegExtractAudio'
        assert options['postprocessors'][0]['preferredcodec'] == 'mp3'
        assert options['postprocessors'][0]['preferredquality'] == '192'
        assert 'progress_hooks' in options
        assert len(options['progress_hooks']) == 1
    
    def test_create_audio_ydl_options_with_callback(self):
        """Test creation of yt-dlp options with custom progress callback."""
        output_template = "/path/to/%(title)s.%(ext)s"
        custom_callback = Mock()
        
        options = create_audio_ydl_options(output_template, custom_callback)
        
        assert options['progress_hooks'] == [custom_callback]
    
    def test_extract_expected_audio_filename(self):
        """Test extraction of expected audio filename."""
        mock_ydl = Mock()
        mock_ydl.prepare_filename.return_value = "/path/to/video.mp4"
        
        info = {'title': 'Test Video'}
        expected_path = extract_expected_audio_filename(mock_ydl, info)
        
        assert expected_path == "/path/to/video.mp3"
        mock_ydl.prepare_filename.assert_called_once_with(info)
    
    def test_check_audio_file_exists_true(self):
        """Test file existence check when file exists."""
        file_checker = Mock(return_value=True)
        expected_path = "/path/to/audio.mp3"
        
        result = check_audio_file_exists(expected_path, file_checker)
        
        assert result is True
        file_checker.assert_called_once_with(expected_path)
    
    def test_check_audio_file_exists_false(self):
        """Test file existence check when file doesn't exist."""
        file_checker = Mock(return_value=False)
        expected_path = "/path/to/audio.mp3"
        
        result = check_audio_file_exists(expected_path, file_checker)
        
        assert result is False
        file_checker.assert_called_once_with(expected_path)
    
    def test_perform_audio_download_success(self):
        """Test successful audio download."""
        mock_ydl = Mock()
        mock_file_checker = Mock(return_value=True)
        url = "https://youtube.com/watch?v=test"
        expected_path = "/path/to/audio.mp3"
        
        result = perform_audio_download(mock_ydl, url, expected_path, mock_file_checker)
        
        assert result is True
        mock_ydl.download.assert_called_once_with([url])
        mock_file_checker.assert_called_once_with(expected_path)
    
    def test_perform_audio_download_failure(self):
        """Test failed audio download."""
        mock_ydl = Mock()
        mock_file_checker = Mock(return_value=False)
        url = "https://youtube.com/watch?v=test"
        expected_path = "/path/to/audio.mp3"
        
        result = perform_audio_download(mock_ydl, url, expected_path, mock_file_checker)
        
        assert result is False
        mock_ydl.download.assert_called_once_with([url])
        mock_file_checker.assert_called_once_with(expected_path)
    
    def test_default_audio_progress_hook_downloading(self):
        """Test progress hook during download."""
        progress_data = {
            'status': 'downloading',
            '_percent_str': '50.0%'
        }
        
        # Should not raise any exceptions
        default_audio_progress_hook(progress_data)
    
    def test_default_audio_progress_hook_finished(self):
        """Test progress hook when finished."""
        progress_data = {
            'status': 'finished'
        }
        
        # Should not raise any exceptions
        default_audio_progress_hook(progress_data)
    
    @patch('src.yt_audio_app.audio_core.get_audio_output_template')
    @patch('src.yt_audio_app.audio_core.validate_audio_url')
    @patch('src.yt_audio_app.audio_core.create_audio_ydl_options')
    @patch('src.yt_audio_app.audio_core.extract_expected_audio_filename')
    @patch('src.yt_audio_app.audio_core.check_audio_file_exists')
    @patch('src.yt_audio_app.audio_core.perform_audio_download')
    def test_download_audio_mp3_success(self, mock_perform_download, mock_check_exists,
                                       mock_extract_filename, mock_create_options,
                                       mock_validate_url, mock_get_template):
        """Test successful audio download."""
        # Setup mocks
        mock_validate_url.return_value = True
        mock_get_template.return_value = "/path/to/%(title)s.%(ext)s"
        mock_create_options.return_value = {'format': 'bestaudio/best'}
        mock_extract_filename.return_value = "/path/to/audio.mp3"
        mock_check_exists.return_value = False
        mock_perform_download.return_value = True
        
        # Mock yt-dlp
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {'title': 'Test Video'}
        mock_ydl_class = Mock(return_value=mock_ydl_instance)
        
        url = "https://youtube.com/watch?v=test"
        result = download_audio_mp3(url, downloader=mock_ydl_class)
        
        assert result == "/path/to/audio.mp3"
        mock_validate_url.assert_called_once_with(url)
        mock_get_template.assert_called_once_with(None, None)
        mock_create_options.assert_called_once()
        mock_ydl_instance.extract_info.assert_called_once_with(url, download=False)
        mock_extract_filename.assert_called_once_with(mock_ydl_instance, {'title': 'Test Video'})
        mock_check_exists.assert_called_once_with("/path/to/audio.mp3", os.path.exists)
        mock_perform_download.assert_called_once()
    
    def test_download_audio_mp3_invalid_url(self):
        """Test audio download with invalid URL."""
        with patch('src.yt_audio_app.audio_core.validate_audio_url', return_value=False):
            with pytest.raises(ValueError, match="Invalid YouTube URL"):
                download_audio_mp3("invalid_url")
    
    @patch('src.yt_audio_app.audio_core.validate_audio_url')
    def test_get_audio_metadata_success(self, mock_validate_url):
        """Test successful metadata extraction."""
        mock_validate_url.return_value = True
        
        mock_ydl_instance = Mock()
        mock_ydl_instance.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Video',
            'duration': 120,
            'uploader': 'Test Channel',
            'channel': 'Test Channel',
            'description': 'Test description',
            'view_count': 1000,
            'upload_date': '20231201'
        }
        mock_ydl_class = Mock(return_value=mock_ydl_instance)
        
        url = "https://youtube.com/watch?v=test"
        result = get_audio_metadata(url, downloader=mock_ydl_class)
        
        assert result['video_id'] == 'test123'
        assert result['title'] == 'Test Video'
        assert result['duration'] == 120
        assert result['uploader'] == 'Test Channel'
        assert result['channel'] == 'Test Channel'
        assert result['description'] == 'Test description'
        assert result['view_count'] == 1000
        assert result['upload_date'] == '20231201'
    
    def test_get_audio_metadata_invalid_url(self):
        """Test metadata extraction with invalid URL."""
        with patch('src.yt_audio_app.audio_core.validate_audio_url', return_value=False):
            with pytest.raises(ValueError, match="Invalid YouTube URL"):
                get_audio_metadata("invalid_url")
