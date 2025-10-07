"""Gradio web interface for Singaporean-Accent TTS MVP.

This module provides an interactive web UI for generating speech with
Singaporean accent using XTTS v2 voice cloning technology.
"""

import argparse
import logging
from pathlib import Path
from typing import Tuple, Optional
import gradio as gr
import tempfile
import traceback

from src.tts.xtts_infer import XTTSInferenceEngine
from src.tts.tortoise_infer import TortoiseInferenceEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global engine instance (lazy loaded)
_engine_cache = {
    "xtts": None,
    "tortoise": None
}

# Singlish example sentences
SINGLISH_EXAMPLES = [
    "The weather today is quite hot, lah.",
    "Can you help me with this thing or not?",
    "I think we should go there first, then see how.",
    "Wah, this food very nice sia!",
    "Don't worry, everything will be okay one.",
    "You want to go shopping with me anot?",
    "Can lah, no problem one!",
    "Aiyah, don't like that lah!",
]


def get_engine(model_choice: str, device: str = "auto"):
    """Get or create TTS engine instance (with caching).
    
    Args:
        model_choice: Model choice from UI
        device: Compute device
        
    Returns:
        TTS engine instance
    """
    global _engine_cache
    
    engine_type = "xtts" if "XTTS" in model_choice else "tortoise"
    
    if _engine_cache[engine_type] is None:
        logger.info(f"Initializing {engine_type.upper()} engine...")
        try:
            if engine_type == "xtts":
                _engine_cache[engine_type] = XTTSInferenceEngine(device=device)
            else:
                _engine_cache[engine_type] = TortoiseInferenceEngine(device=device)
        except Exception as e:
            logger.error(f"Failed to initialize {engine_type} engine: {e}")
            raise
    
    return _engine_cache[engine_type]


def generate_speech(
    text: str,
    ref_folder: Optional[str],
    model_choice: str,
    temperature: float,
    seed: int
) -> Tuple[Optional[str], str]:
    """Generate speech from text input.
    
    Args:
        text: Text to synthesize
        ref_folder: Path to reference audio folder
        model_choice: TTS model to use (XTTS or Tortoise)
        temperature: Generation temperature (0.1-1.0)
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (audio_path, status_message)
    """
    try:
        # Validate inputs
        if not text or text.strip() == "":
            return None, "❌ Error: Please enter some text to generate speech."
        
        if not ref_folder:
            return None, "❌ Error: Please select a reference audio folder containing Singaporean accent samples."
        
        ref_path = Path(ref_folder)
        if not ref_path.exists():
            return None, f"❌ Error: Reference folder not found: {ref_folder}"
        
        # Check for audio files in reference folder
        audio_files = list(ref_path.glob("*.wav"))
        if len(audio_files) == 0:
            return None, f"❌ Error: No .wav files found in {ref_folder}. Please run 'make prepare' to process your reference audio first."
        
        logger.info(f"Found {len(audio_files)} reference audio files")
        logger.info(f"Generating speech with {model_choice}: '{text[:50]}...'")
        logger.info(f"Temperature: {temperature}, Seed: {seed}")
        
        status_msg = "🎤 **Generation Started**\n\n"
        status_msg += f"- Model: {model_choice}\n"
        status_msg += f"- Reference clips: {len(audio_files)} files\n"
        status_msg += f"- Text length: {len(text)} characters\n\n"
        
        # Set random seed
        if seed is not None:
            import torch
            import numpy as np
            torch.manual_seed(seed)
            np.random.seed(seed)
            status_msg += f"🎲 Set random seed: {seed}\n"
        
        # Check for Tortoise
        if "Tortoise" in model_choice:
            return None, (
                status_msg + "\n⚠️ **Tortoise-TTS Not Implemented**\n\n"
                "Tortoise-TTS requires additional dependencies and setup.\n"
                "Please select 'XTTS v2 (Fast)' instead.\n\n"
                "XTTS v2 provides excellent quality with much faster inference."
            )
        
        # Initialize engine
        status_msg += "🔄 Loading XTTS v2 model...\n"
        engine = get_engine(model_choice)
        status_msg += "✅ Model loaded\n\n"
        
        # Build speaker embedding
        status_msg += f"🎯 Building speaker profile from {len(audio_files)} clips...\n"
        engine.build_speaker_embedding(audio_files, min_clips=1)
        status_msg += "✅ Speaker profile ready\n\n"
        
        # Generate speech
        status_msg += "🎵 Generating speech...\n"
        audio, sample_rate = engine.generate_speech(
            text=text,
            temperature=temperature,
            repetition_penalty=2.0,
            speed=1.0
        )
        status_msg += f"✅ Generated {len(audio)/sample_rate:.2f}s of audio\n\n"
        
        # Save to temporary file for Gradio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            output_path = tmp_file.name
        
        engine.save_audio(audio, sample_rate, output_path)
        status_msg += f"💾 Audio saved temporarily\n"
        status_msg += f"📊 Sample rate: {sample_rate} Hz\n"
        status_msg += f"📏 Duration: {len(audio)/sample_rate:.2f} seconds\n\n"
        status_msg += "✨ **Generation Complete!**\n"
        status_msg += "You can now play or download the audio using the controls above."
        
        logger.info("✅ Speech generation successful")
        return output_path, status_msg
        
    except NotImplementedError as e:
        error_msg = f"⚠️ Feature Not Implemented\n\n{str(e)}"
        logger.warning(error_msg)
        return None, error_msg
        
    except Exception as e:
        error_msg = f"❌ **Error During Generation**\n\n{str(e)}\n\n"
        error_msg += "**Troubleshooting:**\n"
        error_msg += "- Ensure XTTS v2 model is downloaded (first run downloads automatically)\n"
        error_msg += "- Check that reference audio files are valid WAV format\n"
        error_msg += "- Try using a shorter text input\n"
        error_msg += "- Check terminal output for detailed error logs\n\n"
        error_msg += f"**Technical Details:**\n```\n{traceback.format_exc()}\n```"
        logger.error(error_msg, exc_info=True)
        return None, error_msg


