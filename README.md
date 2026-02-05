# AV-Studio M4

**AI-Powered Audio/Video Production Studio for Apple M4 Max**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## Overview

AV-Studio is a local-first, AI-powered audio/video production platform optimized for Apple M4 Max. It combines state-of-the-art processing capabilities (Demucs, Whisper, MLX) with an intelligent agent system that can autonomously execute production workflows while maintaining human oversight at critical gates.

## Key Features

- 🎵 **Professional Audio Processing**: Studio-grade stem separation, mastering, and transcription
- 🎬 **Video Processing**: Fast decoding with TorchCodec and advanced frame extraction
- 🤖 **AI-Native**: Built-in agent orchestration for automated workflows
- ⚡ **Local-First**: Maximize M4 Max GPU; minimize external API costs
- 🔌 **Extensible**: MCP protocol for tool extension; plugin architecture
- 💰 **Cost-Aware**: Smart routing minimizes API spend while maintaining quality

## Tech Stack

### Core Frameworks
- **Python 3.12** - Modern Python with type hints
- **PyTorch 2.10** - ML framework with Metal (MPS) acceleration
- **MLX 0.30** - Apple's ML framework for Apple Silicon
- **FastAPI 0.115** - High-performance async API server

### Audio Processing
- **Demucs 4.0** - State-of-the-art stem separation
- **Whisper** - High-accuracy speech transcription
- **Pedalboard** - Real-time audio effects
- **Librosa** - Audio analysis and feature extraction

### Video Processing
- **TorchCodec** - Hardware-accelerated video decoding
- **OpenCV** - Computer vision and video effects

### AI/LLM Integration
- **MLX-LM** - Native Apple Silicon LLM inference
- **Ollama** - Local LLM serving
- **OpenAI/Anthropic/Google** - External LLM APIs with smart routing

## Project Structure

```
av-studio-m4/
├── src/av_studio/          # Main package
│   ├── agents/             # Agent system (orchestrator, specialized agents)
│   ├── llm/                # LLM clients and routing
│   ├── gateway/            # API gateway and smart router
│   ├── processing/         # Audio/video processing pipelines
│   ├── mcp/                # MCP server and tools
│   └── config/             # Configuration and settings
├── spec-kit/               # Project specifications
├── tests/                  # Test suite
├── scripts/                # Setup and utility scripts
├── config/                 # Configuration files (models, pricing)
└── pyproject.toml          # Project dependencies
```

## Quick Start

### Prerequisites

- macOS with Apple M4 Max chip
- Python 3.12 or higher
- 36GB+ unified memory recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/scotlaclair/av-studio-m4.git
cd av-studio-m4

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and preferences

# Run setup script (coming soon)
# ./scripts/setup.sh
```

### Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linting
ruff check .

# Run type checking
mypy src/av_studio

# Run tests
pytest
```

## Configuration

See `.env.example` for all available configuration options. Key settings:

- **LLM Provider**: Choose between local (MLX/Ollama) or external APIs
- **Processing Models**: Select Demucs and Whisper model sizes
- **Budget Limits**: Set daily spending caps for external APIs
- **Hardware**: Configure GPU usage and parallel processing

## Architecture

AV-Studio follows an AI-First SDLC approach with:

1. **Smart Gateway**: Routes requests to optimal LLM based on cost/latency/quality
2. **Agent Orchestrator**: Manages multi-step workflows and task delegation
3. **Specialized Agents**: Audio, video, and integration-specific agents
4. **MCP Tools**: Extensible tool system for agent capabilities
5. **Local-First Processing**: Maximize Apple Silicon GPU usage

See [spec-kit/](./spec-kit/) for detailed specifications.

## Development Status

**Version**: 0.1.0 (MVP in development)

- [x] Project structure and configuration
- [ ] Core LLM integration (Phase 3)
- [ ] Audio processing pipeline (Phase 4)
- [ ] Agent system (Phase 5)
- [ ] API layer (Phase 6)
- [ ] MCP server (Phase 7)

## Contributing

This is currently a personal project. Contributions will be welcome after v1.0.0 release.

## License

MIT License - see LICENSE file for details.

## Author

- **@scotlaclair** - Human Director
- Built with AI-First SDLC methodology

## Acknowledgments

- Demucs by Facebook Research
- Whisper by OpenAI
- MLX by Apple
- MCP Protocol by Anthropic
