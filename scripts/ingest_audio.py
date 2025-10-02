#!/usr/bin/env python3
"""
Audio ingestion script for Singaporean-Accent TTS MVP.
Recursively finds and copies audio files from raw to processed directory.
"""

import os
import shutil
from pathlib import Path
import argparse
from loguru import logger

def ingest_audio_files(raw_dir: Path, output_dir: Path) -> int:
    """
    Find and copy audio files from organized raw directory folders to processed/audio.
    
    Args:
        raw_dir: Source directory containing organized folders (e.g., realtalk-ep17, soniachew-xixi)
        output_dir: Destination directory for processed files (will create audio/ subdirectory)
        
    Returns:
        Number of files copied
    """
    # Create new organized directory structure
    audio_output_dir = output_dir / "audio"
    audio_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Supported audio extensions
    audio_exts = ['*.wav', '*.mp3', '*.flac', '*.m4a', '*.ogg']
    
    # Find all audio files in organized folders
    files_found = []
    folder_mapping = {}  # Track which folder each file came from
    
    for ext in audio_exts:
        for audio_file in raw_dir.rglob(ext):
            files_found.append(audio_file)
            # Get the immediate parent folder name (e.g., realtalk-ep17, soniachew-xixi)
            folder_name = audio_file.parent.name
            if folder_name != raw_dir.name:  # Skip if it's directly in raw dir
                folder_mapping[audio_file] = folder_name
    
    logger.info(f"Found {len(files_found)} audio files in organized folders")
    
    # Copy files with folder-based naming (skip if already exists)
    copied_count = 0
    skipped_count = 0
    for src in files_found:
        try:
            # Get folder name for prefix
            folder_name = folder_mapping.get(src, "unknown")
            
            # Create filename with folder prefix: folder-name-original-filename
            new_name = f"{folder_name}-{src.name}"
            dst = audio_output_dir / new_name
            
            # Skip if destination file already exists
            if dst.exists():
                logger.info(f"  Skipped (already exists): {folder_name}/{src.name} -> audio/{dst.name}")
                skipped_count += 1
                continue
            
            shutil.copy2(src, dst)
            logger.info(f"  Copied: {folder_name}/{src.name} -> audio/{dst.name}")
            copied_count += 1
        except Exception as e:
            logger.error(f"  Error copying {src.name}: {e}")
    
    if skipped_count > 0:
        logger.success(f"✅ Audio ingestion complete - {copied_count} files copied, {skipped_count} files skipped (already exist)")
    else:
        logger.success(f"✅ Audio ingestion complete - {copied_count} files copied to audio/ directory")
    return copied_count

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description="Ingest audio files for TTS training")
    parser.add_argument("--raw-dir", type=Path, default="data/raw", 
                       help="Source directory containing audio files")
    parser.add_argument("--output-dir", type=Path, default="data/processed/segments",
                       help="Output directory for processed files")
    
    args = parser.parse_args()
    
    if not args.raw_dir.exists():
        logger.error(f"Raw directory does not exist: {args.raw_dir}")
        return 1
    
    try:
        copied_count = ingest_audio_files(args.raw_dir, args.output_dir)
        # Success even if no files were copied (they might already exist)
        return 0
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
