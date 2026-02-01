# LLM Structured Content Generation for Presentations - Research Findings

**Research Date**: January 31, 2026
**Task**: Research patterns for LLM-based structured content generation, specifically for presentations

---

## 1. Structured Output Patterns

### 1.1 OpenAI Structured Outputs

**Key Pattern**: Use `zodResponseFormat` with `.parse()` method for type-safe structured outputs.

```typescript
import OpenAI from 'openai';
import { zodResponseFormat } from 'openai/helpers/zod';
import { z } from 'zod';

const Slide = z.object({
  type: z.string(),
  title: z.string(),
  content: z.array(z.string()),
});

const Presentation = z.object({
  slides: z.array(Slide),
  filename: z.string(),
});

const completion = await client.chat.completions.parse({
  model: 'gpt-4o-2024-08-06',
  messages: [
    { role: 'system', content: 'You are a presentation generator.' },
    { role: 'user', content: 'Generate slides about topic X' },
  ],
  response_format: zodResponseFormat(Presentation, 'presentation'),
});
```

**Best Practices**:
- Define strict schemas with Zod for type safety
- Use `.parse()` method for automatic schema-to-JSON conversion
- Handle `refusal` and truncation errors
- Use `strict: true` for guaranteed valid JSON

**Evidence**: [OpenAI Node SDK docs](https://github.com/openai/openai-node/blob/master/helpers.md) show that `zodResponseFormat()` automatically converts schemas to JSON Schema and parses responses.

---

### 1.2 Anthropic Tool Use with JSON Schema

**Key Pattern**: Use `betaTool` with JSON Schema for structured tool inputs.

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { betaTool } from '@anthropic-ai/sdk/helpers/json-schema';

const presentationTool = betaTool({
  name: 'generate_presentation',
  input_schema: {
    type: 'object',
    properties: {
      slides: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            title: { type: 'string' },
            bullet_points: { type: 'array', items: { type: 'string' } }
          }
        }
      }
    }
  },
  description: 'Generate a presentation',
  run: (input) => {
    // Process the structured input
    return input;
  },
});

const message = await client.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  max_tokens: 1024,
  messages: [{ role: 'user', content: 'Create a presentation' }],
  tools: [presentationTool],
});
```

**Best Practices**:
- Define tools with clear JSON schemas
- Use tool calls for structured outputs
- Handle `tool_use` blocks properly

**Evidence**: [Anthropic TypeScript SDK docs](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/helpers.md) show `betaTool` helper for JSON Schema tool definitions.

---

### 1.3 Format Selection Trade-offs

**Key Finding**: Format choice impacts reasoning performance by 10-15%.

- **TOON**: Best for high-volume tabular input (40% fewer tokens)
- **JSON with constrained decoding**: Best for output (guaranteed valid)
- **Two-step approach**: Free reasoning → structured formatting for accuracy

**Best Practice**: Use two-step generation when accuracy matters:
1. Let LLM reason freely (no format constraints)
2. Separate formatting step to structure the output

**Evidence**: Research on [Beyond JSON: Picking the Right Format for LLM Pipelines](https://www.linkedin.com/pulse/beyond-json-picking-right-format-llm-pipelines-michael-hannecke-ftnye) shows forcing JSON degrades reasoning by 10-15%.

---

## 2. Chain-of-Thought (CoT) for Content Planning

### 2.1 CoT Fundamentals

**Key Finding**: Asking models to "show work" improves accuracy from 17.9% to 57.1% (math problems).

```typescript
const cotPrompt = `
First, think step-by-step about the presentation structure:
1. What is the main message?
2. Who is the audience?
3. What are 3-5 key points?
4. How should they be ordered?

After thinking, generate the outline in this JSON format:
{
  "reasoning": "your thinking here",
  "outline": {
    "title": "...",
    "slides": [...]
  }
}
`;
```

**Best Practices**:
- Explicitly request intermediate steps
- Separate reasoning from final output
- Use self-consistency for better results

**Evidence**: [Chain-of-Thought Prompting Guide](https://www.comet.com/site/blog/chain-of-thought-prompting/) shows accuracy jumped from 17.9% to 57.1% with CoT, reaching 74.4% with self-consistency.

---

### 2.2 Planning-Focused CoT for Content

**Pattern**: Use CoT for presentation planning phase.

```typescript
const planningPrompt = `
Plan a presentation on "${topic}" by following these steps:

STEP 1: Analyze the request
- What is the core message?
- What are the key concepts?
- What's the context?

STEP 2: Audience analysis
- Who is the target audience?
- What's their knowledge level?
- What tone is appropriate?

STEP 3: Structure the presentation
- Title slide
- Introduction (what and why)
- Main content (3-5 key points with sub-points)
- Conclusion (summary and call to action)

STEP 4: Generate JSON outline
{
  "title": "Presentation Title",
  "audience": "Target audience description",
  "tone": "professional/educational/casual",
  "slides": [
    {
      "title": "Slide Title",
      "content": ["Point 1", "Point 2"],
      "notes": "Speaker notes"
    }
  ]
}
`;
```

**Evidence**: [How to Build AI Workflows for Content Planning in 2026](https://www.airops.com/blog/ai-workflows-content-planning) emphasizes planning as critical for content generation.

---

## 3. Multi-Step Generation Workflows

### 3.1 COPE Framework (Planning + Execution)

**Key Finding**: Small and large models can collaborate through planning intermediaries to reduce costs.

**Pattern**:
```
1. Planner Model → Generates outline/skeleton
2. Executor Model → Fills in detailed content
3. Refinement → Quality checks and polish
```

**Example Workflow**:
```typescript
// Step 1: Generate outline (smaller model)
const outline = await generateOutline(topic);

