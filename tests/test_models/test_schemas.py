"""Unit tests for Pydantic models and schemas.

Tests all data models used throughout the AI PowerPoint Generator system,
including validation, serialization, and deserialization.
"""

import json

import pytest
from pydantic import ValidationError

from src.models import (
    AgentState,
    PresentationOutline,
    PresentationRequest,
    QAReport,
    SlideContent,
    SlideOutline,
)

# ============================================================================
# PresentationRequest Tests
# ============================================================================


class TestPresentationRequest:
    """Tests for PresentationRequest model."""

    def test_create_valid_request(self, valid_presentation_request):
        """Test creating a valid PresentationRequest."""
        assert valid_presentation_request.topic == "AI Trends 2024"
        assert valid_presentation_request.audience == "executives"
        assert valid_presentation_request.goal == "Inform about latest AI developments"
        assert valid_presentation_request.num_slides == 10
        assert valid_presentation_request.style == "professional"
        assert len(valid_presentation_request.key_points) == 3

    def test_create_minimal_request(self):
        """Test creating a PresentationRequest with only required fields."""
        request = PresentationRequest(
            topic="Test Topic",
            goal="Test Goal",
        )
        assert request.topic == "Test Topic"
        assert request.goal == "Test Goal"
        assert request.audience == "general"
        assert request.style == "professional"
        assert request.key_points == []
        assert request.num_slides is None
        assert request.template is None

    def test_topic_required(self):
        """Test that topic is required."""
        with pytest.raises(ValidationError) as exc_info:
            PresentationRequest(goal="Test Goal")
        assert "topic" in str(exc_info.value)

    def test_goal_required(self):
        """Test that goal is required."""
        with pytest.raises(ValidationError) as exc_info:
            PresentationRequest(topic="Test Topic")
        assert "goal" in str(exc_info.value)

    def test_topic_min_length(self):
        """Test that topic must not be empty."""
        with pytest.raises(ValidationError):
            PresentationRequest(topic="", goal="Test Goal")

    def test_goal_min_length(self):
        """Test that goal must not be empty."""
        with pytest.raises(ValidationError):
            PresentationRequest(topic="Test Topic", goal="")

    def test_num_slides_validation(self):
        """Test num_slides must be between 1 and 100."""
        # Valid upper bound
        request = PresentationRequest(topic="Test", goal="Goal", num_slides=100)
        assert request.num_slides == 100

        # Valid lower bound
        request = PresentationRequest(topic="Test", goal="Goal", num_slides=1)
        assert request.num_slides == 1

        # Invalid: too high
        with pytest.raises(ValidationError):
            PresentationRequest(topic="Test", goal="Goal", num_slides=101)

        # Invalid: too low
        with pytest.raises(ValidationError):
            PresentationRequest(topic="Test", goal="Goal", num_slides=0)

    def test_request_serialization(self, valid_presentation_request):
        """Test that PresentationRequest can be serialized to JSON."""
        json_data = valid_presentation_request.model_dump_json()
        assert isinstance(json_data, str)
        parsed = json.loads(json_data)
        assert parsed["topic"] == "AI Trends 2024"
        assert parsed["audience"] == "executives"

    def test_request_deserialization(self):
        """Test that PresentationRequest can be deserialized from JSON."""
        json_str = """{
            "topic": "Test Topic",
            "goal": "Test Goal",
            "audience": "students",
            "num_slides": 15
        }"""
        request = PresentationRequest.model_validate_json(json_str)
        assert request.topic == "Test Topic"
        assert request.goal == "Test Goal"
        assert request.audience == "students"
        assert request.num_slides == 15


# ============================================================================
# SlideOutline Tests
# ============================================================================


