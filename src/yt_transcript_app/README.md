# YouTube Transcript Downloader

A comprehensive Python application for downloading and analyzing YouTube video transcripts with rich metadata collection, multiple output formats, and advanced content analysis features.

## Features

### 🎯 **Core Functionality**
- **Multiple Output Formats**: Clean text, timestamped, and structured JSON
- **Auto-Language Detection**: Automatically selects the best available transcript
- **Rich Metadata Collection**: Comprehensive content analysis and quality assessment
- **Chapter Detection**: Automatic chapter segmentation based on content gaps
- **Content Analysis**: Topic extraction, keyword analysis, and readability assessment
- **LLM Suitability**: Analysis of content quality for AI/LLM processing

### 📊 **Export Formats**
- **JSON**: Structured data with metadata and analysis
- **CSV**: Flattened data for spreadsheet analysis
- **Markdown**: Human-readable reports with insights
- **Clean Text**: Optimized for LLM consumption
- **Timestamped**: Original format with timing information

### 🔍 **Content Analysis**
- **Quality Assessment**: Artifact detection and completeness scoring
- **Topic Extraction**: Automatic subject identification
- **Keyword Analysis**: Frequency and relevance scoring
- **Language Detection**: Automatic language identification
- **Readability Analysis**: Content complexity assessment
- **Speaking Rate**: Words per minute calculation

## Installation

### Prerequisites
```bash
pip install youtube-transcript-api yt-dlp
```

### Dependencies
- `youtube-transcript-api` - YouTube transcript extraction
- `yt-dlp` - Video metadata extraction
- `pathlib` - Cross-platform path handling
- `typing` - Type hints support

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Download transcript with all formats
python -m src.yt_transcript_app "https://www.youtube.com/watch?v=VIDEO_ID"

# Download specific formats only
python -m src.yt_transcript_app "URL" --formats clean structured

# Specify language
python -m src.yt_transcript_app "URL" --language en

# Custom output directory
python -m src.yt_transcript_app "URL" --output-dir ./my_transcripts
```

#### Advanced Options
```bash
# Preview transcript without downloading
python -m src.yt_transcript_app "URL" --preview

# Show available languages
python -m src.yt_transcript_app "URL" --list-languages

# Display metadata only
python -m src.yt_transcript_app "URL" --metadata

# Disable metadata analysis (faster)
python -m src.yt_transcript_app "URL" --no-metadata-analysis

# Quiet mode (suppress progress)
python -m src.yt_transcript_app "URL" --quiet
```

#### Custom Templates
```bash
# Custom filename template
python -m src.yt_transcript_app "URL" --template "my_transcript_%(id)s"

# Combine with custom directory
python -m src.yt_transcript_app "URL" --output-dir ./docs --template "transcript_%(title)s"
```

### Programmatic Usage

#### Basic Download
```python
from src.yt_transcript_app import download_transcript

# Download with all formats
files = download_transcript("https://www.youtube.com/watch?v=VIDEO_ID")
print(f"Downloaded: {files}")

# Download specific formats
files = download_transcript(
    "URL", 
    formats=['clean', 'structured'],
    language_code='en'
)
```

#### Metadata Extraction
```python
from src.yt_transcript_app import get_transcript_metadata

# Get transcript metadata
metadata = get_transcript_metadata("https://www.youtube.com/watch?v=VIDEO_ID")
print(f"Available languages: {metadata['available_languages']}")
print(f"Total transcripts: {metadata['total_transcripts']}")
```

#### Preview Content
```python
from src.yt_transcript_app import preview_transcript

# Preview transcript content
preview = preview_transcript("https://www.youtube.com/watch?v=VIDEO_ID")
if preview:
    print(f"Word count: {preview['statistics']['word_count']}")
    print(f"Quality: {preview['quality_insights']['quality_category']}")
```

## Output Files

### File Naming Convention
```
{base_name}_clean.txt          # Clean text format
{base_name}_timestamped.txt    # Timestamped format
{base_name}_structured.json    # Structured JSON with metadata
{base_name}_metadata.json      # Rich metadata analysis
{base_name}_metadata.csv       # CSV export of metadata
{base_name}_report.md          # Markdown report
```

### Structured JSON Format
```json
{
  "metadata": {
    "video_id": "VIDEO_ID",
    "title": "Video Title",
    "duration": 300,
    "uploader": "Channel Name",
    "processed_at": "2024-01-01T12:00:00"
  },
  "statistics": {
    "word_count": 1500,
    "speaking_rate_wpm": 180,
    "lexical_diversity": 0.75,
    "chapters_detected": 5
  },
  "transcript": {
    "entries": [...],
    "chapters": [...]
  },
  "formats": {
    "clean_text": "...",
    "timestamped_text": "..."
  },
  "comprehensive_metadata": {
    "video_metadata": {...},
    "transcript_analysis": {...},
    "content_summary": {...}
  }
}
```

## Configuration

### Default Settings
- **Output Directory**: `./downloads/transcripts`
- **Default Formats**: `['clean', 'timestamped', 'structured']`
- **Language Detection**: Auto-selects best available
- **Metadata Analysis**: Enabled by default
- **Chapter Detection**: 3-second minimum gap, 30-second minimum length

### Customization
The app uses the centralized configuration system. Key settings can be modified in `src/common/app_config.py`:

```python
# Transcript-specific configuration
"transcripts": {
    "processing": {
        "text_cleaning": {
            "enabled": True,
            "remove_filler_words": True,
            "normalize_whitespace": True
        },
        "chapter_detection": {
            "enabled": True,
            "min_silence_gap_seconds": 3.0,
            "min_chapter_length_seconds": 30.0
        }
    },
    "preferred_languages": ["en", "en-US", "en-GB"]
}
```

## Examples

### Example 1: Educational Content Analysis
```bash
# Download with full analysis for educational content
python -m src.yt_transcript_app "https://youtu.be/EDUCATIONAL_VIDEO" \
    --formats clean structured \
    --language en \
    --output-dir ./education_transcripts
