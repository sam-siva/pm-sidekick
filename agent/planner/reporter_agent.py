from pathlib import Path
from typing import Literal

from docx import Document as DocxDocument
from langgraph.graph import MessagesState
from pptx import Presentation
from pptx.util import Pt
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from utils.logger import _logger
from utils.model import llmmodel

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"

GENERATE_REPORT_PROMPT = (
    "You are a creative report generator. "
    "For the given input, generate a report in the most suitable structure and format "
    "(e.g. PowerPoint, Word, Excel, or PDF). "
    "Use only the provided data and do not invent or add any additional information.\n\n"
    "<project_information>\n{context}\n</project_information>\n\n"
    "Pick the correct tool from the MS Office suite, or PDF, as the output format.\n\n"
    "Break the content into logical sections (e.g. Overview, Key Points, Details, Conclusion). "
    "Each section needs a short, clear heading and a set of concise bullet points — not long paragraphs. "
    "Keep each section focused on one idea, aim for 3-6 bullets per section, "
    "and avoid dense text blocks so the report stays readable at any output size. "
    "Do not create a title/cover section yourself — the report title and subtitle are added separately."
)

response_model = llmmodel


class ReportSection(BaseModel):
    """One logical section of the report (rendered as a PPT slide, or a heading with
    paragraphs in Word/PDF)."""

    heading: str = Field(description="Short, clear heading for this section")
    bullets: list[str] = Field(
        description="Concise bullet points for this section, one idea per bullet"
    )


class ReportOutput(BaseModel):
    """Structured report output, including the chosen output file format."""

    format: Literal["docx", "pdf", "pptx"] = Field(description="The chosen output file format")
    title: str = Field(description="A short title for the report, used as the filename")
    subtitle: str = Field(
        default="", description="Optional one-line subtitle shown under the title"
    )
    sections: list[ReportSection] = Field(
        description="The report content broken into logical sections, in display order"
    )


def _slugify(title: str) -> str:
    return "_".join(title.strip().lower().split()) or "report"


def _save_docx(title: str, subtitle: str, sections: list[ReportSection], path: Path) -> None:
    document = DocxDocument()
    document.add_heading(title, level=1)
    if subtitle:
        document.add_paragraph(subtitle)
    for section in sections:
        document.add_heading(section.heading, level=2)
        for bullet in section.bullets:
            document.add_paragraph(bullet, style="List Bullet")
    document.save(path)


def _save_pdf(title: str, subtitle: str, sections: list[ReportSection], path: Path) -> None:
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"])]
    if subtitle:
        story.append(Paragraph(subtitle, styles["Normal"]))
    story.append(Spacer(1, 12))
    for section in sections:
        story.append(Paragraph(section.heading, styles["Heading2"]))
        for bullet in section.bullets:
            story.append(Paragraph(f"• {bullet}", styles["Normal"]))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 8))
    SimpleDocTemplate(str(path), pagesize=LETTER).build(story)


def _save_pptx(title: str, subtitle: str, sections: list[ReportSection], path: Path) -> None:
    presentation = Presentation()

    title_slide = presentation.slides.add_slide(presentation.slide_layouts[0])
    title_slide.shapes.title.text = title
    if subtitle and len(title_slide.placeholders) > 1:
        title_slide.placeholders[1].text = subtitle

    for section in sections:
        slide = presentation.slides.add_slide(presentation.slide_layouts[1])
        slide.shapes.title.text = section.heading
        for paragraph in slide.shapes.title.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(32)
                run.font.bold = True

        body = slide.placeholders[1].text_frame
        body.clear()
        body.word_wrap = True
        if section.bullets:
            body.paragraphs[0].text = section.bullets[0]
            body.paragraphs[0].font.size = Pt(20)
            for bullet in section.bullets[1:]:
                paragraph = body.add_paragraph()
                paragraph.text = bullet
                paragraph.font.size = Pt(20)

    presentation.save(path)


_SAVERS = {
    "docx": _save_docx,
    "pdf": _save_pdf,
    "pptx": _save_pptx,
}


def generate_report(state: MessagesState) -> dict:
    """Generate a report from the full conversation context and save it to disk
    in the format the model chooses (Word, PDF, or PowerPoint)."""
    messages = state.get("messages", [])
    context = "\n\n".join(
        message.content for message in messages if getattr(message, "content", None)
    )
    prompt = GENERATE_REPORT_PROMPT.format(context=context)
    result = response_model.with_structured_output(ReportOutput).invoke(
        [{"role": "user", "content": prompt}]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{_slugify(result.title)}.{result.format}"
    _SAVERS[result.format](result.title, result.subtitle, result.sections, output_path)
    _logger.info("Report saved to %s", output_path)

    return {"messages": [{"role": "assistant", "content": f"Report saved to {output_path}"}]}
