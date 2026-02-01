"""Quick example - Generate a simple 3-slide presentation."""

import asyncio
import os
from pathlib import Path

from src.config.llm_config import create_llm
from src.agents.planner import PlannerAgent
from src.agents.content import ContentAgent
from src.agents.design import DesignAgent
from src.tools.pptx_tool import PPTXTool
from src.models.schemas import PresentationRequest


async def generate_quick_presentation():
    """Generate a quick 3-slide presentation."""
    # Ensure output directory exists
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    # Create LLM
    print("🤖 Initializing AI...")
    llm = create_llm(model="moonshotai/kimi-k2.5")

    # Create request - simple 3-slide presentation
    request = PresentationRequest(
        topic="Healthy Eating Habits",
        audience="general public",
        goal="Teach basic nutrition principles",
        num_slides=3,
        style="casual",
    )

    # Step 1: Plan
    print("\n🎯 Step 1: Creating outline...")
    planner = PlannerAgent(llm=llm)
    outline = await planner.create_outline(request)
    print(f"✅ Title: {outline.title}")
    print(f"   Slides planned: {len(outline.slides)}")

    # Step 2: Generate content
    print("\n📝 Step 2: Writing content...")
    content_agent = ContentAgent(llm=llm)
    slide_contents = []

    for slide_outline in outline.slides:
        content = await content_agent.generate_slide_content(
            slide_outline,
            audience=request.audience,
            style=request.style,
        )
        slide_contents.append(content)
        print(f"   ✅ Slide {slide_outline.slide_number}: {content.title}")

    # Step 3: Create PowerPoint
    print("\n🎨 Step 3: Creating PowerPoint...")
    design_agent = DesignAgent()
    presentation = design_agent.create_presentation(
        slides=slide_contents,
        output_path=str(output_dir / "healthy_eating.pptx"),
    )
    print(f"   ✅ Saved to: ./output/healthy_eating.pptx")

    print("\n✨ Done! Your presentation is ready.")
    return outline, slide_contents


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY not set!")
        print("   Set it in your .env file or environment")
        exit(1)

    asyncio.run(generate_quick_presentation())
