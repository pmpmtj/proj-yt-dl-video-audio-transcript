"""
Unit tests for path_utils module.

This module tests the path utilities with mocked dependencies
to ensure fast, reliable testing without file system operations.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# Import the functions we're testing
from path_utils import (
    get_script_directories,
    load_config,
    resolve_path,
    ensure_directory
)


class TestGetScriptDirectories:
    """Test cases for get_script_directories function."""
    
    def test_get_script_directories_regular_python(self, mocker):
        """Test that function returns correct paths for regular Python execution."""
        # Arrange
        mock_file_path = Path("/project/path_utils/path_utils.py")
        mocker.patch('path_utils.path_utils.__file__', str(mock_file_path))
        mocker.patch('sys.frozen', False, create=True)
        
        # Act
        script_dir, base_dir = get_script_directories()
        
        # Assert - Use actual resolved paths for cross-platform compatibility
        expected_script_dir = Path("/project")
        expected_base_dir = Path("/project")
        assert script_dir.resolve() == expected_script_dir.resolve()
        assert base_dir.resolve() == expected_base_dir.resolve()
    
    def test_get_script_directories_frozen_executable(self, mocker):
        """Test that function returns correct paths for frozen executable."""
        # Arrange
        mocker.patch('path_utils.path_utils.getattr', return_value=True)
        mocker.patch('sys._MEIPASS', '/temp/pyinstaller', create=True)
        mocker.patch('sys.executable', '/usr/local/bin/myapp')
        
        # Act
        script_dir, base_dir = get_script_directories()
        
        # Assert
        assert script_dir == Path('/temp/pyinstaller')
        assert base_dir == Path('/usr/local/bin')
    
    def test_get_script_directories_returns_tuple(self):
        """Test that function returns a tuple of two Path objects."""
        # Act
        result = get_script_directories()
        
        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], Path)
        assert isinstance(result[1], Path)


class TestLoadConfig:
    """Test cases for load_config function."""
    
    def test_load_config_calls_get_config(self, mocker):
        """Test that function calls get_config from app_config module."""
        # Arrange
        mock_config = {"test": "value"}
        mocker.patch('path_utils.path_utils.get_config', return_value=mock_config)
        
        # Act
        result = load_config()
        
        # Assert
        assert result == mock_config
        from path_utils.path_utils import get_config
        get_config.assert_called_once()
    
    def test_load_config_ignores_config_file_param(self, mocker):
        """Test that function ignores config_file parameter for backward compatibility."""
        # Arrange
        mock_config = {"test": "value"}
        mocker.patch('path_utils.path_utils.get_config', return_value=mock_config)
        
        # Act
        result = load_config("ignored_file.json")
        
        # Assert
        assert result == mock_config


class TestResolvePath:
    """Test cases for resolve_path function."""
    
    def test_resolve_path_absolute_path(self):
        """Test that function returns absolute paths as-is."""
        # Arrange
        absolute_path = Path("/absolute/path")
        
        # Act
        result = resolve_path(absolute_path)
        
        # Assert - Use resolve() for cross-platform compatibility
        assert result.resolve() == absolute_path.resolve()
    
    def test_resolve_path_relative_path_with_default_base(self, mocker):
        """Test that function resolves relative paths with default base directory."""
        # Arrange
        relative_path = "relative/path"
        mock_script_dir = Path("/project")
        mock_base_dir = Path("/project")
        mocker.patch('path_utils.path_utils.get_script_directories', 
                    return_value=(mock_script_dir, mock_base_dir))
        
        # Act
        result = resolve_path(relative_path)
        
        # Assert - Use resolve() for cross-platform compatibility
        expected = mock_base_dir / relative_path
        assert result.resolve() == expected.resolve()
    
    def test_resolve_path_relative_path_with_custom_base(self):
        """Test that function resolves relative paths with custom base directory."""
        # Arrange
        relative_path = "relative/path"
        custom_base = Path("/custom/base")
        
        # Act
        result = resolve_path(relative_path, custom_base)
        
        # Assert - Use resolve() for cross-platform compatibility
        expected = custom_base / relative_path
        assert result.resolve() == expected.resolve()
    
    def test_resolve_path_string_input(self):
        """Test that function works with string input."""
        # Arrange
        path_string = "/absolute/string/path"
        
        # Act
        result = resolve_path(path_string)
        
        # Assert - Use resolve() for cross-platform compatibility
        assert result.resolve() == Path(path_string).resolve()


class TestEnsureDirectory:
    """Test cases for ensure_directory function."""
    
    def test_ensure_directory_creates_directory(self, mocker):
        """Test that function creates directory if it doesn't exist."""
        # Arrange
        test_path = Path("/test/directory")
        mock_mkdir = mocker.patch('pathlib.Path.mkdir')
        
        # Act
        result = ensure_directory(test_path)
        
        # Assert
        assert result == test_path
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_ensure_directory_string_input(self, mocker):
        """Test that function works with string input."""
        # Arrange
        test_path = "/test/string/directory"
        mock_mkdir = mocker.patch('pathlib.Path.mkdir')
        
        # Act
        result = ensure_directory(test_path)
        
        # Assert
        assert result == Path(test_path)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    def test_ensure_directory_returns_path_object(self, mocker):
        """Test that function returns Path object."""
        # Arrange
        test_path = Path("/test/directory")
        mock_mkdir = mocker.patch('pathlib.Path.mkdir')
        
        # Act
        result = ensure_directory(test_path)
        
        # Assert
        assert isinstance(result, Path)
        assert result == test_path
