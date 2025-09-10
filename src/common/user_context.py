"""
User context management for multiuser support.

This module provides session-based user management without requiring a database.
Each user session gets isolated download directories and unique identifiers.
"""

import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path

# Import UUID functions from path_utils
from path_utils.path_utils import (
    generate_session_uuid, 
    generate_video_uuid, 
    get_user_download_path
)

# Initialize logger for this module
logger = logging.getLogger("user_context")


class UserContext:
    """
    Manages user session context for multiuser support.
    
    Each UserContext represents a user session with:
    - Unique session UUID
    - Isolated download directories
    - Session-specific configuration
    - Video-specific download tracking
    """
    
    def __init__(self, session_uuid: Optional[str] = None):
        """
        Initialize a user context.
        
        Args:
            session_uuid: Existing session UUID, or None to create new session
        """
        self.session_uuid = session_uuid or generate_session_uuid()
        self._video_sessions: Dict[str, str] = {}  # video_url -> video_uuid mapping
        logger.info(f"Initialized user context with session: {self.session_uuid}")
    
    def get_session_id(self) -> str:
        """
        Get the session UUID for this user context.
        
        Returns:
            Session UUID string
        """
        return self.session_uuid
    
    def get_video_uuid(self, video_url: str) -> str:
        """
        Get or create a video UUID for a given video URL.
        
        This ensures the same video URL always gets the same video UUID
        within a session, enabling proper file organization.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Video UUID string
        """
        if video_url not in self._video_sessions:
            self._video_sessions[video_url] = generate_video_uuid()
            logger.debug(f"Created video UUID for URL: {video_url} -> {self._video_sessions[video_url]}")
        
        return self._video_sessions[video_url]
    
    def get_audio_download_path(self, video_url: str, base_dir: Optional[Union[str, Path]] = None) -> Path:
        """
        Get the audio download path for a video in this user's session.
        
        Args:
            video_url: YouTube video URL
            base_dir: Base downloads directory (uses config default if None)
            
        Returns:
            Path to the audio download directory
        """
        video_uuid = self.get_video_uuid(video_url)
        return get_user_download_path(self.session_uuid, video_uuid, "audio", base_dir)
    
    def get_video_download_path(self, video_url: str, base_dir: Optional[Union[str, Path]] = None) -> Path:
        """
        Get the video download path for a video in this user's session.
        
        Args:
            video_url: YouTube video URL
            base_dir: Base downloads directory (uses config default if None)
            
        Returns:
            Path to the video download directory
        """
        video_uuid = self.get_video_uuid(video_url)
        return get_user_download_path(self.session_uuid, video_uuid, "video", base_dir)
    
    def get_transcript_download_path(self, video_url: str, base_dir: Optional[Union[str, Path]] = None) -> Path:
        """
        Get the transcript download path for a video in this user's session.
        
        Args:
            video_url: YouTube video URL
            base_dir: Base downloads directory (uses config default if None)
            
        Returns:
            Path to the transcript download directory
        """
        video_uuid = self.get_video_uuid(video_url)
        return get_user_download_path(self.session_uuid, video_uuid, "transcripts", base_dir)
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get information about this user session.
        
        Returns:
            Dictionary with session information
        """
        return {
            'session_uuid': self.session_uuid,
            'total_videos': len(self._video_sessions),
            'video_urls': list(self._video_sessions.keys()),
            'video_uuids': list(self._video_sessions.values())
        }
    
    def get_video_info(self, video_url: str) -> Dict[str, str]:
        """
        Get information about a specific video in this session.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Dictionary with video information
        """
        video_uuid = self.get_video_uuid(video_url)
        return {
            'video_url': video_url,
            'video_uuid': video_uuid,
            'session_uuid': self.session_uuid
        }


def create_user_context(session_uuid: Optional[str] = None) -> UserContext:
    """
    Create a new user context for multiuser support.
    
    Args:
        session_uuid: Existing session UUID, or None to create new session
        
    Returns:
        New UserContext instance
    """
    return UserContext(session_uuid)


def get_default_user_context() -> UserContext:
    """
    Get a default user context (creates new session if none exists).
    
    This is useful for backward compatibility with existing single-user code.
    
    Returns:
        UserContext instance
    """
    return UserContext()
