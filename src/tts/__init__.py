"""TTS inference engines for Singaporean-Accent TTS MVP.

This module provides XTTS v2 and Tortoise-TTS engines for generating
speech with authentic Singaporean accent characteristics.
"""

from .base import BaseTTSEngine
from .xtts_infer import XTTSInferenceEngine
from .tortoise_infer import TortoiseInferenceEngine

__all__ = [
    "BaseTTSEngine",
    "XTTSInferenceEngine",
    "TortoiseInferenceEngine",
]
