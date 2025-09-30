#!/usr/bin/env python3
"""
Audio processing script for Singaporean-Accent TTS MVP.
Resamples, normalizes, and processes audio files for TTS training.
"""

import librosa
import soundfile as sf
import numpy as np
from pathlib import Path
import argparse
from loguru import logger
import pyloudnorm as pyln

def process_audio_files(processed_dir: Path) -> int:
    """
    Process audio files: resample to 16kHz, normalize loudness, convert to WAV.
    
    Args:
        processed_dir: Directory containing audio/ subdirectory with MP3 files
        
    Returns:
        Number of files processed
    """
    # Define input directory
    audio_dir = processed_dir / "audio"
    
    # Ensure directory exists
    if not audio_dir.exists():
        logger.error(f"Audio directory does not exist: {audio_dir}")
        return 0
    
    # Find all audio files in audio directory
    audio_files = list(audio_dir.glob('*.wav')) + list(audio_dir.glob('*.mp3'))
    logger.info(f"Processing {len(audio_files)} audio files from audio/ directory...")
    
    # Initialize loudness meter
    meter = pyln.Meter(16000)
    processed_count = 0
    
    for audio_file in audio_files:
        try:
            # Load audio at 16kHz mono
            y, sr = librosa.load(audio_file, sr=16000, mono=True)
            
            # Skip files that are too short (less than 2 seconds)
            if len(y) > 16000 * 2:
                # Normalize loudness to -23 LUFS (broadcast standard)
                loudness = meter.integrated_loudness(y)
                y_norm = pyln.normalize.loudness(y, loudness, -23.0)
                
                # Clip to prevent distortion
                y_norm = np.clip(y_norm, -1.0, 1.0)
                
                # Save as processed WAV file in same directory, replacing original
                # Change extension from .mp3 to .wav and keep folder-based naming
                out_path = audio_dir / f"{audio_file.stem}.wav"
                sf.write(out_path, y_norm, 16000)
                
                logger.info(f"  Processed: {audio_file.name} -> {out_path.name}")
                processed_count += 1
            else:
                logger.warning(f"  Skipped (too short): {audio_file.name}")
                
        except Exception as e:
            logger.error(f"  Error processing {audio_file.name}: {e}")
    
    logger.success(f"✅ Audio processing complete - {processed_count} files processed in audio/ directory")
    return processed_count

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description="Process audio files for TTS training")
    parser.add_argument("--segments-dir", type=Path, default="data/processed/segments",
                       help="Directory containing audio files to process")
    
    args = parser.parse_args()
    
    if not args.segments_dir.exists():
        logger.error(f"Segments directory does not exist: {args.segments_dir}")
        return 1
    
    try:
        processed_count = process_audio_files(args.segments_dir)
        if processed_count == 0:
            logger.warning("No audio files were processed")
            return 1
        return 0
    except Exception as e:
        logger.error(f"Audio processing failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
