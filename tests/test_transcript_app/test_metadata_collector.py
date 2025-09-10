"""
Unit tests for metadata_collector.py

Tests rich metadata collection and content analysis functionality with mocked
external dependencies to ensure isolated unit testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import the modules under test
from src.yt_transcript_app.metadata_collector import (
    MetadataCollector,
    collect_comprehensive_metadata
)


class TestMetadataCollectorInitialization:
    """Test cases for MetadataCollector initialization."""
    
    def test_init_with_config(self):
        """Test initialization with provided config."""
        # Arrange
        config = {
            "metadata_collection": {
                "content_analysis": {
                    "stop_words": ["test", "words"],
                    "extract_keywords": True
                },
                "video_metadata": {
                    "technical_details": True
                }
            }
        }
        
        # Act
        collector = MetadataCollector(config)
        
        # Assert
        assert collector.config == config["metadata_collection"]
        assert collector.content_analysis_config == config["metadata_collection"]["content_analysis"]
        assert collector.video_metadata_config == config["metadata_collection"]["video_metadata"]
        assert "test" in collector.stop_words
        assert "words" in collector.stop_words
    
    @patch('src.yt_transcript_app.metadata_collector.load_config')
    def test_init_without_config_loads_default(self, mock_load_config):
        """Test initialization loads config when none provided."""
        # Arrange
        mock_load_config.return_value = {
            "metadata_collection": {
                "content_analysis": {"stop_words": ["default"]}
            }
        }
        
        # Act
        collector = MetadataCollector()
        
        # Assert
        assert collector.config == {"content_analysis": {"stop_words": ["default"]}}
        mock_load_config.assert_called_once()
    
    @patch('src.yt_transcript_app.metadata_collector.load_config')
    def test_init_with_config_load_failure(self, mock_load_config):
        """Test initialization handles config load failure gracefully."""
        # Arrange
        mock_load_config.side_effect = Exception("Config error")
        
        # Act
        collector = MetadataCollector()
        
        # Assert
        assert collector.config == {}
        assert collector.stop_words == collector._get_default_stop_words()
    
    def test_load_stop_words_from_config(self):
        """Test loading stop words from config."""
        # Arrange
        config = {
            "metadata_collection": {
                "content_analysis": {
                    "stop_words": ["custom", "stop", "words"]
                }
            }
        }
        
        # Act
        collector = MetadataCollector(config)
        
        # Assert
        assert "custom" in collector.stop_words
        assert "stop" in collector.stop_words
        assert "words" in collector.stop_words
    
    def test_load_stop_words_fallback_to_default(self):
        """Test fallback to default stop words when config fails."""
        # Arrange
        config = {
            "metadata_collection": {
                "content_analysis": {
                    "stop_words": "invalid_format"  # Should cause fallback
                }
            }
        }
        
        # Act
        collector = MetadataCollector(config)
        
        # Assert
        assert collector.stop_words == collector._get_default_stop_words()
        assert "the" in collector.stop_words  # Default stop word


class TestVideoMetadataExtraction:
    """Test cases for video metadata extraction."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = MetadataCollector()
        
        self.sample_video_info = {
            "id": "test_video_123",
            "title": "Test Video Title",
            "description": "A test video description",
            "duration": 300,
            "view_count": 1000,
            "like_count": 50,
            "uploader": "Test Channel",
            "uploader_id": "test_channel_123",
            "upload_date": "20231201",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "format": "mp4",
            "filesize": 50000000
        }
    
    def test_extract_video_metadata_success(self):
        """Test successful video metadata extraction."""
        # Act
        result = self.collector.extract_video_metadata(self.sample_video_info)
        
        # Assert
        assert isinstance(result, dict)
        # Check the actual structure returned by the method
        assert "basic_info" in result
        assert "technical_details" in result
        assert "engagement_metrics" in result
        assert "channel_info" in result
    
    def test_extract_video_metadata_none_input(self):
        """Test video metadata extraction with None input."""
        # Act
        result = self.collector.extract_video_metadata(None)
        
        # Assert
        assert isinstance(result, dict)
        assert result["basic_info"]["video_id"] is None
        assert result["basic_info"]["title"] is None
        assert result["technical_details"]["duration_formatted"] == "0:00"
    
    def test_extract_video_metadata_partial_data(self):
        """Test video metadata extraction with partial data."""
        # Arrange
        partial_info = {
            "id": "partial_123",
            "title": "Partial Title"
            # Missing other fields
        }
        
        # Act
        result = self.collector.extract_video_metadata(partial_info)
        
        # Assert
        assert result["basic_info"]["video_id"] == "partial_123"
        assert result["basic_info"]["title"] == "Partial Title"
        assert result["technical_details"]["duration_formatted"] == "0:00"  # Default
        assert result["engagement_metrics"]["view_count"] == 0  # Default
    
    def test_extract_basic_info(self):
        """Test basic info extraction."""
        # Act
        result = self.collector._extract_basic_info(self.sample_video_info)
        
        # Assert
        assert result["video_id"] == "test_video_123"
        assert result["title"] == "Test Video Title"
        assert result["description"] == "A test video description"
        assert result["upload_date"] == "20231201"
    
    def test_extract_technical_details(self):
        """Test technical details extraction."""
        # Act
        result = self.collector._extract_technical_details(self.sample_video_info)
        
        # Assert
        assert result["duration_seconds"] == 300
        assert result["duration_formatted"] == "5:00"
        assert result["resolution"] == "1920x1080"
        assert result["fps"] == 30
        assert result["format"] == "mp4"
        assert result["file_size_mb"] == 50.0
    
    def test_extract_engagement_metrics(self):
        """Test engagement metrics extraction."""
        # Act
        result = self.collector._extract_engagement_metrics(self.sample_video_info)
        
        # Assert
        assert result["view_count"] == 1000
        assert result["like_count"] == 50
        assert result["engagement_rate"] == 0.05  # 50/1000
        assert result["days_since_upload"] > 0
    
    def test_extract_channel_info(self):
        """Test channel info extraction."""
        # Act
        result = self.collector._extract_channel_info(self.sample_video_info)
        
        # Assert
        assert result["uploader"] == "Test Channel"
        assert result["uploader_id"] == "test_channel_123"
    
    def test_extract_content_details(self):
        """Test content details extraction."""
        # Act
        result = self.collector._extract_content_details(self.sample_video_info)
        
        # Assert
        assert result["title_length"] == 17  # "Test Video Title"
        assert result["description_length"] == 25  # "A test video description"
        assert result["has_description"] is True


