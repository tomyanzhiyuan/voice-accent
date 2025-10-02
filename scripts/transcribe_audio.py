#!/usr/bin/env python3
"""
Audio transcription script for Singaporean-Accent TTS MVP.
Uses OpenAI Whisper to generate transcripts for processed audio files.
"""

import whisper
import json
from pathlib import Path
import argparse
from loguru import logger

def transcribe_audio_files(processed_dir: Path, transcripts_dir: Path, model_name: str = "small.en") -> int:
    """
    Transcribe audio files using Whisper.
    
    Args:
        processed_dir: Directory containing audio/ subdirectory with WAV files
        transcripts_dir: Directory to save transcripts
        model_name: Whisper model to use
        
    Returns:
        Number of files transcribed
    """
    # Define audio directory
    audio_dir = processed_dir / "audio"
    
    # Ensure directories exist
    if not audio_dir.exists():
        logger.error(f"Audio directory does not exist: {audio_dir}")
        return 0
    
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Whisper model
    logger.info(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name)
    
    # Find processed WAV files (with folder-based naming)
    audio_files = list(audio_dir.glob('*.wav'))
    logger.info(f"Transcribing {len(audio_files)} audio files from audio/ directory...")
    
    transcribed_count = 0
    skipped_count = 0
    
    for audio_file in audio_files:
        try:
            # Define transcript output path
            transcript_file = transcripts_dir / f"{audio_file.stem}.json"
            
            # Skip if transcript already exists and is newer than audio file
            if transcript_file.exists() and transcript_file.stat().st_mtime >= audio_file.stat().st_mtime:
                logger.info(f"  Skipped (already transcribed): audio/{audio_file.name}")
                skipped_count += 1
                continue
            
            # Transcribe audio
            result = model.transcribe(str(audio_file), language='en')
            
            # Save transcript as JSON with matching name
            transcript_data = {
                'file': f"audio/{audio_file.name}",
                'text': result['text'],
                'segments': result['segments']
            }
            
            with open(transcript_file, 'w') as f:
                json.dump(transcript_data, f, indent=2)
            
            logger.info(f"  Transcribed: audio/{audio_file.name}")
            transcribed_count += 1
            
        except Exception as e:
            logger.error(f"  Error transcribing {audio_file.name}: {e}")
    
    if skipped_count > 0:
        logger.success(f"✅ Transcription complete - {transcribed_count} files transcribed, {skipped_count} files skipped (already transcribed)")
    else:
        logger.success(f"✅ Transcription complete - {transcribed_count} files transcribed")
    return transcribed_count

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description="Transcribe audio files using Whisper")
    parser.add_argument("--segments-dir", type=Path, default="data/processed/segments",
                       help="Directory containing processed audio files")
    parser.add_argument("--transcripts-dir", type=Path, default="data/processed/transcripts",
                       help="Directory to save transcripts")
    parser.add_argument("--model", type=str, default="small.en",
                       help="Whisper model to use (tiny, base, small, medium, large)")
    
    args = parser.parse_args()
    
    if not args.segments_dir.exists():
        logger.error(f"Segments directory does not exist: {args.segments_dir}")
        return 1
    
    try:
        transcribed_count = transcribe_audio_files(args.segments_dir, args.transcripts_dir, args.model)
        # Success even if no files were transcribed (they might already be transcribed)
        return 0
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
