"""Utility functions and shared components for Singaporean-Accent TTS MVP.

This module provides common utilities for audio processing, configuration
management, logging, and other shared functionality.
"""

from .audio import AudioUtils, validate_audio_file, normalize_audio
from .config import load_config, get_env_var
from .logging import setup_logger, get_logger

__all__ = [
    "AudioUtils",
    "validate_audio_file", 
    "normalize_audio",
    "load_config",
    "get_env_var",
    "setup_logger",
    "get_logger",
]
