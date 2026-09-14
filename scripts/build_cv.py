from typing import Final, Literal, TypedDict, cast
from urllib.parse import urlparse

from fpdf import FPDF

from scripts.constants import BUILD, DATA, STATIC
from scripts.data import load_data


PAGE_MARGIN: Final = 15
BODY_FONT_SIZE: Final = 9
OUTPUT_PATH: Final = BUILD / "marco_ramos_cv.pdf"
FONT_DIRECTORY: Final = STATIC / "css" / "fonts"
FONT_REGULAR: Final = FONT_DIRECTORY / "JetBrainsMono-Regular.ttf"
FONT_BOLD: Final = FONT_DIRECTORY / "JetBrainsMono-Bold.ttf"


class Urls(TypedDict):
    linkedin: str
    gitlab: str


class Meta(TypedDict):
    full_name: str
    contact_email: str
    urls: Urls


class TimelineEntry(TypedDict):
    type: Literal["work", "education"]
    include: bool
    title: str
    where: str
    start: str | None
    end: str | None
    description: list[str]


class Skill(TypedDict):
    name: str


class CVData(TypedDict):
    meta: Meta
    timeline: list[TimelineEntry]
    skills: list[Skill]


def _format_dates(entry: TimelineEntry) -> str:
    if entry["start"] is None:
        return entry["end"] or ""

    end = entry["end"] or "Present"
    return f"{entry['start']} - {end}"


def _add_section_heading(pdf: FPDF, title: str) -> None:
    pdf.set_font("JetBrainsMono", style="B", size=13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=8, text=title.upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(30, 30, 30)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(3)


def _add_timeline_entry(pdf: FPDF, entry: TimelineEntry) -> None:
    pdf.set_font("JetBrainsMono", style="B", size=10)
    pdf.multi_cell(w=0, h=5, text=entry["title"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf.set_font("JetBrainsMono", size=BODY_FONT_SIZE)
    pdf.set_text_color(75, 75, 75)
    pdf.multi_cell(
        w=0,
        h=4.5,
        text=f"{entry['where']} | {_format_dates(entry)}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1)

    pdf.set_text_color(30, 30, 30)
    for description in entry["description"]:
        pdf.multi_cell(
            w=0, h=4.5, text=f"- {description}", new_x="LMARGIN", new_y="NEXT"
        )
    pdf.ln(3)


def _add_timeline_section(
    pdf: FPDF, title: str, entry_type: str, entries: list[TimelineEntry]
) -> None:
    _add_section_heading(pdf, title)
    for entry in entries:
        if entry["type"] == entry_type and entry["include"]:
            _add_timeline_entry(pdf, entry)


def _add_skills_section(pdf: FPDF, skills: list[Skill]) -> None:
    _add_section_heading(pdf, "Skills")
    pdf.set_font("JetBrainsMono", size=BODY_FONT_SIZE)
    skill_text = " · ".join(f"{skill['name']}" for skill in skills)
    pdf.multi_cell(w=0, h=4.5, text=skill_text, new_x="LMARGIN", new_y="NEXT")


def _url_label(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.removeprefix("www.")
    return f"{host}{parsed.path}".rstrip("/")


def _add_contact_line(pdf: FPDF, email: str, urls: Urls) -> None:
    linkedin_url = urls["linkedin"]
    gitlab_url = urls["gitlab"]

    linkedin_label = _url_label(linkedin_url)
    gitlab_label = _url_label(gitlab_url)

    parts = (
        email,
        " | ",
        linkedin_label,
        " | ",
        gitlab_label,
    )
    contact_width = sum(pdf.get_string_width(part) for part in parts)

    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    start_x = pdf.l_margin + (usable_width - contact_width) / 2
    pdf.set_x(start_x)

    pdf.write(h=4.5, text=email)
    pdf.write(h=4.5, text=" | ")
    pdf.write(h=4.5, text=linkedin_label, link=linkedin_url)
    pdf.write(h=4.5, text=" | ")
    pdf.write(h=4.5, text=gitlab_label, link=gitlab_url)

    pdf.ln(5)


def build_cv() -> None:
    """Create a PDF CV from the JSON data files."""
    data: CVData = cast(CVData, load_data(DATA))

    pdf = FPDF(format="A4")
    pdf.set_margins(PAGE_MARGIN, PAGE_MARGIN, PAGE_MARGIN)
    pdf.set_auto_page_break(auto=True, margin=PAGE_MARGIN)
    pdf.add_font("JetBrainsMono", fname=FONT_REGULAR)
    pdf.add_font("JetBrainsMono", style="B", fname=FONT_BOLD)
    pdf.add_page()

    pdf.set_font("JetBrainsMono", style="B", size=22)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(
        w=0,
        h=10,
        text=data["meta"]["full_name"],
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1)

    pdf.set_font("JetBrainsMono", size=BODY_FONT_SIZE)
    _add_contact_line(
        pdf,
        email=data["meta"]["contact_email"],
        urls=data["meta"]["urls"],
    )
    _add_timeline_section(pdf, "Experience", "work", data["timeline"])
    _add_timeline_section(pdf, "Education", "education", data["timeline"])
    _add_skills_section(pdf, data["skills"])

    BUILD.mkdir(parents=True, exist_ok=True)
    pdf.output(OUTPUT_PATH)


if __name__ == "__main__":
    build_cv()
