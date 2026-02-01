# Research Summary - AI PowerPoint Generator

## Quick Reference for Agents

This document summarizes all research findings for quick reference during implementation.

---

## PowerPoint Libraries

### Primary: python-pptx
```python
from pptx import Presentation

# Basic usage
prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.shapes.title
title.text = "Hello World"
prs.save('output.pptx')
```

**Key Features:**
- 3.2k stars, MIT license
- Pure Python, cross-platform
- Slides, text, images, tables, charts
- No PowerPoint installation required

**Installation:** `pip install python-pptx`

**Documentation:** https://python-pptx.readthedocs.io/

---

## LangGraph Patterns

### 1. Basic State Graph
```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    topic: str
    content: str

builder = StateGraph(State)
builder.add_node("node_name", node_function)
builder.add_edge(START, "node_name")
builder.add_edge("node_name", END)
graph = builder.compile()
```

### 2. Parallel Execution
```python
# Parallel nodes from START
builder.add_edge(START, "agent_1")
builder.add_edge(START, "agent_2")
builder.add_edge("agent_1", "aggregator")
builder.add_edge("agent_2", "aggregator")
```

### 3. Conditional Edges (Feedback Loop)
```python
from typing import Literal

def route(state: State) -> Literal["retry", END]:
    if state["approved"]:
        return END
    return "retry"

builder.add_conditional_edges("reviewer", route, {
    "retry": "generator",
    END: END
})
```

### 4. Structured Output
```python
from pydantic import BaseModel

class SlideContent(BaseModel):
    title: str
    bullets: list[str]

# Method 1: ProviderStrategy (native)
agent = llm.with_structured_output(SlideContent)
result = agent.invoke(prompt)

# Method 2: ToolStrategy
from langchain.agents.structured_output import ToolStrategy
agent = create_agent(
    model="gpt-4o",
    response_format=ToolStrategy(SlideContent)
)
```

---

## Recommended Architecture

```python
class PPTState(TypedDict):
    request: PresentationRequest
    outline: Optional[PresentationOutline]
    slides: Annotated[list, operator.add]
    approved: bool
    feedback: str
    output_path: str

# Nodes
builder.add_node("planner", planner_agent)
builder.add_node("content", content_agent)
builder.add_node("design", design_agent)
builder.add_node("qa", qa_agent)
builder.add_node("export", export_agent)

# Flow
builder.add_edge(START, "planner")
builder.add_edge("planner", "content")
builder.add_edge("content", "design")
builder.add_edge("design", "qa")
builder.add_conditional_edges("qa", route_qa, {
    "content": "content",
    "export": "export"
})
builder.add_edge("export", END)
```

---

## Agent Patterns

### Planner Agent
- **Input:** PresentationRequest
- **Output:** PresentationOutline
- **Strategy:** Single LLM call with structured output
- **Prompt:** "Create outline for {topic} with {num_slides} slides"

### Content Agent
- **Input:** SlideOutline
- **Output:** SlideContent
- **Strategy:** Can run in parallel for each slide
- **Prompt:** "Generate content for slide: {title}"

### Design Agent
- **Input:** SlideContent + template
- **Output:** Slide (python-pptx object)
- **Strategy:** Direct PPTX manipulation
- **Uses:** PPTXTool wrapper

### QA Agent
- **Input:** List of slides
- **Output:** QAReport (approved, feedback)
- **Strategy:** Structured output with grading
- **Triggers:** Revision loop if not approved

---

## Data Models

```python
class PresentationRequest(BaseModel):
    topic: str
    audience: str = "general"
    goal: str
    num_slides: Optional[int] = None
    style: str = "professional"
    key_points: list[str] = []

class SlideOutline(BaseModel):
    slide_number: int
    type: Literal["title", "content", "section", "chart", "summary"]
    title: str
    key_points: list[str]
    content_notes: str

class PresentationOutline(BaseModel):
    title: str
    objective: str
    slides: list[SlideOutline]
    design_theme: str

class SlideContent(BaseModel):
    title: str
    content: list[str]
    notes: str
```

---

## File Structure

```
src/
├── agents/
│   ├── planner.py      # Creates outline
│   ├── content.py      # Generates content
│   ├── design.py       # Applies visuals
│   └── qa.py          # Validates output
├── models/
│   ├── schemas.py      # Pydantic models
│   └── state.py        # LangGraph state
├── tools/
│   ├── pptx_tool.py    # python-pptx wrapper
│   └── chart_tool.py   # Chart generation
└── graph/
    └── workflow.py     # LangGraph workflow
```

---

## Common Commands

```bash
# Install
pip install -e ".[dev]"

# Test
pytest tests/test_agents/test_planner.py -v

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/

# All quality checks
ruff check src/ tests/ && mypy src/ && pytest
```

---

## Key Decisions

1. **python-pptx** - Most mature, best choice
2. **LangGraph** - Better than CrewAI for stateful workflows
3. **Pydantic models** - For structured output validation
4. **Template-first** - Use templates for consistent branding
5. **JSON mode** - Use structured output for reliable parsing

---

## Resources

- **python-pptx docs:** https://python-pptx.readthedocs.io/
- **LangGraph docs:** https://docs.langchain.com/oss/python/langgraph
- **LangChain docs:** https://docs.langchain.com/oss/python
- **SPEC.md:** Full technical specification
- **TASKS.md:** Task breakdown and assignments
- **AGENTS.md:** Code style guidelines

---

## Next Steps

1. Set up project structure (Task 1.1)
2. Create Pydantic models (Task 1.2)
3. Build PPTXTool wrapper (Task 1.3)
4. Implement Planner Agent (Task 2.1)
5. Build LangGraph workflow (Task 3.1)

See TASKS.md for complete task list.
