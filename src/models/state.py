"""Agent state for LangGraph workflow.

This module defines the AgentState class that represents the complete
state of a presentation generation workflow, passed between agents
in the LangGraph execution.
"""

from pydantic import BaseModel, Field

from src.models.schemas import PresentationOutline, PresentationRequest, SlideContent


class AgentState(BaseModel):
    """Complete state for presentation generation workflow.

    This model represents the entire state of the presentation generation
    process as it flows through the LangGraph workflow. Each agent receives
    this state, processes it, and returns an updated version.

    Attributes:
        request: The original user request for the presentation
        outline: The generated presentation outline (created by planner agent)
        current_slide: Index of the slide currently being processed
        slides: List of generated slide contents
        errors: Any errors that occurred during processing
        completed: Whether the workflow has completed successfully

    Example:
        >>> state = AgentState(
        ...     request=request,
        ...     outline=None,
        ...     current_slide=0,
        ...     slides=[],
        ...     errors=[],
        ...     completed=False
        ... )
    """

    request: PresentationRequest = Field(
        ...,
        description="The original user request for the presentation",
    )
    outline: PresentationOutline | None = Field(
        default=None,
        description="The generated presentation outline (created by planner agent)",
    )
    current_slide: int = Field(
        default=0,
        ge=0,
        description="Index of the slide currently being processed",
    )
    slides: list[SlideContent] = Field(
        default=[],
        description="List of generated slide contents",
    )
    errors: list[str] = Field(
        default=[],
        description="Any errors that occurred during processing",
    )
    completed: bool = Field(
        default=False,
        description="Whether the workflow has completed successfully",
    )