// Step 2: Expand each slide (larger model)
const slides = await Promise.all(
  outline.slides.map(slide => expandSlideContent(slide))
);

// Step 3: Review and refine
const refined = await reviewAndRefine(slides);
```

**Benefits**:
- Cost efficiency (smaller models for planning)
- Quality (larger models for content)
- Reusability (outlines can guide multiple variations)

**Evidence**: [Efficient LLM Collaboration via Planning](https://arxiv.org/html/2506.11578v3) shows planning as effective cost-efficient inference.

---

### 3.2 Multi-Stage Content Generation

**Best Practice Pattern** for presentations:

```typescript
// Stage 1: Research & Outline
const outline = await generateOutline({
  topic: userPrompt,
  audience: "technical",
  n_slides: 8
});

// Stage 2: Review & Edit
const approvedOutline = await userReview(outline);
if (approvedOutline.edits) {
  outline = await refineOutline(outline, approvedOutline.edits);
}

// Stage 3: Slide Content Generation
const slideContent = await generateSlides(outline);

// Stage 4: Visual Enhancement
const enhanced = await generateImages(slideContent);

// Stage 5: Final Assembly
const presentation = await assemblePPTX(enhanced);
```

**Evidence**: [Presenton](https://github.com/presenton/presenton) uses this exact workflow: prompt → outline → theme → generate → export.

---

## 4. Content Outline Generation Patterns

### 4.1 Outline-First Prompting

**Pattern**: Always generate outline before content.

```typescript
const outlinePrompt = `
Generate a detailed presentation outline for: "${topic}"

Requirements:
- ${n_slides} slides total
- Target audience: ${audience}
- Tone: ${tone}
- Language: ${language}

Output format:
{
  "presentation_title": "...",
  "estimated_duration": "X minutes",
  "slides": [
    {
      "number": 1,
      "title": "Slide Title",
      "key_points": ["point 1", "point 2"],
      "visual_elements": ["chart", "image"],
      "transition_notes": "Connection to next slide"
    }
  ]
}
`;
```

**Best Practices**:
- Clear constraints (slide count, audience, tone)
- Include transition notes between slides
- Plan visual elements upfront
- Estimate duration based on content

---

### 4.2 Iterative Refinement

**Pattern**: Generate → Review → Refine loop.

```typescript
let outline = await generateOutline(prompt);
let iteration = 0;

