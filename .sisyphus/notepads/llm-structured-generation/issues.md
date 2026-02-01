# Issues, Gotchas, and Potential Problems

**Research Date**: January 31, 2026

---

## Critical Issues

### 1. JSON Mode Degrades Reasoning Performance

**Problem**: Forcing structured output (JSON) degrades LLM reasoning by 10-15%.

**Impact**: 
- Lower quality content when structure is enforced
- More generic, less creative outputs
- Missed nuance in complex topics

**Mitigation**:
- Use two-step approach: free reasoning → separate formatting
- Generate reasoning separately from structured output
- Use CoT without JSON constraints first

**Evidence**: [Beyond JSON: Picking Right Format for LLM Pipelines](https://www.linkedin.com/pulse/beyond-json-picking-right-format-llm-pipelines-michael-hannecke-ftnye)

---

### 2. Token Limit Constraints for Long Presentations

**Problem**: Large presentations (15+ slides) may exceed context window in single call.

**Impact**:
- Incomplete generation
- Truncated slides
- Inconsistent quality

**Mitigation**:
- Generate outline first (fewer tokens)
- Generate slides in batches (3-5 at a time)
- Use smaller models for outline expansion
- Implement continuation logic

---

### 3. Schema Complexity Reduces Generation Success

**Problem**: Overly complex JSON schemas confuse LLMs, leading to:
- Invalid JSON
- Missing required fields
- Incorrect data types
- High retry rates

**Impact**:
- Slower generation (multiple retries)
- Failed generations
- Poor user experience

**Mitigation**:
- Keep schemas minimal (10-15 fields max)
- Use optional fields liberally
- Provide examples in prompts
- Validate incrementally (not all at once)

---

## Common Gotchas

### 4. Nested Bullet Points Are Difficult for LLMs

**Problem**: Multi-level bullet nesting (3+ levels) has high error rates.

**Example**:
```json
{
  "points": [
    {
      "text": "Level 1",
      "children": [
        {
          "text": "Level 2",
          "children": [
            { "text": "Level 3", "children": [...] }  // Error prone
          ]
        }
      ]
    }
  ]
}
```

**Mitigation**:
- Limit to 2 levels maximum
- Use flat arrays with `level` field instead
- Provide explicit nesting examples in prompt

**Better Approach**:
```json
{
  "points": [
    { "text": "Level 1", "level": 0 },
    { "text": "Level 2", "level": 1 },
    { "text": "Level 3", "level": 2 }
  ]
}
```

---

### 5. Image URL Generation Is Unreliable

**Problem**: LLMs hallucinate image URLs or generate broken links.

**Issues**:
- Non-existent URLs
- Expired links
- Copyrighted images
- Wrong aspect ratio

**Mitigation**:
- Use image generation API directly (DALL-E, Midjourney)
- Prompt for image descriptions instead of URLs
- Use stock photo APIs (Pexels, Pixabay) with proper API keys
- Implement fallback logic for broken images

---

### 6. Context Loss Across Slide Generation

**Problem**: When generating slides sequentially, context from earlier slides is lost.

**Impact**:
- Inconsistent terminology
- Contradictory information
- Poor transitions between slides

**Mitigation**:
- Pass previous slides as context to each generation
- Generate slides in small batches (3-5 at a time)
- Include "transition_notes" in schema
- Implement final consistency check pass

---

### 7. Tone and Style Inconsistency

**Problem**: Different slides may have different tones/styles when generated separately.

**Example**: 
- Slide 1: Professional and formal
- Slide 3: Casual and conversational
- Slide 7: overly academic

**Mitigation**:
- Explicitly define tone in system prompt
- Include tone in schema with validation
- Pass tone constraint to each slide generation
- Implement style consistency check

---

## Technical Debt Considerations

### 8. No Built-in Slide Number Tracking

**Problem**: Simple JSON schemas don't automatically track slide order.

**Impact**:
- Manual reordering required
- Difficult to generate Table of Contents
- Hard to create navigation

**Solution**:
```json
{
  "slides": [
    {
      "number": 1,
      "title": "...",
      "content": "..."
    }
  ]
}
```

---

### 9. Limited Layout Flexibility

**Problem**: Type-based schemas (title, bullet, image) are rigid.

**Issues**:
- Hard to combine multiple element types
- Difficult to create custom layouts
- Limited support for complex slides (e.g., chart + bullets)

**Solution**:
- Use flexible "elements" array instead of fixed types
- Or use split layouts with nested sections

```json
{
  "type": "split",
  "layout": "left-right",
  "sections": [
    { "type": "bullet", "points": [...] },
    { "type": "chart", "data": {...} }
  ]
}
```

---

### 10. No Native Template/Theme Support in Basic Schemas

**Problem**: Simple JSON schemas don't capture visual design.

**Impact**:
- Presentations need post-processing for styling
- No way to specify templates in JSON
- Manual theme application required

**Solution**:
- Add metadata section to schema
- Use external template mapping system
- Let python-pptx handle theme application

```json
{
  "metadata": {
    "theme": "modern",
    "color_scheme": "blue",
    "font": "Arial",
    "master_slide": "Title and Content"
  }
}
```

---

## Model-Specific Issues

### 11. OpenAI JSON Mode Doesn't Support Streaming

**Problem**: `response_format: { type: 'json_object' }` disables streaming.

**Impact**:
- Poor user experience (waiting for full generation)
- No progress indicators
- High latency perception

**Mitigation**:
- Use non-streaming for outline generation (fast)
- Use streaming for individual slide content (with manual parsing)
- Or use tool use instead of JSON mode

---

### 12. Anthropic Tool Call Latency

**Problem**: Multiple tool calls for complex content increase latency.

**Workflow**:
```
Request → Tool Call → Tool Result → Request → Tool Call → Tool Result → ...
```

**Impact**: 3-5x slower than single-shot generation

**Mitigation**:
- Batch multiple tool parameters in single call
- Use `client.messages.toolRunner()` for automatic execution
- Consider single-shot generation for simple cases

---

## Scalability Issues

### 13. Cost Accumulation with Multi-Step Workflows

**Problem**: Multi-step workflows multiply API costs.

**Example**:
- Outline: GPT-4o (1000 tokens)
- 10 Slides: GPT-4o (10 × 500 = 5000 tokens)
- Review: GPT-4o (1000 tokens)
- **Total**: 7000 tokens vs ~4000 for single-shot

**Mitigation**:
- Use smaller models for planning (GPT-4o-mini)
- Use larger models only for critical content
- Cache repeated patterns (outlines, templates)

---

### 14. Rate Limiting on Batch Slide Generation

**Problem**: Parallel slide generation hits rate limits.

**Example**: Generating 20 slides in parallel → 20 concurrent API calls

**Impact**:
- Rate limit errors (429)
- Failed generations
- Exponential backoff delays

**Mitigation**:
- Generate in batches of 3-5 slides
- Implement rate limit queue
- Use exponential backoff with jitter

---

## Validation and Testing Issues

### 15. Schema Validation Doesn't Catch Semantic Errors

**Problem**: JSON validation passes but content is wrong.

**Examples**:
- JSON valid, but bullets are nonsense
- Types correct, but content irrelevant
- Structure valid, but slides don't tell a coherent story

**Mitigation**:
- Implement semantic validation (LLM-based quality check)
- Check slide sequence makes sense
- Verify each slide's content matches its title
- Human review stage

---

### 16. Difficult to Test Generated Presentations

**Problem**: Quality of generated presentations is subjective and hard to test automatically.

**Issues**:
- Content quality requires human judgment
- Visual appeal is subjective
- "Good presentation" has no objective metric

**Mitigation**:
- Use automated checks (length, spelling, format)
- Implement LLM-based consistency scoring
- Create evaluation rubrics for human review
- Use A/B testing for prompt variations

---

## Integration Challenges

### 17. python-pptx Schema Mismatch

**Problem**: LLM-generated JSON doesn't map directly to python-pptx API.

**Issues**:
- Different property names
- Nested structures don't match
- python-pptx uses different object model

**Mitigation**:
- Create transformation layer between JSON and python-pptx
- Design JSON schema to match python-pptx structure
- Or use existing libraries (pptx-api) that handle this

---

### 18. Template and Theme Application Complexity

**Problem**: Generated content needs to be merged with PowerPoint templates.

**Issues**:
- python-pptx template loading is manual
- Slide layout selection requires index mapping
- Placeholder replacement is error-prone

**Mitigation**:
- Design JSON schema to match template structure
- Use named placeholders in templates
- Implement robust fallback for missing elements

---

## Edge Cases

### 19. Empty or Null Content Fields

**Problem**: LLMs sometimes generate null or empty fields.

**Example**:
```json
{
  "title": "Introduction",
  "content": [],
  "bullet_points": null
}
```

**Impact**:
- Empty slides in presentation
- python-pptx errors
- Poor user experience

**Mitigation**:
- Add validation: reject generations with empty required fields
- Provide fallback defaults
- Prompt for minimum content requirements

---

### 20. Overly Long Text in Single Field

**Problem**: LLMs generate paragraphs in fields meant for short text.

**Example**:
```json
{
  "title": "A very long paragraph that exceeds what should be a slide title by a significant margin and causes formatting issues..."
}
```

**Impact**:
- Slides overflow
- Poor formatting
- Text truncated

**Mitigation**:
- Add character limits to schema
- Implement truncation with ellipsis
- Use separate "subtitle" field for longer text

---

## Recommendations

### Immediate Actions

1. **Implement two-step generation** (reasoning → structured output)
2. **Add schema validation** before python-pptx processing
3. **Implement retry logic** for failed generations
4. **Use GPT-4o-mini for planning**, GPT-4o for content
5. **Generate slides in batches of 3-5** to avoid rate limits
6. **Add tone/style constraints** to every generation
7. **Implement quality check** pass after content generation

### Medium-Term Improvements

1. Build transformation layer between JSON and python-pptx
2. Implement semantic validation with LLM reviewer
3. Create template mapping system for themes
4. Add progress indicators for user experience
5. Build evaluation rubric for presentation quality

### Long-Term Considerations

1. Explore alternative formats (TOON) for efficiency
2. Implement fine-tuning on presentation-specific data
3. Build human-in-the-loop review workflow
4. Create custom template editor for visual control

---

**End of Issues Document**
