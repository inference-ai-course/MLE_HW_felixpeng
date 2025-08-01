#!/usr/bin/env python3
"""
Test script to verify ASR setup and dependencies
"""

import sys
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    try:
        import yt_dlp
        print("✅ yt-dlp imported successfully")
    except ImportError as e:
        print(f"❌ yt-dlp import failed: {e}")
        return False
    
    try:
        import whisper
        print("✅ whisper imported successfully")
    except ImportError as e:
        print(f"❌ whisper import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ opencv-python imported successfully")
    except ImportError as e:
        print(f"❌ opencv-python import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    try:
        import pytesseract
        print("✅ pytesseract imported successfully")
    except ImportError as e:
        print(f"❌ pytesseract import failed: {e}")
        return False
    
    try:
        from moviepy import VideoFileClip
        print("✅ moviepy imported successfully")
    except ImportError as e:
        print(f"❌ moviepy import failed: {e}")
        return False
    
    return True

def test_ffmpeg():
    """Test if FFmpeg is available"""
    print("\nTesting FFmpeg installation...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
            return True
        else:
            print("❌ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        print("\nTo install FFmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Ubuntu: sudo apt-get install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ FFmpeg test failed: {e}")
        return False

def test_tesseract():
    """Test if Tesseract is available"""
    print("\nTesting Tesseract installation...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract not found: {e}")
        print("\nTo install Tesseract:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt-get install tesseract-ocr")
        return False

def test_whisper_model():
    """Test if Whisper can load a model"""
    print("\nTesting Whisper model loading...")
    
    try:
        import whisper
        print("Loading tiny Whisper model for testing...")
        model = whisper.load_model("tiny")
        print("✅ Whisper model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Whisper model loading failed: {e}")
        return False

def test_yt_dlp():
    """Test if yt-dlp can extract video info"""
    print("\nTesting yt-dlp functionality...")
    
    try:
        import yt_dlp
        
        # Test URL (short video)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            if info:
                print("✅ yt-dlp can extract video info")
                return True
            else:
                print("❌ yt-dlp failed to extract video info")
                return False
                
    except Exception as e:
        print(f"❌ yt-dlp test failed: {e}")
        return False

def test_directories():
    """Test if required directories can be created"""
    print("\nTesting directory creation...")
    
    try:
        test_dir = Path("test_transcripts")
        test_dir.mkdir(exist_ok=True)
        
        # Test subdirectories
        (test_dir / "audio").mkdir(exist_ok=True)
        (test_dir / "frames").mkdir(exist_ok=True)
        (test_dir / "transcripts").mkdir(exist_ok=True)
        
        print("✅ Directory creation successful")
        
        # Clean up
        import shutil
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ Directory creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("ASR SETUP TEST")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("FFmpeg Installation", test_ffmpeg),
        ("Tesseract Installation", test_tesseract),
        ("Whisper Model Loading", test_whisper_model),
        ("yt-dlp Functionality", test_yt_dlp),
        ("Directory Creation", test_directories)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("✅ All tests passed! ASR system is ready to use.")
        print("\nYou can now run:")
        print("  python run_transcription.py")
        print("  or")
        print("  python whisper_transcription_bot.py --urls <youtube_url>")
    else:
        print("❌ Some tests failed. Please fix the issues above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 