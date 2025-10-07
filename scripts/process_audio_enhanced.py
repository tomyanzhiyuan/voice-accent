#!/usr/bin/env python3
"""
Enhanced audio processing CLI script.
Processes audio files through the complete enhanced pipeline.
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.enhanced_processor import EnhancedAudioProcessor


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced audio processing pipeline for TTS training data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with all enhancements (recommended)
  python scripts/process_audio_enhanced.py \\
    --input data/raw/realtalk-ep17/ \\
    --output data/processed/ \\
    --config config/processing_config.yaml \\
    --enable-all

  # Process with specific features
  python scripts/process_audio_enhanced.py \\
    --input data/raw/ \\
    --output data/processed/ \\
    --diarize --vad --quality-filter

  # Process single file
  python scripts/process_audio_enhanced.py \\
    --input data/raw/interview.mp3 \\
    --output data/processed/ \\
    --enable-all
        """
    )
    
    # Input/Output
    parser.add_argument(
        '--input', '-i',
        type=Path,
        required=True,
        help='Input audio file or directory'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Output directory for processed segments'
    )
    
    # Configuration
    parser.add_argument(
        '--config', '-c',
        type=Path,
        default=Path('config/processing_config.yaml'),
        help='Path to configuration YAML file (default: config/processing_config.yaml)'
    )
    
    # Feature flags
    parser.add_argument(
        '--enable-all',
        action='store_true',
        help='Enable all processing features'
    )
    parser.add_argument(
        '--diarize',
        action='store_true',
        help='Enable speaker diarization'
    )
    parser.add_argument(
        '--vad',
        action='store_true',
        help='Enable voice activity detection'
    )
    parser.add_argument(
        '--denoise',
        action='store_true',
        help='Enable noise reduction'
    )
    parser.add_argument(
        '--quality-filter',
        action='store_true',
        help='Enable quality filtering'
    )
    
    # Logging
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        type=Path,
        help='Save logs to file'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=args.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    
    if args.log_file:
        logger.add(
            args.log_file,
            level='DEBUG',
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
        )
    
    # Validate inputs
    if not args.input.exists():
        logger.error(f"Input path does not exist: {args.input}")
        return 1
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Load or create configuration
    if args.config.exists():
        logger.info(f"Using configuration: {args.config}")
        config_path = args.config
    else:
        logger.warning(f"Configuration file not found: {args.config}")
        logger.info("Using default configuration")
        config_path = None
    
    try:
        # Initialize processor
        logger.info("Initializing enhanced audio processor...")
        processor = EnhancedAudioProcessor(config_path=config_path)
        
        # Override configuration with CLI flags
        if args.enable_all:
            processor.config['diarization']['enabled'] = True
            processor.config['vad']['enabled'] = True
            processor.config['noise_reduction']['enabled'] = True
            logger.info("All features enabled")
        else:
            if args.diarize:
                processor.config['diarization']['enabled'] = True
                logger.info("Speaker diarization enabled")
            if args.vad:
                processor.config['vad']['enabled'] = True
                logger.info("VAD enabled")
            if args.denoise:
                processor.config['noise_reduction']['enabled'] = True
                logger.info("Noise reduction enabled")
            if args.quality_filter:
                # Quality filter is always enabled
                logger.info("Quality filtering enabled")
        
        # Re-initialize modules with updated config
        processor._init_modules()
        
        # Process input
        if args.input.is_file():
            logger.info(f"Processing single file: {args.input.name}")
            stats = processor.process_file(args.input, args.output)
        else:
            logger.info(f"Processing directory: {args.input}")
            stats = processor.process_directory(args.input, args.output)
        
        # Print summary
        logger.success("\n" + "="*60)
        logger.success("PROCESSING COMPLETE")
        logger.success("="*60)
        logger.success(f"Files processed: {stats['files_processed']}")
        logger.success(f"Total duration: {stats['total_duration']:.1f}s")
        logger.success(f"Speakers detected: {stats['speakers_detected']}")
        logger.success(f"Segments generated: {stats['segments_generated']}")
        logger.success(f"Segments rejected: {stats['segments_rejected']}")
        
        if stats['rejection_reasons']:
            logger.info("\nRejection reasons:")
            for reason, count in stats['rejection_reasons'].items():
                logger.info(f"  {reason}: {count}")
        
        logger.success(f"\nOutput saved to: {args.output}")
        logger.success("="*60 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\nProcessing interrupted by user")
        return 130
    
    except Exception as e:
        logger.exception(f"Processing failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
