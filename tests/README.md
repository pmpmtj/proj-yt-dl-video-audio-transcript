# Testing Guide for yt_transcript_app

This directory contains unit tests for the YouTube transcript application.

## Test Structure

```
tests/
├── conftest.py                           # Shared fixtures and configuration
├── run_tests.py                          # Test runner script
├── test_transcript_app/
│   └── test_transcript_processor.py      # Tests for transcript processing
└── README.md                             # This file
```

## Running Tests

### Method 1: Using the test runner script
```bash
# From the project root directory
python tests/run_tests.py
```

### Method 2: Using pytest directly
```bash
# From the project root directory
pytest tests/test_transcript_app/test_transcript_processor.py -v
```

### Method 3: Run all tests
```bash
# From the project root directory
pytest tests/ -v
```

## Test Coverage

The current test suite covers:

### TranscriptProcessor Class
- ✅ Initialization with and without configuration
- ✅ Text cleaning functionality (filler words, whitespace, artifacts)
- ✅ Clean transcript generation
- ✅ Timestamped transcript generation
- ✅ Chapter detection
- ✅ Structured transcript generation
- ✅ Preview generation

### process_transcript_data Function
- ✅ Processing with all formats
- ✅ Processing with single format
- ✅ Default format handling

## Test Philosophy

These tests follow these principles:

1. **Isolation**: Each test is independent and doesn't rely on external services
2. **Mocking**: External dependencies (APIs, file system) are mocked
3. **Fixtures**: Common test data is shared through pytest fixtures
4. **Clarity**: Tests are readable and clearly show what's being tested

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_<function_name>`
2. Use the provided fixtures from `conftest.py`
3. Mock external dependencies
4. Test both success and failure scenarios
5. Keep tests focused on a single behavior

## Dependencies

The tests require:
- `pytest>=7.4.0`
- `pytest-mock>=3.12.0`

These are included in the main `requirements.txt` file.