class TestSlideOutline:
    """Tests for SlideOutline model."""

    def test_create_valid_outline(self, valid_slide_outline):
        """Test creating a valid SlideOutline."""
        assert valid_slide_outline.slide_number == 1
        assert valid_slide_outline.type == "title"
        assert valid_slide_outline.title == "AI Trends 2024"
        assert valid_slide_outline.key_points == []
        assert valid_slide_outline.content_notes == "Opening slide with presentation title"

    def test_slide_number_required(self):
        """Test that slide_number is required."""
        with pytest.raises(ValidationError) as exc_info:
            SlideOutline(
                type="content",
                title="Test",
            )
        assert "slide_number" in str(exc_info.value)

    def test_slide_number_positive(self):
        """Test that slide_number must be positive."""
        with pytest.raises(ValidationError):
            SlideOutline(
                slide_number=0,
                type="content",
                title="Test",
            )

    def test_type_required(self):
        """Test that type is required."""
        with pytest.raises(ValidationError) as exc_info:
            SlideOutline(
                slide_number=1,
                title="Test",
            )
        assert "type" in str(exc_info.value)

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError) as exc_info:
            SlideOutline(
                slide_number=1,
                type="content",
            )
        assert "title" in str(exc_info.value)

    def test_title_min_length(self):
        """Test that title must not be empty."""
        with pytest.raises(ValidationError):
            SlideOutline(
                slide_number=1,
                type="content",
                title="",
            )

    def test_different_slide_types(self):
        """Test creating outlines with different slide types."""
        types = ["title", "content", "section", "chart", "image", "summary"]
        for slide_type in types:
            outline = SlideOutline(
                slide_number=1,
                type=slide_type,
                title="Test",
            )
            assert outline.type == slide_type

    def test_outline_with_key_points(self):
        """Test SlideOutline with key points."""
        outline = SlideOutline(
            slide_number=2,
            type="content",
            title="Key Points",
            key_points=["Point 1", "Point 2", "Point 3"],
        )
        assert len(outline.key_points) == 3
        assert outline.key_points[0] == "Point 1"

    def test_outline_serialization(self, valid_slide_outline):
        """Test that SlideOutline can be serialized to JSON."""
        json_data = valid_slide_outline.model_dump_json()
        parsed = json.loads(json_data)
        assert parsed["slide_number"] == 1
        assert parsed["type"] == "title"
        assert parsed["title"] == "AI Trends 2024"


# ============================================================================
# PresentationOutline Tests
# ============================================================================


class TestPresentationOutline:
    """Tests for PresentationOutline model."""

    def test_create_valid_outline(self, valid_presentation_outline):
        """Test creating a valid PresentationOutline."""
        assert valid_presentation_outline.title == "AI Trends 2024"
        assert (
            valid_presentation_outline.objective == "Inform executives about latest AI developments"
        )
        assert len(valid_presentation_outline.slides) == 1
        assert valid_presentation_outline.design_theme == "corporate_blue"

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            PresentationOutline(
                objective="Test",
                slides=[],
            )

    def test_objective_required(self):
        """Test that objective is required."""
        with pytest.raises(ValidationError):
            PresentationOutline(
                title="Test",
                slides=[],
            )

    def test_slides_required(self):
        """Test that at least one slide is required."""
        with pytest.raises(ValidationError):
            PresentationOutline(
                title="Test",
                objective="Test",
                slides=[],
            )

    def test_outline_with_multiple_slides(self, valid_slide_outline):
        """Test PresentationOutline with multiple slides."""
        slide2 = SlideOutline(
            slide_number=2,
            type="content",
            title="Slide 2",
        )
        outline = PresentationOutline(
            title="Multi-slide",
            objective="Test multiple slides",
            slides=[valid_slide_outline, slide2],
        )
        assert len(outline.slides) == 2

    def test_outline_default_theme(self, valid_slide_outline):
        """Test that design_theme defaults to 'professional'."""
        outline = PresentationOutline(
            title="Test",
            objective="Test",
            slides=[valid_slide_outline],
        )
        assert outline.design_theme == "professional"

    def test_outline_serialization(self, valid_presentation_outline):
        """Test that PresentationOutline can be serialized to JSON."""
        json_data = valid_presentation_outline.model_dump_json()
        parsed = json.loads(json_data)
        assert parsed["title"] == "AI Trends 2024"
        assert len(parsed["slides"]) == 1
        assert parsed["design_theme"] == "corporate_blue"


