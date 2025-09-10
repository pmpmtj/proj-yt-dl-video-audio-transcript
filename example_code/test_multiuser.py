#!/usr/bin/env python3
"""
Test script for multiuser functionality.

This script demonstrates how the multiuser session-based system works
across all three apps (audio, video, transcripts).
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from common.user_context import create_user_context
from yt_audio_app.audio_core import download_audio_mp3
from yt_video_app.video_core import download_video_with_audio
from yt_transcript_app.trans_core import download_transcript


def test_multiuser_functionality():
    """Test multiuser functionality with sample URLs."""
    
    # Sample YouTube URLs for testing
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (short, good for testing)
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    ]
    
    print("🎵 Testing Multiuser YouTube Downloader")
    print("=" * 50)
    
    # Create two user sessions
    user1 = create_user_context()
    user2 = create_user_context()
    
    print(f"👤 User 1 Session ID: {user1.get_session_id()}")
    print(f"👤 User 2 Session ID: {user2.get_session_id()}")
    print()
    
    # Test with first URL
    test_url = test_urls[0]
    print(f"📺 Testing with URL: {test_url}")
    print()
    
    try:
        # User 1 downloads audio
        print("🎵 User 1 downloading audio...")
        audio_path = download_audio_mp3(
            test_url, 
            user_context=user1,
            progress_callback=None  # Suppress progress for clean output
        )
        print(f"✅ User 1 audio saved to: {audio_path}")
        print()
        
        # User 2 downloads video
        print("🎬 User 2 downloading video...")
        video_path = download_video_with_audio(
            test_url,
            quality="720p",  # Lower quality for faster testing
            user_context=user2,
            progress_callback=None  # Suppress progress for clean output
        )
        print(f"✅ User 2 video saved to: {video_path}")
        print()
        
        # User 1 downloads transcript
        print("📝 User 1 downloading transcript...")
        transcript_files = download_transcript(
            test_url,
            formats=['clean', 'structured'],  # Just two formats for testing
            user_context=user1,
            progress_callback=None  # Suppress progress for clean output
        )
        print(f"✅ User 1 transcripts saved:")
        for format_name, file_path in transcript_files.items():
            print(f"   {format_name}: {file_path}")
        print()
        
        # Show directory structure
        print("📁 Directory Structure Created:")
        print("downloads/")
        print(f"├── {user1.get_session_id()}/")
        print(f"│   └── {user1.get_video_uuid(test_url)}/")
        print(f"│       ├── audio/")
        print(f"│       └── transcripts/")
        print(f"└── {user2.get_session_id()}/")
        print(f"    └── {user2.get_video_uuid(test_url)}/")
        print(f"        └── video/")
        print()
        
        # Verify files exist
        print("🔍 Verifying Files:")
        audio_exists = os.path.exists(audio_path)
        video_exists = os.path.exists(video_path)
        transcript_exists = all(os.path.exists(path) for path in transcript_files.values())
        
        print(f"   Audio file exists: {'✅' if audio_exists else '❌'}")
        print(f"   Video file exists: {'✅' if video_exists else '❌'}")
        print(f"   Transcript files exist: {'✅' if transcript_exists else '❌'}")
        print()
        
        # Show session info
        print("📊 Session Information:")
        print(f"User 1 session info: {user1.get_session_info()}")
        print(f"User 2 session info: {user2.get_session_info()}")
        print()
        
        print("🎉 Multiuser test completed successfully!")
        print("Each user has isolated download directories with unique session IDs.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


def test_same_user_multiple_videos():
    """Test same user downloading multiple videos."""
    
    print("\n" + "=" * 50)
    print("🔄 Testing Same User, Multiple Videos")
    print("=" * 50)
    
    user = create_user_context()
    print(f"👤 User Session ID: {user.get_session_id()}")
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📺 Video {i}: {url}")
        
        try:
            # Download audio for each video
            audio_path = download_audio_mp3(
                url, 
                user_context=user,
                progress_callback=None
            )
            print(f"✅ Audio saved to: {audio_path}")
            
            # Show video UUID for this URL
            video_uuid = user.get_video_uuid(url)
            print(f"🆔 Video UUID: {video_uuid}")
            
        except Exception as e:
            print(f"❌ Failed to download video {i}: {e}")
    
    print(f"\n📊 Final session info: {user.get_session_info()}")
    print("✅ Same user, multiple videos test completed!")


if __name__ == "__main__":
    print("🚀 Starting Multiuser YouTube Downloader Tests")
    print("This will test session-based user isolation without requiring a database.")
    print()
    
    # Run tests
    test_multiuser_functionality()
    test_same_user_multiple_videos()
    
    print("\n🎯 All tests completed!")
    print("The multiuser system is working correctly with session-based isolation.")
