# Singaporean-Accent TTS MVP

A minimal viable product for generating English speech with authentic Singaporean accent using XTTS v2 and Tortoise-TTS voice cloning technology.

## 🎯 Quick Start (5 Minutes)

```bash
# Prerequisites: Install conda (Miniconda or Anaconda)
# https://docs.conda.io/en/latest/miniconda.html

# Clone and setup with conda
cd voice-accent
make setup

# Activate the conda environment
conda activate voice-accent

# Add your Singaporean accent reference clips to data/raw/refs/
# (3-10 audio files, 30s-2min each, WAV/MP3 format)

# Process reference audio
make prepare

# Launch web interface
make ui

# Generate demo audio
make demo
```

Open http://localhost:7860 in your browser and start generating Singaporean-accented speech!

**✅ Now using Conda for dependency management** - eliminates version conflicts and provides better ML library support!

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Reference Audio Guide](#reference-audio-guide)
- [API Reference](#api-reference)
- [Evaluation Framework](#evaluation-framework)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)

## 🌟 Overview

This project implements a complete pipeline for generating English speech with authentic Singaporean accent characteristics including:

- **Phonetic Features**: TH-stopping (thing→ting), final consonant deletion (want→wan)
- **Prosodic Patterns**: Syllable-timed rhythm, rising intonation
- **Voice Cloning**: Few-shot learning from 3-10 reference audio clips
- **Dual Engines**: XTTS v2 (fast) and Tortoise-TTS (high quality)

### Technical Architecture

```
Reference Audio → Audio Processing → Speaker Embedding → TTS Generation
     ↓                    ↓                 ↓               ↓
  data/raw/refs/    data/processed/    Voice Profile    outputs/
```

## ✨ Features

### 🎤 Voice Cloning

- **Few-shot Learning**: Generate accent from 3-10 reference clips
- **Dual TTS Engines**: XTTS v2 (primary) + Tortoise-TTS (fallback)
- **Quality Tiers**: 30s demo → 5min good → 30min premium quality

### 🎵 Audio Processing

- **Format Support**: WAV, MP3, OGG input formats
- **Auto-Processing**: 16kHz mono, normalized, segmented
- **Quality Validation**: Noise detection, clipping analysis

### 🌐 Web Interface

- **Gradio UI**: Intuitive web interface with real-time generation
- **Pre-filled Examples**: Singlish sentences for testing
- **Model Selection**: Switch between XTTS and Tortoise engines
- **Parameter Control**: Temperature, seed, generation settings

### 📊 Evaluation Tools

- **Accent Checklist**: Phonetic and prosodic feature assessment
- **A/B Testing**: Compare generated vs reference audio
- **Quality Metrics**: Intelligibility, naturalness, authenticity scores

## 🚀 Installation

### System Requirements

- **OS**: macOS 10.15+ (tested), Linux, Windows WSL2
- **Python**: 3.11 (Anything newer isn't fully supported)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 5-10GB for models and audio data
- **GPU**: Optional (CUDA/MPS), 3-5x speedup when available

### Prerequisites

Install system dependencies:

```bash
# macOS (using Homebrew)
brew install ffmpeg git-lfs

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg git-lfs

# Verify installation
ffmpeg -version
```

### Python Environment Setup

```bash
# Navigate to project directory
cd voice-accent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify PyTorch installation
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

### Automated Setup

Use the Makefile for one-command setup:

```bash
make setup
```

This will:

1. Create Python virtual environment
2. Install all dependencies with proper versions
3. Download required TTS models
4. Verify FFmpeg and system dependencies
5. Create necessary directories
6. Run basic functionality tests

## 📖 Usage

### 1. Prepare Reference Audio

Add Singaporean-accented English audio files to `data/raw/refs/`:

```bash
# Example file structure
data/raw/refs/
├── speaker1_conversation.wav
├── speaker2_interview.mp3
├── speaker3_reading.wav
└── speaker4_casual.mp3
```

**Audio Requirements**:

- **Duration**: 30 seconds to 2 minutes per file
- **Quality**: Clear speech, minimal background noise
- **Content**: Natural conversational English with Singaporean accent
- **Format**: WAV (preferred) or MP3

### 2. Process Audio Pipeline

```bash
# Run complete processing pipeline (intelligent skip logic - only processes new/changed files)
make prepare

# Or run individual steps
python -m src.data.ingest      # Copy and validate audio files
python -m src.data.prepare     # Resample, normalize, segment
python -m src.data.transcribe  # Generate transcripts with Whisper
```

**✨ Smart Processing**: The pipeline now intelligently skips files that have already been processed, making subsequent runs much faster. Only new or modified files will be reprocessed.

### 3. Launch Web Interface

```bash
make ui
```

Open http://localhost:7860 in your browser. The interface includes:

- **Reference Folder**: Select processed audio directory
- **Text Input**: Enter text to synthesize (try the Singlish examples!)
- **Model Selection**: Choose XTTS (fast) or Tortoise (quality)
- **Parameters**: Adjust temperature, seed for variation
- **Generate**: Create and play Singaporean-accented speech

### 4. Generate Demo Audio

```bash
make demo
```

Creates `outputs/demo.wav` with sample Singlish text using your reference clips.

### 5. Programmatic Usage

```python
from src.tts.xtts_infer import XTTSInferenceEngine
from pathlib import Path

# Initialize engine
engine = XTTSInferenceEngine(device="auto")

# Build speaker embedding from reference clips
ref_clips = list(Path("data/processed/segments").glob("*.wav"))
engine.build_speaker_embedding(ref_clips)

# Generate speech
text = "The weather today is quite hot, lah."
audio, sample_rate = engine.generate_speech(text, temperature=0.7)

# Save output
import soundfile as sf
sf.write("output.wav", audio, sample_rate)
```

## 🎤 Reference Audio Guide

### Quality Tiers

| Duration | Quality Level | Characteristics                   |
| -------- | ------------- | --------------------------------- |
| 30-60s   | Demo          | Basic accent, unstable prosody    |
| 5-10min  | Good          | Stable accent, recommended for v1 |
| 30-60min | Premium       | High fidelity, varied expressions |

### Recording Tips

**Content Suggestions**:

- Casual conversations with friends/family
- Reading news articles or stories aloud
- Phone calls or video calls (with permission)
- Podcast segments or interview clips

**Technical Quality**:

- Use quiet environment (minimal echo, background noise)
- Consistent distance from microphone
- Avoid music, overlapping speech, long silences
- Natural speaking pace and intonation

**Accent Authenticity**:

- Include varied vocabulary and sentence structures
- Natural use of Singaporean English features
- Conversational tone rather than formal reading
- Multiple speakers if available for diversity

### Privacy & Consent

⚠️ **Important**: Only use audio with explicit permission from speakers. This system is designed for:

- Personal voice cloning (your own voice)
- Family/friends with clear consent
- Public domain or Creative Commons audio
- Educational/research purposes with proper attribution

## 🔧 API Reference

### Command Line Interface

```bash
# Setup and environment
make setup          # Complete environment setup
make clean          # Remove processed files and outputs
make test           # Run test suite with coverage
make lint           # Code formatting and linting

# Data processing
make prepare        # Full audio processing pipeline
python -m src.data.ingest --input data/raw --output data/processed
python -m src.data.prepare --normalize --segment-length 10
python -m src.data.transcribe --model small.en --language en

# TTS generation
make demo           # Generate demo with default settings
python -m src.tts.xtts_infer --text "Hello world" --output demo.wav
python -m src.tts.tortoise_infer --text "Hello world" --quality high

# Web interface
make ui             # Launch Gradio on localhost:7860
python -m src.ui.app --port 7860 --share False
```

### Python API

#### XTTS Engine

```python
from src.tts.xtts_infer import XTTSInferenceEngine

engine = XTTSInferenceEngine(
    model_path="models/xtts_v2",
    device="auto"  # "cuda", "cpu", or "auto"
)

# Build speaker profile
ref_clips = ["clip1.wav", "clip2.wav", "clip3.wav"]
embedding = engine.build_speaker_embedding(ref_clips, min_clips=3)

# Generate speech
audio, sr = engine.generate_speech(
    text="Your text here",
    temperature=0.7,    # Prosody variation (0.1-1.0)
    seed=42            # Reproducible generation
)
```

#### Tortoise Engine

```python
from src.tts.tortoise_infer import TortoiseInferenceEngine

engine = TortoiseInferenceEngine(
    model_path="models/tortoise",
    quality="standard"  # "ultra_fast", "fast", "standard", "high"
)

# Voice cloning setup
engine.setup_voice_cloning(ref_clips, voice_name="singaporean")

# Generate with quality control
audio, sr = engine.generate_speech(
    text="Your text here",
    voice="singaporean",
    preset="standard",
    candidates=1  # Number of generations to choose from
)
```

#### Audio Processing

```python
from src.data.prepare import AudioProcessor

processor = AudioProcessor(
    target_sr=16000,
    target_loudness=-23,  # LUFS
    max_segment_length=10  # seconds
)

# Process single file
metadata = processor.process_file(
    input_path="raw_audio.mp3",
    output_dir="processed/"
)

# Batch processing
results = processor.process_directory(
    input_dir="data/raw/refs/",
    output_dir="data/processed/segments/"
)
```

## 📊 Evaluation Framework

### Accent Assessment Checklist

Use `src/eval/checklist.md` for systematic evaluation:

#### Phonetic Features (1-5 scale)

- **TH-stopping**: "thing" → "ting", "that" → "dat"
- **Final consonant deletion**: "want" → "wan", "and" → "an"
- **Vowel system**: Singaporean English vowel inventory
- **Consonant clusters**: Simplification patterns

#### Prosodic Features (1-5 scale)

- **Rhythm**: Syllable-timed vs stress-timed patterns
- **Intonation**: Rising final intonation, question patterns
- **Stress**: Even syllable prominence
- **Pace**: Natural conversational speed

#### Overall Quality (1-5 scale)

- **Naturalness**: Sounds like native Singaporean speaker
- **Intelligibility**: Clear and understandable
- **Consistency**: Stable accent throughout
- **Authenticity**: Recognizable as Singaporean accent

### A/B Testing Framework

```python
from src.eval.assessment import AccentEvaluator

evaluator = AccentEvaluator()

# Compare generated vs reference
scores = evaluator.compare_audio(
    generated_path="outputs/generated.wav",
    reference_path="data/raw/refs/reference.wav",
    metrics=["phonetic", "prosodic", "overall"]
)

print(f"Accent similarity: {scores['accent_similarity']:.2f}")
print(f"Quality score: {scores['quality']:.2f}")
```

## 🔧 Troubleshooting

### Common Issues

#### Installation Problems

**FFmpeg not found**:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian  
sudo apt install ffmpeg

# Verify
ffmpeg -version
```

**PyTorch CUDA issues**:

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA support
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Memory errors during model loading**:

```bash
# Use CPU-only mode
export ACCENT_TTS_DEVICE=cpu

# Or reduce batch size
export ACCENT_TTS_BATCH_SIZE=1
```

#### Audio Processing Issues

**"No audio files found"**:

- Check file formats (WAV, MP3, OGG supported)
- Verify file permissions (readable by Python)
- Ensure files are not corrupted

**"Audio too short/long"**:

- Reference clips should be 30s-2min each
- Use `--min-duration` and `--max-duration` flags
- Check audio segmentation settings

**"Poor audio quality"**:

- Use quiet recording environment
- Avoid compressed/low-bitrate files
- Check for clipping or distortion

#### TTS Generation Issues

**"Speaker embedding failed"**:

- Need at least 3 reference clips
- Ensure clips contain clear speech
- Check audio preprocessing completed successfully

**"Generation too slow"**:

- Use XTTS instead of Tortoise for speed
- Enable GPU acceleration if available
- Reduce text length for testing

**"Poor accent quality"**:

- Use more/better reference clips (5-10 recommended)
- Ensure reference audio has strong Singaporean accent
- Try different temperature settings (0.5-0.9)

### Performance Optimization

#### GPU Acceleration

```bash
# Check GPU availability
nvidia-smi  # NVIDIA GPUs
system_profiler SPDisplaysDataType | grep Metal  # Apple Silicon

# Enable GPU in environment
export ACCENT_TTS_DEVICE=cuda  # or "mps" for Apple Silicon
```

#### Memory Management

```bash
# Reduce memory usage
export ACCENT_TTS_LOW_MEMORY=true
export ACCENT_TTS_BATCH_SIZE=1

# Clear model cache
python -c "from src.tts.xtts_infer import clear_model_cache; clear_model_cache()"
```

### Getting Help

1. **Check logs**: `tail -f logs/accent_tts.log`
2. **Run diagnostics**: `make test`
3. **Verify setup**: `python -m src.utils.diagnostics`
4. **GitHub Issues**: Report bugs with system info and logs

## 🛠 Development

### Project Structure

```
accent-tts/
├── src/                    # Source code
│   ├── data/              # Audio processing pipeline
│   ├── tts/               # TTS inference engines
│   ├── ui/                # Gradio web interface
│   ├── eval/              # Evaluation framework
│   └── utils/             # Shared utilities
├── tests/                 # Test suite
├── config/                # Configuration files
├── docs/                  # Additional documentation
└── scripts/               # Utility scripts
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov=src

# Code formatting
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Adding New TTS Engines

1. Inherit from `BaseTTSEngine` in `src/tts/base.py`
2. Implement required methods: `build_speaker_embedding`, `generate_speech`
3. Add engine to `src/tts/__init__.py`
4. Update UI model selector in `src/ui/app.py`
5. Add tests in `tests/tts/test_new_engine.py`

### Contributing Guidelines

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Follow** code standards in `.clinerules`
4. **Add** tests for new functionality
5. **Update** documentation as needed
6. **Commit** with conventional format: `feat(tts): add new engine`
7. **Push** and create Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Coqui TTS**: XTTS v2 model and inference engine
- **Tortoise-TTS**: High-quality voice cloning technology
- **OpenAI Whisper**: Speech recognition and transcription
- **Gradio**: Web interface framework
- **Singapore English Corpus**: Linguistic research and accent analysis

## 📞 Contact

- **Author**: Tom Yan
- **Email**: zhiyuanyan@rochester.edu
- **GitHub**: [@tomyanzhiyuan](https://github.com/tomyanzhiyuan)
- **Project**: [voice-accent](https://github.com/tomyanzhiyuan/voice-accent)

---

**Built with ❤️ for the Singaporean community and accent preservation**
