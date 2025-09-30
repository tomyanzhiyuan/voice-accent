#!/usr/bin/env python3
"""
Download TTS models with PyTorch 2.7+ compatibility fix.
This script handles the weights_only security change in PyTorch 2.7.
"""

import os
import sys
import torch
from loguru import logger

def patch_torch_load():
    """Patch torch.load to use weights_only=False for TTS compatibility."""
    original_load = torch.load
    
    def patched_load(*args, **kwargs):
        # Force weights_only=False for TTS model loading
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    
    torch.load = patched_load
    logger.info("✅ Patched torch.load to use weights_only=False")

def download_xtts_model():
    """Download XTTS v2 model with proper error handling."""
    try:
        logger.info("🤖 Downloading XTTS v2 model...")
        
        # Patch torch.load for TTS compatibility
        patch_torch_load()
        
        # Import TTS after patching
        from TTS.api import TTS
        
        # Download and initialize the model
        tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cpu')
        
        logger.success("✅ XTTS v2 model downloaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download XTTS model: {e}")
        logger.info("💡 Error details:")
        logger.info(f"   {str(e)}")
        return False

def main():
    """Main function to download all required models."""
    logger.info("🚀 Starting model download process...")
    
    success = download_xtts_model()
    
    if success:
        logger.success("🎉 All models downloaded successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Model download failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
