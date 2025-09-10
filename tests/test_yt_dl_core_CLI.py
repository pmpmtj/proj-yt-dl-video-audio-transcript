"""
Unit tests for yt_dl_core_CLI module.

This module tests the CLI interface functionality with mocked dependencies
to ensure fast, reliable testing without actual network calls or file operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import argparse
import sys
from io import StringIO

# Import the functions we're testing
from src.yt_dl_app.yt_dl_core_CLI import (
    parse_args,
    CLIController,
    main
)


class TestParseArgs:
    """Test cases for parse_args function."""
    
    def test_parse_args_basic_audio(self, mocker):
        """Test parsing basic audio download arguments."""
        # Arrange
        test_args = ["https://youtube.com/watch?v=test123", "--audio-only"]
        
        # Mock config loading
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False}}
        mocker.patch('src.yt_dl_app.yt_dl_core_CLI.load_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core_CLI.get_default_video_settings', 
                    return_value={'ext': 'mp4', 'quality': 'best', 'output_template': '%(title)s.%(ext)s', 'restrict_filenames': False})
        
        # Act
        with patch.object(sys, 'argv', ['test_script'] + test_args):
            args = parse_args()
        
        # Assert
        assert args.url == "https://youtube.com/watch?v=test123"
        assert args.audio_only is True
        assert args.ext == 'mp4'
        assert args.quality == 'best'
        assert args.output_template == '%(title)s.%(ext)s'
        assert args.restrict_filenames is False
    
    def test_parse_args_video_with_options(self, mocker):
        """Test parsing video download arguments with custom options."""
        # Arrange
        test_args = [
            "https://youtube.com/watch?v=test123",
            "--ext", "webm",
            "--quality", "1080p",
            "--output-template", "%(title)s - %(uploader)s.%(ext)s",
            "--restrict-filenames"
        ]
        
        # Mock config loading
        mock_config = {"video": {"output_template": "%(title)s.%(ext)s", "restrict_filenames": False}}
        mocker.patch('src.yt_dl_app.yt_dl_core_CLI.load_config', return_value=mock_config)
        mocker.patch('src.yt_dl_app.yt_dl_core_CLI.get_default_video_settings', 
                    return_value={'ext': 'mp4', 'quality': 'best', 'output_template': '%(title)s.%(ext)s', 'restrict_filenames': False})
        
        # Act
        with patch.object(sys, 'argv', ['test_script'] + test_args):
            args = parse_args()
        
        # Assert
        assert args.url == "https://youtube.com/watch?v=test123"
        assert args.audio_only is False
        assert args.ext == 'webm'
        assert args.quality == '1080p'
        assert args.output_template == '%(title)s - %(uploader)s.%(ext)s'
        assert args.restrict_filenames is True
    
    def test_parse_args_config_fallback(self, mocker):
        """Test parsing arguments when config loading fails."""
        # Arrange
        test_args = ["https://youtube.com/watch?v=test123"]
        
        # Mock config loading failure
        mocker.patch('src.yt_dl_app.yt_dl_core_CLI.load_config', side_effect=FileNotFoundError("Config not found"))
        
        # Act
        with patch.object(sys, 'argv', ['test_script'] + test_args):
            args = parse_args()
        
        # Assert
        assert args.url == "https://youtube.com/watch?v=test123"
        assert args.audio_only is False
        assert args.ext == 'mp4'  # Fallback value
        assert args.quality == 'best'  # Fallback value
        assert args.output_template == '%(title)s.%(ext)s'  # Fallback value
        assert args.restrict_filenames is False  # Fallback value


class TestCLIController:
    """Test cases for CLIController class."""
    
    def test_init_with_defaults(self):
        """Test controller initialization with default dependencies."""
        # Act
        controller = CLIController()
        
        # Assert
        assert controller.config_loader is not None
        assert controller.video_settings_loader is not None
        assert controller.audio_downloader is not None
        assert controller.video_downloader is not None
        assert controller.progress_hook is not None
    
    def test_init_with_custom_dependencies(self):
        """Test controller initialization with custom dependencies."""
        # Arrange
        mock_config_loader = Mock()
        mock_video_settings_loader = Mock()
        mock_audio_downloader = Mock()
        mock_video_downloader = Mock()
        mock_progress_hook = Mock()
        
        # Act
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader,
            audio_downloader=mock_audio_downloader,
            video_downloader=mock_video_downloader,
            progress_hook=mock_progress_hook
        )
        
        # Assert
        assert controller.config_loader == mock_config_loader
        assert controller.video_settings_loader == mock_video_settings_loader
        assert controller.audio_downloader == mock_audio_downloader
        assert controller.video_downloader == mock_video_downloader
        assert controller.progress_hook == mock_progress_hook


class TestCLIControllerLoadConfiguration:
    """Test cases for CLIController.load_configuration method."""
    
    def test_load_configuration_success(self):
        """Test successful configuration loading."""
        # Arrange
        mock_config = {"video": {"ext": "mp4"}}
        mock_video_settings = {"ext": "mp4", "quality": "best"}
        
        mock_config_loader = Mock(return_value=mock_config)
        mock_video_settings_loader = Mock(return_value=mock_video_settings)
        
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader
        )
        
        # Act
        config, video_settings = controller.load_configuration()
        
        # Assert
        assert config == mock_config
        assert video_settings == mock_video_settings
        mock_config_loader.assert_called_once()
        mock_video_settings_loader.assert_called_once_with(mock_config)
    
    def test_load_configuration_failure(self):
        """Test configuration loading failure with fallback."""
        # Arrange
        mock_config_loader = Mock(side_effect=FileNotFoundError("Config not found"))
        mock_video_settings_loader = Mock()
        
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader
        )
        
        # Act
        config, video_settings = controller.load_configuration()
        
        # Assert
        assert config is None
        assert video_settings == {'output_template': '%(title)s.%(ext)s'}
        mock_config_loader.assert_called_once()
        mock_video_settings_loader.assert_not_called()


class TestCLIControllerDetermineOutputTemplate:
    """Test cases for CLIController.determine_output_template method."""
    
    def test_determine_output_template_same_values(self):
        """Test when args and config templates are the same."""
        # Arrange
        controller = CLIController()
        args_template = "%(title)s.%(ext)s"
        config_template = "%(title)s.%(ext)s"
        
        # Act
        result = controller.determine_output_template(args_template, config_template)
        
        # Assert
        assert result is None
    
    def test_determine_output_template_different_values(self):
        """Test when args and config templates are different."""
        # Arrange
        controller = CLIController()
        args_template = "%(title)s - %(uploader)s.%(ext)s"
        config_template = "%(title)s.%(ext)s"
        
        # Act
        result = controller.determine_output_template(args_template, config_template)
        
        # Assert
        assert result == args_template


class TestCLIControllerHandleAudioDownload:
    """Test cases for CLIController.handle_audio_download method."""
    
    def test_handle_audio_download_success(self):
        """Test successful audio download."""
        # Arrange
        mock_audio_downloader = Mock(return_value="/downloads/test.mp3")
        mock_progress_hook = Mock()
        
        controller = CLIController(
            audio_downloader=mock_audio_downloader,
            progress_hook=mock_progress_hook
        )
        
        url = "https://youtube.com/watch?v=test123"
        output_template = "%(title)s.%(ext)s"
        restrict_filenames = False
        config = {"video": {"ext": "mp4"}}
        
        # Act
        result = controller.handle_audio_download(url, output_template, restrict_filenames, config)
        
        # Assert
        assert result == "/downloads/test.mp3"
        mock_audio_downloader.assert_called_once_with(
            url, 
            output_template, 
            restrict_filenames,
            progress_callback=mock_progress_hook,
            config=config
        )


class TestCLIControllerHandleVideoDownload:
    """Test cases for CLIController.handle_video_download method."""
    
    def test_handle_video_download_success(self):
        """Test successful video download."""
        # Arrange
        mock_video_downloader = Mock(return_value="/downloads/test.mp4")
        mock_progress_hook = Mock()
        
        controller = CLIController(
            video_downloader=mock_video_downloader,
            progress_hook=mock_progress_hook
        )
        
        url = "https://youtube.com/watch?v=test123"
        output_template = "%(title)s.%(ext)s"
        restrict_filenames = False
        ext = "mp4"
        quality = "best"
        config = {"video": {"ext": "mp4"}}
        
        # Act
        result = controller.handle_video_download(url, output_template, restrict_filenames, ext, quality, config)
        
        # Assert
        assert result == "/downloads/test.mp4"
        mock_video_downloader.assert_called_once_with(
            url, 
            output_template, 
            restrict_filenames, 
            ext, 
            quality,
            progress_callback=mock_progress_hook,
            config=config
        )
    
    def test_handle_video_download_failure(self):
        """Test video download failure."""
        # Arrange
        mock_video_downloader = Mock(return_value=None)
        mock_progress_hook = Mock()
        
        controller = CLIController(
            video_downloader=mock_video_downloader,
            progress_hook=mock_progress_hook
        )
        
        url = "https://youtube.com/watch?v=test123"
        output_template = "%(title)s.%(ext)s"
        restrict_filenames = False
        ext = "mp4"
        quality = "best"
        config = {"video": {"ext": "mp4"}}
        
        # Act
        result = controller.handle_video_download(url, output_template, restrict_filenames, ext, quality, config)
        
        # Assert
        assert result is None


class TestCLIControllerHandleDownloadError:
    """Test cases for CLIController.handle_download_error method."""
    
    def test_handle_download_error_yt_dlp_error(self, mocker):
        """Test handling yt-dlp download error."""
        # Arrange
        controller = CLIController()
        
        # Create a mock yt-dlp error class
        class MockDownloadError(Exception):
            pass
        
        error = MockDownloadError("Download failed")
        
        # Mock isinstance to return True for yt-dlp error
        mocker.patch('src.yt_dl_app.yt_dl_core_CLI.isinstance', return_value=True)
        mocker.patch('builtins.print')
        
        # Act
        controller.handle_download_error(error)
        
        # Assert
        # Verify print was called with error message
        from unittest.mock import call
        import builtins
        builtins.print.assert_called_with("Download error: Download failed")
    
    def test_handle_download_error_generic_error(self, mocker):
        """Test handling generic error."""
        # Arrange
        controller = CLIController()
        error = Exception("Unexpected error")
        
        # Mock isinstance to return False for yt-dlp error
        mocker.patch('src.yt_dl_app.yt_dl_core_CLI.isinstance', return_value=False)
        mocker.patch('builtins.print')
        
        # Act
        controller.handle_download_error(error)
        
        # Assert
        # Verify print was called with error message
        from unittest.mock import call
        import builtins
        builtins.print.assert_called_with("Unexpected error: Unexpected error")


class TestCLIControllerRun:
    """Test cases for CLIController.run method."""
    
    def test_run_audio_download_success(self, mocker):
        """Test running audio download successfully."""
        # Arrange
        mock_audio_downloader = Mock(return_value="/downloads/test.mp3")
        mock_config_loader = Mock(return_value={"video": {"ext": "mp4"}})
        mock_video_settings_loader = Mock(return_value={"output_template": "%(title)s.%(ext)s"})
        
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader,
            audio_downloader=mock_audio_downloader
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            audio_only=True,
            output_template="%(title)s.%(ext)s",
            restrict_filenames=False,
            ext="mp4",
            quality="best"
        )
        
        mocker.patch('builtins.print')
        
        # Act
        controller.run(args)
        
        # Assert
        mock_audio_downloader.assert_called_once()
        # Verify print was called with success message
        from unittest.mock import call
        import builtins
        builtins.print.assert_called_with("\nDone: /downloads/test.mp3")
    
    def test_run_video_download_success(self, mocker):
        """Test running video download successfully."""
        # Arrange
        mock_video_downloader = Mock(return_value="/downloads/test.mp4")
        mock_config_loader = Mock(return_value={"video": {"ext": "mp4"}})
        mock_video_settings_loader = Mock(return_value={"output_template": "%(title)s.%(ext)s"})
        
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader,
            video_downloader=mock_video_downloader
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            audio_only=False,
            output_template="%(title)s.%(ext)s",
            restrict_filenames=False,
            ext="mp4",
            quality="best"
        )
        
        mocker.patch('builtins.print')
        
        # Act
        controller.run(args)
        
        # Assert
        mock_video_downloader.assert_called_once()
        # Verify print was called with success message
        from unittest.mock import call
        import builtins
        builtins.print.assert_called_with("\nDone: /downloads/test.mp4")
    
    def test_run_video_download_failure(self, mocker):
        """Test running video download with failure."""
        # Arrange
        mock_video_downloader = Mock(return_value=None)
        mock_config_loader = Mock(return_value={"video": {"ext": "mp4"}})
        mock_video_settings_loader = Mock(return_value={"output_template": "%(title)s.%(ext)s"})
        
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader,
            video_downloader=mock_video_downloader
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            audio_only=False,
            output_template="%(title)s.%(ext)s",
            restrict_filenames=False,
            ext="mp4",
            quality="best"
        )
        
        mocker.patch('builtins.print')
        
        # Act
        controller.run(args)
        
        # Assert
        mock_video_downloader.assert_called_once()
        # Verify print was called with failure message
        from unittest.mock import call
        import builtins
        builtins.print.assert_called_with("\nDone: completed")
    
    def test_run_with_custom_output_template(self, mocker):
        """Test running with custom output template."""
        # Arrange
        mock_audio_downloader = Mock(return_value="/downloads/test.mp3")
        mock_config_loader = Mock(return_value={"video": {"ext": "mp4"}})
        mock_video_settings_loader = Mock(return_value={"output_template": "%(title)s.%(ext)s"})
        
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader,
            audio_downloader=mock_audio_downloader
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            audio_only=True,
            output_template="%(title)s - %(uploader)s.%(ext)s",  # Different from config
            restrict_filenames=False,
            ext="mp4",
            quality="best"
        )
        
        mocker.patch('builtins.print')
        
        # Act
        controller.run(args)
        
        # Assert
        # Verify audio downloader was called with custom template
        call_args = mock_audio_downloader.call_args
        assert call_args[0][1] == "%(title)s - %(uploader)s.%(ext)s"  # output_template parameter
    
    def test_run_with_exception(self, mocker):
        """Test running with exception handling."""
        # Arrange
        mock_audio_downloader = Mock(side_effect=Exception("Download failed"))
        mock_config_loader = Mock(return_value={"video": {"ext": "mp4"}})
        mock_video_settings_loader = Mock(return_value={"output_template": "%(title)s.%(ext)s"})
        
        controller = CLIController(
            config_loader=mock_config_loader,
            video_settings_loader=mock_video_settings_loader,
            audio_downloader=mock_audio_downloader
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            audio_only=True,
            output_template="%(title)s.%(ext)s",
            restrict_filenames=False,
            ext="mp4",
            quality="best"
        )
        
        mocker.patch('builtins.print')
        
        # Act & Assert
        with pytest.raises(Exception, match="Download failed"):
            controller.run(args)
        
        # Verify error handling was called
        from unittest.mock import call
        import builtins
        builtins.print.assert_called_with("Unexpected error: Download failed")


class TestMain:
    """Test cases for main function."""
    
    def test_main_success(self, mocker):
        """Test main function success."""
        # Arrange
        mock_args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            audio_only=True,
            output_template="%(title)s.%(ext)s",
            restrict_filenames=False,
            ext="mp4",
            quality="best"
        )
        
        mock_parse_args = mocker.patch('src.yt_dl_app.yt_dl_core_CLI.parse_args', return_value=mock_args)
        mock_controller = mocker.patch('src.yt_dl_app.yt_dl_core_CLI.CLIController')
        mock_controller_instance = Mock()
        mock_controller.return_value = mock_controller_instance
        
        # Act
        main()
        
        # Assert
        mock_parse_args.assert_called_once()
        mock_controller.assert_called_once()
        mock_controller_instance.run.assert_called_once_with(mock_args)
    
    def test_main_with_exception(self, mocker):
        """Test main function with exception."""
        # Arrange
        mock_args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            audio_only=True,
            output_template="%(title)s.%(ext)s",
            restrict_filenames=False,
            ext="mp4",
            quality="best"
        )
        
        mock_parse_args = mocker.patch('src.yt_dl_app.yt_dl_core_CLI.parse_args', return_value=mock_args)
        mock_controller = mocker.patch('src.yt_dl_app.yt_dl_core_CLI.CLIController')
        mock_controller_instance = Mock()
        mock_controller_instance.run.side_effect = Exception("Test error")
        mock_controller.return_value = mock_controller_instance
        
        # Act & Assert
        with pytest.raises(Exception, match="Test error"):
            main()
        
        # Assert
        mock_parse_args.assert_called_once()
        mock_controller.assert_called_once()
        mock_controller_instance.run.assert_called_once_with(mock_args)
