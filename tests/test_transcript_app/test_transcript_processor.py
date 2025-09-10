"""
Unit tests for transcript_processor.py

Tests the TranscriptProcessor class and process_transcript_data function
with mocked dependencies to ensure isolated unit testing.
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Import the modules under test
from src.yt_transcript_app.transcript_processor import TranscriptProcessor, process_transcript_data


class TestTranscriptProcessor:
    """Test cases for TranscriptProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock configuration to avoid external dependencies
        self.mock_config = {
            "transcripts": {
                "processing": {
                    "text_cleaning": {
                        "enabled": True,
                        "remove_filler_words": True,
                        "filler_words": ["um", "uh", "er", "ah"],
                        "normalize_whitespace": True,
                        "fix_transcription_artifacts": True
                    },
                    "chapter_detection": {
                        "enabled": True,
                        "min_silence_gap_seconds": 3.0,
                        "min_chapter_length_seconds": 30.0,
                        "include_chapter_summaries": True
                    },
                    "preview": {
                        "max_lines": 10,
                        "include_stats": True,
                        "include_quality_indicators": True
                    }
                }
            }
        }
        
        # Sample transcript data for testing
        self.sample_transcript_entries = [
            {"start": 0.0, "text": "Hello everyone, welcome to this tutorial."},
            {"start": 3.5, "text": "Today we're going to learn about Python programming."},
            {"start": 7.2, "text": "First, let's start with the basics."},
            {"start": 10.8, "text": "Python is a great language for beginners."},
            {"start": 15.0, "text": "It's easy to read and write."},
            {"start": 18.5, "text": "Now let's move on to more advanced topics."},
            {"start": 22.0, "text": "We'll cover functions, classes, and modules."},
            {"start": 25.5, "text": "That's all for today's tutorial."},
            {"start": 28.0, "text": "Thanks for watching and see you next time!"}
        ]
        
        # Sample video metadata
        self.sample_video_metadata = {
            "id": "test_video_123",
            "title": "Python Programming Tutorial",
            "duration": 30,
            "uploader": "Test Channel",
            "upload_date": "20231201"
        }
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_processor_initialization_with_config(self, mock_load_config):
        """Test TranscriptProcessor initialization with configuration."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        
        # Act
        processor = TranscriptProcessor()
        
        # Assert
        assert processor.config == self.mock_config["transcripts"]["processing"]
        assert processor.text_cleaning_config["enabled"] is True
        assert processor.chapter_config["enabled"] is True
        assert processor.preview_config["max_lines"] == 10
        mock_load_config.assert_called_once()
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_processor_initialization_without_config(self, mock_load_config):
        """Test TranscriptProcessor initialization when config loading fails."""
        # Arrange
        mock_load_config.side_effect = Exception("Config load failed")
        
        # Act
        processor = TranscriptProcessor()
        
        # Assert
        assert processor.config == {}
        assert processor.text_cleaning_config == {}
        assert processor.chapter_config == {}
        assert processor.preview_config == {}
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_clean_text_basic(self, mock_load_config):
        """Test basic text cleaning functionality."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        dirty_text = "Hello um everyone, uh welcome to this er tutorial."
        
        # Act
        cleaned_text = processor.clean_text(dirty_text)
        
        # Assert
        assert "um" not in cleaned_text
        assert "uh" not in cleaned_text
        # Note: "er" in "everyone" is not removed as it's part of a word, not standalone
        assert "Hello everyone, welcome to this tutorial." in cleaned_text
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_clean_text_with_whitespace_normalization(self, mock_load_config):
        """Test text cleaning with whitespace normalization."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        messy_text = "Hello    world.\n\n\nThis   is   a   test.\n\n"
        
        # Act
        cleaned_text = processor.clean_text(messy_text)
        
        # Assert
        assert "    " not in cleaned_text  # Multiple spaces removed
        assert "\n\n\n" not in cleaned_text  # Multiple newlines removed
        # The actual behavior joins lines with spaces, not newlines
        assert cleaned_text.strip() == "Hello world. This is a test."
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_clean_text_with_transcription_artifacts(self, mock_load_config):
        """Test text cleaning with transcription artifacts."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        artifact_text = "The the quick brown fox - fox jumps over the lazy dog."
        
        # Act
        cleaned_text = processor.clean_text(artifact_text)
        
        # Assert
        assert "the the" not in cleaned_text
        assert "fox - fox" not in cleaned_text
        assert "The quick brown fox jumps over the lazy dog." in cleaned_text
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_clean_text_disabled(self, mock_load_config):
        """Test text cleaning when disabled in config."""
        # Arrange
        disabled_config = self.mock_config.copy()
        disabled_config["transcripts"]["processing"]["text_cleaning"]["enabled"] = False
        mock_load_config.return_value = disabled_config
        processor = TranscriptProcessor()
        
        dirty_text = "Hello um everyone, uh welcome."
        
        # Act
        cleaned_text = processor.clean_text(dirty_text)
        
        # Assert
        assert cleaned_text == dirty_text  # No cleaning applied
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_generate_clean_transcript(self, mock_load_config):
        """Test clean transcript generation."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        # Act
        clean_transcript = processor.generate_clean_transcript(self.sample_transcript_entries)
        
        # Assert
        assert isinstance(clean_transcript, str)
        assert "Hello everyone, welcome to this tutorial" in clean_transcript
        assert "Python programming" in clean_transcript
        assert "Thanks for watching" in clean_transcript
        # Should be cleaned (no timestamps, no filler words)
        assert "[0.0s]" not in clean_transcript
        assert "um" not in clean_transcript.lower()
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_generate_timestamped_transcript(self, mock_load_config):
        """Test timestamped transcript generation."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        # Act
        timestamped_transcript = processor.generate_timestamped_transcript(self.sample_transcript_entries)
        
        # Assert
        assert isinstance(timestamped_transcript, str)
        # The actual format uses 2 decimal places
        assert "[0.00s] Hello everyone, welcome to this tutorial." in timestamped_transcript
        assert "[3.50s] Today we're going to learn about Python programming." in timestamped_transcript
        assert "[28.00s] Thanks for watching and see you next time!" in timestamped_transcript
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_detect_chapters(self, mock_load_config):
        """Test chapter detection functionality."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        # Create transcript with clear chapter breaks (gaps > 3 seconds)
        chapter_transcript = [
            {"start": 0.0, "text": "Introduction to the topic."},
            {"start": 5.0, "text": "This is the first chapter content."},
            {"start": 10.0, "text": "More first chapter content."},
            {"start": 15.0, "text": "End of first chapter."},
            # Gap of 5 seconds (should trigger chapter break)
            {"start": 20.0, "text": "Second chapter starts here."},
            {"start": 25.0, "text": "More second chapter content."},
            {"start": 30.0, "text": "End of second chapter."}
        ]
        
        # Act
        chapters = processor.detect_chapters(chapter_transcript)
        
        # Assert
        assert isinstance(chapters, list)
        assert len(chapters) >= 1  # Should detect at least one chapter
        if chapters:
            chapter = chapters[0]
            assert "start_time" in chapter
            assert "end_time" in chapter
            assert "duration" in chapter
            assert "text" in chapter
            assert "summary" in chapter
            assert "word_count" in chapter
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_generate_structured_transcript(self, mock_load_config):
        """Test structured transcript generation."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        # Act
        structured = processor.generate_structured_transcript(
            self.sample_transcript_entries, 
            self.sample_video_metadata
        )
        
        # Assert
        assert isinstance(structured, dict)
        assert "metadata" in structured
        assert "statistics" in structured
        assert "transcript" in structured
        assert "formats" in structured
        
        # Check metadata
        assert structured["metadata"]["video_id"] == "test_video_123"
        assert structured["metadata"]["title"] == "Python Programming Tutorial"
        
        # Check statistics
        assert "word_count" in structured["statistics"]
        assert "character_count" in structured["statistics"]
        assert "estimated_reading_time_minutes" in structured["statistics"]
        assert structured["statistics"]["word_count"] > 0
        
        # Check transcript structure
        assert "entries" in structured["transcript"]
        assert "chapters" in structured["transcript"]
        assert len(structured["transcript"]["entries"]) == len(self.sample_transcript_entries)
        
        # Check formats
        assert "clean_text" in structured["formats"]
        assert "timestamped_text" in structured["formats"]
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_generate_preview(self, mock_load_config):
        """Test preview generation functionality."""
        # Arrange
        mock_load_config.return_value = self.mock_config
        processor = TranscriptProcessor()
        
        # Act
        preview = processor.generate_preview(self.sample_transcript_entries, self.sample_video_metadata)
        
        # Assert
        assert isinstance(preview, dict)
        assert "preview_text" in preview
        assert "total_entries" in preview
        assert preview["total_entries"] == len(self.sample_transcript_entries)
        
        # Check preview text contains first few entries
        assert "[0.00s]" in preview["preview_text"]
        assert "Hello everyone" in preview["preview_text"]
        
        # Check statistics if included
        if "statistics" in preview:
            assert "word_count" in preview["statistics"]
            assert "character_count" in preview["statistics"]
            assert preview["statistics"]["word_count"] > 0


