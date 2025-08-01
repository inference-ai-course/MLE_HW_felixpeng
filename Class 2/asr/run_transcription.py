#!/usr/bin/env python3
"""
Run transcription on the specified YouTube videos
"""

from whisper_transcription_bot import WhisperTranscriptionBot

def main():
    # YouTube video URLs to process
    video_urls = [
        "https://www.youtube.com/watch?v=fOvTtapxa9c",
        "https://www.youtube.com/watch?v=fLvJ8VdHLA0", 
        "https://www.youtube.com/watch?v=1I6bQ12VxV0",
        "https://www.youtube.com/watch?v=aircAruvnKk"
    ]
    
    print("🎤 Whisper Transcription Bot")
    print("=" * 50)
    print(f"Processing {len(video_urls)} videos...")
    print()
    
    # Initialize the transcription bot
    bot = WhisperTranscriptionBot(
        output_dir="transcripts",
        model_size="base"  # Use base model for faster processing
    )
    
    # Process all videos
    results = bot.process_videos(video_urls, extract_frames=True)
    
    # Save results
    if results:
        bot.save_jsonl(results, "talks_transcripts.jsonl")
        
        print(f"\n{'='*60}")
        print("TRANSCRIPTION COMPLETED")
        print(f"{'='*60}")
        print(f"✅ Successfully processed {len(results)} videos")
        print(f"📁 Output saved to: transcripts/talks_transcripts.jsonl")
        print(f"🎵 Audio files: transcripts/audio/")
        print(f"🖼️  Video frames: transcripts/frames/")
        
        # Show summary for each video
        for i, result in enumerate(results, 1):
            video_info = result['video_info']
            transcription = result['transcription']
            ocr_results = result['ocr_results']
            
            print(f"\n📹 Video {i}: {video_info['title']}")
            print(f"   ⏱️  Duration: {video_info['duration']} seconds")
            print(f"   🗣️  Transcription segments: {len(transcription.get('segments', []))}")
            print(f"   📝 OCR text blocks: {len(ocr_results)}")
            
            # Show first few words of transcription
            if 'text' in transcription:
                preview = transcription['text'][:100] + "..." if len(transcription['text']) > 100 else transcription['text']
                print(f"   💬 Preview: {preview}")
        
        print(f"\n🎉 All transcriptions completed successfully!")
        
    else:
        print("❌ No videos were processed successfully")

if __name__ == "__main__":
    main() 