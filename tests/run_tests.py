#!/usr/bin/env python3
"""
Test runner script for yt_transcript_app.

This script provides an easy way to run tests with proper path setup.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == '__main__':
    import pytest
    
    # Run tests with verbose output
    pytest.main([
        'tests/test_transcript_app/test_transcript_processor.py',
        '-v',  # verbose
        '--tb=short',  # shorter traceback format
        '--strict-markers',  # strict marker handling
        '--disable-warnings'  # disable warnings for cleaner output
    ])