class TestProcessTranscriptData:
    """Test cases for process_transcript_data function."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.sample_transcript_entries = [
            {"start": 0.0, "text": "Hello world."},
            {"start": 2.0, "text": "This is a test."}
        ]
        
        self.sample_video_metadata = {
            "id": "test_123",
            "title": "Test Video"
        }
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_process_transcript_data_all_formats(self, mock_load_config):
        """Test processing transcript data with all formats."""
        # Arrange
        mock_load_config.return_value = {}
        formats = ['clean', 'timestamped', 'structured']
        
        # Act
        results = process_transcript_data(
            self.sample_transcript_entries,
            self.sample_video_metadata,
            formats
        )
        
        # Assert
        assert isinstance(results, dict)
        assert 'clean' in results
        assert 'timestamped' in results
        assert 'structured' in results
        
        # Check clean format
        assert isinstance(results['clean'], str)
        assert "Hello world" in results['clean']
        
        # Check timestamped format
        assert isinstance(results['timestamped'], str)
        assert "[0.00s]" in results['timestamped']
        
        # Check structured format
        assert isinstance(results['structured'], dict)
        assert "metadata" in results['structured']
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_process_transcript_data_single_format(self, mock_load_config):
        """Test processing transcript data with single format."""
        # Arrange
        mock_load_config.return_value = {}
        formats = ['clean']
        
        # Act
        results = process_transcript_data(
            self.sample_transcript_entries,
            self.sample_video_metadata,
            formats
        )
        
        # Assert
        assert isinstance(results, dict)
        assert 'clean' in results
        assert 'timestamped' not in results
        assert 'structured' not in results
        assert isinstance(results['clean'], str)
    
    @patch('src.yt_transcript_app.transcript_processor.load_config')
    def test_process_transcript_data_default_formats(self, mock_load_config):
        """Test processing transcript data with default formats (None)."""
        # Arrange
        mock_load_config.return_value = {}
        
        # Act
        results = process_transcript_data(
            self.sample_transcript_entries,
            self.sample_video_metadata
        )
        
        # Assert
        assert isinstance(results, dict)
        # Should default to all formats
        assert 'clean' in results
        assert 'timestamped' in results
        assert 'structured' in results


if __name__ == '__main__':
    pytest.main([__file__])
