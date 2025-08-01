# Whisper Transcription Bot

Automatic Speech Recognition (ASR) system that transcribes YouTube videos using Whisper and extracts OCR text from video frames using Tesseract.

## Features

- **YouTube Video Download**: Uses yt-dlp to fetch videos and extract audio
- **Speech Recognition**: OpenAI Whisper for high-quality audio transcription
- **OCR Text Extraction**: Tesseract OCR to extract text from video frames
- **Timestamped Output**: JSONL format with precise timestamps
- **Multi-format Support**: Handles various video formats and qualities
- **Comprehensive Logging**: Detailed processing logs and error handling

## System Requirements

### System Dependencies

#### macOS:
```bash
# Install FFmpeg for audio/video processing
brew install ffmpeg

# Install Tesseract for OCR
brew install tesseract

# Install yt-dlp (if not installing via pip)
brew install yt-dlp
```

#### Ubuntu/Debian:
```bash
# Install FFmpeg
sudo apt-get update
sudo apt-get install ffmpeg

# Install Tesseract OCR
sudo apt-get install tesseract-ocr

# Install yt-dlp (if not installing via pip)
sudo apt-get install yt-dlp
```

### Python Dependencies

```bash
# Install required Python packages
pip install -r requirements_asr.txt

# Or install individually:
pip install yt-dlp openai-whisper moviepy opencv-python numpy pytesseract Pillow
```

## Installation

1. **Clone or download the project files**
2. **Install system dependencies** (see above)
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements_asr.txt
   ```
4. **Verify installation**:
   ```bash
   python test_asr_setup.py
   ```

## Usage

### Quick Start

Run transcription on the provided YouTube videos:

```bash
python run_transcription.py
```

This will process the following videos:
- https://www.youtube.com/watch?v=fOvTtapxa9c
- https://www.youtube.com/watch?v=fLvJ8VdHLA0
- https://www.youtube.com/watch?v=1I6bQ12VxV0
- https://www.youtube.com/watch?v=aircAruvnKk

### Command Line Usage

```bash
# Process specific videos
python whisper_transcription_bot.py --urls "https://www.youtube.com/watch?v=VIDEO_ID"

# Use different Whisper model
python whisper_transcription_bot.py --urls "https://www.youtube.com/watch?v=VIDEO_ID" --model-size large

# Skip frame extraction (audio only)
python whisper_transcription_bot.py --urls "https://www.youtube.com/watch?v=VIDEO_ID" --no-frames

# Custom output directory
python whisper_transcription_bot.py --urls "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir my_transcripts
```

### Python Script Usage

```python
from whisper_transcription_bot import WhisperTranscriptionBot

# Initialize bot
bot = WhisperTranscriptionBot(output_dir="transcripts", model_size="base")

# Process videos
urls = ["https://www.youtube.com/watch?v=VIDEO_ID"]
results = bot.process_videos(urls, extract_frames=True)

# Save results
bot.save_jsonl(results, "my_transcripts.jsonl")
```

## Output Structure

```
transcripts/
├── talks_transcripts.jsonl          # Main output file
├── audio/                           # Downloaded audio files
│   ├── VIDEO_ID.wav
│   └── VIDEO_ID.info.json
├── frames/                          # Extracted video frames
│   ├── VIDEO_ID_frame_0000.png
│   ├── VIDEO_ID_frame_0030.png
│   └── ...
└── transcripts/                     # Additional transcript files
```

## Output Format

The `talks_transcripts.jsonl` file contains one JSON object per video:

```json
{
  "video_info": {
    "id": "VIDEO_ID",
    "title": "Video Title",
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "duration": 3600,
    "upload_date": "20230101",
    "channel": "Channel Name",
    "description": "Video description...",
    "audio_file": "transcripts/audio/VIDEO_ID.wav",
    "info_file": "transcripts/audio/VIDEO_ID.info.json"
  },
  "transcription": {
    "text": "Full transcription text...",
    "segments": [
      {
        "start": 0.0,
        "end": 5.0,
        "text": "Segment text...",
        "words": [
          {
            "start": 0.0,
            "end": 0.5,
            "word": "Word"
          }
        ]
      }
    ],
    "language": "en"
  },
  "ocr_results": [
    {
      "timestamp": 30,
      "text": "Text extracted from frame at 30 seconds",
      "frame_path": "transcripts/frames/VIDEO_ID_frame_0030.png"
    }
  ],
  "processed_at": "2023-01-01T12:00:00"
}
```

## Configuration

### Whisper Models

Available model sizes (larger = better accuracy, slower processing):
- **tiny**: Fastest, lowest accuracy
- **base**: Good balance (default)
- **small**: Better accuracy
- **medium**: High accuracy
- **large**: Best accuracy, slowest

### Frame Extraction

- **Frame Interval**: Extract frame every N seconds (default: 30)
- **Quality**: Limited to 720p for faster processing
- **OCR Processing**: Uses Tesseract with PSM 6 mode

## Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found
```
Error: FFmpeg not found
```
**Solution**: Install FFmpeg (see installation instructions above)

#### 2. Whisper Model Download Issues
```
Error: Model download failed
```
**Solution**: Check internet connection, try smaller model size

#### 3. YouTube Download Errors
```
Error: Video unavailable or restricted
```
**Solution**: Check if video is publicly available, try different video

#### 4. Memory Issues
**Solutions**:
- Use smaller Whisper model (`--model-size tiny`)
- Skip frame extraction (`--no-frames`)
- Process videos one at a time

#### 5. Tesseract OCR Issues
```
Error: TesseractNotFoundError
```
**Solution**: Install Tesseract OCR (see installation instructions)

### Performance Tips

1. **For Long Videos**: Use `--model-size tiny` for faster processing
2. **For High Accuracy**: Use `--model-size large` (requires more memory)
3. **For OCR Focus**: Reduce frame interval for more text extraction
4. **For Audio Only**: Use `--no-frames` to skip video processing

### Logging

The system creates detailed logs in `asr_transcription.log`:
- Download progress
- Transcription status
- OCR processing
- Error details

## Advanced Usage

### Custom Frame Extraction

```python
# Extract frames every 10 seconds instead of 30
frame_paths = bot.extract_video_frames(url, frame_interval=10)
```

### Custom OCR Processing

```python
# Process specific frames
for frame_path in frame_paths:
    text = bot.extract_text_from_frame(frame_path)
    if text:
        print(f"Found text: {text}")
```

### Batch Processing

```python
# Process multiple videos with different settings
urls = ["url1", "url2", "url3"]
results = []

for url in urls:
    try:
        result = bot.process_video(url, extract_frames=True)
        results.append(result)
    except Exception as e:
        print(f"Failed to process {url}: {e}")
        continue

bot.save_jsonl(results, "batch_results.jsonl")
```

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the transcription system. 