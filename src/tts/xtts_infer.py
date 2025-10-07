"""XTTS v2 inference engine for Singaporean-Accent TTS MVP.

This module implements voice cloning using Coqui XTTS v2, which provides
fast, high-quality few-shot voice cloning from reference audio clips.
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import torch
import logging

from .base import BaseTTSEngine

logger = logging.getLogger(__name__)


class XTTSInferenceEngine(BaseTTSEngine):
    """XTTS v2 inference engine for voice cloning.
    
    Uses Coqui XTTS v2 model for few-shot voice cloning with support
    for preserving accent characteristics and prosodic patterns.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """Initialize XTTS inference engine.
        
        Args:
            model_path: Path to XTTS model files (None for auto-download)
            device: Target device ("cuda", "mps", "cpu", or "auto")
        """
        super().__init__(model_path, device)
        self.model = None
        self.gpt_cond_latent = None
        self.speaker_embedding = None
        self._load_model()
    
    def _patch_torch_load(self) -> None:
        """Patch torch.load to use weights_only=False for compatibility with PyTorch 2.6+.
        
        PyTorch 2.6 changed the default weights_only from False to True for security.
        TTS models need to load custom classes, so we need weights_only=False.
        """
        import torch
        original_load = torch.load
        
        def patched_load(*args, **kwargs):
            # Force weights_only=False if not explicitly set
            if 'weights_only' not in kwargs:
                kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        
        torch.load = patched_load
        logger.info("✅ Patched torch.load to use weights_only=False for TTS compatibility")
    
    def _load_model(self) -> None:
        """Load XTTS v2 model from Coqui TTS."""
        try:
            # Patch torch.load for PyTorch 2.6+ compatibility
            self._patch_torch_load()
            
            from TTS.api import TTS
            
            logger.info("Loading XTTS v2 model...")
            
            # Initialize TTS with XTTS v2
            # Use tts_models/multilingual/multi-dataset/xtts_v2
            self.model = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                progress_bar=True
            ).to(self.device)
            
            logger.info("✅ XTTS v2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load XTTS v2 model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def build_speaker_embedding(
        self, 
        reference_clips: List[Path], 
        min_clips: int = 1
    ) -> np.ndarray:
        """Build speaker embedding from reference audio clips.
        
        For XTTS v2, we use the first reference clip to compute the
        speaker embedding (latent representation).
        
        Args:
            reference_clips: List of paths to reference audio files
            min_clips: Minimum number of clips required (XTTS needs at least 1)
            
        Returns:
            Speaker embedding vector (stored internally)
            
        Raises:
            ValueError: If insufficient clips provided or invalid audio
        """
        if len(reference_clips) < min_clips:
            raise ValueError(
                f"Need at least {min_clips} reference clip(s), got {len(reference_clips)}"
            )
        
        # Filter out non-existent files
        valid_clips = [clip for clip in reference_clips if Path(clip).exists()]
        
        if len(valid_clips) < min_clips:
            raise ValueError(
                f"Only {len(valid_clips)} valid audio files found out of {len(reference_clips)}"
            )
        
        logger.info(f"Building speaker embedding from {len(valid_clips)} reference clips")
        
        # Use the first reference clip for speaker embedding
        # (XTTS v2 can work with a single reference audio)
        reference_audio = str(valid_clips[0])
        
        try:
            # The speaker embedding is computed internally by XTTS
            # We just store the reference audio path for generation
            self.reference_audio = reference_audio
            self.speaker_embedding = reference_audio  # Store for compatibility
            
            logger.info(f"✅ Speaker embedding built from: {Path(reference_audio).name}")
            return np.array([reference_audio])  # Return dummy array
            
        except Exception as e:
            logger.error(f"Failed to build speaker embedding: {e}")
            raise RuntimeError(f"Speaker embedding failed: {e}")
    
    def generate_speech(
        self, 
        text: str,
        temperature: float = 0.7,
        repetition_penalty: float = 2.0,
        speed: float = 1.0,
        language: str = "en",
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """Generate speech from text using cloned voice.
        
        Args:
            text: Text to synthesize
            temperature: Sampling temperature (0.1-1.0)
            repetition_penalty: Penalty for repetitive tokens
            speed: Speech speed multiplier (0.5-2.0)
            language: Language code (default: "en")
            **kwargs: Additional XTTS parameters
            
        Returns:
            Tuple of (audio_array, sample_rate)
            
        Raises:
            ValueError: If speaker embedding not set
            RuntimeError: If generation fails
        """
        if self.speaker_embedding is None:
            raise ValueError(
                "Speaker embedding not set. Call build_speaker_embedding() first."
            )
        
        if not text or text.strip() == "":
            raise ValueError("Text cannot be empty")
        
        logger.info(f"Generating speech for text: '{text[:50]}...'")
        logger.info(f"Parameters - temp: {temperature}, rep_penalty: {repetition_penalty}, speed: {speed}")
        
        try:
            # Generate speech using XTTS v2
            # Note: XTTS generates to a file, so we need to use a temp file
            import tempfile
            import soundfile as sf
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Generate audio
            self.model.tts_to_file(
                text=text,
                file_path=tmp_path,
                speaker_wav=self.reference_audio,
                language=language,
                temperature=temperature,
                repetition_penalty=repetition_penalty,
                speed=speed
            )
            
            # Read the generated audio
            audio, sample_rate = sf.read(tmp_path)
            
            # Clean up temp file
            Path(tmp_path).unlink()
            
            logger.info(f"✅ Generated {len(audio)/sample_rate:.2f}s of audio at {sample_rate}Hz")
            
            return audio, sample_rate
            
        except Exception as e:
            logger.error(f"Speech generation failed: {e}", exc_info=True)
            raise RuntimeError(f"Generation failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get XTTS v2 model information.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "name": "XTTS v2",
            "type": "Few-shot Voice Cloning",
            "provider": "Coqui TTS",
            "device": self.device,
            "sample_rate": 24000,
            "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn"],
            "features": [
                "Few-shot voice cloning",
                "Multi-language support",
                "Fast inference",
                "Accent preservation"
            ]
        }


def main():
    """Command-line interface for XTTS inference."""
    import argparse
    import soundfile as sf
    
    parser = argparse.ArgumentParser(description="Generate speech using XTTS v2")
    parser.add_argument("--text", type=str, required=True, help="Text to synthesize")
    parser.add_argument("--ref-dir", type=Path, required=True, help="Reference audio directory")
    parser.add_argument("--output", type=Path, required=True, help="Output WAV file")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature (0.1-1.0)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--device", type=str, default="auto", help="Device (cuda/mps/cpu/auto)")
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        torch.manual_seed(args.seed)
        np.random.seed(args.seed)
    
    # Initialize engine
    logger.info("Initializing XTTS v2 engine...")
    engine = XTTSInferenceEngine(device=args.device)
    
    # Find reference audio files
    ref_dir = Path(args.ref_dir)
    ref_clips = list(ref_dir.glob("*.wav"))
    
    if not ref_clips:
        logger.error(f"No WAV files found in {ref_dir}")
        return 1
    
    logger.info(f"Found {len(ref_clips)} reference clips")
    
    # Build speaker embedding
    engine.build_speaker_embedding(ref_clips)
    
    # Generate speech
    audio, sr = engine.generate_speech(
        text=args.text,
        temperature=args.temperature
    )
    
    # Save output
    engine.save_audio(audio, sr, args.output)
    logger.info(f"✅ Generation complete: {args.output}")
    
    return 0


if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    sys.exit(main())