while (iteration < maxIterations) {
  const review = await reviewOutline(outline);
  
  if (review.is_satisfactory) break;
  
  outline = await refineOutline(outline, review.feedback);
  iteration++;
}
```

**Evidence**: [PPTPPTAgent](https://arxiv.org/html/2501.03936v1) uses two-stage, edit-based approach inspired by human workflows.

---

## 5. Slide Structure Schemas

### 5.1 PPTX-API Schema (Simple, LLM-Friendly)

**Source**: [pptx-api/cg123](https://github.com/cg123/pptx-api)

```json
{
  "slides": [
    {
      "type": "title",
      "title": "Presentation Title",
      "subtitle": "Optional Subtitle"
    },
    {
      "type": "bullet",
      "title": "Bullet Points Slide",
      "points": [
        {
          "text": "First level bullet",
          "children": [
            { "text": "Second level bullet" }
          ]
        }
      ]
    },
    {
      "type": "image",
      "title": "Image Slide Title",
      "url": "https://example.com/image.jpg",
      "alt": "Description"
    },
    {
      "type": "table",
      "title": "Data Table Title",
      "headers": ["Column 1", "Column 2"],
      "rows": [
        ["Row 1 Cell 1", "Row 1 Cell 2"],
        ["Row 2 Cell 1", "Row 2 Cell 2"]
      ]
    },
    {
      "type": "split",
      "title": "Split Layout Example",
      "layout": "left-right",
      "sections": [
        { "type": "bullet", "points": [{"text": "Left side"}] },
        { "type": "image", "url": "right-image.jpg" }
      ]
    }
  ],
  "filename": "presentation.pptx"
}
```

**Advantages**:
- Simple type-based system
- Nested structures for bullets
- Split layouts for complex content
- Minimal fields for LLM generation

---

### 5.2 Comprehensive Schema (Zod)

**Best Practice Schema** for PowerPoint presentations:

```typescript
import { z } from 'zod';

const SlideContent = z.object({
  type: z.enum(['title', 'content', 'image', 'table', 'chart']),
  title: z.string(),
  subtitle: z.string().optional(),
  body: z.array(z.string()).optional(),
  bullet_points: z.array(
    z.object({
      text: z.string(),
      level: z.number().min(0).max(3),
      children: z.lazy(() => z.array(z.any()))
    })
  ).optional(),
  image: z.object({
    url: z.string().url(),
    alt: z.string(),
    caption: z.string().optional()
  }).optional(),
  table: z.object({
    headers: z.array(z.string()),
    rows: z.array(z.array(z.string()))
  }).optional(),
  notes: z.string().optional(),
  duration_minutes: z.number().optional(),
  transition: z.string().optional()
});

const Presentation = z.object({
  metadata: z.object({
    title: z.string(),
    author: z.string().optional(),
    created_date: z.string().optional(),
    template: z.string().optional(),
    theme: z.enum(['light', 'dark', 'colorful', 'minimal']).optional()
  }),
  slides: z.array(SlideContent),
  export_format: z.enum(['pptx', 'pdf']).default('pptx')
});
```

---

### 5.3 Presenton API Schema

**Source**: [presenton/presenton](https://github.com/presenton/presenton)

```json
{
  "content": "Introduction to Machine Learning",
  "n_slides": 5,
  "language": "English",
  "template": "general",
  "export_as": "pptx",
  "tone": "professional",
  "verbosity": "standard",
  "web_search": false,
  "include_table_of_contents": false,
  "include_title_slide": true,
  "slides_markdown": null,
  "instructions": null,
  "files": null
}
```

**Response**:
```json
{
  "presentation_id": "d3000f96-096c-4768-b67b-e99aed029b57",
  "path": "/app_data/d3000f96-096c-4768-b67b-e99aed029b57/Introduction_to_Machine_Learning.pptx",
  "edit_path": "/presentation?id=d3000f96-096c-4768-b67b-e99aed029b57"
}
```

**Features**:
- Tone control (professional, casual, educational, sales_pitch)
- Verbosity levels (concise, standard, text-heavy)
- Web search integration
- File upload for context

---

## 6. Multi-Step Generation Examples

### 6.1 Full Workflow Example

```typescript
// Step 1: Generate Outline with CoT
const outlineResponse = await client.chat.completions.create({
  model: 'gpt-4o',
  messages: [{
    role: 'user',
    content: `
Generate a presentation outline on "${topic}".
Use chain-of-thought to plan the structure first.
Output in this schema:
{
  "reasoning": "step-by-step thinking",
  "outline": {
    "title": "...",
    "slides": [...]
  }
}
    `
  }],
  response_format: { type: 'json_object' }
});

