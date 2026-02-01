# OpenRouter Integration Guide

## Overview

The AI PowerPoint Generator now uses **OpenRouter** as its default LLM provider. OpenRouter provides a unified API for accessing multiple LLM providers including Anthropic (Claude), OpenAI (GPT), Google (Gemini), and many others.

## Why OpenRouter?

1. **Multi-Provider Access**: Use Claude, GPT, Gemini, and 100+ models with one API key
2. **Unified Interface**: Same API format for all providers
3. **Cost Effective**: Competitive pricing and rate limiting
4. **Easy Switching**: Change models by changing the model identifier
5. **Fallback Support**: Automatic failover between providers

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Required
OPENROUTER_API_KEY=sk-or-your-api-key-here

# Optional (with defaults)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_SITE_URL=https://your-site.com
OPENROUTER_SITE_NAME=YourAppName
```

Get your API key at: https://openrouter.ai/

### Available Models

Popular models available through OpenRouter:

| Model | Provider | Best For |
|-------|----------|----------|
| `anthropic/claude-3.5-sonnet` | Anthropic | General purpose, reasoning |
| `anthropic/claude-3-opus` | Anthropic | Complex tasks, analysis |
| `openai/gpt-4-turbo` | OpenAI | General purpose |
| `openai/gpt-4o` | OpenAI | Fast, cost-effective |
| `google/gemini-pro` | Google | Multilingual, reasoning |
| `meta-llama/llama-3.1-405b` | Meta | Open source, large context |

See full list: https://openrouter.ai/models

## Usage

### Basic Usage

```python
from src.config.llm_config import create_llm
from src.agents.planner import PlannerAgent

# Create LLM with default settings
llm = create_llm()

# Or specify a model
llm = create_llm(model="anthropic/claude-3.5-sonnet")

# Use with agents
planner = PlannerAgent(llm=llm)
```

### Advanced Configuration

```python
from src.config.llm_config import create_llm

llm = create_llm(
    model="anthropic/claude-3.5-sonnet",
    api_key="sk-or-your-key",  # Or use env var
    temperature=0.5,
    max_tokens=2000,
    site_url="https://your-site.com",
    site_name="YourApp",
)
```

### Direct Class Usage

```python
from src.config.llm_config import ChatOpenRouter

llm = ChatOpenRouter(
    api_key="sk-or-your-key",
    model="anthropic/claude-3.5-sonnet",
    temperature=0.7,
)

response = llm.invoke("Hello, world!")
print(response.content)
```

## Example: Generate Presentation

```python
import asyncio
from src.config.llm_config import create_llm
from src.agents.planner import PlannerAgent
from src.models.schemas import PresentationRequest

async def main():
    # Create LLM
    llm = create_llm(model="anthropic/claude-3.5-sonnet")
    
    # Create request
    request = PresentationRequest(
        topic="AI Trends in 2026",
        audience="business executives",
        goal="Inform about upcoming AI developments",
        num_slides=10,
        style="professional",
    )
    
    # Generate outline
    planner = PlannerAgent(llm=llm)
    outline = await planner.create_outline(request)
    
    print(f"Title: {outline.title}")
    print(f"Slides: {len(outline.slides)}")

if __name__ == "__main__":
    asyncio.run(main())
```

See full example: `examples/openrouter_usage.py`

## Architecture

### ChatOpenRouter Class

Extends `ChatOpenAI` from `langchain_openai` with OpenRouter-specific configuration:

- **API Endpoint**: `https://openrouter.ai/api/v1`
- **Headers**: Automatically adds `HTTP-Referer` and `X-Title`
- **Error Handling**: Validates API key presence
- **Environment Integration**: Reads from environment variables

### create_llm() Factory

Convenience function that:
- Reads configuration from environment variables
- Provides sensible defaults
- Supports parameter override
- Returns a configured `ChatOpenRouter` instance

## Migration from OpenAI

If you were previously using OpenAI directly:

### Before (OpenAI)
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="sk-...",
    model="gpt-4-turbo",
)
```

### After (OpenRouter)
```python
from src.config.llm_config import create_llm

llm = create_llm(
    model="openai/gpt-4-turbo",  # Just add provider prefix
)
```

## Troubleshooting

### Error: "OPENROUTER_API_KEY not set"

**Solution**: Set the environment variable:
```bash
export OPENROUTER_API_KEY=sk-or-your-key-here
```

Or provide it directly:
```python
llm = create_llm(api_key="sk-or-your-key")
```

### Error: "Model not found"

**Solution**: Check the model identifier format. It should be `provider/model-name`:
```python
# Correct
llm = create_llm(model="anthropic/claude-3.5-sonnet")

# Incorrect
llm = create_llm(model="claude-3.5-sonnet")  # Missing provider prefix
```

### Rate Limiting

OpenRouter uses rate limiting based on your account tier. If you hit limits:
1. Set `OPENROUTER_SITE_URL` and `OPENROUTER_SITE_NAME` for higher limits
2. Consider upgrading your OpenRouter account
3. Implement retry logic with exponential backoff

## Files

- `src/config/llm_config.py` - LLM configuration module
- `src/config/__init__.py` - Module exports
- `.env.example` - Environment variable examples
- `examples/openrouter_usage.py` - Usage examples

## Resources

- OpenRouter Docs: https://openrouter.ai/docs
- Model Pricing: https://openrouter.ai/models
- API Reference: https://openrouter.ai/docs/api-reference
