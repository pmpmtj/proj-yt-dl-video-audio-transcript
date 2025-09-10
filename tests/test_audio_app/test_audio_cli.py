"""
Tests for audio_cli.py

Tests the audio CLI interface functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import argparse

# Import the functions to test
from src.yt_audio_app.audio_cli import (
    parse_audio_args,
    AudioCLIController,
    main
)


class TestAudioCLI:
    """Test cases for audio CLI functionality."""
    
    def test_parse_audio_args_basic(self):
        """Test parsing basic audio CLI arguments."""
        with patch('sys.argv', ['audio_cli.py', 'https://youtube.com/watch?v=test']):
            args = parse_audio_args()
            
            assert args.url == 'https://youtube.com/watch?v=test'
            assert args.output_dir is None
            assert args.template is None
            assert args.metadata is False
            assert args.quiet is False
    
    def test_parse_audio_args_with_options(self):
        """Test parsing audio CLI arguments with options."""
        with patch('sys.argv', [
            'audio_cli.py', 
            'https://youtube.com/watch?v=test',
            '--output-dir', '/custom/path',
            '--template', '%(uploader)s - %(title)s.%(ext)s',
            '--metadata',
            '--quiet'
        ]):
            args = parse_audio_args()
            
            assert args.url == 'https://youtube.com/watch?v=test'
            assert args.output_dir == '/custom/path'
            assert args.template == '%(uploader)s - %(title)s.%(ext)s'
            assert args.metadata is True
            assert args.quiet is True
    
    def test_audio_cli_controller_init_defaults(self):
        """Test AudioCLIController initialization with defaults."""
        controller = AudioCLIController()
        
        assert controller.audio_downloader is not None
        assert controller.metadata_extractor is not None
        assert controller.progress_hook is not None
    
    def test_audio_cli_controller_init_custom(self):
        """Test AudioCLIController initialization with custom dependencies."""
        mock_downloader = Mock()
        mock_extractor = Mock()
        mock_hook = Mock()
        
        controller = AudioCLIController(
            audio_downloader=mock_downloader,
            metadata_extractor=mock_extractor,
            progress_hook=mock_hook
        )
        
        assert controller.audio_downloader == mock_downloader
        assert controller.metadata_extractor == mock_extractor
        assert controller.progress_hook == mock_hook
    
    @patch('src.yt_audio_app.audio_cli.get_audio_output_template')
    def test_handle_audio_download_default_template(self, mock_get_template):
        """Test audio download with default template."""
        mock_get_template.return_value = '/downloads/audio/%(title)s.%(ext)s'
        mock_downloader = Mock(return_value='/downloads/audio/test.mp3')
        
        controller = AudioCLIController(audio_downloader=mock_downloader)
        
        result = controller.handle_audio_download(
            'https://youtube.com/watch?v=test',
            None,  # output_dir
            None,  # template
            False  # quiet
        )
        
        assert result == '/downloads/audio/test.mp3'
        mock_get_template.assert_called_once_with(None, None)
        mock_downloader.assert_called_once()
    
    @patch('src.yt_audio_app.audio_cli.get_audio_output_template')
    def test_handle_audio_download_custom_template(self, mock_get_template):
        """Test audio download with custom template."""
        mock_get_template.return_value = '/custom/path/%(uploader)s - %(title)s.%(ext)s'
        mock_downloader = Mock(return_value='/custom/path/artist - song.mp3')
        
        controller = AudioCLIController(audio_downloader=mock_downloader)
        
        result = controller.handle_audio_download(
            'https://youtube.com/watch?v=test',
            '/custom/path',  # output_dir
            '%(uploader)s - %(title)s.%(ext)s',  # template
            False  # quiet
        )
        
        assert result == '/custom/path/artist - song.mp3'
        mock_get_template.assert_called_once_with('/custom/path', '%(uploader)s - %(title)s.%(ext)s')
        mock_downloader.assert_called_once()
    
    @patch('src.yt_audio_app.audio_cli.get_audio_output_template')
    def test_handle_audio_download_quiet(self, mock_get_template):
        """Test audio download with quiet mode."""
        mock_get_template.return_value = '/downloads/audio/%(title)s.%(ext)s'
        mock_downloader = Mock(return_value='/downloads/audio/test.mp3')
        
        controller = AudioCLIController(audio_downloader=mock_downloader)
        
        result = controller.handle_audio_download(
            'https://youtube.com/watch?v=test',
            None,  # output_dir
            None,  # template
            True   # quiet
        )
        
        assert result == '/downloads/audio/test.mp3'
        # Check that progress callback is None when quiet
        call_args = mock_downloader.call_args
        assert call_args[1]['progress_callback'] is None
    
    def test_handle_metadata_request_success(self):
        """Test successful metadata request."""
        mock_metadata = {
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'duration': 120,
            'view_count': 1000
        }
        mock_extractor = Mock(return_value=mock_metadata)
        
        controller = AudioCLIController(metadata_extractor=mock_extractor)
        
        # Should not raise any exceptions
        controller.handle_metadata_request('https://youtube.com/watch?v=test')
        
        mock_extractor.assert_called_once_with('https://youtube.com/watch?v=test')
    
    def test_handle_metadata_request_failure(self):
        """Test metadata request failure."""
        mock_extractor = Mock(side_effect=Exception('Metadata extraction failed'))
        
        controller = AudioCLIController(metadata_extractor=mock_extractor)
        
        with pytest.raises(Exception, match='Metadata extraction failed'):
            controller.handle_metadata_request('https://youtube.com/watch?v=test')
    
    def test_handle_download_error_download_error(self):
        """Test handling of download errors."""
        error = Exception('Download failed')
        error.__class__.__name__ = 'DownloadError'
        
        controller = AudioCLIController()
        
        # Should not raise any exceptions
        controller.handle_download_error(error)
    
    def test_handle_download_error_unexpected_error(self):
        """Test handling of unexpected errors."""
        error = Exception('Unexpected error')
        
        controller = AudioCLIController()
        
        # Should not raise any exceptions
        controller.handle_download_error(error)
    
    @patch('src.yt_audio_app.audio_cli.parse_audio_args')
    @patch('src.yt_audio_app.audio_cli.AudioCLIController')
    def test_main_metadata_request(self, mock_controller_class, mock_parse_args):
        """Test main function with metadata request."""
        # Setup mocks
        mock_args = Mock()
        mock_args.metadata = True
        mock_args.url = 'https://youtube.com/watch?v=test'
        mock_parse_args.return_value = mock_args
        
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        main()
        
        mock_parse_args.assert_called_once()
        mock_controller_class.assert_called_once()
        mock_controller.run.assert_called_once_with(mock_args)
    
    @patch('src.yt_audio_app.audio_cli.parse_audio_args')
    @patch('src.yt_audio_app.audio_cli.AudioCLIController')
    def test_main_download_request(self, mock_controller_class, mock_parse_args):
        """Test main function with download request."""
        # Setup mocks
        mock_args = Mock()
        mock_args.metadata = False
        mock_args.url = 'https://youtube.com/watch?v=test'
        mock_parse_args.return_value = mock_args
        
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        main()
        
        mock_parse_args.assert_called_once()
        mock_controller_class.assert_called_once()
        mock_controller.run.assert_called_once_with(mock_args)
