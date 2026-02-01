# AI PowerPoint Generator - Technical Specification

## Project Overview

An AI agent system that generates professional PowerPoint presentations using LangGraph for orchestration, python-pptx for file generation, and LLMs for content creation.

---

## Architecture Overview

```
User Request → Orchestrator (LangGraph) → Specialized Agents → PPTX Output
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
Planner Agent  Content Agent   Design Agent
    ↓               ↓               ↓
  Outline      Slide Content    Visual Design
    └───────────────┴───────────────┘
                    ↓
            QA Agent (Validation)
                    ↓
            Output Generator
```

---

## Phase 1: Foundation (Sprint 1)

### Task 1.1: Project Setup
**Priority:** HIGH  
**Status:** TODO  
**Dependencies:** None

#### Requirements
- [ ] Initialize Python project with pyproject.toml
- [ ] Set up src/ package structure
- [ ] Configure development dependencies (pytest, ruff, mypy)
- [ ] Create .gitignore and .env.example
- [ ] Set up pre-commit hooks

#### Acceptance Criteria
- `pip install -e ".[dev]"` works successfully
- `pytest` runs without errors (even if no tests yet)
- `ruff check src/` passes
- Project structure matches AGENTS.md specification

#### Technical Notes
- Use Python 3.10+
- Include ruff, mypy, pytest in dev dependencies
- Set up src/ layout (not flat)

---

### Task 1.2: Core Models & Schemas
**Priority:** HIGH  
**Status:** TODO  
**Dependencies:** Task 1.1

#### Requirements
- [ ] Create Pydantic models for presentation structures
- [ ] Define AgentState for LangGraph
- [ ] Create input/output schemas
- [ ] Add validation rules

#### Data Models

**PresentationRequest** (Input)
```python
class PresentationRequest(BaseModel):
    topic: str
    audience: str = "general"
    goal: str
    num_slides: Optional[int] = None
    style: str = "professional"  # professional, casual, academic, creative
    key_points: list[str] = []
    template: Optional[str] = None
```

**SlideOutline** (Intermediate)
```python
class SlideOutline(BaseModel):
    slide_number: int
    type: SlideType  # title, content, section, chart, image, summary
    title: str
    key_points: list[str]
    content_notes: str
    visual_recommendation: str
```

**PresentationOutline** (Planner Output)
```python
class PresentationOutline(BaseModel):
    title: str
    objective: str
    slides: list[SlideOutline]
    design_theme: str
```

**AgentState** (LangGraph State)
```python
class AgentState(BaseModel):
    request: PresentationRequest
    outline: Optional[PresentationOutline] = None
    current_slide: int = 0
    slides: list[SlideContent] = []
    errors: list[str] = []
    completed: bool = False
```

#### Acceptance Criteria
- All models have proper type hints
- Validation works for all fields
- Models can be serialized to JSON
- Field descriptions are clear

---

### Task 1.3: PowerPoint Tool (python-pptx)
**Priority:** HIGH  
**Status:** TODO  
**Dependencies:** Task 1.1

#### Requirements
- [ ] Create PPTXTool class wrapper around python-pptx
- [ ] Implement slide creation methods
- [ ] Support text, images, charts
- [ ] Add template loading
- [ ] Implement save/export functionality

#### Interface
```python
class PPTXTool:
    def __init__(self, template_path: Optional[str] = None)
    def add_slide(self, layout: str) -> Slide
    def add_title(self, slide: Slide, text: str)
    def add_bullets(self, slide: Slide, items: list[str])
    def add_image(self, slide: Slide, image_path: str, position: tuple)
    def add_chart(self, slide: Slide, chart_data: ChartData, chart_type: str)
    def save(self, output_path: str)
```

#### Acceptance Criteria
- Can create presentation from scratch
- Can load and modify existing template
- Supports all basic slide layouts
- Handles images and charts
- Saves to valid .pptx file

---

## Phase 2: Agents (Sprint 2)

### Task 2.1: Planner Agent
**Priority:** HIGH  
**Status:** TODO  
**Dependencies:** Task 1.2

#### Requirements
- [ ] Implement PlannerAgent class
- [ ] Create prompt template for outline generation
- [ ] Integrate with LLM (OpenAI/Anthropic)
- [ ] Add structured output parsing
- [ ] Handle errors gracefully

#### Interface
```python
class PlannerAgent:
    def __init__(self, llm: BaseChatModel)
    async def create_outline(self, request: PresentationRequest) -> PresentationOutline
    def _build_prompt(self, request: PresentationRequest) -> str
```

#### Prompt Template
```
You are a presentation planning expert. Create a structured outline for a PowerPoint presentation.

TOPIC: {topic}
AUDIENCE: {audience}
GOAL: {goal}
STYLE: {style}
KEY POINTS: {key_points}

Create an outline with:
1. A compelling title
2. Clear objective statement
3. Logical slide sequence (intro, content, conclusion)
4. Specific content notes for each slide
5. Visual recommendations

Output as JSON matching the PresentationOutline schema.
```

