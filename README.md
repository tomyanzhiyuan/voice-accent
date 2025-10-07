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

### 🎵 Enhanced Audio Processing Pipeline

- **Multi-Speaker Support**: Automatic speaker diarization and separation
- **Voice Activity Detection**: Removes silence, music, and background noise
- **Noise Reduction**: Cleans up background noise while preserving speech
- **Quality Filtering**: SNR analysis, clipping detection, frequency validation
- **Smart Segmentation**: Splits on natural pauses, preserves prosodic units
- **Format Support**: WAV, MP3, OGG input formats
- **Auto-Processing**: 16kHz mono, normalized to -23 LUFS
- **Comprehensive Reporting**: Detailed quality statistics and metrics

###  Web Interface

- **Gradio UI**: Intuitive web interface with real-time generation
- **Pre-filled Examples**: Singlish sentences for testing
- **Model Selection**: Switch between XTTS and Tortoise engines
- **Parameter Control**: Temperature, seed, generation settings

### 📊 Evaluation Tools

- **Accent Checklist**: Phonetic and prosodic feature assessment
- **A/B Testing**: Compare generated vs reference audio
- **Quality Metrics**: Intelligibility, naturalness, authenticity scores

## 🎵 Enhanced Audio Processing Pipeline

The enhanced pipeline provides production-grade audio preprocessing for multi-speaker audio with background noise, transforming raw recordings into high-quality TTS training data.

### Pipeline Architecture

```
Raw Audio (MP3/WAV/OGG)
    ↓
[1] Speaker Diarization
    ↓ Identify and separate individual speakers (pyannote.audio)
[2] Voice Activity Detection
    ↓ Remove silence, music, background noise (silero-vad)
[3] Noise Reduction
    ↓ Clean up remaining background noise (noisereduce)
[4] Quality Filtering
    ↓ Reject poor segments (SNR, clipping, frequency analysis)
[5] Smart Segmentation
    ↓ Split on natural pauses, not mid-word
[6] Duration Filtering
    ↓ Keep 1-10 second chunks (target 3-8s)
[7] Normalization
    ↓ Consistent volume (-23 LUFS)
[8] Export + Statistics
    ↓ Organized by speaker with quality report
High-Quality Training Segments
```

### Key Features

#### Multi-Speaker Diarization
- Automatically identifies 1-10 speakers in audio
- Separates overlapping speech
- Labels and tracks speakers throughout recording
- Organizes output by speaker ID

#### Voice Activity Detection (VAD)
- Removes silence, music intros, and background noise
- Configurable aggressiveness (0.0-1.0)
- Preserves natural speech boundaries
- Fast and accurate (silero-vad)

#### Quality Filtering
- **SNR (Signal-to-Noise Ratio)**: Rejects segments < 15 dB
- **Clipping Detection**: Rejects if > 1% samples clipped
- **Frequency Analysis**: Validates speech spectrum (80Hz-8kHz)
- **Energy Variance**: Rejects monotone/flat segments
- **Duration Check**: Keeps 1-10 second segments

#### Smart Segmentation
- Detects natural pauses (>300ms silence)
- Splits on sentence/phrase boundaries
- Avoids mid-word cuts
- Targets 3-8 second segments (optimal for TTS)
- Merges very short segments (<1s)

### Configuration

Create `config/processing_config.yaml` to customize the pipeline:

```yaml
# Enhanced Audio Processing Configuration

diarization:
  enabled: true
  min_speakers: 1
  max_speakers: 10
  min_segment_duration: 1.0  # seconds

vad:
  enabled: true
  threshold: 0.5  # 0.0-1.0, higher = more aggressive
  min_speech_duration: 0.5
  min_silence_duration: 0.3

noise_reduction:
  enabled: true
  stationary: true
  prop_decrease: 0.8  # 0.0-1.0, noise reduction strength

quality_filter:
  min_snr: 15.0  # dB
  max_clipping_ratio: 0.01  # 1%
  min_frequency: 80  # Hz
  max_frequency: 8000  # Hz
  min_energy_variance: 0.1

segmentation:
  min_duration: 1.0  # seconds
  max_duration: 10.0
  target_duration: 5.0
  pause_threshold: 0.3
  merge_short_segments: true

normalization:
  target_loudness: -23.0  # LUFS
  sample_rate: 16000
  mono: true

output:
  format: "wav"
  bit_depth: 16
  export_rejected: false  # Save rejected segments for review
  generate_report: true
```

### Usage

```bash
# Process with all enhancements (recommended)
python scripts/process_audio.py \
  --input data/raw/realtalk-ep17/ \
  --output data/processed/ \
  --config config/processing_config.yaml \
  --enable-all

# Process with specific features
python scripts/process_audio.py \
  --input data/raw/ \
  --output data/processed/ \
  --diarize \
  --vad \
  --denoise \
  --quality-filter

# Analyze audio quality without processing
python scripts/analyze_quality.py \
  --input data/raw/realtalk-ep17/ \
  --report quality_analysis.html
```

