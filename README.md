# AI PowerPoint Generator

An intelligent PowerPoint presentation generator powered by LangGraph agents and LLMs. This tool leverages advanced language models and agentic workflows to automatically create professional presentations from natural language prompts.

## Features

- 🤖 LangGraph-based multi-agent orchestration
- 🎨 Professional PowerPoint generation with python-pptx
- 🧠 LLM-powered content generation and summarization
- 📊 Support for various slide types and layouts
- 🔄 Agentic workflow for research, planning, and content creation
- ✅ Type-safe with Pydantic validation
- 🚀 Async support for efficient processing

## Project Structure

```
powerpoint-generator/
├── src/
│   └── powerpoint_generator/
│       ├── __init__.py
│       ├── agents/                # LangGraph agent definitions
│       ├── models/                # Pydantic models for data validation
│       ├── presenters/            # PowerPoint generation logic
│       ├── utils/                 # Utility functions
│       └── config.py              # Configuration management
├── tests/
│   ├── __init__.py
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── conftest.py                # Pytest configuration
├── pyproject.toml                 # Project metadata and dependencies
├── .pre-commit-config.yaml        # Pre-commit hooks configuration
├── .gitignore                     # Git ignore rules
├── .env.example                   # Example environment variables
└── README.md                      # This file
```

## Prerequisites

- Python 3.10 or higher
- OpenRouter API key (for LLM functionality)
- pip or your preferred package manager

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-org/powerpoint-generator.git
cd powerpoint-generator
```

### Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode with all development dependencies.

### Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_SITE_URL=https://your-site.com
OPENROUTER_SITE_NAME=YourApp
```

Get your OpenRouter API key at: https://openrouter.ai/

**Why OpenRouter?**
- Access multiple LLM providers (Claude, GPT, Gemini, etc.) with one API key
- Unified interface for all models
- Cost-effective with competitive pricing
- Easy to switch between models

### Set Up Pre-commit Hooks

```bash
pre-commit install
```

This ensures code quality checks run automatically on every commit.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/powerpoint_generator

# Run only unit tests
pytest tests/unit

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Run Ruff linter and formatter
ruff check src/ tests/
ruff format src/ tests/

# Run type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

### Building the Package

```bash
# Build wheel and source distribution
python -m build
```

## Usage

*(To be updated as implementation progresses)*

## Dependencies

### Core Dependencies
- **python-pptx** - PowerPoint file generation and manipulation
- **langchain** - LLM application framework
- **langgraph** - Agentic orchestration and workflow management
- **pydantic** - Data validation using Python type annotations
- **openai** - OpenAI API client
- **python-dotenv** - Environment variable management

### Development Dependencies
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage reporting
- **ruff** - Fast Python linter and formatter
- **mypy** - Static type checker
- **black** - Code formatter
- **isort** - Import sorter
- **pre-commit** - Git hook framework

## Configuration

### pyproject.toml

The project uses `pyproject.toml` for all configuration:
- Project metadata and dependencies
- Pytest settings
- Mypy type checking rules
- Ruff linting and formatting rules
- Black formatting configuration

### Environment Variables

See `.env.example` for all available configuration options. Key variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - LLM model to use (default: gpt-4-turbo)
- `LOG_LEVEL` - Logging level (default: INFO)
- `OUTPUT_DIR` - Output directory for generated presentations

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and ensure tests pass
3. Pre-commit hooks will format and lint your code
4. Commit your changes: `git commit -m "Add your feature"`
5. Push to the branch: `git push origin feature/your-feature`
6. Open a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
