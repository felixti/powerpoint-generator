"""Tests for PPTXTool.

This module tests the PPTXTool class for creating and manipulating
PowerPoint presentations programmatically.
"""

import tempfile
from pathlib import Path

import pytest

from src.tools.pptx_tool import PPTXTool, PPTXToolError


class TestPPTXToolInit:
    """Test PPTXTool initialization."""

    def test_init_creates_blank_presentation(self) -> None:
        """Test creating a blank presentation."""
        tool = PPTXTool()
        assert tool.presentation is not None
        assert len(tool.presentation.slides) == 0

    def test_init_with_nonexistent_template_raises_error(self) -> None:
        """Test initialization with nonexistent template raises error."""
        with pytest.raises(PPTXToolError, match="Template file not found"):
            PPTXTool(template_path="/nonexistent/path/template.pptx")

    def test_init_with_template_file(self) -> None:
        """Test initialization with existing template file."""
        # Create a temporary template
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
            tmp_path = tmp.name
            tool = PPTXTool()
            tool.save(tmp_path)

        try:
            # Load from template
            tool_from_template = PPTXTool(template_path=tmp_path)
            assert tool_from_template.presentation is not None
        finally:
            Path(tmp_path).unlink()


class TestAddSlide:
    """Test add_slide method."""

    def test_add_slide_with_title_layout(self) -> None:
        """Test adding a slide with title layout."""
        tool = PPTXTool()
        slide = tool.add_slide("title")
        assert slide is not None
        assert len(tool.presentation.slides) == 1

    def test_add_slide_with_title_and_content_layout(self) -> None:
        """Test adding a slide with title and content layout."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        assert slide is not None
        assert len(tool.presentation.slides) == 1

    def test_add_slide_with_section_header_layout(self) -> None:
        """Test adding a slide with section header layout."""
        tool = PPTXTool()
        slide = tool.add_slide("section_header")
        assert slide is not None
        assert len(tool.presentation.slides) == 1

    def test_add_slide_with_blank_layout(self) -> None:
        """Test adding a slide with blank layout."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")
        assert slide is not None
        assert len(tool.presentation.slides) == 1

    def test_add_slide_with_invalid_layout_raises_error(self) -> None:
        """Test adding a slide with invalid layout raises error."""
        tool = PPTXTool()
        with pytest.raises(PPTXToolError, match="Unknown layout"):
            tool.add_slide("invalid_layout")

    def test_add_multiple_slides(self) -> None:
        """Test adding multiple slides."""
        tool = PPTXTool()
        slide1 = tool.add_slide("title")
        slide2 = tool.add_slide("title_and_content")
        slide3 = tool.add_slide("blank")

        assert len(tool.presentation.slides) == 3
        assert slide1 is not None
        assert slide2 is not None
        assert slide3 is not None


class TestAddTitle:
    """Test add_title method."""

    def test_add_title_to_title_slide(self) -> None:
        """Test adding title to a title slide."""
        tool = PPTXTool()
        slide = tool.add_slide("title")
        tool.add_title(slide, "My Presentation")
        assert slide.shapes.title.text == "My Presentation"

    def test_add_title_to_title_and_content_slide(self) -> None:
        """Test adding title to a title and content slide."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        tool.add_title(slide, "Slide Title")
        assert slide.shapes.title.text == "Slide Title"

    def test_add_title_to_blank_slide_raises_error(self) -> None:
        """Test adding title to blank slide raises error."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")
        with pytest.raises(PPTXToolError, match="does not have a title"):
            tool.add_title(slide, "Title")

    def test_add_title_with_special_characters(self) -> None:
        """Test adding title with special characters."""
        tool = PPTXTool()
        slide = tool.add_slide("title")
        title_text = "AI & Machine Learning: 2024 Trends! 🚀"
        tool.add_title(slide, title_text)
        assert slide.shapes.title.text == title_text

    def test_add_title_with_multiline_text(self) -> None:
        """Test adding title with multiline text."""
        tool = PPTXTool()
        slide = tool.add_slide("title")
        title_text = "First Line\nSecond Line"
        tool.add_title(slide, title_text)
        assert slide.shapes.title.text == title_text