class TestTranscriptContentAnalysis:
    """Test cases for transcript content analysis."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = MetadataCollector()
        
        self.sample_transcript_entries = [
            {"start": 0.0, "text": "Hello everyone, welcome to this tutorial."},
            {"start": 3.0, "text": "Today we're going to learn about Python programming."},
            {"start": 6.0, "text": "Python is a great language for beginners."},
            {"start": 9.0, "text": "Let's start with the basics."}
        ]
        
        self.sample_video_metadata = {
            "basic_info": {
                "title": "Python Tutorial",
                "description": "Learn Python programming"
            }
        }
    
    def test_analyze_transcript_content_success(self):
        """Test successful transcript content analysis."""
        # Act
        result = self.collector.analyze_transcript_content(
            self.sample_transcript_entries, 
            self.sample_video_metadata
        )
        
        # Assert
        assert isinstance(result, dict)
        assert "content_metrics" in result
        assert "quality_assessment" in result
        assert "keywords" in result
        assert "topics" in result
        assert "language_analysis" in result
        assert "content_categorization" in result
        
        # Check content metrics (actual structure)
        assert "content_metrics" in result
        assert "content_analysis" in result
        assert "quality_assessment" in result
    
    def test_analyze_transcript_content_empty_entries(self):
        """Test transcript analysis with empty entries."""
        # Act
        result = self.collector.analyze_transcript_content([], self.sample_video_metadata)
        
        # Assert
        assert isinstance(result, dict)
        assert result["content_metrics"]["total_words"] == 0
        assert result["content_metrics"]["total_characters"] == 0
        assert result["keywords"] == []
        assert result["topics"] == []
    
    def test_analyze_transcript_content_none_metadata(self):
        """Test transcript analysis with None metadata."""
        # Act
        result = self.collector.analyze_transcript_content(self.sample_transcript_entries, None)
        
        # Assert
        assert isinstance(result, dict)
        assert "content_metrics" in result
        assert "quality_assessment" in result
    
    def test_calculate_content_metrics(self):
        """Test content metrics calculation."""
        # Act
        result = self.collector._calculate_content_metrics(
            "Hello world. This is a test.", 
            self.sample_transcript_entries
        )
        
        # Assert
        assert result["total_words"] == 6
        assert result["total_characters"] == 25
        assert result["average_words_per_sentence"] == 3.0
        assert result["speaking_rate_wpm"] > 0
        assert result["total_entries"] == 4
    
    def test_assess_content_quality(self):
        """Test content quality assessment."""
        # Act
        result = self.collector._assess_content_quality(
            "Hello world. This is a test.", 
            self.sample_transcript_entries
        )
        
        # Assert
        assert "quality_score" in result
        assert "quality_category" in result
        assert "artifact_ratio" in result
        assert "readability" in result
        assert 0 <= result["quality_score"] <= 100
        assert result["quality_category"] in ["Poor", "Fair", "Good", "Very Good", "Excellent"]
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        # Act
        result = self.collector._extract_keywords("Python programming tutorial for beginners", max_keywords=3)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) <= 3
        for keyword in result:
            assert "keyword" in keyword  # Actual field name
            assert "frequency" in keyword
            assert "relevance_score" in keyword
    
    def test_extract_topics(self):
        """Test topic extraction."""
        # Act
        result = self.collector._extract_topics("Python programming tutorial for beginners")
        
        # Assert
        assert isinstance(result, list)
        # Should extract meaningful topics
        assert len(result) > 0
    
    def test_analyze_language(self):
        """Test language analysis."""
        # Act
        result = self.collector._analyze_language("Hello world. This is a test.")
        
        # Assert
        assert "detected_language" in result
        assert "confidence" in result
        assert "character_distribution" in result
        assert "sentence_count" in result
        assert result["sentence_count"] == 2
    
    def test_categorize_content(self):
        """Test content categorization."""
        # Act
        result = self.collector._categorize_content(
            "Python programming tutorial for beginners",
            self.sample_video_metadata
        )
        
        # Assert
        assert "content_category" in result
        assert "educational_level" in result
        assert "target_audience" in result
        assert "content_type" in result


class TestUtilityMethods:
    """Test cases for utility methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = MetadataCollector()
    
    def test_format_duration(self):
        """Test duration formatting."""
        # Test various durations (actual format includes spaces)
        assert self.collector._format_duration(0) == "0s"
        assert self.collector._format_duration(30) == "30s"
        assert self.collector._format_duration(60) == "1m 0s"
        assert self.collector._format_duration(90) == "1m 30s"
        assert self.collector._format_duration(3661) == "61m 1s"
    
    def test_calculate_days_since_upload(self):
        """Test days since upload calculation."""
        # Test with recent date
        recent_date = "20231201"
        days = self.collector._calculate_days_since_upload(recent_date)
        assert days >= 0
        
        # Test with old date
        old_date = "20200101"
        days = self.collector._calculate_days_since_upload(old_date)
        assert days > 1000
    
    def test_categorize_quality(self):
        """Test quality categorization."""
        # Actual categories include "Very Poor"
        assert self.collector._categorize_quality(0) == "Very Poor"
        assert self.collector._categorize_quality(25) == "Poor"
        assert self.collector._categorize_quality(50) == "Fair"
        assert self.collector._categorize_quality(75) == "Good"
        assert self.collector._categorize_quality(90) == "Very Good"
        assert self.collector._categorize_quality(95) == "Excellent"
    
    def test_assess_readability(self):
        """Test readability assessment."""
        # Easy readability
        result = self.collector._assess_readability(10.0, 0.1)
        assert result in ["Easy", "Moderate", "Difficult", "Very Difficult"]
        
        # Difficult readability
        result = self.collector._assess_readability(25.0, 0.8)
        assert result in ["Easy", "Moderate", "Difficult", "Very Difficult"]


