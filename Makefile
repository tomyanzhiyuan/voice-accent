# Singaporean-Accent TTS MVP - Makefile
# Automation commands for setup, development, and deployment

# ============================================================================
# CONFIGURATION AND VARIABLES
# ============================================================================

# Python and virtual environment settings
PYTHON := python3.11
VENV_DIR := venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip
VENV_ACTIVATE := source $(VENV_DIR)/bin/activate

# Project directories
SRC_DIR := src
DATA_DIR := data
OUTPUT_DIR := outputs
LOG_DIR := logs
MODEL_DIR := models
CONFIG_DIR := config

# Gradio settings
GRADIO_HOST := 127.0.0.1
GRADIO_PORT := 7860

# Test settings
TEST_DIR := tests
COVERAGE_MIN := 80

# Code quality settings
BLACK_LINE_LENGTH := 88
FLAKE8_MAX_LINE_LENGTH := 88

# ============================================================================
# HELP AND DOCUMENTATION
# ============================================================================

.PHONY: help
help: ## Show this help message
	@echo "Singaporean-Accent TTS MVP - Available Commands"
	@echo "================================================"
	@echo ""
	@echo "Setup and Environment:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(setup|install|clean)"
	@echo ""
	@echo "Data Processing:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(prepare|ingest|transcribe)"
	@echo ""
	@echo "TTS and Generation:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(demo|ui|generate)"
	@echo ""
	@echo "Development and Testing:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(test|lint|format)"
	@echo ""
	@echo "Utilities:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -v -E "(setup|install|clean|prepare|ingest|transcribe|demo|ui|generate|test|lint|format)"
	@echo ""

# ============================================================================
# SETUP AND ENVIRONMENT MANAGEMENT
# ============================================================================

.PHONY: setup
setup: ## Complete project setup (venv, deps, models, directories)
	@echo "🚀 Setting up Singaporean-Accent TTS MVP..."
	@$(MAKE) check-system
	@$(MAKE) create-venv
	@$(MAKE) install-deps
	@$(MAKE) create-dirs
	@$(MAKE) download-models
	@$(MAKE) verify-setup
	@echo "✅ Setup complete! Run 'make help' to see available commands."

.PHONY: check-system
check-system: ## Check system dependencies (Python, FFmpeg)
	@echo "🔍 Checking system dependencies..."
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "❌ Python 3.11 not found. Please install Python 3.11+"; exit 1; }
	@$(PYTHON) --version | grep -E "3\.(10|11|12)" >/dev/null || { echo "❌ Python 3.10+ required"; exit 1; }
	@command -v ffmpeg >/dev/null 2>&1 || { echo "❌ FFmpeg not found. Install with: brew install ffmpeg"; exit 1; }
	@echo "✅ System dependencies OK"

.PHONY: create-venv
create-venv: ## Create Python virtual environment
	@echo "🐍 Creating virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "✅ Virtual environment created"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi

