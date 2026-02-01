"""Example usage of AI PowerPoint Generator with OpenRouter.

This example demonstrates how to use the PowerPoint Generator with OpenRouter
as the LLM provider. OpenRouter supports multiple models including Claude, GPT,
and others through a unified API.
"""

import asyncio
import os

from src.config.llm_config import create_llm
from src.agents.planner import PlannerAgent
from src.agents.content import ContentAgent
from src.agents.design import DesignAgent
from src.models.schemas import PresentationRequest


async def generate_presentation():
    """Generate a presentation using OpenRouter.

    This example shows how to:
    1. Create an LLM instance using OpenRouter
    2. Initialize agents with the LLM
    3. Generate a presentation from a request
    """
    # Create LLM using OpenRouter
    # Uses OPENROUTER_API_KEY from environment variables
    llm = create_llm(
        model="moonshotai/kimi-k2.5",  # or "openai/gpt-4-turbo", etc.
        temperature=0.7,
    )

    # Create presentation request
    request = PresentationRequest(
        topic="The Future of Artificial Intelligence",
        audience="business executives",
        goal="Inform executives about AI trends and opportunities",
        num_slides=8,
        style="professional",
        key_points=[
            "Current AI capabilities",
            "Industry applications",
            "Investment opportunities",
            "Implementation strategies",
        ],
    )

    # Initialize agents
    planner = PlannerAgent(llm=llm)
    content_agent = ContentAgent(llm=llm)
    # design_agent = DesignAgent(...)  # Requires PPTXTool

    print("🎯 Step 1: Creating presentation outline...")
    outline = await planner.create_outline(request)
    print(f"✅ Outline created: {outline.title}")
    print(f"   Objective: {outline.objective}")
    print(f"   Number of slides: {len(outline.slides)}")

    print("\n📝 Step 2: Generating slide content...")
    slide_contents = []
    for slide_outline in outline.slides:
        content = await content_agent.generate_slide_content(
            slide_outline,
            audience=request.audience,
            style=request.style,
        )
        slide_contents.append(content)
        print(f"   ✅ Slide {slide_outline.slide_number}: {content.title}")

    print("\n🎨 Step 3: Creating PowerPoint file...")
    from src.tools.pptx_tool import PPTXTool

    design_agent = DesignAgent()
    output_path = design_agent.create_presentation(
        slides=slide_contents,
        output_path="./output/presentation.pptx",
    )
    print(f"   ✅ PowerPoint saved to: {output_path}")

    print("\n✨ Presentation generation complete!")
    print(f"   Title: {outline.title}")
    print(f"   Slides: {len(slide_contents)}")

    return outline, slide_contents


async def compare_models():
    """Compare different models available through OpenRouter.

    OpenRouter provides access to multiple providers:
    - Anthropic: claude-3.5-sonnet, claude-3-opus
    - OpenAI: gpt-4-turbo, gpt-4o
    - Google: gemini-pro
    - Meta: llama-3.1-405b
    - And many more...
    """
    models = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4-turbo",
        "google/gemini-pro",
    ]

    request = PresentationRequest(
        topic="Climate Change Solutions",
        audience="general public",
        goal="Explain practical climate solutions",
        num_slides=5,
        style="casual",
    )

    for model in models:
        print(f"\n🤖 Testing model: {model}")
        llm = create_llm(model=model, temperature=0.7)
        planner = PlannerAgent(llm=llm)

        try:
            outline = await planner.create_outline(request)
            print(f"   ✅ Success! Title: {outline.title}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    # Ensure OPENROUTER_API_KEY is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  Warning: OPENROUTER_API_KEY not set!")
        print("   Set it with: export OPENROUTER_API_KEY=your_key_here")
        print("   Get your key at: https://openrouter.ai/")
        exit(1)

    # Run the example
    asyncio.run(generate_presentation())

    # Uncomment to compare different models:
    # asyncio.run(compare_models())