class TestContentSummaryGeneration:
    """Test cases for content summary generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = MetadataCollector()
        
        self.sample_video_info = {
            "id": "test_video_123",
            "title": "Python Tutorial",
            "description": "Learn Python programming"
        }
        
        self.sample_transcript_analysis = {
            "content_metrics": {
                "total_words": 100,
                "speaking_rate_wpm": 120
            },
            "quality_assessment": {
                "quality_score": 85.0,
                "quality_category": "Very Good"
            },
            "keywords": [
                {"word": "python", "frequency": 5, "relevance_score": 0.9}
            ],
            "topics": ["programming", "tutorial"]
        }
    
    def test_generate_content_summary_success(self):
        """Test successful content summary generation."""
        # Act
        result = self.collector.generate_content_summary(
            self.sample_video_info, 
            self.sample_transcript_analysis
        )
        
        # Assert
        assert isinstance(result, dict)
        assert "summary" in result
        assert "key_insights" in result
        assert "llm_suitability" in result
        assert "processing_notes" in result
        assert "metadata" in result
        
        # Check summary structure
        assert "video_title" in result["summary"]
        assert "content_overview" in result["summary"]
        assert "quality_indicators" in result["summary"]
    
    def test_generate_content_summary_none_inputs(self):
        """Test content summary generation with None inputs."""
        # Act
        result = self.collector.generate_content_summary(None, None)
        
        # Assert
        assert isinstance(result, dict)
        assert "summary" in result
        assert result["summary"]["video_title"] is None
    
    def test_assess_llm_suitability(self):
        """Test LLM suitability assessment."""
        # Act
        result = self.collector._assess_llm_suitability(
            self.sample_transcript_analysis["content_metrics"],
            self.sample_transcript_analysis["quality_assessment"]
        )
        
        # Assert
        assert "overall_suitability" in result
        assert "suitability_score" in result
        assert "recommendations" in result
        assert "strengths" in result
        assert "weaknesses" in result
    
    def test_generate_processing_notes(self):
        """Test processing notes generation."""
        # Act
        result = self.collector._generate_processing_notes(
            self.sample_transcript_analysis["content_metrics"],
            self.sample_transcript_analysis["quality_assessment"]
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
        for note in result:
            assert isinstance(note, str)
            assert len(note) > 0


class TestComprehensiveMetadataCollection:
    """Test cases for the comprehensive metadata collection function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_video_info = {
            "id": "test_video_123",
            "title": "Test Video",
            "duration": 300
        }
        
        self.sample_transcript_entries = [
            {"start": 0.0, "text": "Hello world."},
            {"start": 2.0, "text": "This is a test."}
        ]
    
    @patch('src.yt_transcript_app.metadata_collector.MetadataCollector')
    def test_collect_comprehensive_metadata_success(self, mock_collector_class):
        """Test successful comprehensive metadata collection."""
        # Arrange
        mock_collector = Mock()
        mock_collector_class.return_value = mock_collector
        mock_collector.extract_video_metadata.return_value = {"video": "metadata"}
        mock_collector.analyze_transcript_content.return_value = {"transcript": "analysis"}
        mock_collector.generate_content_summary.return_value = {"summary": "data"}
        
        # Act
        result = collect_comprehensive_metadata(
            self.sample_video_info, 
            self.sample_transcript_entries
        )
        
        # Assert
        assert isinstance(result, dict)
        assert "video_metadata" in result
        assert "transcript_analysis" in result
        assert "content_summary" in result
        assert "collection_timestamp" in result
        
        mock_collector.extract_video_metadata.assert_called_once_with(self.sample_video_info)
        mock_collector.analyze_transcript_content.assert_called_once_with(
            self.sample_transcript_entries, 
            {"video": "metadata"}
        )
        mock_collector.generate_content_summary.assert_called_once()
    
    @patch('src.yt_transcript_app.metadata_collector.MetadataCollector')
    def test_collect_comprehensive_metadata_none_inputs(self, mock_collector_class):
        """Test comprehensive metadata collection with None inputs."""
        # Arrange
        mock_collector = Mock()
        mock_collector_class.return_value = mock_collector
        mock_collector.extract_video_metadata.return_value = {}
        mock_collector.analyze_transcript_content.return_value = {}
        mock_collector.generate_content_summary.return_value = {}
        
        # Act
        result = collect_comprehensive_metadata(None, None)
        
        # Assert
        assert isinstance(result, dict)
        assert "video_metadata" in result
        assert "transcript_analysis" in result
        assert "content_summary" in result
        
        mock_collector.extract_video_metadata.assert_called_once_with(None)
        mock_collector.analyze_transcript_content.assert_called_once_with([], {})
    
    @patch('src.yt_transcript_app.metadata_collector.MetadataCollector')
    def test_collect_comprehensive_metadata_exception_handling(self, mock_collector_class):
        """Test comprehensive metadata collection with exception handling."""
        # Arrange
        mock_collector = Mock()
        mock_collector_class.return_value = mock_collector
        mock_collector.extract_video_metadata.side_effect = Exception("Test error")
        
        # Act
        result = collect_comprehensive_metadata(self.sample_video_info, self.sample_transcript_entries)
        
        # Assert
        assert isinstance(result, dict)
        assert "error" in result
        assert "Test error" in result["error"]


if __name__ == '__main__':
    pytest.main([__file__])