#### Acceptance Criteria
- Generates valid PresentationOutline
- Respects user constraints (num_slides, style)
- Handles missing optional fields
- Includes error handling for LLM failures
- Tests pass: `pytest tests/test_agents/test_planner.py -v`

---

### Task 2.2: Content Agent
**Priority:** HIGH  
**Status:** TODO  
**Dependencies:** Task 2.1

#### Requirements
- [ ] Implement ContentAgent class
- [ ] Generate slide titles and content
- [ ] Create bullet points from key points
- [ ] Generate speaker notes
- [ ] Support different content types

#### Interface
```python
class ContentAgent:
    def __init__(self, llm: BaseChatModel)
    async def generate_slide_content(self, outline: SlideOutline) -> SlideContent
    def _build_content_prompt(self, outline: SlideOutline) -> str
    def _build_notes_prompt(self, content: SlideContent) -> str
```

#### Content Types
- Title slides
- Bullet point content
- Section dividers
- Summary/conclusion
- Two-column layouts

#### Acceptance Criteria
- Generates clear, concise content
- Adapts tone to audience and style
- Creates appropriate speaker notes
- Handles all slide types
- Content fits slide constraints

---

### Task 2.3: Design Agent
**Priority:** MEDIUM  
**Status:** TODO  
**Dependencies:** Task 1.3, Task 2.2

#### Requirements
- [ ] Implement DesignAgent class
- [ ] Apply templates and themes
- [ ] Position text and visual elements
- [ ] Generate charts from data
- [ ] Handle image placement

#### Interface
```python
class DesignAgent:
    def __init__(self, pptx_tool: PPTXTool)
    async def design_slide(self, content: SlideContent, template: str) -> Slide
    def _select_layout(self, content_type: str) -> str
    def _apply_theme(self, slide: Slide, theme: str)
    def _create_chart(self, data: ChartData) -> Image
```

#### Design Capabilities
- Layout selection based on content type
- Color scheme application
- Font styling
- Image positioning
- Chart generation

#### Acceptance Criteria
- Applies templates correctly
- Consistent styling across slides
- Proper visual hierarchy
- Charts render correctly
- Images positioned appropriately

---

### Task 2.4: QA Agent
**Priority:** MEDIUM  
**Status:** TODO  
**Dependencies:** Task 2.1, Task 2.2, Task 2.3

#### Requirements
- [ ] Implement QAAgent class
- [ ] Validate slide count and structure
- [ ] Check content completeness
- [ ] Verify formatting consistency
- [ ] Generate review report

#### Interface
```python
class QAAgent:
    def review_presentation(self, presentation: Presentation) -> QAReport
    def _check_completeness(self, presentation: Presentation) -> list[str]
    def _check_consistency(self, presentation: Presentation) -> list[str]
    def _check_quality(self, presentation: Presentation) -> list[str]
```

#### QA Checks
- All slides have titles
- No empty content slides
- Consistent formatting
- Proper spelling/grammar
- Logical flow

#### Acceptance Criteria
- Identifies missing content
- Catches formatting issues
- Provides actionable feedback
- Can trigger revision loops

---

## Phase 3: Workflow (Sprint 3)

### Task 3.1: LangGraph Workflow
**Priority:** HIGH  
**Status:** TODO  
**Dependencies:** Task 2.1, Task 2.2, Task 2.3

#### Requirements
- [ ] Define workflow state machine
- [ ] Create agent nodes
- [ ] Implement conditional edges
- [ ] Add error handling paths
- [ ] Create workflow compilation

#### Workflow States
1. `receive_request` - User input received
2. `plan_presentation` - PlannerAgent creates outline
3. `generate_content` - ContentAgent writes text
4. `apply_design` - DesignAgent creates visuals
5. `quality_check` - QAAgent reviews
6. `revise` - Loop back if needed
7. `finalize` - Generate final PPTX
8. `deliver` - Return to user

#### Interface
```python
def create_workflow(
    planner: PlannerAgent,
    content_agent: ContentAgent,
    design_agent: DesignAgent,
    qa_agent: QAAgent
) -> StateGraph:
    # Build and compile workflow
    pass

async def run_presentation_generation(
    request: PresentationRequest
) -> PresentationResult:
    # Execute workflow
    pass
```

#### Acceptance Criteria
- Workflow compiles without errors
- All states transition correctly
- Error paths work
- State is maintained through workflow
- Can handle async operations

---

### Task 3.2: API/CLI Interface
**Priority:** MEDIUM  
**Status:** TODO  
**Dependencies:** Task 3.1

#### Requirements
- [ ] Create CLI interface
- [ ] Add API endpoints (FastAPI optional)
- [ ] Implement input validation
- [ ] Add progress reporting
- [ ] Create output handling

#### CLI Interface
```bash
# Generate presentation
pptgen generate --topic "AI Trends" --audience "executives" --output ./output.pptx

# Use template
pptgen generate --topic "Q4 Review" --template ./templates/corporate.pptx

# Interactive mode
pptgen interactive
```

#### API Interface (Optional)
```python
@app.post("/generate")
async def generate_presentation(request: PresentationRequest) -> PresentationResponse:
    result = await run_presentation_generation(request)
    return result
```

