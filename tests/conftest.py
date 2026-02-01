"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_presentation_data() -> dict:
    return {
        "title": "Sample Presentation",
        "description": "A sample presentation for testing",
        "slides": [],
    }


@pytest.fixture
def sample_slide_data() -> dict:
    return {
        "title": "Sample Slide",
        "content": "This is sample content",
        "layout": "title_and_content",
    }


# ============================================================================
# Fixtures for Pydantic Models
# ============================================================================


@pytest.fixture
def valid_presentation_request():
    """Fixture for a valid PresentationRequest."""
    from src.models import PresentationRequest

    return PresentationRequest(
        topic="AI Trends 2024",
        audience="executives",
        goal="Inform about latest AI developments",
        num_slides=10,
        style="professional",
        key_points=["LLM improvements", "AI ethics", "Industry applications"],
    )


@pytest.fixture
def valid_slide_outline():
    """Fixture for a valid SlideOutline."""
    from src.models import SlideOutline

    return SlideOutline(
        slide_number=1,
        type="title",
        title="AI Trends 2024",
        key_points=[],
        content_notes="Opening slide with presentation title",
        visual_recommendation="Use company logo and professional background",
    )


@pytest.fixture
def valid_presentation_outline(valid_slide_outline):
    """Fixture for a valid PresentationOutline."""
    from src.models import PresentationOutline

    return PresentationOutline(
        title="AI Trends 2024",
        objective="Inform executives about latest AI developments",
        slides=[valid_slide_outline],
        design_theme="corporate_blue",
    )


@pytest.fixture
def valid_slide_content():
    """Fixture for a valid SlideContent."""
    from src.models import SlideContent

    return SlideContent(
        title="Key Findings",
        content=[
            "LLMs have improved significantly",
            "Cost per token has decreased 90%",
            "New applications emerging daily",
        ],
        notes="Emphasize the cost reduction and practical applications",
    )


@pytest.fixture
def valid_qa_report():
    """Fixture for a valid QAReport."""
    from src.models import QAReport

    return QAReport(
        approved=True,
        issues=[],
        suggestions=[
            "Consider adding more visuals to slide 3",
            "Some bullets in slide 5 could be more concise",
        ],
    )


@pytest.fixture
def valid_agent_state(valid_presentation_request, valid_presentation_outline):
    """Fixture for a valid AgentState."""
    from src.models import AgentState

    return AgentState(
        request=valid_presentation_request,
        outline=valid_presentation_outline,
        current_slide=0,
        slides=[],
        errors=[],
        completed=False,
    )
