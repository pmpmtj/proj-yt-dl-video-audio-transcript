"""
Pytest configuration and shared fixtures for transcript app tests.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def sample_transcript_entries():
    """Sample transcript entries for testing."""
    return [
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


@pytest.fixture
def sample_video_metadata():
    """Sample video metadata for testing."""
    return {
        "id": "test_video_123",
        "title": "Python Programming Tutorial",
        "duration": 30,
        "uploader": "Test Channel",
        "upload_date": "20231201",
        "view_count": 1000,
        "like_count": 50
    }


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
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
        },
        "metadata_collection": {
            "enabled": True
        }
    }


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch('builtins.open', mock_open()) as mock_file, \
         patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('os.path.exists', return_value=False) as mock_exists:
        yield {
            'mock_file': mock_file,
            'mock_mkdir': mock_mkdir,
            'mock_exists': mock_exists
        }
