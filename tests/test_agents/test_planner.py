from unittest.mock import AsyncMock

import pytest

from src.agents.planner import PlannerAgent, PlannerAgentError
from src.models.schemas import PresentationOutline, PresentationRequest


@pytest.fixture
def planner_agent() -> PlannerAgent:
    mock_llm = AsyncMock()
    return PlannerAgent(llm=mock_llm)


@pytest.mark.asyncio
async def test_create_outline_success(planner_agent: PlannerAgent) -> None:
    request = PresentationRequest(
        topic="AI Trends 2024",
        audience="executives",
        goal="Inform about latest AI developments",
        num_slides=3,
        style="professional",
        key_points=["LLM improvements", "AI ethics", "Industry applications"],
    )

    outline = PresentationOutline(
        title="AI Trends 2024",
        objective="Inform executives about the latest AI developments",
        design_theme="professional",
        slides=[
            {
                "slide_number": 1,
                "type": "title",
                "title": "AI Trends 2024",
                "key_points": ["Overview", "Agenda", "Context"],
                "content_notes": "Opening title slide",
                "visual_recommendation": "Use a bold title with AI-themed imagery",
            },
            {
                "slide_number": 2,
                "type": "content",
                "title": "Key Developments",
                "key_points": ["LLM improvements", "AI ethics", "Applications"],
                "content_notes": "Highlight major AI trends",
                "visual_recommendation": "Use icons for each trend",
            },
            {
                "slide_number": 3,
                "type": "summary",
                "title": "Summary",
                "key_points": ["Takeaways", "Risks", "Next steps"],
                "content_notes": "Recap and call to action",
                "visual_recommendation": "Use a concise summary layout",
            },
        ],
    )

    planner_agent.llm.ainvoke.return_value = AsyncMock(
        content=outline.model_dump_json(),
    )

    result = await planner_agent.create_outline(request)

    assert result == outline
    planner_agent.llm.ainvoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_outline_wraps_llm_errors(planner_agent: PlannerAgent) -> None:
    request = PresentationRequest(topic="AI", goal="Teach basics")

    planner_agent.llm.ainvoke.side_effect = RuntimeError("LLM unavailable")

    with pytest.raises(PlannerAgentError):
        await planner_agent.create_outline(request)


@pytest.mark.asyncio
async def test_create_outline_wraps_parser_errors(planner_agent: PlannerAgent) -> None:
    request = PresentationRequest(topic="AI", goal="Teach basics")

    planner_agent.llm.ainvoke.return_value = AsyncMock(content="not valid json")

    with pytest.raises(PlannerAgentError):
        await planner_agent.create_outline(request)