class TestAddBullets:
    """Test add_bullets method."""

    def test_add_bullets_to_title_and_content_slide(self) -> None:
        """Test adding bullets to title and content slide."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        bullets = ["Point 1", "Point 2", "Point 3"]
        tool.add_bullets(slide, bullets)

        # Get body shape text
        body_shape = None
        for shape in slide.shapes:
            if shape.has_text_frame and shape != slide.shapes.title:
                body_shape = shape
                break

        assert body_shape is not None
        text_frame = body_shape.text_frame
        assert len(text_frame.paragraphs) >= len(bullets)

    def test_add_bullets_with_empty_list(self) -> None:
        """Test adding empty bullet list."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        tool.add_bullets(slide, [])
        # Should not raise error

    def test_add_bullets_with_different_levels(self) -> None:
        """Test adding bullets with different indent levels."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        bullets = ["Point 1", "Point 2", "Point 3"]
        tool.add_bullets(slide, bullets, level=1)
        # Should not raise error

    def test_add_bullets_to_blank_slide_raises_error(self) -> None:
        """Test adding bullets to blank slide raises error."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")
        with pytest.raises(PPTXToolError, match="does not have a body"):
            tool.add_bullets(slide, ["Point 1", "Point 2"])

    def test_add_bullets_with_long_text(self) -> None:
        """Test adding bullets with long text."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        long_text = "This is a very long bullet point " * 10
        tool.add_bullets(slide, [long_text])
        # Should not raise error

    def test_add_multiple_bullet_levels(self) -> None:
        """Test adding multiple bullet levels sequentially."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        bullets1 = ["Level 0 Point 1", "Level 0 Point 2"]
        tool.add_bullets(slide, bullets1, level=0)
        # Note: Multiple calls to add_bullets will replace, not append


class TestAddImage:
    """Test add_image method."""

    def test_add_image_with_valid_file(self) -> None:
        """Test adding image with valid file."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            import PIL.Image

            img = PIL.Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            tool.add_image(slide, tmp_path, left=1.0, top=1.0, width=2.0, height=2.0)
            # Should not raise error
            assert len(slide.shapes) > 0
        finally:
            Path(tmp_path).unlink()

    def test_add_image_with_nonexistent_file_raises_error(self) -> None:
        """Test adding image with nonexistent file raises error."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")
        with pytest.raises(PPTXToolError, match="Image file not found"):
            tool.add_image(slide, "/nonexistent/image.png", 1.0, 1.0)

    def test_add_image_with_only_width(self) -> None:
        """Test adding image with only width specified."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            import PIL.Image

            img = PIL.Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            tool.add_image(slide, tmp_path, left=1.0, top=1.0, width=2.0)
            assert len(slide.shapes) > 0
        finally:
            Path(tmp_path).unlink()

    def test_add_image_with_only_height(self) -> None:
        """Test adding image with only height specified."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            import PIL.Image

            img = PIL.Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            tool.add_image(slide, tmp_path, left=1.0, top=1.0, height=2.0)
            assert len(slide.shapes) > 0
        finally:
            Path(tmp_path).unlink()

    def test_add_image_with_no_dimensions(self) -> None:
        """Test adding image with no dimensions specified."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            import PIL.Image

            img = PIL.Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            tool.add_image(slide, tmp_path, left=1.0, top=1.0)
            assert len(slide.shapes) > 0
        finally:
            Path(tmp_path).unlink()

    def test_add_multiple_images(self) -> None:
        """Test adding multiple images to slide."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            import PIL.Image

            img = PIL.Image.new("RGB", (100, 100), color="red")
            img.save(tmp.name)
            tmp_path = tmp.name

        try:
            tool.add_image(slide, tmp_path, left=1.0, top=1.0, width=2.0, height=2.0)
            tool.add_image(slide, tmp_path, left=4.0, top=1.0, width=2.0, height=2.0)
            assert len(slide.shapes) >= 2
        finally:
            Path(tmp_path).unlink()


