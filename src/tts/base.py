"""Base TTS engine interface for Singaporean-Accent TTS MVP.

This module provides the abstract base class that all TTS engines
must implement for consistent API across different models.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BaseTTSEngine(ABC):
    """Abstract base class for TTS inference engines.
    
    All TTS implementations (XTTS, Tortoise, etc.) must inherit from this
    class and implement the required methods for speaker embedding and
    speech generation.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """Initialize TTS engine.
        
        Args:
            model_path: Path to model files (None for default/auto-download)
            device: Target device ("cuda", "mps", "cpu", or "auto")
        """
        self.model_path = model_path
        self.device = self._detect_device(device)
        self.speaker_embedding = None
        logger.info(f"Initialized {self.__class__.__name__} on device: {self.device}")
    
    def _detect_device(self, device: str) -> str:
        """Detect and validate the compute device.
        
        Args:
            device: Requested device ("cuda", "mps", "cpu", or "auto")
            
        Returns:
            Valid device string
        """
        import torch
        
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            # Note: MPS has compatibility issues with XTTS (large convolutions not supported)
            # Force CPU on Mac for now
            # elif torch.backends.mps.is_available():
            #     return "mps"
            else:
                return "cpu"
        
        # Validate requested device
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA requested but not available, falling back to CPU")
            return "cpu"
        
        if device == "mps":
            logger.warning(
                "MPS requested but XTTS has known compatibility issues with MPS "
                "(convolutions >65536 channels not supported). Falling back to CPU."
            )
            return "cpu"
        
        return device
    
    @abstractmethod
    def build_speaker_embedding(
        self, 
        reference_clips: List[Path], 
        min_clips: int = 3
    ) -> np.ndarray:
        """Build speaker embedding from reference audio clips.
        
        Extracts voice characteristics from reference audio to enable
        voice cloning with the target accent and prosody.
        
        Args:
            reference_clips: List of paths to reference audio files
            min_clips: Minimum number of clips required
            
        Returns:
            Speaker embedding vector
            
        Raises:
            ValueError: If insufficient clips provided
            RuntimeError: If embedding extraction fails
        """
        pass
    
    @abstractmethod
    def generate_speech(
        self, 
        text: str,
        temperature: float = 0.7,
        repetition_penalty: float = 2.0,
        speed: float = 1.0,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """Generate speech from text using cloned voice.
        
        Args:
            text: Text to synthesize
            temperature: Sampling temperature (0.1-1.0, higher = more variation)
            repetition_penalty: Penalty for repetitive tokens (1.0-10.0)
            speed: Speech speed multiplier (0.5-2.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Tuple of (audio_array, sample_rate)
            
        Raises:
            RuntimeError: If generation fails
            ValueError: If speaker embedding not set
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata and capabilities.
        
        Returns:
            Dictionary with model information (name, version, capabilities)
        """
        pass
    
    def save_audio(
        self, 
        audio: np.ndarray, 
        sample_rate: int, 
        output_path: Path
    ) -> None:
        """Save generated audio to file.
        
        Args:
            audio: Audio array
            sample_rate: Sample rate in Hz
            output_path: Output file path (WAV format)
        """
        import soundfile as sf
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        sf.write(str(output_path), audio, sample_rate)
        logger.info(f"Saved audio to {output_path}")

