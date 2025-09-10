"""
Unit tests for refactored_trans_core_cli.py

Demonstrates how dependency injection makes CLI testing simple and clean.
No complex mocking required - just inject test doubles!
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any, List
import argparse

# Import the refactored module
from src.yt_transcript_app.refactored_trans_core_cli import (
    RefactoredTranscriptCLI,
    MockTranscriptDownloader,
    MockMetadataExtractor,
    MockPreviewGenerator,
    MockLanguageLister,
    MockProgressReporter,
    MockOutputHandler,
    create_cli,
    parse_transcript_args
)


class TestRefactoredTranscriptCLI:
    """Test cases for the refactored CLI with dependency injection."""
    
    def test_initialization_with_dependencies(self):
        """Test initialization with injected dependencies."""
        # Arrange
        mock_downloader = MockTranscriptDownloader()
        mock_metadata = MockMetadataExtractor()
        mock_preview = MockPreviewGenerator()
        mock_languages = MockLanguageLister()
        mock_progress = MockProgressReporter()
        mock_output = MockOutputHandler()
        config = {"test": "value"}
        
        # Act
        cli = RefactoredTranscriptCLI(
            transcript_downloader=mock_downloader,
            metadata_extractor=mock_metadata,
            preview_generator=mock_preview,
            language_lister=mock_languages,
            progress_reporter=mock_progress,
            output_handler=mock_output,
            config=config
        )
        
        # Assert
        assert cli.downloader == mock_downloader
        assert cli.metadata_extractor == mock_metadata
        assert cli.preview_generator == mock_preview
        assert cli.language_lister == mock_languages
        assert cli.progress_reporter == mock_progress
        assert cli.output_handler == mock_output
        assert cli.config == config
    
    def test_handle_metadata_request_success(self):
        """Test successful metadata extraction."""
        # Arrange
        mock_metadata = MockMetadataExtractor(should_succeed=True)
        mock_output = MockOutputHandler()
        mock_progress = MockProgressReporter()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=MockTranscriptDownloader(),
            metadata_extractor=mock_metadata,
            preview_generator=MockPreviewGenerator(),
            language_lister=MockLanguageLister(),
            progress_reporter=mock_progress,
            output_handler=mock_output
        )
        
        url = "https://youtube.com/watch?v=test123"
        
        # Act
        cli.handle_metadata_request(url)
        
        # Assert
        assert len(mock_metadata.extract_calls) == 1
        assert mock_metadata.extract_calls[0]['url'] == url
        
        assert len(mock_output.success_messages) == 1
        assert "✅ Metadata extracted successfully!" in mock_output.success_messages[0]
        
        assert len(mock_progress.progress_calls) == 1
        assert "Extracting metadata..." in mock_progress.progress_calls[0]['message']
    
    def test_handle_metadata_request_failure(self):
        """Test metadata extraction failure."""
        # Arrange
        mock_metadata = MockMetadataExtractor(should_succeed=False)
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=MockTranscriptDownloader(),
            metadata_extractor=mock_metadata,
            preview_generator=MockPreviewGenerator(),
            language_lister=MockLanguageLister(),
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        url = "https://youtube.com/watch?v=test123"
        
        # Act
        cli.handle_metadata_request(url)
        
        # Assert
        assert len(mock_output.error_messages) == 1
        assert "❌ Failed to extract metadata" in mock_output.error_messages[0]
    
    def test_handle_preview_request_success(self):
        """Test successful preview generation."""
        # Arrange
        mock_preview = MockPreviewGenerator(should_succeed=True)
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=MockTranscriptDownloader(),
            metadata_extractor=MockMetadataExtractor(),
            preview_generator=mock_preview,
            language_lister=MockLanguageLister(),
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        url = "https://youtube.com/watch?v=test123"
        language = "en"
        
        # Act
        cli.handle_preview_request(url, language)
        
        # Assert
        assert len(mock_preview.preview_calls) == 1
        assert mock_preview.preview_calls[0]['url'] == url
        assert mock_preview.preview_calls[0]['language_code'] == language
        
        assert len(mock_output.success_messages) == 1
        assert "✅ Preview generated successfully!" in mock_output.success_messages[0]
    
    def test_handle_list_languages_request_success(self):
        """Test successful language listing."""
        # Arrange
        mock_languages = MockLanguageLister()
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=MockTranscriptDownloader(),
            metadata_extractor=MockMetadataExtractor(),
            preview_generator=MockPreviewGenerator(),
            language_lister=mock_languages,
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        url = "https://youtube.com/watch?v=test123"
        
        # Act
        cli.handle_list_languages_request(url)
        
        # Assert
        assert len(mock_languages.list_calls) == 1
        assert mock_languages.list_calls[0]['url'] == url
        
        assert len(mock_output.success_messages) == 1
        assert "✅ Available languages:" in mock_output.success_messages[0]
        
        # Check that languages were displayed
        assert len(mock_output.info_messages) >= 3  # At least 3 languages
        assert any("English (en)" in msg for msg in mock_output.info_messages)
        assert any("Spanish (es)" in msg for msg in mock_output.info_messages)
    
    def test_handle_transcript_download_success(self):
        """Test successful transcript download."""
        # Arrange
        mock_downloader = MockTranscriptDownloader(should_succeed=True)
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=mock_downloader,
            metadata_extractor=MockMetadataExtractor(),
            preview_generator=MockPreviewGenerator(),
            language_lister=MockLanguageLister(),
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        url = "https://youtube.com/watch?v=test123"
        language = "en"
        output_dir = "/test/output"
        filename_template = "test_transcript"
        formats = ["clean", "timestamped"]
        
        # Act
        cli.handle_transcript_download(url, language, output_dir, filename_template, formats)
        
        # Assert
        assert len(mock_downloader.download_calls) == 1
        call = mock_downloader.download_calls[0]
        assert call['url'] == url
        assert call['language_code'] == language
        assert call['output_dir'] == output_dir
        assert call['filename_template'] == filename_template
        assert call['formats'] == formats
        
        assert len(mock_output.success_messages) == 1
        assert "✅ Transcript downloaded successfully!" in mock_output.success_messages[0]
        
        # Check that file paths were displayed
        assert len(mock_output.info_messages) >= 2  # At least 2 file paths
        assert any("clean:" in msg for msg in mock_output.info_messages)
        assert any("timestamped:" in msg for msg in mock_output.info_messages)
    
    def test_handle_transcript_download_failure(self):
        """Test transcript download failure."""
        # Arrange
        mock_downloader = MockTranscriptDownloader(should_succeed=False)
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=mock_downloader,
            metadata_extractor=MockMetadataExtractor(),
            preview_generator=MockPreviewGenerator(),
            language_lister=MockLanguageLister(),
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        url = "https://youtube.com/watch?v=test123"
        
        # Act
        cli.handle_transcript_download(url, "en", "/test", "test", ["clean"])
        
        # Assert
        assert len(mock_output.error_messages) == 1
        assert "❌ Download failed: Mock download failed" in mock_output.error_messages[0]
    
    def test_run_with_metadata_flag(self):
        """Test CLI run with metadata flag."""
        # Arrange
        mock_metadata = MockMetadataExtractor()
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=MockTranscriptDownloader(),
            metadata_extractor=mock_metadata,
            preview_generator=MockPreviewGenerator(),
            language_lister=MockLanguageLister(),
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            metadata=True,
            preview=False,
            list_languages=False,
            language=None,
            output_dir="./downloads",
            filename_template="transcript",
            formats=["clean"]
        )
        
        # Act
        cli.run(args)
        
        # Assert
        assert len(mock_metadata.extract_calls) == 1
        assert mock_metadata.extract_calls[0]['url'] == args.url
    
    def test_run_with_preview_flag(self):
        """Test CLI run with preview flag."""
        # Arrange
        mock_preview = MockPreviewGenerator()
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=MockTranscriptDownloader(),
            metadata_extractor=MockMetadataExtractor(),
            preview_generator=mock_preview,
            language_lister=MockLanguageLister(),
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            metadata=False,
            preview=True,
            list_languages=False,
            language="en",
            output_dir="./downloads",
            filename_template="transcript",
            formats=["clean"]
        )
        
        # Act
        cli.run(args)
        
        # Assert
        assert len(mock_preview.preview_calls) == 1
        assert mock_preview.preview_calls[0]['url'] == args.url
        assert mock_preview.preview_calls[0]['language_code'] == args.language
    
    def test_run_with_list_languages_flag(self):
        """Test CLI run with list languages flag."""
        # Arrange
        mock_languages = MockLanguageLister()
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=MockTranscriptDownloader(),
            metadata_extractor=MockMetadataExtractor(),
            preview_generator=MockPreviewGenerator(),
            language_lister=mock_languages,
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            metadata=False,
            preview=False,
            list_languages=True,
            language=None,
            output_dir="./downloads",
            filename_template="transcript",
            formats=["clean"]
        )
        
        # Act
        cli.run(args)
        
        # Assert
        assert len(mock_languages.list_calls) == 1
        assert mock_languages.list_calls[0]['url'] == args.url
    
    def test_run_with_download_default(self):
        """Test CLI run with default download behavior."""
        # Arrange
        mock_downloader = MockTranscriptDownloader()
        mock_output = MockOutputHandler()
        
        cli = RefactoredTranscriptCLI(
            transcript_downloader=mock_downloader,
            metadata_extractor=MockMetadataExtractor(),
            preview_generator=MockPreviewGenerator(),
            language_lister=MockLanguageLister(),
            progress_reporter=MockProgressReporter(),
            output_handler=mock_output
        )
        
        args = argparse.Namespace(
            url="https://youtube.com/watch?v=test123",
            metadata=False,
            preview=False,
            list_languages=False,
            language="en",
            output_dir="./downloads",
            filename_template="transcript",
            formats=["clean", "timestamped"]
        )
        
        # Act
        cli.run(args)
        
        # Assert
        assert len(mock_downloader.download_calls) == 1
        call = mock_downloader.download_calls[0]
        assert call['url'] == args.url
        assert call['language_code'] == args.language
        assert call['output_dir'] == args.output_dir
        assert call['filename_template'] == args.filename_template
        assert call['formats'] == args.formats


class TestFactoryFunction:
    """Test cases for the factory function."""
    
    def test_create_cli_with_defaults(self):
        """Test creating CLI with default implementations."""
        # Act
        cli = create_cli()
        
        # Assert
        assert isinstance(cli.downloader, MockTranscriptDownloader)
        assert isinstance(cli.metadata_extractor, MockMetadataExtractor)
        assert isinstance(cli.preview_generator, MockPreviewGenerator)
        assert isinstance(cli.language_lister, MockLanguageLister)
        assert isinstance(cli.progress_reporter, MockProgressReporter)
        assert isinstance(cli.output_handler, MockOutputHandler)
        assert cli.config == {}
    
    def test_create_cli_with_custom_dependencies(self):
        """Test creating CLI with custom dependencies."""
        # Arrange
        custom_downloader = MockTranscriptDownloader()
        custom_metadata = MockMetadataExtractor()
        custom_preview = MockPreviewGenerator()
        custom_languages = MockLanguageLister()
        custom_progress = MockProgressReporter()
        custom_output = MockOutputHandler()
        custom_config = {"custom": "value"}
        
        # Act
        cli = create_cli(
            transcript_downloader=custom_downloader,
            metadata_extractor=custom_metadata,
            preview_generator=custom_preview,
            language_lister=custom_languages,
            progress_reporter=custom_progress,
            output_handler=custom_output,
            config=custom_config
        )
        
        # Assert
        assert cli.downloader == custom_downloader
        assert cli.metadata_extractor == custom_metadata
        assert cli.preview_generator == custom_preview
        assert cli.language_lister == custom_languages
        assert cli.progress_reporter == custom_progress
        assert cli.output_handler == custom_output
        assert cli.config == custom_config


class TestMockImplementations:
    """Test cases for the mock implementations."""
    
    def test_mock_transcript_downloader(self):
        """Test mock transcript downloader."""
        # Arrange
        mock_downloader = MockTranscriptDownloader(should_succeed=True)
        
        # Act
        result = mock_downloader.download_transcript("test_url", "en", "/test", "test", ["clean"])
        
        # Assert
        assert result['success'] is True
        assert len(mock_downloader.download_calls) == 1
        assert mock_downloader.download_calls[0]['url'] == "test_url"
    
    def test_mock_metadata_extractor(self):
        """Test mock metadata extractor."""
        # Arrange
        mock_metadata = MockMetadataExtractor(should_succeed=True)
        
        # Act
        result = mock_metadata.get_transcript_metadata("test_url")
        
        # Assert
        assert result['success'] is True
        assert 'video_info' in result
        assert len(mock_metadata.extract_calls) == 1
        assert mock_metadata.extract_calls[0]['url'] == "test_url"
    
    def test_mock_preview_generator(self):
        """Test mock preview generator."""
        # Arrange
        mock_preview = MockPreviewGenerator(should_succeed=True)
        
        # Act
        result = mock_preview.preview_transcript("test_url", "en")
        
        # Assert
        assert result['success'] is True
        assert 'preview_text' in result
        assert len(mock_preview.preview_calls) == 1
        assert mock_preview.preview_calls[0]['url'] == "test_url"
    
    def test_mock_language_lister(self):
        """Test mock language lister."""
        # Arrange
        mock_languages = MockLanguageLister()
        
        # Act
        result = mock_languages.list_available_languages("test_url")
        
        # Assert
        assert len(result) == 3  # English, Spanish, French
        assert any(lang['language_code'] == 'en' for lang in result)
        assert len(mock_languages.list_calls) == 1
        assert mock_languages.list_calls[0]['url'] == "test_url"
    
    def test_mock_progress_reporter(self):
        """Test mock progress reporter."""
        # Arrange
        mock_progress = MockProgressReporter()
        
        # Act
        mock_progress.report_progress("Test message", 50.0)
        
        # Assert
        assert len(mock_progress.progress_calls) == 1
        assert mock_progress.progress_calls[0]['message'] == "Test message"
        assert mock_progress.progress_calls[0]['percentage'] == 50.0
    
    def test_mock_output_handler(self):
        """Test mock output handler."""
        # Arrange
        mock_output = MockOutputHandler()
        
        # Act
        mock_output.print_info("Info message")
        mock_output.print_error("Error message")
        mock_output.print_success("Success message")
        
        # Assert
        assert len(mock_output.info_messages) == 1
        assert mock_output.info_messages[0] == "Info message"
        assert len(mock_output.error_messages) == 1
        assert mock_output.error_messages[0] == "Error message"
        assert len(mock_output.success_messages) == 1
        assert mock_output.success_messages[0] == "Success message"


class TestArgumentParsing:
    """Test cases for argument parsing."""
    
    def test_parse_basic_arguments(self):
        """Test parsing basic arguments."""
        # Arrange
        test_args = ["https://youtube.com/watch?v=test123"]
        
        # Act
        with pytest.MonkeyPatch().context() as m:
            m.setattr("sys.argv", ["script"] + test_args)
            args = parse_transcript_args()
        
        # Assert
        assert args.url == "https://youtube.com/watch?v=test123"
        assert args.metadata is False
        assert args.preview is False
        assert args.list_languages is False
        assert args.language is None
        assert args.output_dir == "./downloads/transcripts"
        assert args.filename_template == "transcript"
        assert args.formats == ["clean", "timestamped", "structured"]
    
    def test_parse_with_all_options(self):
        """Test parsing with all options."""
        # Arrange
        test_args = [
            "https://youtube.com/watch?v=test123",
            "--metadata",
            "--language", "es",
            "--output-dir", "/custom/output",
            "--filename-template", "custom_name",
            "--formats", "clean", "timestamped",
            "--verbose"
        ]
        
        # Act
        with pytest.MonkeyPatch().context() as m:
            m.setattr("sys.argv", ["script"] + test_args)
            args = parse_transcript_args()
        
        # Assert
        assert args.url == "https://youtube.com/watch?v=test123"
        assert args.metadata is True
        assert args.preview is False
        assert args.list_languages is False
        assert args.language == "es"
        assert args.output_dir == "/custom/output"
        assert args.filename_template == "custom_name"
        assert args.formats == ["clean", "timestamped"]
        assert args.verbose is True


if __name__ == '__main__':
    pytest.main([__file__])
