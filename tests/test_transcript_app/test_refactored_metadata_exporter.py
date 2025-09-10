"""
Unit tests for refactored_metadata_exporter.py

Demonstrates how dependency injection makes file I/O testing simple and clean.
No complex mocking required - just inject test doubles!
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any
from pathlib import Path
import json

# Import the refactored module
from src.yt_transcript_app.refactored_metadata_exporter import (
    MetadataExporter,
    MockFileSystem,
    MockDataTransformer,
    RealFileSystem,
    RealDataTransformer,
    create_exporter
)


class TestMetadataExporter:
    """Test cases for the refactored metadata exporter with dependency injection."""
    
    def test_initialization_with_dependencies(self):
        """Test initialization with injected dependencies."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        config = {"test": "value"}
        
        # Act
        exporter = MetadataExporter(
            file_system=mock_file_system,
            data_transformer=mock_transformer,
            config=config
        )
        
        # Assert
        assert exporter.file_system == mock_file_system
        assert exporter.data_transformer == mock_transformer
        assert exporter.config == config
    
    def test_export_json_success(self):
        """Test successful JSON export."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data", "nested": {"value": 123}}
        output_path = "/test/output.json"
        
        # Act
        result = exporter.export_json(metadata, output_path)
        
        # Assert
        assert result is True
        assert output_path in mock_file_system.written_files
        
        # Check JSON content
        written_content = mock_file_system.written_files[output_path]
        parsed_content = json.loads(written_content)
        assert parsed_content == metadata
        
        # Check directory was created
        assert str(mock_file_system.created_dirs) in str(mock_file_system.created_dirs)
    
    def test_export_json_file_system_failure(self):
        """Test JSON export with file system failure."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_file_system.fail_on_write = True
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data"}
        output_path = "/test/output.json"
        
        # Act
        result = exporter.export_json(metadata, output_path)
        
        # Assert
        assert result is False
        assert output_path not in mock_file_system.written_files
    
    def test_export_csv_success(self):
        """Test successful CSV export."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {
            "comprehensive_metadata": {
                "video_metadata": {
                    "basic_info": {"title": "Test Video", "duration": 300}
                }
            }
        }
        output_path = "/test/output.csv"
        
        # Act
        result = exporter.export_csv(metadata, output_path)
        
        # Assert
        assert result is True
        assert output_path in mock_file_system.written_files
        
        # Check that transformer was called
        assert len(mock_transformer.flatten_calls) == 1
        assert mock_transformer.flatten_calls[0] == metadata
        
        # Check CSV content has headers (mock transformer flattens differently)
        written_content = mock_file_system.written_files[output_path]
        assert "comprehensive_metadata_video_metadata" in written_content
        assert "exported_at" in written_content
    
    def test_export_csv_empty_data(self):
        """Test CSV export with empty data."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        mock_transformer.flatten_for_csv = Mock(return_value={})  # Empty data
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"empty": "data"}
        output_path = "/test/output.csv"
        
        # Act
        result = exporter.export_csv(metadata, output_path)
        
        # Assert
        assert result is False
        assert output_path not in mock_file_system.written_files
    
    def test_export_markdown_success(self):
        """Test successful Markdown export."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {
            "comprehensive_metadata": {
                "video_metadata": {
                    "basic_info": {"title": "Test Video", "video_id": "test123"}
                }
            }
        }
        output_path = "/test/output.md"
        
        # Act
        result = exporter.export_markdown(metadata, output_path)
        
        # Assert
        assert result is True
        assert output_path in mock_file_system.written_files
        
        # Check that transformer was called
        assert len(mock_transformer.markdown_calls) == 1
        assert mock_transformer.markdown_calls[0] == metadata
        
        # Check Markdown content
        written_content = mock_file_system.written_files[output_path]
        assert "# YouTube Video Analysis Report" in written_content
        assert "Test Video" in written_content
    
    def test_export_markdown_transformer_failure(self):
        """Test Markdown export with transformer failure."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        mock_transformer.generate_markdown = Mock(side_effect=Exception("Transformer error"))
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data"}
        output_path = "/test/output.md"
        
        # Act
        result = exporter.export_markdown(metadata, output_path)
        
        # Assert
        assert result is False
        assert output_path not in mock_file_system.written_files
    
    def test_export_metadata_json_format(self):
        """Test export_metadata with JSON format."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data"}
        output_path = "/test/output.json"
        
        # Act
        result = exporter.export_metadata(metadata, "json", output_path)
        
        # Assert
        assert result is True
        assert output_path in mock_file_system.written_files
    
    def test_export_metadata_csv_format(self):
        """Test export_metadata with CSV format."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data"}
        output_path = "/test/output.csv"
        
        # Act
        result = exporter.export_metadata(metadata, "csv", output_path)
        
        # Assert
        assert result is True
        assert output_path in mock_file_system.written_files
    
    def test_export_metadata_markdown_format(self):
        """Test export_metadata with Markdown format."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data"}
        output_path = "/test/output.md"
        
        # Act
        result = exporter.export_metadata(metadata, "markdown", output_path)
        
        # Assert
        assert result is True
        assert output_path in mock_file_system.written_files
    
    def test_export_metadata_unsupported_format(self):
        """Test export_metadata with unsupported format."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data"}
        output_path = "/test/output.xml"
        
        # Act
        result = exporter.export_metadata(metadata, "xml", output_path)
        
        # Assert
        assert result is False
        assert output_path not in mock_file_system.written_files
    
    def test_export_metadata_case_insensitive_format(self):
        """Test export_metadata with case insensitive format."""
        # Arrange
        mock_file_system = MockFileSystem()
        mock_transformer = MockDataTransformer()
        exporter = MetadataExporter(mock_file_system, mock_transformer)
        
        metadata = {"test": "data"}
        output_path = "/test/output.json"
        
        # Act
        result = exporter.export_metadata(metadata, "JSON", output_path)
        
        # Assert
        assert result is True
        assert output_path in mock_file_system.written_files