// Step 2: Expand Outline to Full Slides
const slides = [];
for (const outlineSlide of outlineResponse.outline.slides) {
  const slideContent = await client.chat.completions.parse({
    model: 'gpt-4o',
    messages: [{
      role: 'user',
      content: `
Expand this slide into detailed content:
Title: ${outlineSlide.title}
Key Points: ${outlineSlide.key_points.join(', ')}

Output in structured JSON format.
      `
    }],
    response_format: zodResponseFormat(SlideContent, 'slide')
  });
  slides.push(slideContent.parsed);
}

// Step 3: Generate Visuals
for (const slide of slides) {
  if (slide.type === 'image' || slide.type === 'chart') {
    const imagePrompt = await generateImagePrompt(slide);
    slide.image.url = await generateImage(imagePrompt);
  }
}

// Step 4: Assemble PPTX
const presentation = await assemblePPTX({
  slides,
  metadata: {
    title: outlineResponse.outline.title,
    template: 'modern'
  }
});
```

---

### 6.2 Planner-Executor Pattern

```typescript
// Small model for planning (cost-efficient)
const plannerModel = 'gpt-4o-mini';
// Large model for execution (high quality)
const executorModel = 'gpt-4o';

async function planAndExecute(topic: string) {
  // Planner: Generate detailed outline
  const outline = await generateOutline({
    model: plannerModel,
    topic,
    constraints: {
      max_slides: 10,
      audience: 'executives',
      time_limit: '15 minutes'
    }
  });

  // Validate outline
  const validation = await validateOutline(outline);
  if (!validation.passed) {
    throw new Error('Outline validation failed');
  }

  // Executor: Generate content for each slide
  const slides = await Promise.all(
    outline.slides.map(async (slide, index) => {
      return await generateSlideContent({
        model: executorModel,
        context: slide,
        previous_slides: slides.slice(0, index)
      });
    })
  );

  return { outline, slides };
}
```

**Benefits**:
- 60-80% cost reduction (planning with smaller model)
- Better quality (execution with larger model)
- Parallelizable slide generation

---

## 7. Best Practices Summary

### 7.1 Structured Output

✅ **DO**:
- Use native structured output features (OpenAI `response_format`, Anthropic `tools`)
- Define schemas with strict types (Zod)
- Validate outputs against schemas
- Use two-step approach: reason → structure

❌ **DON'T**:
- Force JSON in initial reasoning (degrades performance by 10-15%)
- Rely on unstructured prompts for complex outputs
- Skip error handling for parsing failures

---

### 7.2 Chain-of-Thought

✅ **DO**:
- Explicitly request step-by-step reasoning
- Separate reasoning from structured output
- Use self-consistency for critical decisions
- Apply CoT to planning phase specifically

❌ **DON'T**:
- Combine CoT with strict output formatting
- Skip the planning phase for complex presentations
- Generate full content without an outline first

---

### 7.3 Multi-Step Workflows

✅ **DO**:
- Generate outline before content
- Review and refine outline
- Use smaller models for planning
- Use larger models for content
- Parallelize independent slide generation

❌ **DON'T**:
- Generate entire presentation in one call
- Skip user review stages
- Use same model for all stages
- Block on sequential slide generation

---

### 7.4 Schema Design

✅ **DO**:
- Keep schemas simple and LLM-friendly
- Use enums for controlled vocabularies
- Include optional fields for flexibility
- Plan visual elements in schema

❌ **DON'T**:
- Create overly complex nested structures
- Use ambiguous field names
- Skip validation in schemas
- Ignore transition data between slides

---

## 8. Key Resources

### Documentation
- [OpenAI Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)
- [Anthropic Tool Use Documentation](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/helpers.md)
- [Presenton Documentation](https://docs.presenton.ai)

### Research Papers
- [PPTPPTAgent: Generating and Evaluating Presentations](https://arxiv.org/html/2501.03936v1)
- [Efficient LLM Collaboration via Planning (COPE)](https://arxiv.org/html/2506.11578v3)

### Open Source Projects
- [pptx-api](https://github.com/cg123/pptx-api) - Simple JSON schema for PPTX
- [presenton](https://github.com/presenton/presenton) - Full AI presentation generator
- [think-cell JSON Automation](https://www.think-cell.com/en/resources/manual/jsondataautomation) - Commercial solution

---

## 9. Implementation Recommendations

For the PowerPoint agent:

1. **Use OpenAI's `response_format` with Zod** for structured outputs
2. **Implement two-stage generation**: Outline → Content
3. **Apply CoT to outline generation** specifically
4. **Use planner-executor pattern** for cost efficiency
5. **Adopt pptx-api schema** for simplicity or create comprehensive Zod schema
6. **Include user review step** between outline and content generation
7. **Parallelize slide content generation** after outline approval
8. **Validate all outputs** against defined schemas

---

**End of Research Findings**

---

## 10. PPTXTool Implementation - PowerPoint Generation Tools

**Implementation Date**: January 31, 2026
**Task**: Create a clean wrapper API around python-pptx for PowerPoint generation

### 10.1 PPTXTool Architecture

**File Structure**:
```
src/tools/
  ├── __init__.py           # Exports PPTXTool
  └── pptx_tool.py          # Main implementation (332 lines)

