"""Pydantic schemas for presentation data structures.

This module defines all data models used throughout the AI PowerPoint Generator
system, including requests, outlines, content, and validation rules.
"""

from pydantic import BaseModel, Field

# ============================================================================
# Input Models
# ============================================================================


class PresentationRequest(BaseModel):
    """User request for presentation generation.

    This model captures all the information needed to generate a presentation,
    including the topic, audience, style preferences, and any specific content
    requirements.

    Attributes:
        topic: The main subject of the presentation
        audience: Target audience for the presentation (general, executives, students, etc.)
        goal: Primary goal or purpose of the presentation
        num_slides: Optional target number of slides (if not specified, will be auto-determined)
        style: Presentation style (professional, casual, academic, creative)
        key_points: List of important points to include in the presentation
        template: Optional path to or name of a template to use

    Example:
        >>> request = PresentationRequest(
        ...     topic="AI Trends 2024",
        ...     audience="executives",
        ...     goal="Inform about latest AI developments",
        ...     num_slides=10,
        ...     style="professional",
        ...     key_points=["LLM improvements", "AI ethics", "Industry applications"]
        ... )
    """

    topic: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Main subject of the presentation",
    )
    audience: str = Field(
        default="general",
        min_length=1,
        max_length=100,
        description="Target audience (e.g., general, executives, students)",
    )
    goal: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Primary goal or purpose of the presentation",
    )
    num_slides: int | None = Field(
        default=None,
        ge=1,
        le=100,
        description="Target number of slides (auto-determined if not specified)",
    )
    style: str = Field(
        default="professional",
        description="Presentation style (professional, casual, academic, creative)",
    )
    key_points: list[str] = Field(
        default=[],
        description="List of important points to include in the presentation",
    )
    template: str | None = Field(
        default=None,
        description="Optional path to or name of a template to use",
    )

    model_config = {"json_schema_extra": {"example": {}}}


# ============================================================================
# Outline Models
# ============================================================================


class SlideOutline(BaseModel):
    """Outline for a single slide.

    Represents the structure and content direction for an individual slide
    within a presentation, including its type, content points, and visual
    recommendations.

    Attributes:
        slide_number: Position of the slide in the presentation (1-indexed)
        type: Type of slide (title, content, section, chart, image, summary)
        title: Title or heading for the slide
        key_points: Main points to cover on this slide
        content_notes: Detailed notes about the slide content
        visual_recommendation: Suggestions for visual elements or layout

    Example:
        >>> outline = SlideOutline(
        ...     slide_number=1,
        ...     type="title",
        ...     title="AI Trends 2024",
        ...     key_points=[],
        ...     content_notes="Opening slide with presentation title",
        ...     visual_recommendation="Use company logo and professional background"
        ... )
    """

    slide_number: int = Field(
        ...,
        ge=1,
        description="Position of the slide in the presentation (1-indexed)",
    )
    type: str = Field(
        ...,
        description="Type of slide (title, content, section, chart, image, summary)",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Title or heading for the slide",
    )
    key_points: list[str] = Field(
        default=[],
        description="Main points to cover on this slide",
    )
    content_notes: str = Field(
        default="",
        description="Detailed notes about the slide content",
    )
    visual_recommendation: str = Field(
        default="",
        description="Suggestions for visual elements or layout",
    )


class PresentationOutline(BaseModel):
    """Complete outline for a presentation.

    Represents the full structure of a presentation created by the planner agent,
    including the overall theme and all individual slide outlines.

    Attributes:
        title: Overall title of the presentation
        objective: Clear statement of the presentation's objective
        slides: List of individual slide outlines
        design_theme: Name or description of the design theme to use

    Example:
        >>> outline = PresentationOutline(
        ...     title="AI Trends 2024",
        ...     objective="Inform executives about latest AI developments",
        ...     slides=[...],
        ...     design_theme="corporate_blue"
        ... )
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Overall title of the presentation",
    )
    objective: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Clear statement of the presentation's objective",
    )
    slides: list[SlideOutline] = Field(
        ...,
        min_length=1,
        description="List of individual slide outlines",
    )
    design_theme: str = Field(
        default="professional",
        description="Name or description of the design theme to use",
    )


# ============================================================================
# Content Models
# ============================================================================


class SlideContent(BaseModel):
    """Generated content for a single slide.

    Output from the content agent, containing the actual text content
    that will be displayed on a slide, including title, bullet points,
    and speaker notes.

    Attributes:
        title: Title of the slide
        content: List of bullet point strings for the slide
        notes: Speaker notes for the slide (not displayed to audience)

    Example:
        >>> content = SlideContent(
        ...     title="Key Findings",
        ...     content=[
        ...         "LLMs have improved significantly",
        ...         "Cost per token has decreased 90%",
        ...         "New applications emerging daily"
        ...     ],
        ...     notes="Emphasize the cost reduction and practical applications"
        ... )
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Title of the slide",
    )
    content: list[str] = Field(
        default=[],
        description="List of bullet point strings for the slide",
    )
    notes: str = Field(
        default="",
        description="Speaker notes for the slide (not displayed to audience)",
    )


# ============================================================================
# QA Report Models
# ============================================================================


class QAReport(BaseModel):
    """Quality assurance report for a presentation.

    Output from the QA agent containing validation results and feedback
    about the generated presentation.

    Attributes:
        approved: Whether the presentation passed all QA checks
        issues: List of issues or problems found during QA
        suggestions: List of suggestions for improvement

    Example:
        >>> report = QAReport(
        ...     approved=True,
        ...     issues=[],
        ...     suggestions=[
        ...         "Consider adding more visuals to slide 3",
        ...         "Some bullets in slide 5 could be more concise"
        ...     ]
        ... )
    """

    approved: bool = Field(
        ...,
        description="Whether the presentation passed all QA checks",
    )
    issues: list[str] = Field(
        default=[],
        description="List of issues or problems found during QA",
    )
    suggestions: list[str] = Field(
        default=[],
        description="List of suggestions for improvement",
    )
