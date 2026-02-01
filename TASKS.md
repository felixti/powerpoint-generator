# Project Tasks - AI PowerPoint Generator

## Overview
This file contains all tasks for the AI PowerPoint Generator project. Agents should reference this when picking up work.

**Status Legend:**
- `[ ]` TODO - Not started
- `[~]` IN_PROGRESS - Currently being worked on
- `[x]` COMPLETED - Done and verified
- `[-]` BLOCKED - Waiting on dependencies

---

## Phase 1: Foundation

### 1.1 Project Setup
**Status:** [ ] TODO  
**Priority:** HIGH  
**Assignee:** TBD  
**Dependencies:** None

#### Tasks
- [ ] Initialize Python project with pyproject.toml
- [ ] Set up src/ package structure
- [ ] Configure development dependencies (pytest, ruff, mypy)
- [ ] Create .gitignore and .env.example
- [ ] Set up pre-commit hooks

#### Acceptance Criteria
- `pip install -e ".[dev]"` works
- `pytest` runs without errors
- `ruff check src/` passes

#### Files to Create
- `pyproject.toml`
- `.gitignore`
- `.env.example`
- `.pre-commit-config.yaml`
- `src/__init__.py`

---

### 1.2 Core Models & Schemas
**Status:** [ ] TODO  
**Priority:** HIGH  
**Assignee:** TBD  
**Dependencies:** 1.1

#### Tasks
- [ ] Create Pydantic models for presentation structures
- [ ] Define AgentState for LangGraph
- [ ] Create input/output schemas
- [ ] Add validation rules
- [ ] Write unit tests for all models

#### Models to Implement
1. **PresentationRequest** - User input schema
2. **SlideOutline** - Individual slide plan
3. **PresentationOutline** - Complete outline
4. **SlideContent** - Generated content
5. **AgentState** - LangGraph state
6. **QAReport** - Quality check results

#### Files to Create
- `src/models/__init__.py`
- `src/models/schemas.py`
- `src/models/state.py`
- `tests/test_models/test_schemas.py`

---

### 1.3 PowerPoint Tool (python-pptx)
**Status:** [ ] TODO  
**Priority:** HIGH  
**Assignee:** TBD  
**Dependencies:** 1.1

#### Tasks
- [ ] Create PPTXTool class wrapper
- [ ] Implement slide creation methods
- [ ] Support text, images, charts
- [ ] Add template loading
- [ ] Implement save/export
- [ ] Write comprehensive tests

#### Methods to Implement
- `__init__(template_path)`
- `add_slide(layout)`
- `add_title(slide, text)`
- `add_bullets(slide, items)`
- `add_image(slide, path, position)`
- `add_chart(slide, data, type)`
- `save(output_path)`

#### Files to Create
- `src/tools/__init__.py`
- `src/tools/pptx_tool.py`
- `tests/test_tools/test_pptx_tool.py`

---

## Phase 2: Agents

### 2.1 Planner Agent
**Status:** [ ] TODO  
**Priority:** HIGH  
**Assignee:** TBD  
**Dependencies:** 1.2

#### Tasks
- [ ] Implement PlannerAgent class
- [ ] Create prompt template
- [ ] Integrate with LLM
- [ ] Add structured output parsing
- [ ] Handle errors gracefully
- [ ] Write unit tests

#### Interface
```python
class PlannerAgent:
    def __init__(self, llm: BaseChatModel)
    async def create_outline(request: PresentationRequest) -> PresentationOutline
    def _build_prompt(request: PresentationRequest) -> str
```

#### Files to Create
- `src/agents/__init__.py`
- `src/agents/planner.py`
- `tests/test_agents/test_planner.py`

---

### 2.2 Content Agent
**Status:** [ ] TODO  
**Priority:** HIGH  
**Assignee:** TBD  
**Dependencies:** 2.1

#### Tasks
- [ ] Implement ContentAgent class
- [ ] Generate slide titles and content
- [ ] Create bullet points
- [ ] Generate speaker notes
- [ ] Support different content types
- [ ] Write unit tests

#### Content Types
- Title slides
- Bullet point content
- Section dividers
- Summary slides
- Two-column layouts

#### Files to Create
- `src/agents/content.py`
- `tests/test_agents/test_content.py`

---

### 2.3 Design Agent
**Status:** [ ] TODO  
**Priority:** MEDIUM  
**Assignee:** TBD  
**Dependencies:** 1.3, 2.2

#### Tasks
- [ ] Implement DesignAgent class
- [ ] Apply templates and themes
- [ ] Position elements
- [ ] Generate charts from data
- [ ] Handle image placement
- [ ] Write unit tests

#### Files to Create
- `src/agents/design.py`
- `tests/test_agents/test_design.py`

---

### 2.4 QA Agent
**Status:** [ ] TODO  
**Priority:** MEDIUM  
**Assignee:** TBD  
**Dependencies:** 2.1, 2.2, 2.3

#### Tasks
- [ ] Implement QAAgent class
- [ ] Validate slide structure
- [ ] Check content completeness
- [ ] Verify formatting consistency
- [ ] Generate review report
- [ ] Write unit tests

#### QA Checks
- All slides have titles
- No empty content
- Consistent formatting
- Spelling/grammar
- Logical flow

#### Files to Create
- `src/agents/qa.py`
- `tests/test_agents/test_qa.py`

---

