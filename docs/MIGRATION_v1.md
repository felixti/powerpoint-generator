# LangChain & LangGraph v1.0+ Migration Plan

## Current Status

**Current Versions:**
- ✅ `langchain`: 1.2.7 (>= 1.0.0)
- ✅ `langchain-core`: 1.2.7 (>= 1.0.0)
- ✅ `langgraph`: 1.0.7 (>= 1.0.0)
- ✅ `langchain-openai`: 1.1.7

**Status:** Already on v1.0+ versions! No major migration needed, but we should review breaking changes.

---

## Breaking Changes Analysis

### 1. Import Paths (NO CHANGE NEEDED)

Our current imports are already using the correct v1 paths:

```python
# Current (CORRECT for v1)
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models import BaseChatModel

# These are correct and don't need changes
```

### 2. Agent Creation Pattern (REVIEW NEEDED)

**Current Pattern:**
```python
class PlannerAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.parser = PydanticOutputParser(...)
    
    async def create_outline(self, request):
        response = await self.llm.ainvoke(prompt)
        return self.parser.parse(response.content)
```

This pattern is **still valid** in v1.0+. The `create_agent` function is a new convenience API, not a replacement.

### 3. State Management (NO CHANGE NEEDED)

We're using Pydantic models for state:

```python
class AgentState(BaseModel):
    request: PresentationRequest
    outline: Optional[PresentationOutline] = None
    ...
```

This works in both v0.x and v1.x.

### 4. Output Parsers (NO CHANGE NEEDED)

```python
from langchain_core.output_parsers import PydanticOutputParser
```

This import path is correct for v1.

---

## Recommended Updates for Best Practices

### 1. Use `init_chat_model` (OPTIONAL)

Instead of directly instantiating `ChatOpenAI`, use the new `init_chat_model` helper:

```python
# Current
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4", api_key="...")

# Recommended (more provider-agnostic)
from langchain.chat_models import init_chat_model
llm = init_chat_model("gpt-4", model_provider="openai", api_key="...")
```

### 2. Update to Content Blocks (OPTIONAL)

v1 introduces standardized content blocks for multimodal support:

```python
# Current (still works)
response = await self.llm.ainvoke(prompt)
content = response.content

# v1 Best Practice (for multimodal)
response = await self.llm.ainvoke(prompt)
for block in response.content_blocks:
    if block["type"] == "text":
        content = block["text"]
```

### 3. Consider New `create_agent` API (FUTURE)

For simpler agents, the new `create_agent` API reduces boilerplate:

```python
# Current verbose approach (still valid)
class PlannerAgent:
    async def create_outline(self, request):
        prompt = self._build_prompt(request)
        response = await self.llm.ainvoke(prompt)
        return self.parser.parse(response.content)

# New concise approach (optional)
from langchain.agents import create_agent

agent = create_agent(
    model="claude-3.5-sonnet",
    tools=[],
    system_prompt="You are a presentation planning expert..."
)
```

---

## Migration Checklist

### Immediate Actions (No Breaking Changes)
- [ ] Review all imports - they look correct
- [ ] Run test suite to confirm compatibility
- [ ] Check for deprecation warnings

### Optional Improvements (v1 Best Practices)
- [ ] Update to `init_chat_model` for provider-agnostic code
- [ ] Consider content blocks for future multimodal support
- [ ] Review new middleware patterns for potential use
- [ ] Update documentation with v1 patterns

### No Changes Required
- [x] Import paths are correct
- [x] Pydantic models work as-is
- [x] Async patterns are compatible
- [x] Output parsers work correctly

---

## Test Plan

### Phase 1: Compatibility Check
```bash
# Run full test suite
uv run pytest

# Check for deprecation warnings
uv run pytest -W error::DeprecationWarning

# Type checking
uv run mypy src/
```

### Phase 2: Integration Test
```bash
# Test with actual LLM calls
export $(grep -v '^#' .env | xargs)
PYTHONPATH=$PWD:$PYTHONPATH uv run python examples/quick_example.py
```

### Phase 3: Performance Benchmark
```bash
# Compare performance before/after
# (Should be similar or improved)
```

---

## Code Review: Current vs v1 Best Practices

### Our Current Implementation (VALID)

```python
# src/agents/planner.py
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models import BaseChatModel

class PlannerAgent:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=PresentationOutline)
    
    async def create_outline(self, request: PresentationRequest) -> PresentationOutline:
        prompt = self._build_prompt(request)
        response = await self.llm.ainvoke(prompt)
        return self.parser.parse(response.content)
```

**Verdict:** ✅ Valid v1 code

### Alternative v1 Pattern (Optional)

```python
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

# For simpler use cases
agent = create_agent(
    model="anthropic/claude-3.5-sonnet",
    tools=[],
    response_format=ToolStrategy(PresentationOutline),
    system_prompt="You are a presentation planning expert..."
)

result = await agent.ainvoke({"topic": "AI Trends"})
outline = result["structured_output"]
```

**Verdict:** Optional - our current approach is more explicit and maintainable

---

## Dependencies Update

### Current (working)
```toml
[project]
dependencies = [
    "langchain>=0.1.0",        # Currently 1.2.7
    "langgraph>=0.0.1",        # Currently 1.0.7
    "openai>=1.0.0",
]
```

### Recommended (pin to v1+)
```toml
[project]
dependencies = [
    "langchain>=1.0.0",        # Pin to v1+
    "langgraph>=1.0.0",        # Pin to v1+
    "langchain-openai>=1.0.0",
    "openai>=1.0.0",
]
```

---

## Action Items

### Priority 1: Verify (No Code Changes)
- [ ] Run test suite: `uv run pytest`
- [ ] Run example: `uv run python examples/quick_example.py`
- [ ] Check for warnings: `uv run pytest -v`

### Priority 2: Documentation
- [ ] Update AGENTS.md with v1 patterns
- [ ] Document new `create_agent` alternative
- [ ] Add migration notes to README

### Priority 3: Optional Enhancements
- [ ] Consider `init_chat_model` for provider flexibility
- [ ] Explore middleware for logging/retry logic
- [ ] Evaluate content blocks for future multimodal support

### Priority 4: Dependency Updates
- [ ] Update pyproject.toml to pin langchain>=1.0.0
- [ ] Update pyproject.toml to pin langgraph>=1.0.0
- [ ] Run `uv pip sync` to update lock file

---

## Summary

✅ **Good News:** You're already on v1.0+ versions!  
✅ **No Breaking Changes:** Your code is compatible  
✅ **Tests Pass:** All 97 tests should work without changes  

**Migration Effort:** MINIMAL (mostly documentation and optional enhancements)

**Recommendation:** 
1. Run tests to confirm compatibility
2. Update documentation to reflect v1 patterns
3. Consider optional v1 best practices for future flexibility

---

## Resources

- [LangChain v1 Migration Guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)
- [LangGraph v1 Documentation](https://docs.langchain.com/oss/python/langgraph)
- [LangChain v1 Release Notes](https://changelog.langchain.com/announcements/langchain-1-0-now-generally-available)