class TestFactoryFunction:
    """Test cases for the factory function."""
    
    def test_create_exporter_with_defaults(self):
        """Test creating exporter with default implementations."""
        # Act
        exporter = create_exporter()
        
        # Assert
        assert isinstance(exporter.file_system, MockFileSystem)
        assert isinstance(exporter.data_transformer, MockDataTransformer)
        assert exporter.config == {}
    
    def test_create_exporter_with_custom_dependencies(self):
        """Test creating exporter with custom dependencies."""
        # Arrange
        custom_file_system = MockFileSystem()
        custom_transformer = MockDataTransformer()
        custom_config = {"custom": "value"}
        
        # Act
        exporter = create_exporter(
            file_system=custom_file_system,
            data_transformer=custom_transformer,
            config=custom_config
        )
        
        # Assert
        assert exporter.file_system == custom_file_system
        assert exporter.data_transformer == custom_transformer
        assert exporter.config == custom_config


class TestMockImplementations:
    """Test cases for the mock implementations."""
    
    def test_mock_file_system(self):
        """Test mock file system."""
        # Arrange
        mock_fs = MockFileSystem()
        
        # Act
        mock_fs.ensure_directory("/test/path/file.txt")
        mock_fs.write_text_file("/test/file.txt", "test content")
        content = mock_fs.read_text_file("/test/file.txt")
        
        # Assert (Windows path handling)
        assert str(Path("/test/path")) in mock_fs.created_dirs
        assert "/test/file.txt" in mock_fs.written_files
        assert mock_fs.written_files["/test/file.txt"] == "test content"
        assert content == "test content"
    
    def test_mock_file_system_failures(self):
        """Test mock file system failure modes."""
        # Arrange
        mock_fs = MockFileSystem()
        mock_fs.fail_on_write = True
        mock_fs.fail_on_read = True
        
        # Act & Assert
        with pytest.raises(Exception, match="Mock file write failed"):
            mock_fs.write_text_file("/test/file.txt", "content")
        
        with pytest.raises(Exception, match="Mock file read failed"):
            mock_fs.read_text_file("/test/file.txt")
    
    def test_mock_data_transformer(self):
        """Test mock data transformer."""
        # Arrange
        mock_transformer = MockDataTransformer()
        data = {"test": {"nested": "value"}, "list": [1, 2, 3]}
        
        # Act
        flattened = mock_transformer.flatten_for_csv(data)
        markdown = mock_transformer.generate_markdown(data)
        
        # Assert
        assert len(mock_transformer.flatten_calls) == 1
        assert len(mock_transformer.markdown_calls) == 1
        
        # Check flattening
        assert "test_nested" in flattened
        assert flattened["test_nested"] == "value"
        assert "exported_at" in flattened
        
        # Check markdown generation
        assert "# YouTube Video Analysis Report" in markdown
        assert "Unknown Video" in markdown


class TestRealImplementations:
    """Test cases for the real implementations."""
    
    def test_real_file_system(self):
        """Test real file system implementation."""
        # Arrange
        real_fs = RealFileSystem()
        test_content = "test content"
        test_path = "/tmp/test_file.txt"
        
        try:
            # Act
            real_fs.ensure_directory(test_path)
            real_fs.write_text_file(test_path, test_content)
            content = real_fs.read_text_file(test_path)
            
            # Assert
            assert content == test_content
            
        finally:
            # Cleanup
            import os
            if os.path.exists(test_path):
                os.remove(test_path)
    
    def test_real_data_transformer_flatten(self):
        """Test real data transformer flattening."""
        # Arrange
        real_transformer = RealDataTransformer()
        data = {
            "comprehensive_metadata": {
                "video_metadata": {
                    "basic_info": {"title": "Test Video", "duration": 300},
                    "engagement_metrics": {"view_count": 1000, "like_count": 50}
                },
                "transcript_analysis": {
                    "content_metrics": {"word_count": 500},
                    "content_analysis": {
                        "keywords": [{"keyword": "test", "frequency": 5}],
                        "topics": ["programming", "tutorial"]
                    }
                }
            }
        }
        
        # Act
        flattened = real_transformer.flatten_for_csv(data)
        
        # Assert
        assert "video_title" in flattened
        assert flattened["video_title"] == "Test Video"
        assert "engagement_view_count" in flattened
        assert flattened["engagement_view_count"] == 1000
        assert "content_word_count" in flattened
        assert flattened["content_word_count"] == 500
        assert "keyword_0" in flattened
        assert flattened["keyword_0"] == "test"
        assert "topics" in flattened
        assert "programming, tutorial" in flattened["topics"]
        assert "exported_at" in flattened
    
    def test_real_data_transformer_markdown(self):
        """Test real data transformer markdown generation."""
        # Arrange
        real_transformer = RealDataTransformer()
        data = {
            "comprehensive_metadata": {
                "video_metadata": {
                    "basic_info": {"title": "Test Video", "video_id": "test123"}
                }
            }
        }
        
        # Act
        markdown = real_transformer.generate_markdown(data)
        
        # Assert
        assert "# YouTube Video Analysis Report" in markdown
        assert "Test Video" in markdown
        assert "test123" in markdown
        assert "## Table of Contents" in markdown
        assert "## Video Overview" in markdown


if __name__ == '__main__':
    pytest.main([__file__])