## Phase 3: Workflow

### 3.1 LangGraph Workflow
**Status:** [ ] TODO  
**Priority:** HIGH  
**Assignee:** TBD  
**Dependencies:** 2.1, 2.2, 2.3

#### Tasks
- [ ] Define workflow state machine
- [ ] Create agent nodes
- [ ] Implement conditional edges
- [ ] Add error handling paths
- [ ] Compile workflow
- [ ] Write integration tests

#### Workflow States
1. `receive_request`
2. `plan_presentation`
3. `generate_content`
4. `apply_design`
5. `quality_check`
6. `revise`
7. `finalize`
8. `deliver`

#### Files to Create
- `src/graph/__init__.py`
- `src/graph/workflow.py`
- `tests/test_graph/test_workflow.py`

---

### 3.2 CLI Interface
**Status:** [ ] TODO  
**Priority:** MEDIUM  
**Assignee:** TBD  
**Dependencies:** 3.1

#### Tasks
- [ ] Create CLI with argparse/click
- [ ] Implement generate command
- [ ] Add progress reporting
- [ ] Handle errors gracefully
- [ ] Write tests

#### Commands
```bash
pptgen generate --topic "AI Trends" --output ./output.pptx
pptgen generate --topic "Q4 Review" --template ./templates/corporate.pptx
pptgen interactive
```

#### Files to Create
- `src/cli/__init__.py`
- `src/cli/main.py`

---

## Phase 4: Advanced Features

### 4.1 Template System
**Status:** [ ] TODO  
**Priority:** MEDIUM  
**Assignee:** TBD  
**Dependencies:** 1.3

#### Tasks
- [ ] Create template library structure
- [ ] Support custom template upload
- [ ] Extract template metadata
- [ ] Map content to layouts
- [ ] Document template creation
- [ ] Create example templates

#### Template Types
- Corporate
- Creative
- Academic

#### Files to Create
- `templates/corporate/master.pptx`
- `templates/creative/master.pptx`
- `templates/academic/master.pptx`

---

### 4.2 Chart Generation
**Status:** [ ] TODO  
**Priority:** MEDIUM  
**Assignee:** TBD  
**Dependencies:** 2.3

#### Tasks
- [ ] Support data import (CSV/Excel)
- [ ] Generate bar charts
- [ ] Generate line charts
- [ ] Generate pie charts
- [ ] Style charts to match theme
- [ ] Write tests

#### Chart Types
- Bar (vertical, horizontal, grouped)
- Line (single, multi-series)
- Pie
- Area

#### Files to Create
- `src/tools/chart_tool.py`
- `tests/test_tools/test_chart_tool.py`

---

### 4.3 Image Integration
**Status:** [ ] TODO  
**Priority:** LOW  
**Assignee:** TBD  
**Dependencies:** 2.3

#### Tasks
- [ ] Support image URLs
- [ ] Support local files
- [ ] Optional: AI image generation
- [ ] Resize and position images
- [ ] Add alt text

#### Files to Create
- `src/tools/image_tool.py`
- `tests/test_tools/test_image_tool.py`

---

## Documentation

### Docs Setup
**Status:** [ ] TODO  
**Priority:** MEDIUM  
**Assignee:** TBD  
**Dependencies:** None

#### Tasks
- [ ] Create README.md with setup instructions
- [ ] Write installation guide
- [ ] Create usage examples
- [ ] Document architecture
- [ ] Add troubleshooting guide

#### Files to Create
- `README.md`
- `docs/installation.md`
- `docs/usage.md`
- `docs/architecture.md`
- `examples/basic_usage.py`
- `examples/custom_template.py`

---

## Testing

### Test Infrastructure
**Status:** [ ] TODO  
**Priority:** HIGH  
**Assignee:** TBD  
**Dependencies:** 1.1

#### Tasks
- [ ] Set up pytest configuration
- [ ] Create conftest.py with fixtures
- [ ] Add pytest-asyncio support
- [ ] Configure coverage reporting
- [ ] Set up CI/CD (GitHub Actions)

#### Coverage Requirements
- Minimum 80% coverage
- Critical paths 100% coverage

#### Files to Create
- `tests/__init__.py`
- `tests/conftest.py`
- `.github/workflows/ci.yml`

---

## Dependencies

### Core Requirements
```
python-pptx>=0.6.21
langchain>=0.1.0
langgraph>=0.0.50
pydantic>=2.0.0
openai>=1.0.0
```

### Development Requirements
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
ruff>=0.1.0
mypy>=1.0.0
```

### Optional Requirements
```
fastapi>=0.100.0
uvicorn>=0.23.0
pandas>=2.0.0
matplotlib>=3.7.0
```

---

## Quick Reference

### Running Tests
```bash
# All tests
pytest

# Single test file
pytest tests/test_agents/test_planner.py

# Single test
pytest tests/test_agents/test_planner.py::test_create_outline

# With coverage
pytest --cov=src --cov-report=html
```

### Code Quality
```bash
# Linting
ruff check src/ tests/
ruff check --fix src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/

# All checks
ruff check src/ tests/ && mypy src/ && pytest
```

### Installation
```bash
pip install -e ".[dev]"
```

---

## Notes

- Follow AGENTS.md for code style guidelines
- Update this file when tasks are completed
- Add new tasks as needed
- Mark dependencies clearly
- Keep acceptance criteria specific and measurable
