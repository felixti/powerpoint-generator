"""Planner agent for building presentation outlines."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser

from src.models.schemas import PresentationOutline, PresentationRequest


class PlannerAgentError(RuntimeError):
    """Raised when the planner agent fails to create an outline."""


class PlannerAgent:
    """Plans presentation structure and content outline."""

    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=PresentationOutline)

    async def create_outline(
        self,
        request: PresentationRequest,
    ) -> PresentationOutline:
        """Generate a structured presentation outline from a request."""
        prompt = self._build_prompt(request)

        try:
            response = await self.llm.ainvoke(prompt)
            outline = self.parser.parse(str(response.content))
        except Exception as exc:  # noqa: BLE001 - wrap any LLM or parsing failure
            raise PlannerAgentError("Failed to generate presentation outline") from exc

        return outline

    def _build_prompt(self, request: PresentationRequest) -> str:
        """Build LLM prompt from presentation request."""
        slide_target = (
            f"Target slide count: {request.num_slides}."
            if request.num_slides
            else "Choose an appropriate slide count."
        )
        key_points = ", ".join(request.key_points) if request.key_points else "None"
        template = request.template or "None"

        format_instructions = self.parser.get_format_instructions()

        return (
            "You are a presentation planning assistant. Create a structured outline "
            "for the requested presentation.\n\n"
            f"Topic: {request.topic}\n"
            f"Audience: {request.audience}\n"
            f"Goal: {request.goal}\n"
            f"Style: {request.style}\n"
            f"Key points: {key_points}\n"
            f"Template: {template}\n"
            f"{slide_target}\n\n"
            "Requirements:\n"
            "- Provide a presentation title and objective.\n"
            "- Create a slide sequence with clear slide types.\n"
            "- Each slide must include 3-5 key points.\n"
            "- Include a visual recommendation for each slide.\n"
            "- Ensure slide numbers are 1-indexed and sequential.\n\n"
            "Return the response using the exact schema below.\n"
            f"{format_instructions}"
        )