#### Acceptance Criteria
- CLI works with all options
- Input validation catches errors
- Progress shown during generation
- Output saved to specified path
- Clear error messages

---

## Phase 4: Advanced Features (Sprint 4)

### Task 4.1: Template System
**Priority:** MEDIUM  
**Status:** TODO  
**Dependencies:** Task 1.3

#### Requirements
- [ ] Create template library
- [ ] Support custom template upload
- [ ] Extract template metadata
- [ ] Map content to template layouts
- [ ] Document template creation

#### Template Structure
```
templates/
├── corporate/
│   ├── master.pptx
│   ├── metadata.json
│   └── preview.png
├── creative/
│   ├── master.pptx
│   ├── metadata.json
│   └── preview.png
└── academic/
    ├── master.pptx
    ├── metadata.json
    └── preview.png
```

#### Acceptance Criteria
- Templates load correctly
- Content maps to appropriate layouts
- Custom templates work
- Metadata extracted properly

---

### Task 4.2: Chart Generation
**Priority:** MEDIUM  
**Status:** TODO  
**Dependencies:** Task 2.3

#### Requirements
- [ ] Support data import (CSV/Excel)
- [ ] Generate bar charts
- [ ] Generate line charts
- [ ] Generate pie charts
- [ ] Style charts to match theme

#### Chart Types
- Bar charts (vertical, horizontal, grouped)
- Line charts (single, multi-series)
- Pie charts
- Area charts

#### Acceptance Criteria
- Charts render in PowerPoint
- Data correctly represented
- Styling matches presentation theme
- Legends and labels clear

---

### Task 4.3: Image Integration
**Priority:** LOW  
**Status:** TODO  
**Dependencies:** Task 2.3

#### Requirements
- [ ] Support image URLs
- [ ] Support local image files
- [ ] Generate images via DALL-E/Stable Diffusion
- [ ] Resize and position images
- [ ] Add alt text

#### Image Sources
- URL download
- Local file
- AI generation (optional)

#### Acceptance Criteria
- Images display correctly
- Proper aspect ratio maintained
- Positioned appropriately
- Alt text added for accessibility

---

## Testing Requirements

### Unit Tests
- [ ] Test all Pydantic models
- [ ] Test each agent in isolation
- [ ] Test PPTXTool methods
- [ ] Test workflow state transitions

### Integration Tests
- [ ] End-to-end presentation generation
- [ ] Multi-agent workflow
- [ ] Error handling scenarios
- [ ] Template loading

### Test Coverage
- Minimum 80% coverage
- Critical paths 100% coverage
- Use pytest-asyncio for async tests

---

## Documentation Requirements

### Code Documentation
- [ ] All public functions have docstrings
- [ ] Complex logic has inline comments
- [ ] README with setup instructions
- [ ] Architecture diagram

### User Documentation
- [ ] Installation guide
- [ ] Usage examples
- [ ] Template creation guide
- [ ] Troubleshooting

---

## Performance Requirements

- Generate 10-slide presentation in < 2 minutes
- Support presentations up to 50 slides
- Memory usage < 500MB for large presentations
- Concurrent request handling (if API mode)

---

## Security Requirements

- API keys stored in environment variables
- Input validation on all user inputs
- Safe file path handling
- No execution of user-provided code

---

## Dependencies

### Core
```
python-pptx>=0.6.21
langchain>=0.1.0
langgraph>=0.0.50
pydantic>=2.0.0
openai>=1.0.0
```

### Development
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
ruff>=0.1.0
mypy>=1.0.0
```

### Optional
```
fastapi>=0.100.0  # For API mode
uvicorn>=0.23.0   # For API server
pandas>=2.0.0     # For chart data
matplotlib>=3.7.0 # For chart generation
```

---

## File Structure

```
.
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py
│   │   ├── content.py
│   │   ├── design.py
│   │   └── qa.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── state.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── pptx_tool.py
│   │   └── image_tool.py
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── exceptions.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agents/
│   │   ├── test_planner.py
│   │   ├── test_content.py
│   │   ├── test_design.py
│   │   └── test_qa.py
│   ├── test_models/
│   │   └── test_schemas.py
│   ├── test_tools/
│   │   └── test_pptx_tool.py
│   └── test_graph/
│       └── test_workflow.py
├── templates/
│   ├── corporate/
│   ├── creative/
│   └── academic/
├── examples/
│   ├── basic_usage.py
│   └── custom_template.py
├── docs/
│   ├── installation.md
│   └── usage.md
├── pyproject.toml
├── README.md
├── AGENTS.md
└── .env.example
```

---

## Success Criteria

1. **Functional:** Can generate complete presentations from text prompts
2. **Quality:** Content is clear, engaging, and audience-appropriate
3. **Visual:** Output looks professional and consistent
4. **Performance:** Generates presentations in under 2 minutes
5. **Reliable:** Handles errors gracefully
6. **Extensible:** Easy to add new agents and features

---

## Notes for Agents

- Follow AGENTS.md for code style
- Run tests before committing: `pytest`
- Run linting: `ruff check src/ tests/`
- Run type checking: `mypy src/`
- Update this spec when requirements change
- Mark tasks as COMPLETED when done
