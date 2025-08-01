#!/usr/bin/env python3
"""
Whisper Transcription Bot
Automatic Speech Recognition (ASR) with OCR text extraction from video frames
Uses yt-dlp to fetch YouTube audio, Whisper for transcription, and Tesseract for OCR
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import argparse
from datetime import datetime
import re

# Audio and video processing
import yt_dlp
import whisper
from moviepy import VideoFileClip
import cv2
import numpy as np

# OCR for text extraction from video frames
import pytesseract
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asr_transcription.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WhisperTranscriptionBot:
    def __init__(self, output_dir: str = "transcripts", model_size: str = "base"):
        """
        Initialize the Whisper Transcription Bot
        
        Args:
            output_dir: Directory to save transcripts and audio files
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.output_dir = Path(output_dir)
        self.model_size = model_size
        self.model = None
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
        (self.output_dir / "frames").mkdir(exist_ok=True)
        (self.output_dir / "transcripts").mkdir(exist_ok=True)
        
        # Tesseract configuration for OCR
        self.tesseract_config = '--psm 6 --oem 3'
        
        logger.info(f"Initialized WhisperTranscriptionBot")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Whisper model: {model_size}")
    
    def load_whisper_model(self):
        """Load the Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise
    
    def download_youtube_video(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Download YouTube video using yt-dlp
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple of (audio_file_path, video_info)
        """
        try:
            logger.info(f"Downloading video: {url}")
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(self.output_dir / "audio" / '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'writethumbnail': True,
                'writeinfojson': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info
                info = ydl.extract_info(url, download=False)
                video_id = info['id']
                title = info['title']
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded audio file
                audio_file = self.output_dir / "audio" / f"{video_id}.wav"
                info_file = self.output_dir / "audio" / f"{video_id}.info.json"
                
                if not audio_file.exists():
                    # Try to find the actual downloaded file
                    audio_files = list(self.output_dir.glob(f"audio/{video_id}.*"))
                    if audio_files:
                        audio_file = audio_files[0]
                
                logger.info(f"Downloaded audio: {audio_file}")
                
                # Load video info
                video_info = {
                    'id': video_id,
                    'title': title,
                    'url': url,
                    'duration': info.get('duration', 0),
                    'upload_date': info.get('upload_date', ''),
                    'channel': info.get('channel', ''),
                    'description': info.get('description', ''),
                    'audio_file': str(audio_file),
                    'info_file': str(info_file)
                }
                
                return str(audio_file), video_info
                
        except Exception as e:
            logger.error(f"Error downloading video {url}: {str(e)}")
            raise
    
    def extract_video_frames(self, video_url: str, frame_interval: int = 30) -> List[str]:
        """
        Extract frames from video for OCR text detection
        
        Args:
            video_url: YouTube video URL
            frame_interval: Extract frame every N seconds
            
        Returns:
            List of frame file paths
        """
        try:
            logger.info(f"Extracting frames from video: {video_url}")
            
            # Download video file
            ydl_opts = {
                'format': 'best[height<=720]',  # Limit to 720p for faster processing
                'outtmpl': str(self.output_dir / "frames" / '%(id)s.%(ext)s'),
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                video_id = info['id']
                ydl.download([video_url])
                
                # Find the downloaded video file
                video_files = list(self.output_dir.glob(f"frames/{video_id}.*"))
                if not video_files:
                    raise FileNotFoundError(f"Video file not found for {video_id}")
                
                video_file = video_files[0]
            
            # Extract frames using OpenCV
            cap = cv2.VideoCapture(str(video_file))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps
            
            frame_paths = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = frame_count / fps
                
                # Extract frame every frame_interval seconds
                if frame_count % int(fps * frame_interval) == 0:
                    frame_filename = f"{video_id}_frame_{int(current_time):04d}.png"
                    frame_path = self.output_dir / "frames" / frame_filename
                    
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(str(frame_path))
                    
                    logger.info(f"Extracted frame at {current_time:.1f}s: {frame_filename}")
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(frame_paths)} frames")
            return frame_paths
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            return []
    
    def extract_text_from_frame(self, frame_path: str) -> str:
        """
        Extract text from a video frame using Tesseract OCR
        
        Args:
            frame_path: Path to the frame image
            
        Returns:
            Extracted text string
        """
        try:
            # Load image
            image = cv2.imread(frame_path)
            if image is None:
                return ""
            
            # Convert to PIL Image for Tesseract
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                pil_image,
                config=self.tesseract_config,
                lang='eng'
            )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from frame {frame_path}: {str(e)}")
            return ""
    
    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """
        Transcribe audio using Whisper
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Whisper transcription result
        """
        try:
            logger.info(f"Transcribing audio: {audio_file}")
            
            if self.model is None:
                self.load_whisper_model()
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_file,
                verbose=True,
                word_timestamps=True
            )
            
            logger.info("Transcription completed")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio {audio_file}: {str(e)}")
            raise
    
    def process_video(self, url: str, extract_frames: bool = True) -> Dict[str, Any]:
        """
        Process a single YouTube video
        
        Args:
            url: YouTube video URL
            extract_frames: Whether to extract frames for OCR
            
        Returns:
            Complete processing result
        """
        try:
            logger.info(f"Processing video: {url}")
            
            # Download audio
            audio_file, video_info = self.download_youtube_video(url)
            
            # Transcribe audio
            transcription = self.transcribe_audio(audio_file)
            
            # Extract frames and OCR text if requested
            ocr_results = []
            if extract_frames:
                frame_paths = self.extract_video_frames(url)
                
                for frame_path in frame_paths:
                    frame_text = self.extract_text_from_frame(frame_path)
                    if frame_text:
                        # Extract timestamp from filename
                        timestamp_match = re.search(r'frame_(\d{4})\.png', frame_path)
                        if timestamp_match:
                            timestamp_seconds = int(timestamp_match.group(1))
                            ocr_results.append({
                                'timestamp': timestamp_seconds,
                                'text': frame_text,
                                'frame_path': frame_path
                            })
            
            # Combine results
            result = {
                'video_info': video_info,
                'transcription': transcription,
                'ocr_results': ocr_results,
                'processed_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing video {url}: {str(e)}")
            raise
    
    def save_jsonl(self, results: List[Dict[str, Any]], filename: str = "talks_transcripts.jsonl"):
        """
        Save results to JSONL format
        
        Args:
            results: List of processing results
            filename: Output filename
        """
        try:
            output_file = self.output_dir / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for result in results:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                    f.write('\n')
            
            logger.info(f"Saved results to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving JSONL file: {str(e)}")
            raise
    
    def process_videos(self, urls: List[str], extract_frames: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple YouTube videos
        
        Args:
            urls: List of YouTube video URLs
            extract_frames: Whether to extract frames for OCR
            
        Returns:
            List of processing results
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"Processing video {i}/{len(urls)}: {url}")
                result = self.process_video(url, extract_frames)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process video {url}: {str(e)}")
                # Continue with next video
                continue
        
        return results

def main():
    """Main function to run the Whisper Transcription Bot"""
    parser = argparse.ArgumentParser(description='Whisper Transcription Bot')
    parser.add_argument('--urls', nargs='+', required=True, help='YouTube video URLs')
    parser.add_argument('--output-dir', default='transcripts', help='Output directory')
    parser.add_argument('--model-size', default='base', choices=['tiny', 'base', 'small', 'medium', 'large'], 
                       help='Whisper model size')
    parser.add_argument('--no-frames', action='store_true', help='Skip frame extraction and OCR')
    parser.add_argument('--frame-interval', type=int, default=30, help='Extract frame every N seconds')
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = WhisperTranscriptionBot(args.output_dir, args.model_size)
    
    # Process videos
    results = bot.process_videos(args.urls, not args.no_frames)
    
    # Save results
    if results:
        bot.save_jsonl(results)
        
        print(f"\n{'='*60}")
        print("TRANSCRIPTION SUMMARY")
        print(f"{'='*60}")
        print(f"Processed {len(results)} videos")
        print(f"Output directory: {args.output_dir}")
        print(f"Model used: {args.model_size}")
        print(f"Frame extraction: {'Disabled' if args.no_frames else 'Enabled'}")
        
        for i, result in enumerate(results, 1):
            video_info = result['video_info']
            transcription = result['transcription']
            ocr_results = result['ocr_results']
            
            print(f"\nVideo {i}: {video_info['title']}")
            print(f"  Duration: {video_info['duration']} seconds")
            print(f"  Transcription segments: {len(transcription.get('segments', []))}")
            print(f"  OCR text blocks: {len(ocr_results)}")
        
        print(f"\n✅ Transcription completed successfully!")
    else:
        print("❌ No videos were processed successfully")

if __name__ == "__main__":
    main() 