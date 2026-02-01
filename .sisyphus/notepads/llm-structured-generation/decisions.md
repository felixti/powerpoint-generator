# Architectural Decisions and Rationales

**Project**: AI PowerPoint Generator
**Date**: January 31, 2026

---

## Decision 1: Use OpenAI's Native Structured Output

**Status**: ✅ **DECIDED**

### Options Considered
1. Manual JSON prompting with regex extraction
2. Pydantic + Instructor library
3. OpenAI native `response_format` with Zod

### Decision
Use OpenAI native `response_format` with Zod schema validation.

### Rationale
- **Guaranteed Valid JSON**: Native response format ensures 100% valid JSON
- **Type Safety**: Zod provides compile-time type checking in TypeScript
- **Error Handling**: Built-in error handling for parsing failures
- **Performance**: SDK handles schema-to-JSON-Schema conversion automatically
- **Maintainability**: Clear, declarative schema definitions

### Trade-offs
- ❌ Streaming disabled when using JSON mode
- ✅ Higher reliability (no parsing errors)
- ✅ Better developer experience

### Evidence
- [OpenAI Node SDK helpers](https://github.com/openai/openai-node/blob/master/helpers.md) show `zodResponseFormat()` provides automatic schema conversion

---

## Decision 2: Two-Step Generation (Outline → Content)

**Status**: ✅ **DECIDED**

### Options Considered
1. Single-shot generation (entire presentation in one call)
2. Two-step (outline first, then content)
3. Multi-stage (research → outline → content → review)

### Decision
Implement two-step generation: Outline → Content → Optional Review.

### Rationale
- **Quality**: Outline allows strategic thinking before content
- **Flexibility**: User can review/edit outline before content generation
- **Cost**: Smaller model can generate outline; larger model for content
- **Parallelism**: Slides can be generated in parallel after outline
- **Control**: User has intervention point

### Trade-offs
- ❌ More API calls (higher latency)
- ✅ Better quality content
- ✅ User agency and control
- ✅ Cost-optimized (smaller model for planning)

### Evidence
- [Beyond JSON: Format Choice Impacts Reasoning](https://www.linkedin.com/pulse/beyond-json-picking-right-format-llm-pipelines-michael-hannecke-ftnye) shows forcing structure degrades reasoning
- [COPE Framework](https://arxiv.org/html/2506.11578v3) shows planning improves cost-efficiency

---

## Decision 3: Chain-of-Thought for Outline Generation Only

**Status**: ✅ **DECIDED**

### Options Considered
1. CoT for all generations (outline + content)
2. CoT for outline only
3. No CoT (direct generation)

### Decision
Apply Chain-of-Thought reasoning to outline generation, not slide content.

### Rationale
- **Reasoning Quality**: CoT improves outline structure significantly (17.9% → 57.1%)
- **Efficiency**: Slide content generation is more straightforward, less need for CoT
- **Token Efficiency**: CoT adds tokens, only use where it helps most
- **Performance**: CoT with JSON constraints can conflict

### Trade-offs
- ❌ Additional tokens for outline generation
- ✅ Better structured presentations
- ✅ Higher quality reasoning
- ✅ No performance degradation on content generation

### Evidence
- [Chain-of-Thought Prompting Guide](https://www.comet.com/site/blog/chain-of-thought-prompting/) shows accuracy improvements with CoT
- [Format Trade-offs](https://www.linkedin.com/pulse/beyond-json-picking-right-format-llm-pipelines-michael-hannecke-ftnye) shows JSON degrades reasoning

---

## Decision 4: Planner-Executor Model Pattern

**Status**: ✅ **DECIDED**

### Options Considered
1. Single model for all stages
2. Planner-Executor (small + large models)
3. Ensemble (multiple models for consensus)

### Decision
Use planner-executor pattern: GPT-4o-mini for planning, GPT-4o for execution.

### Rationale
- **Cost Efficiency**: 60-80% cost reduction (planning with smaller model)
- **Quality**: Larger model for content generation
- **Specialization**: Each model used for appropriate task
- **Parallelism**: Execution stage can be parallelized

### Trade-offs
- ❌ More complex workflow orchestration
- ✅ Significant cost savings
- ✅ Optimal quality/cost balance
- ✅ Scalable design

### Evidence
- [COPE Framework](https://arxiv.org/html/2506.11578v3) demonstrates planner-executor cost efficiency

---

## Decision 5: Schema Design - pptx-api Style (Simple, Type-Based)

**Status**: ✅ **DECIDED**

### Options Considered
1. pptx-api schema (type-based: title, bullet, image, table)
2. Comprehensive Zod schema (all possible fields)
3. Flexible elements array (mix and match)

### Decision
Start with pptx-api style schema, extend with comprehensive fields as needed.

### Rationale
- **LLM-Friendly**: Simple, predictable structure
- **Proven**: Used successfully by cg123/pptx-api
- **Extensible**: Can add fields without breaking changes
- **Clear Intent**: Type field makes intent obvious

### Schema Chosen
```typescript
{
  slides: [{
    type: 'title' | 'bullet' | 'image' | 'table' | 'split',
    title: string,
    content?: string[],
    points?: { text: string, children?: any[] }[],
    image?: { url: string, alt: string },
    table?: { headers: string[], rows: string[][] }
  }],
  filename?: string
}
```

### Trade-offs
- ❌ Limited to predefined types
- ✅ Higher generation success rate
- ✅ Easier to parse and validate
- ✅ Maps well to python-pptx

### Evidence
- [pptx-api README](https://github.com/cg123/pptx-api) shows successful simple schema usage
- [Complex schema issues](#8-schema-complexity-reduces-generation-success) note failure modes

---

## Decision 6: Batch Slide Generation (3-5 Slides per Call)

**Status**: ✅ **DECIDED**

### Options Considered
1. Generate all slides in one call
2. Generate slides one by one
3. Generate in batches of 3-5

### Decision
Generate slides in batches of 3-5 slides per API call.

### Rationale
- **Context Preservation**: Batching maintains context across related slides
- **Rate Limit Management**: Avoid 429 errors from parallel generation
- **Latency**: Faster than one-by-one, more reliable than all-at-once
- **Error Recovery**: Easier to retry failed batches

### Trade-offs
- ❌ Slightly more complex orchestration
- ✅ Balanced performance and reliability
- ✅ Graceful error handling
- ✅ Better user experience (partial progress)

### Evidence
- [Rate limiting issues](#14-rate-limiting-on-batch-slide-generation) show parallel problems
- [Token limits](#2-token-limit-constraints-for-long-presentations) show single-call failures

---

## Decision 7: User Review Stage After Outline

**Status**: ✅ **DECIDED**

### Options Considered
1. Fully automated (no human intervention)
2. Review after outline
3. Review after each slide
4. Review after full presentation

### Decision
Require user approval after outline generation, before content generation.

### Rationale
- **Direction Control**: Users can correct misalignment early
- **Cost Efficiency**: Avoid generating wrong content
- **Satisfaction**: Users feel more in control
- **Efficiency**: Outline review is faster than content review

### Trade-offs
- ❌ Breaks automation flow
- ✅ Better alignment with user intent
- ✅ Cost savings (no wasted generations)
- ✅ Higher satisfaction

### Evidence
- [Presenton workflow](https://github.com/presenton/presenton) includes outline review step
- [PPTPPTAgent](https://arxiv.org/html/2501.03936v1) uses edit-based human workflow

---

## Decision 8: Anthropic Tool Use Alternative (for Users with Anthropic API)

**Status**: ✅ **DECIDED**

### Options Considered
1. OpenAI only
2. Anthropic only
3. Support both OpenAI and Anthropic

### Decision
Support both OpenAI (native JSON) and Anthropic (tool use).

### Rationale
- **User Choice**: Users may have API credits for different providers
- **Redundancy**: Backup if one service is down
- **Comparison**: Can test both for quality
- **Flexibility**: Future-proof for new providers

### Implementation
```typescript
// OpenAI
response_format: zodResponseFormat(Presentation, 'presentation')

// Anthropic
tools: [betaTool({
  name: 'generate_presentation',
  input_schema: presentationSchema,
  run: (input) => input
})]
```

### Trade-offs
- ❌ More complex codebase
- ✅ User flexibility
- ✅ Vendor independence
- ✅ Better resilience

### Evidence
- [Anthropic Tool Use](https://github.com/anthropics/anthropic-sdk-typescript/blob/main/helpers.md) provides JSON Schema tool definitions
- [Multi-provider support](https://github.com/presenton/presenton) shows this pattern works

---

## Decision 9: Image Generation via Separate API Call

**Status**: ✅ **DECIDED**

### Options Considered
1. Generate image URLs in presentation JSON
2. Generate image descriptions, separate API call for images
3. Generate images inline (if model supports)

### Decision
Generate image descriptions in schema, use separate image generation API.

### Rationale
- **Reliability**: No broken/hallucinated URLs
- **Quality**: Dedicated image APIs (DALL-E, Pexels) produce better images
- **Flexibility**: User can choose image provider
- **Copyright**: Stock photo APIs have proper licensing

### Trade-offs
- ❌ Additional API calls (more latency)
- ✅ Higher quality images
- ✅ No broken links
- ✅ Legal compliance

### Evidence
- [Image URL issues](#5-image-url-generation-is-unreliable) show URL generation problems
- [Presenton](https://github.com/presenton/presenton) uses multiple image providers

---

## Decision 10: Tone and Style as Schema Fields

**Status**: ✅ **DECIDED**

### Options Considered
1. Tone in system prompt only
2. Tone in schema (optional field)
3. Tone as separate metadata object

### Decision
Include tone/style in schema metadata with enum values.

### Rationale
- **Consistency**: Tone is part of presentation definition
- **Validation**: Enum ensures valid tone choices
- **Flexibility**: User can change tone without regeneration
- **Documentation**: Schema captures all presentation parameters

### Implementation
```typescript
{
  metadata: {
    tone: 'professional' | 'casual' | 'educational' | 'sales_pitch',
    verbosity: 'concise' | 'standard' | 'text-heavy',
    language: string,
    audience: string
  }
}
```

### Trade-offs
- ❌ More complex schema
- ✅ Better control
- ✅ Consistency enforcement
- ✅ Clearer intent

### Evidence
- [Presenton API](https://github.com/presenton/presenton) includes tone/verbosity in request schema

---

## Decision 11: Zod for Schema Validation

**Status**: ✅ **DECIDED**

### Options Considered
1. JSON Schema directly
2. Pydantic (Python)
3. Zod (TypeScript)
4. Manual validation

### Decision
Use Zod for schema definition and validation in Python (pydantic) and TypeScript.

### Rationale
- **Type Safety**: Compile-time type checking
- **Runtime Validation**: Automatic parsing and error reporting
- **Ecosystem**: Great tooling (zod-to-openai, zod-to-json-schema)
- **Developer Experience**: IDE autocomplete, error messages

### Trade-offs
- ❌ Additional dependency
- ✅ Type safety
- ✅ Better error messages
- ✅ Less boilerplate

### Evidence
- [OpenAI helpers](https://github.com/openai/openai-node/blob/master/helpers.md) use Zod integration
- Project uses TypeScript and Python (pydantic-compatible)

---

## Decision 12: Sequential with Parallelization Hybrid

**Status**: ✅ **DECIDED**

### Options Considered
1. Fully sequential (outline → slide1 → slide2 → ...)
2. Fully parallel (all slides at once)
3. Sequential outline, parallel content

### Decision
Sequential outline generation, parallel content generation with context.

### Rationale
- **Best of Both**: Sequential for coherence, parallel for speed
- **Context**: Outline provides context for all slides
- **Speed**: Parallel content generation reduces wait time
- **Quality**: Batching maintains context between related slides

### Implementation
```typescript
// Sequential
const outline = await generateOutline();

// Parallel (in batches)
const slideBatches = chunk(outline.slides, 4);
const slides = [];
for (const batch of slideBatches) {
  const batchSlides = await Promise.all(
    batch.map(slide => generateSlide(slide, slides))
  );
  slides.push(...batchSlides);
}
```

### Trade-offs
- ❌ More complex orchestration
- ✅ Optimal performance
- ✅ Better quality than fully parallel
- ✅ Faster than fully sequential

---

## Decision 13: Transformation Layer Between JSON and python-pptx

**Status**: ✅ **DECIDED**

### Options Considered
1. Direct mapping (JSON → python-pptx)
2. Transformation layer
3. Use existing library (pptx-api)

### Decision
Build transformation layer with fallback to existing libraries.

### Rationale
- **Flexibility**: Custom schema for LLM, native python-pptx for output
- **Control**: Handle edge cases (empty fields, type mismatches)
- **Extensibility**: Add custom transformations (templates, themes)
- **Testing**: Easier to test transformation logic

### Trade-offs
- ❌ More code to maintain
- ✅ Better error handling
- ✅ Customizable output
- ✅ Easier testing

### Evidence
- [Schema mismatch issues](#17-python-pptx-schema-mismatch) note integration problems
- [pptx-api](https://github.com/cg123/pptx-api) shows transformation layer works

---

## Decision 14: Evaluation with LLM-Based Quality Check

**Status**: ✅ **DECIDED**

### Options Considered
1. No automated evaluation
2. Rule-based checks (length, format, spelling)
3. LLM-based semantic evaluation
4. Human review only

### Decision
Combine rule-based checks with LLM-based semantic evaluation.

### Rationale
- **Coverage**: Rule-based catches structural issues, LLM catches semantic issues
- **Speed**: Rule-based is instant, LLM is comprehensive
- **Feedback**: LLM can provide specific improvement suggestions
- **Confidence**: Multi-layer evaluation provides confidence score

### Implementation
```typescript
// Rule-based
const structuralCheck = checkSchema(presentation);
const lengthCheck = checkLength(presentation);
const formatCheck = checkFormat(presentation);

// LLM-based
const semanticCheck = await evaluateQuality(presentation);

const score = {
  structural: structuralCheck.pass,
  length: lengthCheck.pass,
  format: formatCheck.pass,
  semantic: semanticCheck.score
};
```

### Trade-offs
- ❌ Additional API calls (evaluation)
- ✅ Better quality assurance
- ✅ Actionable feedback
- ✅ Confidence metrics

### Evidence
- [Semantic validation issues](#15-schema-validation-doesnt-catch-semantic-errors) show need for LLM evaluation

---

## Decision 15: Retry with Backoff for Failed Generations

**Status**: ✅ **DECIDED**

### Options Considered
1. Fail fast (no retries)
2. Fixed retries (3 attempts)
3. Exponential backoff with jitter
4. Manual retry only

### Decision
Implement exponential backoff with jitter for failed generations.

### Rationale
- **Reliability**: Temporary failures (rate limits, timeouts) are common
- **Graceful Degradation**: Automatic retry before showing error to user
- **Cost-Effective**: Only retry when cost of retry is justified
- **Standard Pattern**: Industry best practice

### Implementation
```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;
      
      const delay = Math.min(
        1000 * Math.pow(2, attempt) + Math.random() * 100,
        30000
      );
      await sleep(delay);
    }
  }
}
```

### Trade-offs
- ❌ More complex error handling
- ✅ Higher reliability
- ✅ Better user experience
- ✅ Automatic recovery

---

## Summary of Decisions

| Decision | Choice | Status | Priority |
|-----------|---------|--------|----------|
| Structured Output | OpenAI native + Zod | ✅ Decided | High |
| Generation Steps | Two-step (outline → content) | ✅ Decided | High |
| CoT Application | Outline generation only | ✅ Decided | Medium |
| Model Pattern | Planner-executor (mini + 4o) | ✅ Decided | High |
| Schema Style | pptx-api (simple, type-based) | ✅ Decided | High |
| Batch Size | 3-5 slides per call | ✅ Decided | Medium |
| User Review | After outline generation | ✅ Decided | High |
| Multi-Provider | OpenAI + Anthropic | ✅ Decided | Low |
| Image Generation | Separate API call | ✅ Decided | Medium |
| Tone Control | Schema enum field | ✅ Decided | Medium |
| Validation | Zod + pydantic | ✅ Decided | High |
| Generation Mode | Sequential outline, parallel content | ✅ Decided | High |
| Transformation | Custom layer + python-pptx | ✅ Decided | High |
| Evaluation | Rule-based + LLM semantic | ✅ Decided | Medium |
| Error Handling | Exponential backoff with jitter | ✅ Decided | High |

---

**End of Decisions Document**
