"""
Refactored metadata exporter with dependency injection.

This demonstrates how dependency injection improves testability and maintainability
for file I/O operations and data transformation.
"""

import json
import csv
from typing import Dict, List, Any, Optional, Protocol
from datetime import datetime
from pathlib import Path
import logging

# Setup logger
logger = logging.getLogger("refactored_metadata_exporter")


class FileSystem(Protocol):
    """Protocol for file system operations."""
    
    def ensure_directory(self, path: str) -> None:
        """Ensure directory exists."""
        ...
    
    def write_text_file(self, path: str, content: str, encoding: str = 'utf-8') -> None:
        """Write text content to file."""
        ...
    
    def read_text_file(self, path: str, encoding: str = 'utf-8') -> str:
        """Read text content from file."""
        ...


class DataTransformer(Protocol):
    """Protocol for data transformation operations."""
    
    def flatten_for_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested data structure for CSV export."""
        ...
    
    def generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate markdown report from data."""
        ...


class MetadataExporter:
    """
    Refactored metadata exporter with dependency injection.
    
    This class demonstrates how dependency injection makes file operations:
    - Easy to test (no complex mocking required)
    - More flexible (easy to swap implementations)
    - More maintainable (clear separation of concerns)
    - More configurable (inject different behaviors)
    """
    
    def __init__(self, 
                 file_system: FileSystem,
                 data_transformer: DataTransformer,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize with injected dependencies.
        
        Args:
            file_system: Handles file system operations
            data_transformer: Handles data transformation
            config: Configuration dictionary (optional)
        """
        self.file_system = file_system
        self.data_transformer = data_transformer
        self.config = config or {}
        
        logger.debug("MetadataExporter initialized with injected dependencies")
    
    def export_json(self, metadata: Dict[str, Any], output_path: str) -> bool:
        """
        Export metadata as JSON file.
        
        Args:
            metadata: Metadata dictionary to export
            output_path: Output file path
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            logger.debug(f"Exporting metadata to JSON: {output_path}")
            
            # Ensure directory exists
            self.file_system.ensure_directory(output_path)
            
            # Convert to JSON string
            json_content = json.dumps(metadata, indent=2, ensure_ascii=False, default=str)
            
            # Write to file
            self.file_system.write_text_file(output_path, json_content)
            
            logger.info(f"✅ Metadata exported to JSON: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export JSON: {str(e)}")
            return False
    
    def export_csv(self, metadata: Dict[str, Any], output_path: str) -> bool:
        """
        Export metadata as CSV file.
        
        Args:
            metadata: Metadata dictionary to export
            output_path: Output file path
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            logger.debug(f"Exporting metadata to CSV: {output_path}")
            
            # Ensure directory exists
            self.file_system.ensure_directory(output_path)
            
            # Flatten metadata for CSV export
            flattened_data = self.data_transformer.flatten_for_csv(metadata)
            
            if not flattened_data:
                logger.warning("No data to export to CSV")
                return False
            
            # Generate CSV content
            csv_content = self._generate_csv_content(flattened_data)
            
            # Write to file
            self.file_system.write_text_file(output_path, csv_content)
            
            logger.info(f"✅ Metadata exported to CSV: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export CSV: {str(e)}")
            return False
    
    def export_markdown(self, metadata: Dict[str, Any], output_path: str) -> bool:
        """
        Export metadata as Markdown report.
        
        Args:
            metadata: Metadata dictionary to export
            output_path: Output file path
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            logger.debug(f"Exporting metadata to Markdown: {output_path}")
            
            # Ensure directory exists
            self.file_system.ensure_directory(output_path)
            
            # Generate markdown content
            markdown_content = self.data_transformer.generate_markdown(metadata)
            
            # Write to file
            self.file_system.write_text_file(output_path, markdown_content)
            
            logger.info(f"✅ Metadata exported to Markdown: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export Markdown: {str(e)}")
            return False
    
    def export_metadata(self, metadata: Dict[str, Any], format_type: str, output_path: str) -> bool:
        """
        Export metadata in specified format.
        
        Args:
            metadata: Metadata dictionary to export
            format_type: Export format ('json', 'csv', 'markdown')
            output_path: Output file path
            
        Returns:
            True if export successful, False otherwise
        """
        logger.info(f"Exporting metadata in {format_type} format to {output_path}")
        
        format_type = format_type.lower()
        
        if format_type == 'json':
            return self.export_json(metadata, output_path)
        elif format_type == 'csv':
            return self.export_csv(metadata, output_path)
        elif format_type == 'markdown':
            return self.export_markdown(metadata, output_path)
        else:
            logger.error(f"Unsupported export format: {format_type}")
            return False
    
    def _generate_csv_content(self, flattened_data: Dict[str, Any]) -> str:
        """Generate CSV content from flattened data."""
        if not flattened_data:
            return ""
        
        # Create CSV content
        output = io.StringIO()
        
        if isinstance(flattened_data, list) and flattened_data:
            # Multiple records
            writer = csv.DictWriter(output, fieldnames=flattened_data[0].keys())
            writer.writeheader()
            writer.writerows(flattened_data)
        else:
            # Single record
            writer = csv.DictWriter(output, fieldnames=flattened_data.keys())
            writer.writeheader()
            writer.writerow(flattened_data)
        
        return output.getvalue()


# Example implementations for testing and demonstration

class MockFileSystem:
    """Mock implementation for testing."""
    
    def __init__(self):
        self.created_dirs = set()
        self.written_files = {}
        self.read_files = {}
        self.should_fail = False
        self.fail_on_write = False
        self.fail_on_read = False
    
    def ensure_directory(self, path: str) -> None:
        if self.should_fail:
            raise Exception("Mock directory creation failed")
        self.created_dirs.add(str(Path(path).parent))
    
    def write_text_file(self, path: str, content: str, encoding: str = 'utf-8') -> None:
        if self.fail_on_write:
            raise Exception("Mock file write failed")
        self.written_files[path] = content
        self.read_files[path] = content  # Also store for reading
    
    def read_text_file(self, path: str, encoding: str = 'utf-8') -> str:
        if self.fail_on_read:
            raise Exception("Mock file read failed")
        return self.read_files.get(path, "")


class MockDataTransformer:
    """Mock implementation for testing."""
    
    def __init__(self):
        self.flatten_calls = []
        self.markdown_calls = []
    
    def flatten_for_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.flatten_calls.append(data)
        
        # Simple flattening for testing
        flattened = {}
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flattened[f"{key}_{sub_key}"] = sub_value
            else:
                flattened[key] = value
        
        # Add timestamp
        flattened['exported_at'] = datetime.now().isoformat()
        
        return flattened
    
    def generate_markdown(self, data: Dict[str, Any]) -> str:
        self.markdown_calls.append(data)
        
        # Simple markdown generation for testing
        title = "Unknown Video"
        if 'comprehensive_metadata' in data:
            comp_meta = data['comprehensive_metadata']
            if 'video_metadata' in comp_meta and 'basic_info' in comp_meta['video_metadata']:
                basic_info = comp_meta['video_metadata']['basic_info']
                title = basic_info.get('title', 'Unknown Video')
        
        return f"""# YouTube Video Analysis Report

**Video:** {title}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
This is a test markdown report.
"""


# Real implementations for production use

class RealFileSystem:
    """Real file system implementation."""
    
    def ensure_directory(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    def write_text_file(self, path: str, content: str, encoding: str = 'utf-8') -> None:
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
    
    def read_text_file(self, path: str, encoding: str = 'utf-8') -> str:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()


class RealDataTransformer:
    """Real data transformer implementation."""
    
    def flatten_for_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested metadata structure for CSV export."""
        flattened = {}
        
        def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_'):
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                
                if isinstance(v, dict):
                    flatten_dict(v, new_key, sep)
                elif isinstance(v, list):
                    if v and isinstance(v[0], dict):
                        # Handle list of dicts (like keywords)
                        for i, item in enumerate(v[:5]):  # Limit to first 5 items
                            if isinstance(item, dict):
                                flatten_dict(item, f"{new_key}_{i}", sep)
                            else:
                                flattened[f"{new_key}_{i}"] = str(item)
                    else:
                        # Handle simple lists
                        flattened[new_key] = ', '.join(str(item) for item in v[:10])  # Limit to first 10
                else:
                    flattened[new_key] = v
        
        # Focus on key sections for CSV
        if 'comprehensive_metadata' in data:
            comp_meta = data['comprehensive_metadata']
            
            # Video metadata
            if 'video_metadata' in comp_meta:
                video_meta = comp_meta['video_metadata']
                if 'basic_info' in video_meta:
                    flatten_dict(video_meta['basic_info'], 'video')
                if 'engagement_metrics' in video_meta:
                    flatten_dict(video_meta['engagement_metrics'], 'engagement')
                if 'technical_details' in video_meta:
                    tech_details = video_meta['technical_details']
                    flattened.update({
                        'tech_max_resolution': tech_details.get('max_resolution'),
                        'tech_total_formats': tech_details.get('total_formats'),
                        'tech_video_codecs': ', '.join(tech_details.get('video_codecs', []))
                    })
            
            # Transcript analysis
            if 'transcript_analysis' in comp_meta:
                trans_analysis = comp_meta['transcript_analysis']
                
                # Content metrics
                if 'content_metrics' in trans_analysis:
                    flatten_dict(trans_analysis['content_metrics'], 'content')
                
                # Quality assessment
                if 'quality_assessment' in trans_analysis:
                    flatten_dict(trans_analysis['quality_assessment'], 'quality')
                
                # Content analysis
                if 'content_analysis' in trans_analysis:
                    content_analysis = trans_analysis['content_analysis']
                    
                    # Keywords (top 5)
                    if 'keywords' in content_analysis:
                        keywords = content_analysis['keywords'][:5]
                        for i, kw in enumerate(keywords):
                            if isinstance(kw, dict):
                                flattened[f'keyword_{i}'] = kw.get('keyword', '')
                                flattened[f'keyword_{i}_freq'] = kw.get('frequency', 0)
                    
                    # Topics
                    if 'topics' in content_analysis:
                        flattened['topics'] = ', '.join(content_analysis['topics'][:5])
                    
                    # Content type
                    if 'content_type' in content_analysis:
                        content_type = content_analysis['content_type']
                        flattened['content_category'] = content_type.get('primary_category')
                        flattened['content_confidence'] = content_type.get('confidence')
                    
                    # Language analysis
                    if 'language_analysis' in content_analysis:
                        flatten_dict(content_analysis['language_analysis'], 'language')
            
            # Content summary
            if 'content_summary' in comp_meta:
                content_summary = comp_meta['content_summary']
                if 'llm_suitability' in content_summary:
                    flatten_dict(content_summary['llm_suitability'], 'llm')
        
        # Add timestamp
        flattened['exported_at'] = datetime.now().isoformat()
        
        return flattened
    
    def generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate a comprehensive Markdown report."""
        sections = []
        
        # Header
        title = "Unknown Video"
        video_id = "Unknown"
        
        if 'comprehensive_metadata' in data:
            comp_meta = data['comprehensive_metadata']
            if 'video_metadata' in comp_meta and 'basic_info' in comp_meta['video_metadata']:
                basic_info = comp_meta['video_metadata']['basic_info']
                title = basic_info.get('title', 'Unknown Video')
                video_id = basic_info.get('video_id', 'Unknown')
        
        sections.append(f"# YouTube Video Analysis Report")
        sections.append(f"")
        sections.append(f"**Video:** {title}")
        sections.append(f"**Video ID:** {video_id}")
        sections.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append(f"")
        
        # Table of Contents
        sections.append("## Table of Contents")
        sections.append("- [Video Overview](#video-overview)")
        sections.append("- [Content Analysis](#content-analysis)")
        sections.append("- [Quality Assessment](#quality-assessment)")
        sections.append("- [Technical Details](#technical-details)")
        sections.append("- [LLM Suitability](#llm-suitability)")
        sections.append("")
        
        if 'comprehensive_metadata' in data:
            comp_meta = data['comprehensive_metadata']
            
            # Video Overview
            sections.append("## Video Overview")
            if 'video_metadata' in comp_meta:
                self._add_video_overview_section(sections, comp_meta['video_metadata'])
            
            # Content Analysis
            sections.append("## Content Analysis")
            if 'transcript_analysis' in comp_meta:
                self._add_content_analysis_section(sections, comp_meta['transcript_analysis'])
            
            # Quality Assessment
            sections.append("## Quality Assessment")
            if 'transcript_analysis' in comp_meta:
                self._add_quality_assessment_section(sections, comp_meta['transcript_analysis'])
            
            # Technical Details
            sections.append("## Technical Details")
            if 'video_metadata' in comp_meta:
                self._add_technical_details_section(sections, comp_meta['video_metadata'])
            
            # LLM Suitability
            sections.append("## LLM Suitability")
            if 'content_summary' in comp_meta:
                self._add_llm_suitability_section(sections, comp_meta['content_summary'])
        
        return '\n'.join(sections)
    
    def _add_video_overview_section(self, sections: List[str], video_metadata: Dict[str, Any]):
        """Add video overview section to markdown."""
        basic_info = video_metadata.get('basic_info', {})
        engagement = video_metadata.get('engagement_metrics', {})
        channel_info = video_metadata.get('channel_info', {})
        
        sections.append("### Basic Information")
        sections.append(f"- **Title:** {basic_info.get('title', 'N/A')}")
        sections.append(f"- **Uploader:** {basic_info.get('uploader', 'N/A')}")
        sections.append(f"- **Duration:** {basic_info.get('duration_readable', 'N/A')}")
        sections.append(f"- **Upload Date:** {basic_info.get('upload_date', 'N/A')}")
        sections.append(f"- **URL:** {basic_info.get('webpage_url', 'N/A')}")
        sections.append("")
        
        if engagement:
            sections.append("### Engagement Metrics")
            sections.append(f"- **Views:** {engagement.get('view_count', 0):,}")
            sections.append(f"- **Likes:** {engagement.get('like_count', 0):,}")
            sections.append(f"- **Comments:** {engagement.get('comment_count', 0):,}")
            sections.append(f"- **Engagement Rate:** {engagement.get('engagement_rate_percent', 0):.2f}%")
            sections.append(f"- **Views per Day:** {engagement.get('views_per_day', 0):.1f}")
            sections.append("")
        
        if channel_info.get('channel'):
            sections.append("### Channel Information")
            sections.append(f"- **Channel:** {channel_info.get('channel', 'N/A')}")
            sections.append(f"- **Channel URL:** {channel_info.get('channel_url', 'N/A')}")
            if channel_info.get('channel_follower_count'):
                sections.append(f"- **Followers:** {channel_info.get('channel_follower_count'):,}")
            sections.append("")
    
    def _add_content_analysis_section(self, sections: List[str], transcript_analysis: Dict[str, Any]):
        """Add content analysis section to markdown."""
        content_metrics = transcript_analysis.get('content_metrics', {})
        content_analysis = transcript_analysis.get('content_analysis', {})
        
        if content_metrics:
            sections.append("### Content Metrics")
            sections.append(f"- **Word Count:** {content_metrics.get('word_count', 0):,}")
            sections.append(f"- **Speaking Rate:** {content_metrics.get('speaking_rate_wpm', 0):.1f} words/minute")
            sections.append(f"- **Lexical Diversity:** {content_metrics.get('lexical_diversity', 0):.3f}")
            sections.append(f"- **Average Words per Sentence:** {content_metrics.get('average_words_per_sentence', 0):.1f}")
            sections.append(f"- **Reading Time:** {content_metrics.get('estimated_reading_time_minutes', 0):.1f} minutes")
            sections.append("")
        
        if content_analysis.get('keywords'):
            sections.append("### Key Topics")
            keywords = content_analysis['keywords'][:10]
            for kw in keywords:
                if isinstance(kw, dict):
                    sections.append(f"- **{kw.get('keyword', '')}:** {kw.get('frequency', 0)} occurrences ({kw.get('relevance_score', 0):.1f}% relevance)")
            sections.append("")
        
        if content_analysis.get('topics'):
            sections.append("### Main Subjects")
            for topic in content_analysis['topics'][:5]:
                sections.append(f"- {topic}")
            sections.append("")
        
        if content_analysis.get('content_type'):
            content_type = content_analysis['content_type']
            sections.append("### Content Categorization")
            sections.append(f"- **Primary Category:** {content_type.get('primary_category', 'Unknown')}")
            sections.append(f"- **Confidence:** {content_type.get('confidence', 0):.1f}%")
            
            if content_type.get('category_scores'):
                sections.append("- **Category Scores:**")
                for category, score in content_type['category_scores'].items():
                    sections.append(f"  - {category}: {score}")
            sections.append("")
    
    def _add_quality_assessment_section(self, sections: List[str], transcript_analysis: Dict[str, Any]):
        """Add quality assessment section to markdown."""
        quality = transcript_analysis.get('quality_assessment', {})
        
        if quality:
            sections.append("### Transcript Quality")
            sections.append(f"- **Overall Score:** {quality.get('quality_score', 0):.1f}/100")
            sections.append(f"- **Quality Category:** {quality.get('quality_category', 'Unknown')}")
            sections.append(f"- **Artifact Ratio:** {quality.get('artifact_ratio', 0):.1%}")
            sections.append(f"- **Incomplete Ratio:** {quality.get('incomplete_ratio', 0):.1%}")
            sections.append(f"- **Average Entry Length:** {quality.get('average_entry_length', 0):.1f} characters")
            sections.append(f"- **Entry Consistency:** {quality.get('entry_consistency', 0):.2f}")
            sections.append("")
    
    def _add_technical_details_section(self, sections: List[str], video_metadata: Dict[str, Any]):
        """Add technical details section to markdown."""
        technical = video_metadata.get('technical_details', {})
        
        if technical:
            sections.append("### Video Technical Details")
            sections.append(f"- **Max Resolution:** {technical.get('max_resolution', 'Unknown')}")
            sections.append(f"- **Available Qualities:** {', '.join(technical.get('available_qualities', []))}")
            sections.append(f"- **Total Formats:** {technical.get('total_formats', 0)}")
            sections.append(f"- **Video Formats:** {technical.get('video_formats_count', 0)}")
            sections.append(f"- **Audio Formats:** {technical.get('audio_formats_count', 0)}")
            sections.append(f"- **Video Codecs:** {', '.join(technical.get('video_codecs', []))}")
            if technical.get('fps'):
                sections.append(f"- **FPS:** {technical.get('fps')}")
            sections.append("")
    
    def _add_llm_suitability_section(self, sections: List[str], content_summary: Dict[str, Any]):
        """Add LLM suitability section to markdown."""
        llm_suitability = content_summary.get('llm_suitability', {})
        
        if llm_suitability:
            sections.append("### Analysis Suitability")
            sections.append(f"- **Overall Score:** {llm_suitability.get('overall_score', 0):.1f}/100")
            sections.append(f"- **Length Suitability:** {llm_suitability.get('length_suitability', 'Unknown')}")
            sections.append(f"- **Recommended for LLM:** {'✅ Yes' if llm_suitability.get('recommended_for_llm') else '❌ No'}")
            
            if llm_suitability.get('processing_notes'):
                sections.append("- **Processing Notes:**")
                for note in llm_suitability['processing_notes']:
                    sections.append(f"  - {note}")
            sections.append("")


# Factory function for easy creation
def create_exporter(file_system: FileSystem = None,
                   data_transformer: DataTransformer = None,
                   config: Dict[str, Any] = None) -> MetadataExporter:
    """Factory function to create an exporter with default implementations."""
    
    return MetadataExporter(
        file_system=file_system or MockFileSystem(),
        data_transformer=data_transformer or MockDataTransformer(),
        config=config
    )


# Import io for CSV generation
import io