### Output Structure

```
data/processed/
├── speaker_0/
│   ├── file1_seg001.wav
│   ├── file1_seg002.wav
│   └── ...
├── speaker_1/
│   ├── file1_seg001.wav
│   └── ...
├── speaker_2/
│   └── ...
└── quality_report.json
```

### Expected Results

With 12 hours of raw multi-speaker audio:
- **8-10 hours** after VAD (removing silence/music)
- **6-8 hours** after quality filtering (removing poor segments)
- **3-5 speakers** identified and separated
- **1000-2000 segments** per speaker (3-8s each)
- **Quality score**: 85-95% vs 60-70% with basic processing

### Quality Report

The pipeline generates comprehensive statistics:

```json
{
  "input_file": "interview.mp3",
  "total_duration": 3600.0,
  "speakers_detected": 3,
  "segments_generated": 1847,
  "segments_rejected": 423,
  "quality_stats": {
    "avg_snr": 18.5,
    "avg_duration": 4.2,
    "clipping_rate": 0.003,
    "usable_audio_duration": 2891.4
  },
  "speaker_distribution": {
    "speaker_0": 892,
    "speaker_1": 654,
    "speaker_2": 301
  },
  "rejection_reasons": {
    "low_snr": 187,
    "clipping": 45,
    "too_short": 98,
    "too_long": 23,
    "low_energy": 70
  }
}
```

### Performance

**Processing Time** (12 hours of raw audio):
- Diarization: 2-3 hours (GPU) or 6-8 hours (CPU)
- VAD + Quality: 1-2 hours
- Total: 3-10 hours depending on hardware

**Resource Requirements**:
- Memory: 4-8GB RAM recommended
- Storage: 2-3x raw audio size (raw + processed + rejected)
- GPU: Optional but speeds up diarization 3-4x

## 🚀 Installation

### System Requirements

- **OS**: macOS 10.15+ (tested), Linux, Windows WSL2
- **Python**: 3.11 (Anything newer isn't fully supported)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 5-10GB for models and audio data
- **GPU**: CUDA supported, MPS not supported (has compatibility issues), CPU works well

### Known Compatibility Notes

- **PyTorch 2.6+**: Requires `weights_only=False` for model loading (automatically patched)
- **MPS (Apple Silicon)**: Not supported due to convolution limitations, uses CPU instead
- **Transformers**: Use version 4.33.0 (newer versions have breaking changes with TTS 0.21.3)

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

### Hugging Face Authentication (Required for Speaker Diarization)

The enhanced pipeline uses pyannote.audio for speaker diarization, which requires authentication:

1. Create a Hugging Face account at [huggingface.co](https://huggingface.co)
2. Accept the terms for the speaker diarization model:
   - Visit [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization)
   - Click "Agree and access repository"
3. Generate an access token:
   - Go to [Settings > Access Tokens](https://huggingface.co/settings/tokens)
   - Create a new token with "read" permissions
4. Add token to `.env`:
   ```bash
   cp .env.example .env
   # Edit .env and add:
   HF_TOKEN=your_token_here
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
2. Install all dependencies with proper versions (including enhanced pipeline)
3. Download required TTS models
4. Verify FFmpeg and system dependencies
5. Create necessary directories
6. Run basic functionality tests

**New Dependencies Added**:
- `pyannote.audio>=3.1.0` - Speaker diarization
- `silero-vad>=4.0.0` - Voice activity detection
- `noisereduce>=3.0.0` - Noise reduction
- `python-speech-features>=0.6` - Audio feature extraction

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

#### Enhanced Pipeline Issues

**Hugging Face authentication failed**:
```bash
# Verify token is set
echo $HF_TOKEN

# Or check .env file
cat .env | grep HF_TOKEN

# Test authentication
python -c "from huggingface_hub import login; login(token='your_token')"
```

**Speaker diarization too slow**:
- Use GPU if available (3-4x faster)
- Reduce `max_speakers` in config
- Process shorter audio files in batches
- Consider disabling diarization for single-speaker audio

**VAD removing too much speech**:
- Lower `vad.threshold` in config (try 0.3-0.4)
- Reduce `min_silence_duration`
- Check audio quality (low SNR may confuse VAD)

**Too many segments rejected**:
- Lower `quality_filter.min_snr` (try 12-13 dB)
- Increase `max_clipping_ratio` slightly
- Review rejected segments with `export_rejected: true`
- Check if source audio quality is sufficient

**Segmentation issues**:
- Adjust `pause_threshold` (try 0.2-0.5s)
- Modify `target_duration` for different segment lengths
- Enable `merge_short_segments` to reduce fragments

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

## � License

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