# ============================================================================
# SlideContent Tests
# ============================================================================


class TestSlideContent:
    """Tests for SlideContent model."""

    def test_create_valid_content(self, valid_slide_content):
        """Test creating valid SlideContent."""
        assert valid_slide_content.title == "Key Findings"
        assert len(valid_slide_content.content) == 3
        assert "LLMs have improved significantly" in valid_slide_content.content
        assert valid_slide_content.notes != ""

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            SlideContent(content=[])

    def test_title_min_length(self):
        """Test that title must not be empty."""
        with pytest.raises(ValidationError):
            SlideContent(title="", content=[])

    def test_content_optional_defaults_to_empty(self):
        """Test that content defaults to empty list."""
        content = SlideContent(title="Test")
        assert content.content == []

    def test_notes_optional_defaults_to_empty(self):
        """Test that notes defaults to empty string."""
        content = SlideContent(title="Test")
        assert content.notes == ""

    def test_content_with_bullets(self):
        """Test SlideContent with multiple bullet points."""
        content = SlideContent(
            title="Bullets",
            content=["Bullet 1", "Bullet 2", "Bullet 3"],
        )
        assert len(content.content) == 3

    def test_content_serialization(self, valid_slide_content):
        """Test that SlideContent can be serialized to JSON."""
        json_data = valid_slide_content.model_dump_json()
        parsed = json.loads(json_data)
        assert parsed["title"] == "Key Findings"
        assert len(parsed["content"]) == 3
        assert parsed["notes"] != ""


# ============================================================================
# QAReport Tests
# ============================================================================


class TestQAReport:
    """Tests for QAReport model."""

    def test_create_approved_report(self, valid_qa_report):
        """Test creating an approved QA report."""
        assert valid_qa_report.approved is True
        assert valid_qa_report.issues == []
        assert len(valid_qa_report.suggestions) == 2

    def test_create_rejected_report(self):
        """Test creating a rejected QA report."""
        report = QAReport(
            approved=False,
            issues=["Missing content on slide 3", "Title too long on slide 1"],
            suggestions=["Add more visual elements"],
        )
        assert report.approved is False
        assert len(report.issues) == 2

    def test_approved_required(self):
        """Test that approved field is required."""
        with pytest.raises(ValidationError):
            QAReport()

    def test_approved_boolean_type(self):
        """Test that approved must be boolean."""
        # Should work with boolean
        report = QAReport(approved=True)
        assert report.approved is True

        # Pydantic will coerce truthy values to bool
        report = QAReport(approved=1)
        assert report.approved is True

    def test_issues_defaults_to_empty(self):
        """Test that issues defaults to empty list."""
        report = QAReport(approved=True)
        assert report.issues == []

    def test_suggestions_defaults_to_empty(self):
        """Test that suggestions defaults to empty list."""
        report = QAReport(approved=True)
        assert report.suggestions == []

    def test_report_with_many_issues(self):
        """Test QAReport with multiple issues and suggestions."""
        issues = [f"Issue {i}" for i in range(5)]
        suggestions = [f"Suggestion {i}" for i in range(3)]
        report = QAReport(
            approved=False,
            issues=issues,
            suggestions=suggestions,
        )
        assert len(report.issues) == 5
        assert len(report.suggestions) == 3

    def test_report_serialization(self, valid_qa_report):
        """Test that QAReport can be serialized to JSON."""
        json_data = valid_qa_report.model_dump_json()
        parsed = json.loads(json_data)
        assert parsed["approved"] is True
        assert len(parsed["suggestions"]) == 2


# ============================================================================
# AgentState Tests
# ============================================================================


