# LLM Structured Content Generation Research Summary

**Research Date**: January 31, 2026
**Topic**: Patterns for LLM-based structured content generation for presentations

---

## Overview

This document summarizes comprehensive research on LLM-based structured content generation patterns, specifically for PowerPoint presentations. The research covers structured output techniques, chain-of-thought reasoning, multi-step generation workflows, and schema design best practices.

---

## Key Findings

### 1. **Structured Output is Critical but Has Trade-offs**

Forcing LLMs to output JSON degrades reasoning performance by 10-15%. The optimal approach is:
- **Two-step generation**: Free reasoning → separate formatting
- **Native structured output**: Use OpenAI `response_format` or Anthropic `tools`
- **Type-safe schemas**: Use Zod (TypeScript) or Pydantic (Python)

**Best Practice**: Always separate reasoning from structured output when accuracy matters.

### 2. **Chain-of-Thought Improves Accuracy Significantly**

Asking models to "show work" (CoT) improved math problem accuracy from 17.9% to 57.1%, reaching 74.4% with self-consistency.

**Best Practice**: Apply CoT to the planning/outline phase specifically, not slide content generation.

### 3. **Planner-Executor Pattern Balances Cost and Quality**

Small models (GPT-4o-mini) for planning + large models (GPT-4o) for execution achieves performance comparable to large models at 60-80% lower cost.

**Best Practice**: Use smaller models for outline generation, larger models for detailed content.

### 4. **Multi-Step Workflows Produce Better Results**

The most effective pattern for presentations:
1. Research/outline → 2. User review → 3. Content generation → 4. Visual enhancement → 5. Assembly

**Best Practice**: Always generate outline before content, include user review step.

---

## Recommended Architecture for PowerPoint Agent

### Core Design Principles

| Principle | Description |
|----------|-------------|
| **Structured Output** | Use OpenAI `response_format` with Zod schemas |
| **Two-Step Generation** | Outline first, content second |
| **CoT for Planning** | Apply chain-of-thought to outline generation only |
| **Planner-Executor** | GPT-4o-mini for outline, GPT-4o for content |
| **Simple Schemas** | Type-based (title, bullet, image, table) |
| **Batch Processing** | Generate 3-5 slides per API call |
| **User Review** | Require approval after outline generation |
| **Parallel Execution** | Generate slides in parallel after outline approval |
| **Semantic Validation** | Rule-based + LLM quality check |

---

## Schema Design

### Recommended Slide Structure

```typescript
interface Slide {
  type: 'title' | 'bullet' | 'image' | 'table' | 'split';
  title: string;
  subtitle?: string;
  content?: string[];
  bullet_points?: Array<{
    text: string;
    level: 0 | 1 | 2;
  }>;
  image?: {
    url: string;
    alt: string;
    caption?: string;
  };
  table?: {
    headers: string[];
    rows: string[][];
  };
  notes?: string;
  duration_minutes?: number;
  transition?: string;
}

interface Presentation {
  metadata: {
    title: string;
    author?: string;
    tone: 'professional' | 'casual' | 'educational' | 'sales_pitch';
    verbosity: 'concise' | 'standard' | 'text-heavy';
    language: string;
    theme: 'light' | 'dark' | 'colorful' | 'minimal';
  };
  slides: Slide[];
  export_format: 'pptx' | 'pdf';
}
```

**Key Features**:
- **Type-based system**: Clear intent with `type` field
- **Flat bullets**: Level field instead of nested children (less error-prone)
- **Metadata section**: Captures tone, language, theme
- **Optional fields**: Flexibility while maintaining structure
- **Visual support**: Image, table, and split layouts

---

## Multi-Step Workflow Example

```typescript
// Stage 1: Generate Outline (with CoT)
const outline = await client.chat.completions.parse({
  model: 'gpt-4o-mini',
  messages: [{
    role: 'system',
    content: 'You are a presentation planner. Use chain-of-thought to plan structure.'
  }, {
    role: 'user',
    content: `Plan a presentation on "${topic}" with ${n_slides} slides.`
  }],
  response_format: zodResponseFormat(Outline, 'outline')
});

// Stage 2: User Review (CLI/Web Interface)
const approvedOutline = await userReview(outline);

// Stage 3: Generate Content (batched, parallel)
const slideBatches = chunk(approvedOutline.slides, 4);
const slides = [];
for (const batch of slideBatches) {
  const batchSlides = await Promise.all(
    batch.map(slide => 
      client.chat.completions.parse({
        model: 'gpt-4o',
        messages: [{
          role: 'user',
          content: `Expand this slide into detailed content: ${JSON.stringify(slide)}`
        }],
        response_format: zodResponseFormat(Slide, 'slide')
      })
    )
  );
  slides.push(...batchSlides);
}

// Stage 4: Generate Images (separate API)
for (const slide of slides) {
  if (slide.type === 'image' || slide.requires_image) {
    slide.image.url = await generateImage(slide.image_prompt);
  }
}

// Stage 5: Assemble PPTX
const presentation = await assemblePPTX({ 
  slides, 
  metadata: approvedOutline.metadata 
});
```

---

