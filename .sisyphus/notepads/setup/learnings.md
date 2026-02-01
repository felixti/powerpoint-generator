# Setup Task Learnings

## Project Structure
- Using `src/` layout (modern Python packaging standard)
  - Prevents accidental imports before installation
  - Better isolation between tests and source code
  - Recommended by current Python packaging best practices

## Configuration Files

### pyproject.toml
- Uses hatchling as build backend (minimal, fast)
- Python 3.10+ required for modern type hints and async features
- Tool configurations (pytest, mypy, ruff, black, isort) all in single file
- Makes setup.py unnecessary and simplifies packaging

### Pre-commit Hooks
- Configured with ruff for linting and formatting (faster than flake8 + black)
- mypy for static type checking
- Standard pre-commit hooks for file validation
- isort for import organization (black-compatible profile)

## Dependency Management

### Core Dependencies
- `python-pptx`: PowerPoint generation (stable, well-maintained)
- `langchain`: LLM abstraction and utilities
- `langgraph`: Agent orchestration and state management
- `pydantic`: Data validation (v2.0+ for modern typing)
- `openai`: Direct OpenAI API access
- `python-dotenv`: Environment variable management
- `requests`: HTTP utilities (shared dependency)

### Dev Dependencies
- `pytest` + `pytest-asyncio`: Async test support essential
- `ruff`: Fast linting and formatting (Rust-based)
- `mypy`: Type checking with gradual adoption possible
- `black`, `isort`: Code formatting (integrated via ruff)

## Module Organization

Each package has clear responsibilities:
- `agents/`: LangGraph agent definitions and workflows
- `models/`: Pydantic models for data validation
- `presenters/`: PowerPoint generation logic (PPTX handling)
- `utils/`: Helper functions and utilities

## Documentation Template
- README includes installation, development, and usage sections
- .env.example documents all required environment variables
- Structure allows for easy expansion

## Best Practices Implemented
✓ Modern Python packaging (pyproject.toml only, no setup.py)
✓ Type hints support with mypy configuration
✓ Async-first testing setup
✓ Fast tooling (ruff instead of traditional tools)
✓ Clear directory structure for scalability
✓ Pre-commit hooks for code quality
✓ Comprehensive gitignore for Python projects