.PHONY: install-deps
install-deps: create-venv ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	@$(VENV_PIP) install --upgrade pip setuptools wheel
	@$(VENV_PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

.PHONY: install-dev-deps
install-dev-deps: install-deps ## Install development dependencies
	@echo "🛠️ Installing development dependencies..."
	@$(VENV_PIP) install pytest pytest-cov black flake8 mypy pre-commit
	@$(VENV_ACTIVATE) && pre-commit install
	@echo "✅ Development dependencies installed"

.PHONY: create-dirs
create-dirs: ## Create necessary project directories
	@echo "📁 Creating project directories..."
	@mkdir -p $(DATA_DIR)/raw/refs $(DATA_DIR)/processed/segments $(DATA_DIR)/processed/transcripts
	@mkdir -p $(OUTPUT_DIR) $(LOG_DIR) $(MODEL_DIR) $(CONFIG_DIR)
	@mkdir -p .cache tests/data
	@echo "✅ Directories created"

.PHONY: download-models
download-models: ## Download required TTS models
	@echo "🤖 Downloading TTS models..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cpu')"
	@echo "✅ Models downloaded"

.PHONY: verify-setup
verify-setup: ## Verify installation and setup
	@echo "🔍 Verifying setup..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -c "import torch; print(f'PyTorch: {torch.__version__}')"
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -c "import TTS; print('✅ Coqui TTS available')"
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -c "import whisper; print('✅ OpenAI Whisper available')"
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -c "import gradio; print('✅ Gradio available')"
	@echo "✅ Setup verification complete"

# ============================================================================
# DATA PROCESSING PIPELINE
# ============================================================================

.PHONY: prepare
prepare: ## Run complete data processing pipeline (ingest→prepare→transcribe)
	@echo "🎵 Running data processing pipeline..."
	@$(MAKE) ingest
	@$(MAKE) process-audio
	@$(MAKE) transcribe
	@echo "✅ Data processing complete"

.PHONY: ingest
ingest: ## Copy and validate audio files from data/raw to processed
	@echo "📥 Ingesting audio files..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m $(SRC_DIR).data.ingest \
		--input $(DATA_DIR)/raw/refs \
		--output $(DATA_DIR)/processed/segments \
		--validate
	@echo "✅ Audio ingestion complete"

.PHONY: process-audio
process-audio: ## Resample, normalize, and segment audio files
	@echo "🎛️ Processing audio files..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m $(SRC_DIR).data.prepare \
		--input $(DATA_DIR)/processed/segments \
		--output $(DATA_DIR)/processed/segments \
		--sample-rate 16000 \
		--normalize \
		--segment-length 10
	@echo "✅ Audio processing complete"

.PHONY: transcribe
transcribe: ## Generate transcripts using Whisper
	@echo "🎤 Transcribing audio files..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m $(SRC_DIR).data.transcribe \
		--input $(DATA_DIR)/processed/segments \
		--output $(DATA_DIR)/processed/transcripts \
		--model small.en \
		--language en
	@echo "✅ Transcription complete"

# ============================================================================
# TTS GENERATION AND INTERFACE
# ============================================================================

.PHONY: ui
ui: ## Launch Gradio web interface
	@echo "🌐 Launching Gradio interface..."
	@echo "📍 Opening http://$(GRADIO_HOST):$(GRADIO_PORT)"
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m $(SRC_DIR).ui.app \
		--host $(GRADIO_HOST) \
		--port $(GRADIO_PORT) \
		--share false

.PHONY: demo
demo: ## Generate demo audio with sample Singlish text
	@echo "🎭 Generating demo audio..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m $(SRC_DIR).tts.xtts_infer \
		--text "The weather today is quite hot, lah. Can you help me with this thing or not?" \
		--ref-dir $(DATA_DIR)/processed/segments \
		--output $(OUTPUT_DIR)/demo.wav \
		--temperature 0.7 \
		--seed 42
	@echo "✅ Demo generated: $(OUTPUT_DIR)/demo.wav"

.PHONY: generate
generate: ## Generate speech from text (usage: make generate TEXT="your text here")
	@if [ -z "$(TEXT)" ]; then \
		echo "❌ Usage: make generate TEXT=\"your text here\""; \
		exit 1; \
	fi
	@echo "🗣️ Generating speech: $(TEXT)"
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m $(SRC_DIR).tts.xtts_infer \
		--text "$(TEXT)" \
		--ref-dir $(DATA_DIR)/processed/segments \
		--output $(OUTPUT_DIR)/generated_$(shell date +%Y%m%d_%H%M%S).wav \
		--temperature 0.7

# ============================================================================
# TESTING AND QUALITY ASSURANCE
# ============================================================================

.PHONY: test
test: ## Run test suite with coverage
	@echo "🧪 Running tests..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m pytest $(TEST_DIR) \
		--cov=$(SRC_DIR) \
		--cov-report=html \
		--cov-report=term \
		--cov-fail-under=$(COVERAGE_MIN) \
		-v

.PHONY: test-fast
test-fast: ## Run tests without coverage (faster)
	@echo "⚡ Running fast tests..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m pytest $(TEST_DIR) -v

.PHONY: test-audio
test-audio: ## Run audio processing tests
	@echo "🎵 Running audio tests..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m pytest $(TEST_DIR)/audio -v

.PHONY: test-tts
test-tts: ## Run TTS engine tests
	@echo "🤖 Running TTS tests..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m pytest $(TEST_DIR)/unit/test_tts* -v

# ============================================================================
# CODE QUALITY AND FORMATTING
# ============================================================================

.PHONY: lint
lint: ## Run all linting and code quality checks
	@echo "🔍 Running code quality checks..."
	@$(MAKE) format-check
	@$(MAKE) flake8
	@$(MAKE) mypy

.PHONY: format
format: ## Format code with Black
	@echo "🎨 Formatting code..."
	@$(VENV_ACTIVATE) && black --line-length $(BLACK_LINE_LENGTH) $(SRC_DIR) $(TEST_DIR)
	@echo "✅ Code formatted"

.PHONY: format-check
format-check: ## Check code formatting without making changes
	@echo "🎨 Checking code formatting..."
	@$(VENV_ACTIVATE) && black --check --line-length $(BLACK_LINE_LENGTH) $(SRC_DIR) $(TEST_DIR)

.PHONY: flake8
flake8: ## Run flake8 linting
	@echo "🔍 Running flake8..."
	@$(VENV_ACTIVATE) && flake8 --max-line-length $(FLAKE8_MAX_LINE_LENGTH) $(SRC_DIR) $(TEST_DIR)

.PHONY: mypy
mypy: ## Run mypy type checking
	@echo "🔍 Running mypy..."
	@$(VENV_ACTIVATE) && mypy $(SRC_DIR) --ignore-missing-imports

# ============================================================================
# UTILITIES AND MAINTENANCE
# ============================================================================

.PHONY: clean
clean: ## Remove generated files and caches
	@echo "🧹 Cleaning up..."
	@rm -rf $(OUTPUT_DIR)/*.wav
	@rm -rf $(DATA_DIR)/processed/segments/*.wav
	@rm -rf $(DATA_DIR)/processed/transcripts/*.jsonl
	@rm -rf .cache/*
	@rm -rf $(LOG_DIR)/*.log
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

.PHONY: clean-all
clean-all: clean ## Remove all generated files, models, and virtual environment
	@echo "🧹 Deep cleaning..."
	@rm -rf $(VENV_DIR)
	@rm -rf $(MODEL_DIR)/*
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@echo "✅ Deep cleanup complete"

.PHONY: logs
logs: ## Show recent log files
	@echo "📋 Recent logs:"
	@find $(LOG_DIR) -name "*.log" -type f -exec ls -la {} \; 2>/dev/null || echo "No log files found"

.PHONY: status
status: ## Show project status and diagnostics
	@echo "📊 Project Status"
	@echo "=================="
	@echo "Python: $(shell $(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo "Virtual env: $(shell [ -d $(VENV_DIR) ] && echo 'Active' || echo 'Not created')"
	@echo "FFmpeg: $(shell ffmpeg -version 2>/dev/null | head -1 || echo 'Not found')"
	@echo ""
	@echo "📁 Directory Status:"
	@echo "Data files: $(shell find $(DATA_DIR) -name "*.wav" 2>/dev/null | wc -l | tr -d ' ') audio files"
	@echo "Models: $(shell [ -d $(MODEL_DIR) ] && find $(MODEL_DIR) -type f | wc -l | tr -d ' ' || echo '0') model files"
	@echo "Outputs: $(shell [ -d $(OUTPUT_DIR) ] && find $(OUTPUT_DIR) -name "*.wav" | wc -l | tr -d ' ' || echo '0') generated files"
	@echo ""
	@echo "🔧 Quick Commands:"
	@echo "  make setup     - Complete project setup"
	@echo "  make prepare   - Process reference audio"
	@echo "  make ui        - Launch web interface"
	@echo "  make demo      - Generate demo audio"

.PHONY: requirements-update
requirements-update: ## Update requirements.txt with current environment
	@echo "📦 Updating requirements..."
	@$(VENV_ACTIVATE) && pip freeze > requirements-frozen.txt
	@echo "✅ Current environment saved to requirements-frozen.txt"

.PHONY: benchmark
benchmark: ## Run performance benchmarks
	@echo "⚡ Running benchmarks..."
	@$(VENV_ACTIVATE) && $(VENV_PYTHON) -m $(SRC_DIR).utils.benchmark \
		--ref-dir $(DATA_DIR)/processed/segments \
		--output $(OUTPUT_DIR)/benchmark_results.json
	@echo "✅ Benchmark complete"

# ============================================================================
# DEVELOPMENT SHORTCUTS
# ============================================================================

.PHONY: dev
dev: install-dev-deps ## Setup development environment
	@echo "🛠️ Development environment ready"

.PHONY: notebook
notebook: ## Launch Jupyter notebook
	@echo "📓 Launching Jupyter notebook..."
	@$(VENV_ACTIVATE) && jupyter notebook notebooks/

.PHONY: shell
shell: ## Activate virtual environment shell
	@echo "🐚 Activating virtual environment..."
	@echo "Run: source $(VENV_DIR)/bin/activate"

# ============================================================================
# DOCKER SUPPORT (OPTIONAL)
# ============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image (if Dockerfile exists)
	@if [ -f Dockerfile ]; then \
		echo "🐳 Building Docker image..."; \
		docker build -t accent-tts:latest .; \
	else \
		echo "❌ Dockerfile not found"; \
	fi

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	@docker run -p $(GRADIO_PORT):$(GRADIO_PORT) -v $(PWD)/data:/app/data accent-tts:latest

# ============================================================================
# SPECIAL TARGETS
# ============================================================================

# Default target
.DEFAULT_GOAL := help

# Prevent make from deleting intermediate files
.SECONDARY:

# Mark all targets as phony (not file-based)
.PHONY: $(MAKECMDGOALS)