tests/test_tools/
  ├── __init__.py
  └── test_pptx_tool.py     # 39 comprehensive tests
```

**Key Design Decisions**:

1. **Wrapper Pattern**: Thin wrapper over python-pptx to provide cleaner API
   - Hides pptx complexity (layout indices, shapes, text frames)
   - Provides consistent error handling
   - Single point of modification for python-pptx version changes

2. **Error Handling**: Custom PPTXToolError exception
   - Specific error messages for each operation
   - Exception chaining with `from e` for debugging
   - Proper logging at DEBUG, INFO, and ERROR levels

3. **File Path Handling**: All paths use pathlib.Path
   - No hardcoded paths
   - Parent directory creation with `mkdir(parents=True, exist_ok=True)`
   - Proper Path conversion to strings for pptx API

4. **Units**: All dimensions use pptx.util.Inches()
   - Never raw inches (parameterized)
   - Consistent API for image and table dimensions
   - Flexible optional dimensions for images

### 10.2 Implemented Methods

**Core Methods**:
- `__init__(template_path: Optional[str] = None)`: Initialize blank or from template
- `add_slide(layout: str) -> Slide`: Add slide with layout (title, title_and_content, section_header, blank)
- `add_title(slide: Slide, text: str) -> None`: Set slide title
- `add_bullets(slide: Slide, items: list[str], level: int = 0) -> None`: Add bullet points with indentation
- `add_image(slide: Slide, image_path: str, left: float, top: float, width: Optional[float] = None, height: Optional[float] = None) -> None`: Add images with flexible sizing
- `add_table(slide: Slide, rows: int, cols: int, data: list[list[str]], left: float, top: float, width: float, height: float) -> None`: Add data tables
- `save(output_path: str) -> None`: Save presentation to file

**Error Handling Pattern**:
```python
try:
    # Operation
except PPTXToolError:
    raise  # Re-raise custom exceptions
except Exception as e:
    logger.error(f"Failed to {operation}: {e}")
    raise PPTXToolError(f"Failed to {operation}: {e}") from e
