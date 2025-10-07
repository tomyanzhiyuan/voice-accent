"""User interface components for Singaporean-Accent TTS MVP.

This module provides the Gradio web interface for interactive
speech generation with Singaporean accent.
"""

from .app import create_gradio_interface

__all__ = [
    "create_gradio_interface",
]
