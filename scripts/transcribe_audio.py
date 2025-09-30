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

def transcribe_audio_files(segments_dir: Path, transcripts_dir: Path, model_name: str = "small.en") -> int:
    """
    Transcribe audio files using Whisper.
    
    Args:
        segments_dir: Directory containing raw/ and processed/ subdirectories
        transcripts_dir: Directory to save transcripts
        model_name: Whisper model to use
        
    Returns:
        Number of files transcribed
    """
    # Define processed audio directory
    processed_dir = segments_dir / "processed"
    
    # Ensure directories exist
    if not processed_dir.exists():
        logger.error(f"Processed directory does not exist: {processed_dir}")
        return 0
    
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Whisper model
    logger.info(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name)
    
    # Find processed audio files
    audio_files = list(processed_dir.glob('*_processed.wav'))
    logger.info(f"Transcribing {len(audio_files)} audio files from processed/ directory...")
    
    transcribed_count = 0
    
    for audio_file in audio_files:
        try:
            # Transcribe audio
            result = model.transcribe(str(audio_file), language='en')
            
            # Save transcript as JSON
            transcript_file = transcripts_dir / f"{audio_file.stem}.json"
            transcript_data = {
                'file': f"processed/{audio_file.name}",
                'text': result['text'],
                'segments': result['segments']
            }
            
            with open(transcript_file, 'w') as f:
                json.dump(transcript_data, f, indent=2)
            
            logger.info(f"  Transcribed: processed/{audio_file.name}")
            transcribed_count += 1
            
        except Exception as e:
            logger.error(f"  Error transcribing {audio_file.name}: {e}")
    
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
        if transcribed_count == 0:
            logger.warning("No audio files were transcribed")
            return 1
        return 0
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