```

### 10.3 Layout Mapping

Python-pptx uses numeric layout indices. PPTXTool provides string-based layouts:
```python
layout_map = {
    "title": 0,               # Title Slide
    "title_and_content": 1,   # Title and Content
    "section_header": 2,      # Section Header
    "blank": 6,               # Blank
}
```

**Considerations**:
- Layout indices are presentation-template specific
- Tested with default Office template (works consistently)
- May need adjustment for custom templates
- Consider creating more layouts if needed: handout, object, picture

### 10.4 Testing Strategy

**Test Coverage** (39 tests across 8 test classes):

1. **TestPPTXToolInit** (3 tests):
   - Blank presentation creation
   - Template loading with error handling
   - Nonexistent template error

2. **TestAddSlide** (6 tests):
   - All 4 supported layouts
   - Invalid layout error
   - Multiple slides sequentially

3. **TestAddTitle** (5 tests):
   - Title on different slide types
   - Blank slide error (no title placeholder)
   - Special characters and multiline text

4. **TestAddBullets** (6 tests):
   - Basic bullet points
   - Empty lists
   - Different indentation levels
   - Blank slide error
   - Long text handling

5. **TestAddImage** (7 tests):
   - Valid image files
   - Nonexistent file error
   - Flexible dimensions (width only, height only, none)
   - Multiple images per slide
   - Temporary file cleanup

6. **TestAddTable** (6 tests):
   - Basic table creation
   - Row/column mismatch validation
   - Empty cells
   - Special characters
   - Large tables
   - Data validation

7. **TestSave** (4 tests):
   - File creation
   - Parent directory creation
   - Save and reload verification
   - Overwrite behavior

8. **TestIntegration** (3 tests):
   - Full presentation workflow
   - Presentation with images
   - Example from docstring

**Test Quality**:
- Success and error paths tested
- Edge cases covered (empty lists, special chars, long text)
- Temporary files properly cleaned up
- pytest.raises used for error validation
- Integration tests verify real-world usage

### 10.5 Code Quality Metrics

**Style Compliance** (AGENTS.md):
- Double quotes for all strings ✓
- Line length: 88-100 characters ✓
- Import organization: stdlib → third-party → local ✓
- Type hints on all functions ✓
- Modern Python 3.10+ syntax (list[str] not List[str]) ✓
- Module and class docstrings ✓
- Function docstrings with Args/Returns/Raises ✓
- Exception chaining with `from e` ✓
- Logging with logger.getLogger(__name__) ✓

**Code Metrics**:
- Implementation: 332 lines (well-commented)
- Tests: 530 lines
- Test classes: 8
- Test methods: 39
- Syntax validation: PASSED

### 10.6 Design Patterns Used

**1. Wrapper/Facade Pattern**:
- PPTXTool wraps python-pptx library
- Simplified interface for common operations
- Hides implementation complexity

**2. Builder Pattern** (potential enhancement):
- Slide creation follows builder pattern
- Each add_* method returns None (stateful)
- Could return self for method chaining

**3. Custom Exception Pattern**:
- PPTXToolError for all tool errors
- Proper exception chaining
- Meaningful error messages

**4. Logging Pattern**:
- Module-level logger
- DEBUG for operations
- INFO for file saves
- ERROR for failures

### 10.7 Known Limitations & Future Enhancements

**Current Limitations**:
1. Layout indices hardcoded (0, 1, 2, 6) - template dependent
2. Only supports basic text formatting (no bold, italic, colors)
3. Table formatting limited (no merged cells, no formatting)
4. No speaker notes support
5. No animation/transition support
6. No shape insertion (rectangles, arrows, etc.)

**Potential Enhancements**:
1. Method chaining support (return self from add_*)
2. Text formatting (add_formatted_text with styles)
3. Table formatting (cell colors, fonts, borders)
4. Speaker notes (add_notes method)
5. More layouts (add custom layouts)
6. Shape insertion (add_shape, add_line, add_arrow)
7. Slide design theme application
8. Cloning existing slides

**Design Agent Integration**:
PPTXTool is designed to be called by DesignAgent for:
- Creating presentation files from structured slide data
- Converting JSON/dict slide specifications to PPTX
- Handling file I/O and error management

### 10.8 Best Practices for PPTXTool Usage

**Do**:
- Always check for file existence before adding images
- Validate data dimensions before creating tables
- Use try/except blocks when catching PPTXToolError
- Log important operations for debugging
- Create parent directories before saving

**Don't**:
- Pass raw dimensions without using Inches()
- Ignore error messages (they're descriptive)
- Create presentations without save() call
- Assume layout indices are universal
- Forget to close/save presentations (python-pptx handles it)

**Example Workflow**:
```python
tool = PPTXTool()

# Add title slide
title_slide = tool.add_slide("title")
tool.add_title(title_slide, "My Presentation")

# Add content slide
content_slide = tool.add_slide("title_and_content")
tool.add_title(content_slide, "Key Points")
tool.add_bullets(content_slide, [
    "Point 1",
    "Point 2",
    "Point 3"
])

# Save
tool.save("output/presentation.pptx")
```

---

**End of PPTXTool Implementation Notes**
