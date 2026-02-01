"""LangGraph workflow orchestration for presentation generation."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from src.agents.content import ContentAgent
from src.agents.design import DesignAgent
from src.agents.planner import PlannerAgent
from src.models.state import AgentState


def _append_error(state: AgentState, message: str) -> AgentState:
    state.errors = [*state.errors, message]
    state.completed = False
    return state


def create_workflow(
    planner: PlannerAgent,
    content: ContentAgent,
    design: DesignAgent,
) -> Any:
    """Create a compiled LangGraph workflow for presentation generation.

    Returns:
        A compiled StateGraph that can be invoked with an AgentState.
    """

    async def plan_step(state: AgentState) -> AgentState:
        try:
            outline = await planner.create_outline(state.request)
            state.outline = outline
            return state
        except Exception as exc:  # noqa: BLE001 - capture agent failures
            return _append_error(state, f"Planner failed: {exc}")

    async def content_step(state: AgentState) -> AgentState:
        if state.outline is None:
            return _append_error(state, "Content step missing outline")

        try:
            slides = []
            for slide in state.outline.slides:
                state.current_slide = slide.slide_number
                slides.append(await content.generate_slide_content(slide))
            state.slides = slides
            return state
        except Exception as exc:  # noqa: BLE001 - capture agent failures
            return _append_error(state, f"Content failed: {exc}")

    async def design_step(state: AgentState) -> AgentState:
        if not state.slides:
            return _append_error(state, "Design step missing slide content")

        try:
            design.create_presentation(state.slides)
            state.completed = True
            return state
        except Exception as exc:  # noqa: BLE001 - capture agent failures
            return _append_error(state, f"Design failed: {exc}")

    graph = StateGraph(AgentState)
    graph.add_node("planner", plan_step)
    graph.add_node("content", content_step)
    graph.add_node("design", design_step)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "content")
    graph.add_edge("content", "design")
    graph.add_edge("design", END)

    return graph.compile()