```

**Output**: Clean text for note-taking, structured JSON with chapter analysis, and comprehensive metadata for content categorization.

### Example 2: Quick Preview
```bash
# Quick preview to check content quality
python -m src.yt_transcript_app "https://youtu.be/VIDEO_ID" --preview
```

**Output**: Console display showing word count, quality assessment, content insights, and LLM suitability.

### Example 3: Batch Processing
```python
# Process multiple videos programmatically
urls = [
    "https://youtu.be/VIDEO1",
    "https://youtu.be/VIDEO2", 
    "https://youtu.be/VIDEO3"
]

for url in urls:
    try:
        files = download_transcript(url, formats=['clean', 'structured'])
        print(f"✅ Processed: {url}")
    except Exception as e:
        print(f"❌ Failed: {url} - {e}")
```

## Content Analysis Features

### Quality Assessment
- **Artifact Detection**: Identifies transcription errors and audio artifacts
- **Completeness Scoring**: Measures transcript completeness
- **Consistency Analysis**: Evaluates entry length consistency
- **Quality Categories**: Excellent, Very Good, Good, Fair, Poor, Very Poor

### Content Insights
- **Topic Extraction**: Identifies main subjects and themes
- **Keyword Analysis**: Frequency and relevance scoring
- **Content Categorization**: Educational, Entertainment, News, Technical
- **Language Analysis**: Detection and readability assessment

### LLM Suitability
- **Length Assessment**: Optimal content length for AI processing
- **Quality Scoring**: Overall suitability for LLM analysis
- **Processing Notes**: Recommendations for content preparation
- **Chunking Suggestions**: Guidance for large content processing

## Error Handling

### Common Issues
- **No Transcript Available**: App will suggest alternative languages
- **Network Issues**: Automatic retry with exponential backoff
- **Invalid URLs**: Clear error messages with validation
- **Permission Errors**: Helpful guidance for file access issues

### Troubleshooting
```bash
# Check available languages
python -m src.yt_transcript_app "URL" --list-languages

# Test with preview first
python -m src.yt_transcript_app "URL" --preview

# Use quiet mode for debugging
python -m src.yt_transcript_app "URL" --quiet
```

## Integration

### With Other Apps
The transcript app is designed to work alongside the `yt_audio_app`:

```bash
# Download both audio and transcript
python -m src.yt_audio_app "URL" --output-dir ./downloads
python -m src.yt_transcript_app "URL" --output-dir ./downloads
```

### API Integration
```python
# Use in web applications
from src.yt_transcript_app import download_transcript, get_transcript_metadata

def process_video(url):
    # Get metadata first
    metadata = get_transcript_metadata(url)
    
    # Download if suitable
    if metadata['total_transcripts'] > 0:
        files = download_transcript(url, formats=['structured'])
        return files
    return None
```

## Performance

### Optimization Tips
- Use `--no-metadata-analysis` for faster processing
- Specify `--formats` to only generate needed formats
- Use `--quiet` mode for batch processing
- Process shorter videos for quicker results

### Resource Usage
- **Memory**: ~50-100MB for typical videos
- **Storage**: 1-5MB per transcript depending on length
- **Processing Time**: 2-10 seconds per video (with metadata analysis)

## Contributing

### Code Structure
- `trans_core.py` - Core download and processing logic
- `trans_core_cli.py` - Command-line interface
- `transcript_processor.py` - Text processing and formatting
- `metadata_collector.py` - Content analysis and metadata
- `metadata_exporter.py` - Multi-format export functionality
- `get_transcript_list.py` - Language detection and selection

### Adding Features
1. Core functionality goes in `trans_core.py`
2. CLI options in `trans_core_cli.py`
3. Processing logic in `transcript_processor.py`
4. Analysis features in `metadata_collector.py`

## License

This project follows the same license as the parent YouTube downloader project.

## Support

For issues, feature requests, or questions:
1. Check the troubleshooting section above
2. Review the error messages for specific guidance
3. Test with `--preview` mode first
4. Verify URL format and video availability

---

**Note**: This app requires internet connectivity to access YouTube's transcript API. Some videos may not have transcripts available, and the app will provide helpful suggestions for alternatives.