## Implementation Checklist

### Phase 1: Core Structured Output
- [ ] Set up OpenAI client with `response_format`
- [ ] Define Zod schemas for Slide and Presentation
- [ ] Implement Pydantic schemas for Python validation
- [ ] Create transformation layer JSON → python-pptx
- [ ] Add schema validation error handling

### Phase 2: Planning and Content Generation
- [ ] Implement CoT prompt for outline generation
- [ ] Create planner-executor pattern (mini → 4o)
- [ ] Implement batch slide generation (3-5 slides)
- [ ] Add retry logic with exponential backoff
- [ ] Implement parallel slide generation

### Phase 3: User Review Workflow
- [ ] Design CLI review interface
- [ ] Implement outline display and edit
- [ ] Add confirmation workflow
- [ ] Pass approved outline to content generation
- [ ] Implement state persistence

### Phase 4: Visual and Theme Support
- [ ] Define 4-6 theme configurations
- [ ] Implement theme application to slides
- [ ] Add color scheme selection
- [ ] Integrate image generation provider
- [ ] Implement fallback for failed images

### Phase 5: Quality Assurance
- [ ] Implement rule-based validation
- [ ] Create LLM semantic evaluation prompt
- [ ] Add quality scoring system (0-100)
- [ ] Implement improvement suggestions
- [ ] Add logging infrastructure

### Phase 6: Performance and Scalability
- [ ] Implement request queue with rate limiting
- [ ] Add caching layer (24-48 hour TTL)
- [ ] Implement concurrent request limiter
- [ ] Add progress reporting
- [ ] Monitor and optimize batch sizes

---

## Key Resources

### Documentation
- [OpenAI Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)
- [OpenAI Node SDK Helpers](https://github.com/openai/openai-node/blob/master/helpers.md)
- [Anthropic Tool Use Documentation](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/helpers.md)
- [Presenton Documentation](https://docs.presenton.ai)

### Research Papers
- [PPTPPTAgent: Generating and Evaluating Presentations](https://arxiv.org/html/2501.03936v1)
- [Efficient LLM Collaboration via Planning (COPE)](https://arxiv.org/html/2506.11578v3)
- [Chain-of-Thought Prompting](https://www.comet.com/site/blog/chain-of-thought-prompting/)

### Open Source Projects
- [pptx-api](https://github.com/cg123/pptx-api) - Simple JSON schema for PPTX
- [presenton](https://github.com/presenton/presenton) - Full AI presentation generator
- [think-cell JSON Automation](https://www.think-cell.com/en/resources/manual/jsondataautomation) - Commercial solution

### Guides and Articles
- [Beyond JSON: Format Choice for LLM Pipelines](https://www.linkedin.com/pulse/beyond-json-picking-right-format-llm-pipelines-michael-hannecke-ftnye)
- [AI Workflows for Content Planning 2026](https://www.airops.com/blog/ai-workflows-content-planning)
- [Prompt Engineering Guide 2026](https://www.the-ai-corner.com/p/your-2026-guide-to-prompt-engineering)

---

## Critical Gotchas to Avoid

1. **Don't force JSON during CoT** - It degrades reasoning by 10-15%
2. **Don't use nested bullet arrays** - Use flat arrays with level field instead
3. **Don't generate entire presentation in one call** - Split into outline + content
4. **Don't skip schema validation** - Invalid JSON breaks the pipeline
5. **Don't ignore context loss** - Pass previous slides to each generation
6. **Don't rely on LLM-generated URLs** - Use dedicated image generation APIs
7. **Don't mix tones** - Define tone explicitly and enforce it
8. **Don't exceed token limits** - Use batching for long presentations
9. **Don't skip user review** - Outline approval saves cost and improves alignment

---

## Performance Expectations

### Accuracy Improvements
- **CoT for planning**: 17.9% → 57.1% accuracy (up to 74.4% with self-consistency)
- **Structured output**: 100% valid JSON (vs 60-80% with manual parsing)
- **Two-step generation**: Better quality with similar token usage

### Cost Optimization
- **Planner-executor**: 60-80% cost reduction vs full GPT-4o
- **Batch generation**: 20-30% faster than sequential
- **Caching**: 30-50% reduction for repeated topics

### Latency Estimates
- **Outline generation**: 2-5 seconds (GPT-4o-mini)
- **Slide content (batch of 4)**: 10-15 seconds (GPT-4o, parallel)
- **Image generation**: 2-5 seconds per image
- **PPTX assembly**: 1-2 seconds
- **Total (10 slides)**: 30-45 seconds

---

## Next Steps

1. **Review findings** with project stakeholders
2. **Prioritize implementation phases** based on timeline
3. **Set up development environment** with API keys
4. **Begin Phase 1**: Core structured output implementation
5. **Create test cases** for each generation stage

---

## Document Structure

This research package includes:
- **README.md** (this file) - Summary and quick reference
- **learnings.md** - Detailed findings with evidence and examples
- **decisions.md** - Architectural decisions with rationales
- **issues.md** - Problems, gotchas, and failure modes
- **problems.md** - Unresolved issues and technical debt

---

**End of Summary**