def create_gradio_interface() -> gr.Blocks:
    """Create Gradio web interface for TTS generation.
    
    Returns:
        Gradio Blocks interface
    """
    with gr.Blocks(title="Singaporean-Accent TTS", theme=gr.themes.Soft()) as interface:
        gr.Markdown(
            """
            # 🇸🇬 Singaporean-Accent TTS Generator
            
            Generate English speech with authentic Singaporean accent using XTTS v2 voice cloning.
            
            **How to Use:**
            1. Enter text below (or select an example Singlish sentence)
            2. Verify reference audio folder points to your processed audio
            3. Adjust temperature (0.7 recommended) and other settings
            4. Click "Generate Speech" and wait ~5-10 seconds
            5. Play or download the generated audio!
            
            **First Run:** The XTTS v2 model (~1.8GB) will download automatically on first use.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                # Text input
                text_input = gr.Textbox(
                    label="Text to Synthesize",
                    placeholder="Enter English text with Singlish expressions...",
                    lines=4,
                    value=SINGLISH_EXAMPLES[0]
                )
                
                # Example sentences
                gr.Examples(
                    examples=[[text] for text in SINGLISH_EXAMPLES],
                    inputs=[text_input],
                    label="Example Singlish Sentences"
                )
                
                # Reference folder picker
                ref_folder_input = gr.Textbox(
                    label="Reference Audio Folder",
                    value="data/processed/audio",
                    placeholder="Path to folder containing Singaporean accent audio samples",
                    info="Folder should contain processed .wav files from your reference speakers"
                )
                
                with gr.Row():
                    # Model selector
                    model_selector = gr.Radio(
                        choices=["XTTS v2 (Fast)", "Tortoise-TTS (High Quality)"],
                        value="XTTS v2 (Fast)",
                        label="TTS Model",
                        info="XTTS is faster but Tortoise provides higher quality"
                    )
                
                with gr.Row():
                    # Generation parameters
                    temperature_slider = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=0.7,
                        step=0.1,
                        label="Temperature",
                        info="Higher = more prosody variation (0.6-0.8 recommended)"
                    )
                    
                    seed_input = gr.Number(
                        value=42,
                        label="Seed",
                        precision=0,
                        info="Random seed for reproducible generation"
                    )
                
                # Generate button
                generate_btn = gr.Button("🎤 Generate Speech", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                # Audio output
                audio_output = gr.Audio(
                    label="Generated Speech",
                    type="filepath",
                    interactive=False
                )
                
                # Status/log display
                status_output = gr.Textbox(
                    label="Generation Log",
                    lines=15,
                    max_lines=20,
                    interactive=False,
                    value="Ready to generate speech. Configure settings and click 'Generate Speech'."
                )
        
        # Footer with tips
        gr.Markdown(
            """
            ---
            
            ### 💡 Tips for Best Results
            
            - **Reference Audio**: Use 3-10 clips of 30s-2min each from Singaporean speakers
            - **Text Input**: Include natural Singlish particles like "lah", "leh", "sia", "lor"
            - **Temperature**: Start with 0.7, increase for more variation or decrease for consistency
            - **Processing Time**: XTTS takes 2-5 seconds per sentence, Tortoise takes 10-30 seconds
            
            ### 📚 Resources
            
            - Run `make help` to see all available commands
            - See `README.md` for detailed documentation
            - Check `src/eval/checklist.md` for accent evaluation criteria
            """
        )
        
        # Connect generate button to function
        generate_btn.click(
            fn=generate_speech,
            inputs=[
                text_input,
                ref_folder_input,
                model_selector,
                temperature_slider,
                seed_input
            ],
            outputs=[audio_output, status_output]
        )
    
    return interface


def main():
    """Main entry point for the Gradio application."""
    parser = argparse.ArgumentParser(
        description="Launch Gradio web interface for Singaporean-Accent TTS"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port number to use (default: 7860)"
    )
    parser.add_argument(
        "--share",
        type=str,
        default="false",
        choices=["true", "false"],
        help="Create public shareable link (default: false)"
    )
    
    args = parser.parse_args()
    share = args.share.lower() == "true"
    
    logger.info(f"🚀 Launching Singaporean-Accent TTS interface...")
    logger.info(f"📍 Server will be available at http://{args.host}:{args.port}")
    
    demo = create_gradio_interface()
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=share,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    main()

