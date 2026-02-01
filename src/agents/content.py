"""Content agent for generating slide content."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser

from src.models.schemas import SlideContent, SlideOutline


class ContentAgentError(RuntimeError):
    """Raised when the content agent fails to generate slide content."""


class ContentAgent:
    """Generates slide content from outlines."""

    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=SlideContent)

    async def generate_slide_content(
        self,
        outline: SlideOutline,
        audience: str = "general",
        style: str = "professional",
    ) -> SlideContent:
        """Generate slide content from a slide outline."""
        prompt = self._build_prompt(outline, audience, style)

        try:
            response = await self.llm.ainvoke(prompt)
            content = self.parser.parse(str(response.content))
        except Exception as exc:  # noqa: BLE001 - wrap any LLM or parsing failure
            raise ContentAgentError("Failed to generate slide content") from exc

        return content

    def _build_prompt(self, outline: SlideOutline, audience: str, style: str) -> str:
        """Build LLM prompt from a slide outline."""
        key_points = ", ".join(outline.key_points) if outline.key_points else "None"
        format_instructions = self.parser.get_format_instructions()

        return (
            "You are a presentation content assistant. Generate concise slide content "
            "based on the outline provided.\n\n"
            f"Slide number: {outline.slide_number}\n"
            f"Slide type: {outline.type}\n"
            f"Title: {outline.title}\n"
            f"Key points: {key_points}\n"
            f"Content notes: {outline.content_notes}\n"
            f"Visual recommendation: {outline.visual_recommendation}\n"
            f"Target audience: {audience}\n"
            f"Presentation style: {style}\n\n"
            "Requirements:\n"
            "- Provide 3-5 bullet points in the content field.\n"
            "- Ensure bullets are concise and aligned to the key points.\n"
            "- Add helpful speaker notes in the notes field.\n"
            "- Adapt tone and language to the target audience and style.\n\n"
            "Return the response using the exact schema below.\n"
            f"{format_instructions}"
        )
