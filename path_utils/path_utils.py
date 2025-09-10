# my_project/path_utils/path_utils.py
"""
path_utils.py

Generic path resolution and file/directory utilities for cross-platform compatibility.
Handles both frozen (PyInstaller) and regular Python execution.
"""

import sys
import logging
import uuid
from pathlib import Path
from typing import Union, Optional, Dict, Any

# Import the new Python configuration
from src.common.app_config import get_config

# Initialize logger for this module
logger = logging.getLogger("path_utils")

def get_script_directories() -> tuple[Path, Path]:
    """
    Get SCRIPT_DIR and BASE_DIR handling both frozen (PyInstaller) and regular Python execution.
    
    Returns:
        Tuple of (SCRIPT_DIR, BASE_DIR)
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        script_dir = Path(sys._MEIPASS)
        base_dir = Path(sys.executable).parent
        logger.debug("Running as compiled executable (PyInstaller)")
    else:
        # Running as regular Python script
        script_dir = Path(__file__).resolve().parent.parent
        base_dir = script_dir
        logger.debug("Running as regular Python script")
    
    logger.debug(f"Script directories: SCRIPT_DIR={script_dir}, BASE_DIR={base_dir}")
    return script_dir, base_dir

# Note: SCRIPT_DIR and BASE_DIR are now obtained via get_script_directories() function
# This eliminates global state and makes the module more testable

def load_config(config_file: Union[str, Path] = None) -> Dict[str, Any]:
    """
    Load application configuration from Python config module.
    
    Note: The config_file parameter is kept for backward compatibility but ignored.
    The configuration is now loaded from the Python module.

    Args:
        config_file: Ignored for backward compatibility

    Returns:
        Configuration dictionary
    """
    logger.debug("Loading configuration from Python module")
    config = get_config()
    logger.debug("Configuration loaded successfully from Python module")
    return config


def resolve_path(path_input: Union[str, Path], base_dir: Optional[Path] = None) -> Path:
    """
    Resolve a path input to an absolute Path object.

    Args:
        path_input: String or Path object to resolve
        base_dir: Base directory to resolve relative paths against (defaults to SCRIPT_DIR from get_script_directories())

    Returns:
        Resolved absolute Path object
    """
    if base_dir is None:
        _, base_dir = get_script_directories()

    path = Path(path_input)

    # If already absolute, return as-is
    if path.is_absolute():
        return path

    # Resolve relative to base_dir
    return (base_dir / path).resolve()


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists

    Returns:
        Path object of the created/existing directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


# --- Multiuser Session Management Functions ---------------------------------

def generate_session_uuid() -> str:
    """
    Generate a unique session identifier for multiuser support.
    
    Returns:
        String representation of a UUID4
    """
    session_id = str(uuid.uuid4())
    logger.debug(f"Generated session UUID: {session_id}")
    return session_id


def generate_video_uuid() -> str:
    """
    Generate a unique video identifier for multiuser support.
    
    Returns:
        String representation of a UUID4
    """
    video_id = str(uuid.uuid4())
    logger.debug(f"Generated video UUID: {video_id}")
    return video_id


def create_download_structure(base_dir: Union[str, Path], session_uuid: str, 
                            video_uuid: str, media_type: str) -> Path:
    """
    Create the download directory structure for multiuser support.
    
    Creates a hierarchical structure: base_dir/session_uuid/video_uuid/media_type/
    
    Args:
        base_dir: Base downloads directory
        session_uuid: Session identifier (user session)
        video_uuid: Video identifier (unique per video download)
        media_type: Media type (audio, video, transcripts)
    
    Returns:
        Path to the created directory
        
    Example:
        create_download_structure("./downloads", "session-123", "video-456", "audio")
        # Returns: Path("./downloads/session-123/video-456/audio")
    """
    download_path = Path(base_dir) / session_uuid / video_uuid / media_type
    created_path = ensure_directory(download_path)
    logger.debug(f"Created download structure: {created_path}")
    return created_path


def get_user_download_path(session_uuid: str, video_uuid: str, media_type: str, 
                          base_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Get the user-specific download path for a given session and video.
    
    Args:
        session_uuid: Session identifier (user session)
        video_uuid: Video identifier (unique per video download)
        media_type: Media type (audio, video, transcripts)
        base_dir: Base downloads directory (uses config default if None)
    
    Returns:
        Path to the user-specific download directory
    """
    if base_dir is None:
        config = get_config()
        base_dir = config.get("download", {}).get("download_path", "downloads")
    
    return create_download_structure(base_dir, session_uuid, video_uuid, media_type)