class TestAgentState:
    """Tests for AgentState model."""

    def test_create_valid_state(self, valid_agent_state):
        """Test creating a valid AgentState."""
        assert valid_agent_state.request.topic == "AI Trends 2024"
        assert valid_agent_state.outline is not None
        assert valid_agent_state.current_slide == 0
        assert valid_agent_state.slides == []
        assert valid_agent_state.errors == []
        assert valid_agent_state.completed is False

    def test_request_required(self):
        """Test that request is required."""
        with pytest.raises(ValidationError):
            AgentState()

    def test_outline_optional(self, valid_presentation_request):
        """Test that outline is optional."""
        state = AgentState(request=valid_presentation_request)
        assert state.outline is None

    def test_current_slide_defaults_to_zero(self, valid_presentation_request):
        """Test that current_slide defaults to 0."""
        state = AgentState(request=valid_presentation_request)
        assert state.current_slide == 0

    def test_current_slide_non_negative(self, valid_presentation_request):
        """Test that current_slide must be non-negative."""
        with pytest.raises(ValidationError):
            AgentState(request=valid_presentation_request, current_slide=-1)

    def test_slides_defaults_to_empty(self, valid_presentation_request):
        """Test that slides defaults to empty list."""
        state = AgentState(request=valid_presentation_request)
        assert state.slides == []

    def test_state_with_slides(self, valid_presentation_request, valid_slide_content):
        """Test AgentState with generated slides."""
        state = AgentState(
            request=valid_presentation_request,
            slides=[valid_slide_content],
            current_slide=1,
        )
        assert len(state.slides) == 1
        assert state.current_slide == 1

    def test_errors_defaults_to_empty(self, valid_presentation_request):
        """Test that errors defaults to empty list."""
        state = AgentState(request=valid_presentation_request)
        assert state.errors == []

    def test_state_with_errors(self, valid_presentation_request):
        """Test AgentState with error messages."""
        errors = ["Error 1", "Error 2"]
        state = AgentState(
            request=valid_presentation_request,
            errors=errors,
        )
        assert len(state.errors) == 2

    def test_completed_defaults_to_false(self, valid_presentation_request):
        """Test that completed defaults to False."""
        state = AgentState(request=valid_presentation_request)
        assert state.completed is False

    def test_completed_state(self, valid_agent_state):
        """Test marking state as completed."""
        valid_agent_state.completed = True
        assert valid_agent_state.completed is True

    def test_state_serialization(self, valid_agent_state):
        """Test that AgentState can be serialized to JSON."""
        json_data = valid_agent_state.model_dump_json()
        parsed = json.loads(json_data)
        assert parsed["request"]["topic"] == "AI Trends 2024"
        assert parsed["current_slide"] == 0
        assert parsed["completed"] is False

    def test_state_deserialization(self):
        """Test that AgentState can be deserialized from dict."""
        data = {
            "request": {
                "topic": "Test",
                "goal": "Test Goal",
            },
        }
        state = AgentState.model_validate(data)
        assert state.request.topic == "Test"
        assert state.outline is None
        assert state.completed is False


# ============================================================================
# Integration Tests
# ============================================================================


class TestModelIntegration:
    """Integration tests for multiple models working together."""

    def test_full_workflow_models(
        self,
        valid_presentation_request,
        valid_presentation_outline,
        valid_slide_content,
    ):
        """Test models working together in a workflow."""
        # Start with a request
        state = AgentState(request=valid_presentation_request)
        assert state.outline is None

        # Planner creates outline
        state.outline = valid_presentation_outline
        assert state.outline is not None
        assert len(state.outline.slides) > 0

        # Content agent adds slide content
        state.slides.append(valid_slide_content)
        assert len(state.slides) == 1

        # Mark as completed
        state.completed = True
        assert state.completed is True

    def test_models_json_roundtrip(self, valid_agent_state):
        """Test that models can be serialized and deserialized."""
        # Serialize to JSON
        json_str = valid_agent_state.model_dump_json()

        # Deserialize from JSON
        restored = AgentState.model_validate_json(json_str)

        # Check that data is preserved
        assert restored.request.topic == valid_agent_state.request.topic
        assert restored.current_slide == valid_agent_state.current_slide
        assert restored.completed == valid_agent_state.completed
        if valid_agent_state.outline:
            assert restored.outline.title == valid_agent_state.outline.title
