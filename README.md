# Downes 🤖

## Version v0.0.1

Downes is named after Stephen Downes, a Canadian philosopher and commentator in the fields of online learning and new media. He has explored and promoted the educational use of computer and online technologies since 1995. In that spirit, Downes is an autonomous education agent designed to develop comprehensive curriculum by thinking critically, planning strategically, and learning continuously.

Built specifically for curriculum development, Downes transforms complex educational requests into transparent, step-by-step curriculum plans—emulating how an expert instructional designer works, but powered by advanced AI. It merges task planning, self-reflection, and educational best practices into a seamless workflow. It is more than an assistant—it is a self-driven curriculum architect that aims to bring clarity and structure to educational program development.

100% FREE to use! No paid API keys needed for core functionality—Downes leverages powerful AI capabilities to make curriculum development accessible to all educators and instructional designers.


## Overview

Downes takes complex curriculum requests and turns them into clear, step-by-step educational development plans. It structures learning objectives, designs course content, and creates comprehensive curricula that are pedagogically sound and learner-focused.

**Key Capabilities:**
- **Intelligent Curriculum Planning**: Automatically decomposes educational goals into structured learning pathways
- **Autonomous Development**: Selects and applies appropriate instructional design methodologies
- **Self-Validation**: Checks alignment with learning objectives and iterates until curricula are complete
- **Educational Best Practices**: Incorporates proven pedagogical frameworks and assessment strategies
- **Flexible LLM Support**: Works with OpenAI, OpenRouter, Ollama, llama.cpp, or any OpenAI-compatible API
- **Safety Features**: Built-in loop detection and step limits to prevent runaway execution

[![Twitter Follow](https://img.shields.io/twitter/follow/virattt?style=social)](https://twitter.com/virattt)

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- LLM API access (one of):
  - **OpenAI API** key (get [here](https://platform.openai.com/api-keys))
  - **OpenRouter** account (get [here](https://openrouter.ai))
  - **Local LLM** via Ollama or llama.cpp (free!)
  - Any OpenAI-compatible API
- **No additional API keys required!** (Core curriculum development functionality included)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/virattt/downes.git
cd downes
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Set up your environment variables:
```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your LLM API key
# OPENAI_API_KEY=your-openai-api-key
# That's it! Ready to develop curriculum.
```

### LLM Configuration

Downes works with **any OpenAI-compatible API**, giving you complete flexibility:

#### Option 1: OpenAI (Recommended for Production)
```bash
# In your .env file:
OPENAI_API_KEY=sk-...
# Optionally specify model:
# LLM_MODEL=gpt-4o
```

#### Option 2: OpenRouter (Access Multiple Models)
```bash
# In your .env file:
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-3.5-sonnet
```

#### Option 3: Ollama (100% Free & Local)
```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model: ollama pull llama3.2
# 3. In your .env file:
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.2
OPENAI_API_KEY=not-needed
```

#### Option 4: llama.cpp (100% Free & Local)
```bash
# 1. Run llama.cpp server with --api-key option
# 2. In your .env file:
OPENAI_BASE_URL=http://localhost:8080/v1
LLM_MODEL=your-model-name
OPENAI_API_KEY=not-needed
```

#### Option 5: Other OpenAI-Compatible APIs
Works with sage.is, Together.ai, Anyscale, or any other OpenAI-compatible endpoint:
```bash
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-provider.com/v1
LLM_MODEL=your-model-name
```

### Usage

Run Downes in interactive mode:
```bash
uv run downes-agent
```

### Example Queries

Try asking Downes to develop curriculum like:
- "Create a 12-week introduction to Python programming course for beginners"
- "Design a curriculum for teaching machine learning fundamentals to business students"
- "Develop a workshop series on data visualization and storytelling"
- "Build a comprehensive bootcamp curriculum for web development"

Downes will automatically:
1. Break down your request into curriculum development tasks
2. Define clear learning objectives and outcomes
3. Structure modules, lessons, and assessments
4. Provide a comprehensive, pedagogically-sound curriculum plan

## Architecture

Downes uses a multi-agent architecture with specialized components:

- **Planning Agent**: Analyzes curriculum requests and creates structured development task lists
- **Action Agent**: Selects appropriate instructional design methodologies and executes curriculum development steps
- **Validation Agent**: Verifies task completion and curriculum alignment with learning objectives
- **Answer Agent**: Synthesizes findings into comprehensive curriculum plans

## Project Structure

```
downes/
├── src/
│   ├── downes/
│   │   ├── agent.py              # Main agent orchestration logic
│   │   ├── model.py              # LLM interface
│   │   ├── prompts.py            # System prompts for each component
│   │   ├── schemas.py            # Pydantic models
│   │   ├── tools/
│   │   │   ├── search/           # Search and research tools
│   │   │   └── ...               # Additional curriculum development tools
│   │   ├── utils/                # Utility functions
│   │   └── cli.py                # CLI entry point
├── pyproject.toml
└── uv.lock
```

## Configuration

Downes supports configuration via the `Agent` class initialization:

```python
from downes.agent import Agent

agent = Agent(
    max_steps=20,              # Global safety limit
    max_steps_per_task=5       # Per-task iteration limit
)
```

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

**Important**: Please keep your pull requests small and focused.  This will make it easier to review and merge.


## License

This project is licensed under the AGPL License.