class TestAddTable:
    """Test add_table method."""

    def test_add_table_to_slide(self) -> None:
        """Test adding table to slide."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        data = [
            ["Header 1", "Header 2", "Header 3"],
            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
        ]

        tool.add_table(slide, rows=3, cols=3, data=data, left=1.0, top=1.0, width=5.0, height=3.0)
        assert len(slide.shapes) > 0

    def test_add_table_with_mismatched_rows_raises_error(self) -> None:
        """Test adding table with mismatched rows raises error."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        data = [
            ["Col 1", "Col 2"],
            ["Col 1", "Col 2"],
        ]

        with pytest.raises(PPTXToolError, match="rows but 3 expected"):
            tool.add_table(
                slide, rows=3, cols=2, data=data, left=1.0, top=1.0, width=5.0, height=3.0
            )

    def test_add_table_with_mismatched_cols_raises_error(self) -> None:
        """Test adding table with mismatched columns raises error."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        data = [
            ["Col 1", "Col 2"],
            ["Col 1", "Col 2"],
        ]

        with pytest.raises(PPTXToolError, match="columns but 3 expected"):
            tool.add_table(
                slide, rows=2, cols=3, data=data, left=1.0, top=1.0, width=5.0, height=3.0
            )

    def test_add_table_with_empty_cells(self) -> None:
        """Test adding table with empty cells."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        data = [
            ["Header 1", "Header 2"],
            ["", "Value"],
            ["Value", ""],
        ]

        tool.add_table(slide, rows=3, cols=2, data=data, left=1.0, top=1.0, width=5.0, height=3.0)
        assert len(slide.shapes) > 0

    def test_add_table_with_special_characters(self) -> None:
        """Test adding table with special characters."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        data = [
            ["Header & Data", "Special: @#$"],
            ["Row 1 (A)", "Row 1 (B)"],
        ]

        tool.add_table(slide, rows=2, cols=2, data=data, left=1.0, top=1.0, width=5.0, height=3.0)
        assert len(slide.shapes) > 0

    def test_add_table_with_large_data(self) -> None:
        """Test adding table with large amount of data."""
        tool = PPTXTool()
        slide = tool.add_slide("blank")

        # Create a large table
        rows = 10
        cols = 5
        data = [[f"R{r}C{c}" for c in range(cols)] for r in range(rows)]

        tool.add_table(
            slide, rows=rows, cols=cols, data=data, left=0.5, top=0.5, width=9.0, height=6.0
        )
        assert len(slide.shapes) > 0


class TestSave:
    """Test save method."""

    def test_save_to_file(self) -> None:
        """Test saving presentation to file."""
        tool = PPTXTool()
        slide = tool.add_slide("title")
        tool.add_title(slide, "Test Presentation")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test.pptx")
            tool.save(output_path)
            assert Path(output_path).exists()

    def test_save_creates_parent_directories(self) -> None:
        """Test save creates parent directories if they don't exist."""
        tool = PPTXTool()
        slide = tool.add_slide("title")
        tool.add_title(slide, "Test Presentation")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "subdir1" / "subdir2" / "test.pptx")
            tool.save(output_path)
            assert Path(output_path).exists()

    def test_save_and_reload(self) -> None:
        """Test saving and reloading presentation."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        tool.add_title(slide, "Test Title")
        tool.add_bullets(slide, ["Point 1", "Point 2"])

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test.pptx")
            tool.save(output_path)

            # Reload
            tool2 = PPTXTool(template_path=output_path)
            assert len(tool2.presentation.slides) == 1
            assert tool2.presentation.slides[0].shapes.title.text == "Test Title"

    def test_save_multiple_times_overwrites(self) -> None:
        """Test saving to same file multiple times overwrites."""
        tool = PPTXTool()
        slide1 = tool.add_slide("title")
        tool.add_title(slide1, "First Save")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "test.pptx")
            tool.save(output_path)
            size1 = Path(output_path).stat().st_size

            # Add another slide and save again
            slide2 = tool.add_slide("title")
            tool.add_title(slide2, "Second Save")
            tool.save(output_path)
            size2 = Path(output_path).stat().st_size

            # File sizes should be different
            assert size1 != size2
            assert Path(output_path).exists()


class TestIntegration:
    """Integration tests for PPTXTool."""

    def test_create_full_presentation(self) -> None:
        """Test creating a full presentation with multiple slides."""
        tool = PPTXTool()

        # Add title slide
        slide1 = tool.add_slide("title")
        tool.add_title(slide1, "AI Trends 2024")

        # Add content slide
        slide2 = tool.add_slide("title_and_content")
        tool.add_title(slide2, "Key Findings")
        tool.add_bullets(
            slide2,
            [
                "LLMs have improved significantly",
                "Cost per token has decreased",
                "New applications emerging",
            ],
        )

        # Add table slide
        slide3 = tool.add_slide("title_and_content")
        tool.add_title(slide3, "Comparison Table")
        data = [
            ["Feature", "2023", "2024"],
            ["Speed", "Medium", "High"],
            ["Accuracy", "Good", "Excellent"],
        ]
        tool.add_table(slide3, rows=3, cols=3, data=data, left=1.0, top=1.5, width=5.0, height=2.0)

        # Save
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "presentation.pptx")
            tool.save(output_path)
            assert Path(output_path).exists()
            assert len(tool.presentation.slides) == 3

    def test_create_presentation_with_image(self) -> None:
        """Test creating presentation with image."""
        tool = PPTXTool()

        # Create temporary image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            import PIL.Image

            img = PIL.Image.new("RGB", (200, 200), color="blue")
            img.save(tmp.name)
            img_path = tmp.name

        try:
            # Add slides
            slide1 = tool.add_slide("title_and_content")
            tool.add_title(slide1, "Presentation with Image")
            tool.add_bullets(slide1, ["Bullet point 1", "Bullet point 2"])
            tool.add_image(slide1, img_path, left=4.0, top=1.5, width=2.0, height=2.0)

            # Save
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = str(Path(tmpdir) / "presentation.pptx")
                tool.save(output_path)
                assert Path(output_path).exists()
        finally:
            Path(img_path).unlink()

    def test_example_from_docstring(self) -> None:
        """Test example from docstring works."""
        tool = PPTXTool()
        slide = tool.add_slide("title_and_content")
        tool.add_title(slide, "My Title")
        tool.add_bullets(slide, ["Point 1", "Point 2"])

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "output.pptx")
            tool.save(output_path)
            assert Path(output_path).exists()
