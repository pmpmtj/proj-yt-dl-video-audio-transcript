"""
Unit tests for video_cli module.

This module tests the video CLI interface functionality with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import argparse

# Import the functions we're testing
from src.yt_video_app.video_cli import (
    parse_args,
    VideoCLIController,
    main
)


class TestVideoCLI:
    """Test cases for video CLI functionality."""
    
    def test_parse_args_basic(self):
        """Test parsing basic video CLI arguments."""
        with patch('sys.argv', ['video_cli.py', 'https://youtube.com/watch?v=test']):
            args = parse_args()
            
            assert args.url == 'https://youtube.com/watch?v=test'
            assert args.output_template == '%(title)s.%(ext)s'  # Default from config
            assert args.restrict_filenames is True  # Default from config
            assert args.ext == 'mp4'  # Default from config
            assert args.quality == 'best'  # Default from config
    
    def test_parse_args_with_options(self):
        """Test parsing video CLI arguments with options."""
        with patch('sys.argv', [
            'video_cli.py', 
            'https://youtube.com/watch?v=test',
            '--output-template', '%(uploader)s - %(title)s.%(ext)s',
            '--restrict-filenames',
            '--ext', 'webm',
            '--quality', '1080p'
        ]):
            args = parse_args()
            
            assert args.url == 'https://youtube.com/watch?v=test'
            assert args.output_template == '%(uploader)s - %(title)s.%(ext)s'
            assert args.restrict_filenames is True
            assert args.ext == 'webm'
            assert args.quality == '1080p'
    
    def test_video_cli_controller_init_defaults(self):
        """Test VideoCLIController initialization with defaults."""
        controller = VideoCLIController()
        
        assert controller.config_loader is not None
        assert controller.video_settings_loader is not None
        assert controller.video_downloader is not None
        assert controller.progress_hook is not None
    
    def test_video_cli_controller_init_custom(self):
        """Test VideoCLIController initialization with custom dependencies."""
        mock_config_loader = Mock()
        mock_settings_loader = Mock()
        mock_downloader = Mock()
        mock_hook = Mock()
        
        controller = VideoCLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_settings_loader,
            video_downloader=mock_downloader,
            progress_hook=mock_hook
        )
        
        assert controller.config_loader == mock_config_loader
        assert controller.video_settings_loader == mock_settings_loader
        assert controller.video_downloader == mock_downloader
        assert controller.progress_hook == mock_hook
    
    def test_load_configuration_success(self):
        """Test successful configuration loading."""
        mock_config = {"video": {"ext": "mp4"}}
        mock_settings = {"ext": "mp4", "quality": "best"}
        
        controller = VideoCLIController(
            config_loader=Mock(return_value=mock_config),
            video_settings_loader=Mock(return_value=mock_settings)
        )
        
        config, settings = controller.load_configuration()
        
        assert config == mock_config
        assert settings == mock_settings
    
    def test_load_configuration_failure(self):
        """Test configuration loading failure."""
        controller = VideoCLIController(
            config_loader=Mock(side_effect=FileNotFoundError()),
            video_settings_loader=Mock()
        )
        
        config, settings = controller.load_configuration()
        
        assert config is None
        assert settings == {'output_template': '%(title)s.%(ext)s'}
    
    def test_determine_output_template_same(self):
        """Test output template determination when args and config are the same."""
        controller = VideoCLIController()
        
        result = controller.determine_output_template(
            '%(title)s.%(ext)s',
            '%(title)s.%(ext)s'
        )
        
        assert result is None
    
    def test_determine_output_template_different(self):
        """Test output template determination when args and config are different."""
        controller = VideoCLIController()
        
        result = controller.determine_output_template(
            '%(uploader)s - %(title)s.%(ext)s',
            '%(title)s.%(ext)s'
        )
        
        assert result == '%(uploader)s - %(title)s.%(ext)s'
    
    def test_handle_video_download_success(self):
        """Test successful video download."""
        mock_downloader = Mock(return_value='/downloads/video.mp4')
        
        controller = VideoCLIController(video_downloader=mock_downloader)
        
        result = controller.handle_video_download(
            'https://youtube.com/watch?v=test',
            '/downloads/%(title)s.%(ext)s',
            False,  # restrict_filenames
            'mp4',  # ext
            '1080p',  # quality
            {'video': {'ext': 'mp4'}}  # config
        )
        
        assert result == '/downloads/video.mp4'
        mock_downloader.assert_called_once()
    
    def test_handle_video_download_failure(self):
        """Test video download failure."""
        mock_downloader = Mock(return_value=None)
        
        controller = VideoCLIController(video_downloader=mock_downloader)
        
        result = controller.handle_video_download(
            'https://youtube.com/watch?v=test',
            '/downloads/%(title)s.%(ext)s',
            False,  # restrict_filenames
            'mp4',  # ext
            '1080p',  # quality
            {'video': {'ext': 'mp4'}}  # config
        )
        
        assert result is None
        mock_downloader.assert_called_once()
    
    def test_handle_download_error_download_error(self):
        """Test handling of download errors."""
        # Create a custom exception class for testing
        class DownloadError(Exception):
            pass
        
        error = DownloadError('Download failed')
        
        controller = VideoCLIController()
        
        # Should not raise any exceptions
        controller.handle_download_error(error)
    
    def test_handle_download_error_unexpected_error(self):
        """Test handling of unexpected errors."""
        error = Exception('Unexpected error')
        
        controller = VideoCLIController()
        
        # Should not raise any exceptions
        controller.handle_download_error(error)
    
    @patch('src.yt_video_app.video_cli.parse_args')
    @patch('src.yt_video_app.video_cli.VideoCLIController')
    def test_main_success(self, mock_controller_class, mock_parse_args):
        """Test main function success."""
        # Setup mocks
        mock_args = Mock()
        mock_args.url = 'https://youtube.com/watch?v=test'
        mock_parse_args.return_value = mock_args
        
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        
        main()
        
        mock_parse_args.assert_called_once()
        mock_controller_class.assert_called_once()
        mock_controller.run.assert_called_once_with(mock_args)
    
    @patch('src.yt_video_app.video_cli.parse_args')
    @patch('src.yt_video_app.video_cli.VideoCLIController')
    def test_main_with_exception(self, mock_controller_class, mock_parse_args):
        """Test main function with exception."""
        # Setup mocks
        mock_args = Mock()
        mock_parse_args.return_value = mock_args
        
        mock_controller = Mock()
        mock_controller.run.side_effect = Exception('Test error')
        mock_controller_class.return_value = mock_controller
        
        with pytest.raises(Exception, match='Test error'):
            main()
    
    def test_controller_run_success(self):
        """Test controller run method success."""
        # Setup mocks
        mock_args = Mock()
        mock_args.output_template = '%(title)s.%(ext)s'
        mock_args.restrict_filenames = False
        mock_args.ext = 'mp4'
        mock_args.quality = '1080p'
        
        mock_config = {'video': {'output_template': '%(title)s.%(ext)s'}}
        mock_settings = {'output_template': '%(title)s.%(ext)s'}
        
        mock_downloader = Mock(return_value='/downloads/video.mp4')
        
        controller = VideoCLIController(
            config_loader=Mock(return_value=mock_config),
            video_settings_loader=Mock(return_value=mock_settings),
            video_downloader=mock_downloader
        )
        
        controller.run(mock_args)
        
        mock_downloader.assert_called_once()
    
    def test_controller_run_download_error(self):
        """Test controller run method with download error."""
        # Setup mocks
        mock_args = Mock()
        mock_args.output_template = '%(title)s.%(ext)s'
        mock_args.restrict_filenames = False
        mock_args.ext = 'mp4'
        mock_args.quality = '1080p'
        
        mock_config = {'video': {'output_template': '%(title)s.%(ext)s'}}
        mock_settings = {'output_template': '%(title)s.%(ext)s'}
        
        mock_downloader = Mock(side_effect=Exception('Download failed'))
        
        controller = VideoCLIController(
            config_loader=Mock(return_value=mock_config),
            video_settings_loader=Mock(return_value=mock_settings),
            video_downloader=mock_downloader
        )
        
        with pytest.raises(Exception, match='Download failed'):
            controller.run(mock_args)