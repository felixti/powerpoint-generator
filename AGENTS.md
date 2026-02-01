# AGENTS.md - AI PowerPoint Generator

Guidelines for agentic coding agents working on this AI-powered PowerPoint presentation generator.

## Project Overview

This is an AI agent system that generates professional PowerPoint presentations using:
- **LangGraph** for agent orchestration and workflow management
- **python-pptx** for PowerPoint file generation
- **OpenRouter** for unified LLM access (Claude, GPT, etc.)
- **Pydantic** for structured data validation

## Build Commands

**This project uses `uv` as the Python runner and package manager.**

```bash
# Install dependencies (creates venv automatically)
uv pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run single test file
uv run pytest tests/test_planner.py

# Run single test
uv run pytest tests/test_planner.py::test_create_outline

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/ tests/
uv run ruff check --fix src/ tests/

# Formatting
uv run ruff format src/ tests/

# Run all quality checks
uv run ruff check src/ tests/ && uv run mypy src/ && uv run pytest
```

## Code Style Guidelines

### Imports

```python
# 1. Standard library
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# 2. Third-party packages
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph
from pptx import Presentation

# 3. Local modules
from src.agents.planner import PlannerAgent
from src.models.schemas import SlideOutline
```

### Formatting

- **Line length**: 88 characters (Black-compatible)
- **Quotes**: Double quotes for strings, single quotes for dict keys
- **Trailing commas**: Required for multi-line collections
- **Use Ruff** for both linting and formatting

### Type Hints

```python
# Required for all function signatures
def create_slide(
    title: str,
    content: List[str],
    layout: Optional[str] = None
) -> Slide:
    ...

# Use modern syntax (Python 3.10+)
def process_items(items: list[str]) -> dict[str, Any]:
    ...

# Pydantic models for complex structures
class PresentationOutline(BaseModel):
    title: str
    slides: list[SlideOutline]
    theme: str = Field(default="professional")
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Classes | PascalCase | `PlannerAgent`, `SlideOutline` |
| Functions | snake_case | `create_outline()`, `generate_content()` |
| Variables | snake_case | `slide_count`, `output_path` |
| Constants | UPPER_SNAKE_CASE | `MAX_SLIDES`, `DEFAULT_THEME` |
| Private | _leading_underscore | `_internal_helper()` |
| Agents | PascalCase + "Agent" | `ContentAgent`, `DesignAgent` |

### Error Handling

```python
# Use specific exceptions
from src.exceptions import PresentationError, AgentError

# Always catch specific exceptions
try:
    prs = Presentation(template_path)
except FileNotFoundError as e:
    raise PresentationError(f"Template not found: {template_path}") from e
except Exception as e:
    logger.error(f"Unexpected error loading template: {e}")
    raise

# Use result pattern for agent operations
from typing import Union

class AgentResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

def run_agent(input_data: dict) -> AgentResult:
    try:
        result = process(input_data)
        return AgentResult(success=True, data=result)
    except Exception as e:
        return AgentResult(success=False, error=str(e))
```

### Agent Patterns

```python
# LangGraph agent structure
class ContentAgent:
    """Generates slide content from outlines."""
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=SlideContent)
    
    async def run(self, state: AgentState) -> AgentState:
        """Execute agent logic and return updated state."""
        outline = state.outline
        
        prompt = self._build_prompt(outline)
        response = await self.llm.ainvoke(prompt)
        
        content = self.parser.parse(response.content)
        state.slide_content = content
        
        return state
    
    def _build_prompt(self, outline: SlideOutline) -> str:
        """Build LLM prompt from outline."""
        return f"""Generate content for slide: {outline.title}
        
        Key points to cover:
        {outline.key_points}
        """
```

### Testing

```python
# Test file naming: test_*.py
# Test function naming: test_*

import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def planner_agent():
    mock_llm = Mock()
    return PlannerAgent(llm=mock_llm)

@pytest.mark.asyncio
async def test_create_outline_success(planner_agent):
    # Arrange
    request = PresentationRequest(topic="AI Trends")
    
    # Act
    result = await planner_agent.create_outline(request)
    
    # Assert
    assert result.title == "AI Trends"
    assert len(result.slides) > 0

@pytest.mark.parametrize("num_slides", [5, 10, 15])
def test_slide_count_validation(num_slides):
    with pytest.raises(ValueError):
        PresentationRequest(num_slides=num_slides)
```

### Documentation

```python
"""Module for presentation generation agents.

This module implements the multi-agent system for generating
PowerPoint presentations from user requests.
"""

class PlannerAgent:
    """Plans presentation structure and content outline.
    
    The planner agent analyzes user requests and creates a structured
    outline for the presentation, including slide types and content
    direction.
    
    Args:
        llm: Language model for content planning
        config: Optional configuration for planning behavior
    
    Example:
        >>> agent = PlannerAgent(llm=ChatOpenAI())
        >>> outline = await agent.create_outline(request)
    """
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use structured logging
logger.info("Generating presentation", extra={
    "topic": request.topic,
    "num_slides": len(outline.slides),
    "agent": "planner"
})

logger.debug("LLM prompt", extra={"prompt": prompt[:100]})

# Error logging with context
logger.error("Failed to generate slide", extra={
    "slide_number": slide_num,
    "error": str(e),
    "traceback": traceback.format_exc()
})
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── agents/           # Agent implementations
│   │   ├── __init__.py
│   │   ├── planner.py
│   │   ├── content.py
│   │   ├── design.py
│   │   └── qa.py
│   ├── models/           # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── state.py
│   ├── tools/            # Agent tools
│   │   ├── __init__.py
│   │   ├── pptx_tool.py
│   │   └── image_tool.py
│   ├── graph/            # LangGraph workflow
│   │   ├── __init__.py
│   │   └── workflow.py
│   └── exceptions.py     # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_models/
│   └── conftest.py
├── templates/            # PPTX templates
├── examples/             # Example usage
├── pyproject.toml
└── README.md
```

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
```

## Environment Variables

```bash
# .env file
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
LOG_LEVEL=INFO
TEMPLATE_DIR=./templates
OUTPUT_DIR=./output
```

## Common Tasks

```bash
# Create new agent
# 1. Create file in src/agents/{name}.py
# 2. Implement AgentProtocol
# 3. Add tests in tests/test_agents/test_{name}.py
# 4. Register in src/agents/__init__.py

# Add new Pydantic model
# 1. Define in src/models/schemas.py
# 2. Include field descriptions
# 3. Add validation if needed
# 4. Export in src/models/__init__.py

# Run specific agent test
uv run pytest tests/test_agents/test_planner.py -v

# Debug mode
LOG_LEVEL=DEBUG uv run python -m src.main
```
