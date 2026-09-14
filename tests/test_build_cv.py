# tests/test_build_cv.py
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from scripts import build_cv


@pytest.fixture
def work_entry() -> build_cv.TimelineEntry:
    return {
        "type": "work",
        "include": True,
        "title": "Senior Python Developer",
        "where": "Example Company",
        "start": "Jan 2022",
        "end": "Dec 2024",
        "description": [
            "Built internal automation tools",
            "Maintained container infrastructure",
        ],
    }


@pytest.fixture
def education_entry() -> build_cv.TimelineEntry:
    return {
        "type": "education",
        "include": True,
        "title": "BSc Computer Science",
        "where": "Example University",
        "start": "2015",
        "end": "2018",
        "description": ["Graduated with honours"],
    }


@pytest.fixture
def cv_data(
    work_entry: build_cv.TimelineEntry,
    education_entry: build_cv.TimelineEntry,
) -> build_cv.CVData:
    return {
        "meta": {
            "full_name": "Marco Ramos",
            "contact_email": "marco@example.com",
            "urls": {
                "linkedin": "https://www.linkedin.com/in/marco-ramos/",
                "gitlab": "https://gitlab.com/marco-ramos/",
            },
        },
        "timeline": [work_entry, education_entry],
        "skills": [
            {"name": "Python"},
            {"name": "Ansible"},
            {"name": "Podman"},
        ],
    }


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("Jan 2020", "Dec 2021", "Jan 2020 - Dec 2021"),
        ("Jan 2020", None, "Jan 2020 - Present"),
        (None, "2019", "2019"),
        (None, None, ""),
    ],
)
def test_format_dates(
    start: str | None,
    end: str | None,
    expected: str,
) -> None:
    entry: build_cv.TimelineEntry = {
        "type": "work",
        "include": True,
        "title": "Role",
        "where": "Company",
        "start": start,
        "end": end,
        "description": [],
    }

    assert build_cv._format_dates(entry) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.linkedin.com/in/marco-ramos/", "linkedin.com/in/marco-ramos"),
        ("https://gitlab.com/marco-ramos/", "gitlab.com/marco-ramos"),
        ("https://www.example.com/", "example.com"),
        ("https://example.com/path/to/page/", "example.com/path/to/page"),
        ("https://example.com/path?query=value", "example.com/path"),
        ("https://www.example.com", "example.com"),
    ],
)
def test_url_label(url: str, expected: str) -> None:
    assert build_cv._url_label(url) == expected


def test_add_section_heading_formats_and_draws_rule() -> None:
    pdf = MagicMock()
    pdf.l_margin = 15
    pdf.r_margin = 15
    pdf.w = 210
    pdf.get_y.return_value = 42

    build_cv._add_section_heading(pdf, "Experience")

    pdf.set_font.assert_called_once_with("JetBrainsMono", style="B", size=13)
    pdf.set_text_color.assert_called_once_with(30, 30, 30)
    pdf.cell.assert_called_once_with(
        w=0,
        h=8,
        text="EXPERIENCE",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_draw_color.assert_called_once_with(30, 30, 30)
    pdf.line.assert_called_once_with(15, 42, 195, 42)
    pdf.ln.assert_called_once_with(3)


def test_add_timeline_entry_writes_title_metadata_and_bullets(
    work_entry: build_cv.TimelineEntry,
) -> None:
    pdf = MagicMock()

    build_cv._add_timeline_entry(pdf, work_entry)

    assert pdf.set_font.call_args_list == [
        call("JetBrainsMono", style="B", size=10),
        call("JetBrainsMono", size=build_cv.BODY_FONT_SIZE),
    ]
    assert pdf.set_text_color.call_args_list == [
        call(75, 75, 75),
        call(30, 30, 30),
    ]

    assert pdf.multi_cell.call_args_list == [
        call(
            w=0,
            h=5,
            text="Senior Python Developer",
            new_x="LMARGIN",
            new_y="NEXT",
        ),
        call(
            w=0,
            h=4.5,
            text="Example Company | Jan 2022 - Dec 2024",
            new_x="LMARGIN",
            new_y="NEXT",
        ),
        call(
            w=0,
            h=4.5,
            text="- Built internal automation tools",
            new_x="LMARGIN",
            new_y="NEXT",
        ),
        call(
            w=0,
            h=4.5,
            text="- Maintained container infrastructure",
            new_x="LMARGIN",
            new_y="NEXT",
        ),
    ]
    assert pdf.ln.call_args_list == [call(1), call(1), call(3)]


def test_add_timeline_entry_uses_present_for_current_role() -> None:
    entry: build_cv.TimelineEntry = {
        "type": "work",
        "include": True,
        "title": "Current Role",
        "where": "Current Company",
        "start": "Jan 2025",
        "end": None,
        "description": [],
    }
    pdf = MagicMock()

    build_cv._add_timeline_entry(pdf, entry)

    assert (
        call(
            w=0,
            h=4.5,
            text="Current Company | Jan 2025 - Present",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        in pdf.multi_cell.call_args_list
    )


def test_add_timeline_section_adds_only_matching_included_entries(
    monkeypatch: pytest.MonkeyPatch,
    work_entry: build_cv.TimelineEntry,
    education_entry: build_cv.TimelineEntry,
) -> None:
    excluded_work: build_cv.TimelineEntry = {
        **work_entry,
        "title": "Excluded role",
        "include": False,
    }
    another_work: build_cv.TimelineEntry = {
        **work_entry,
        "title": "Another role",
    }
    pdf = MagicMock()

    heading = MagicMock()
    add_entry = MagicMock()
    monkeypatch.setattr(build_cv, "_add_section_heading", heading)
    monkeypatch.setattr(build_cv, "_add_timeline_entry", add_entry)

    build_cv._add_timeline_section(
        pdf,
        "Experience",
        "work",
        [work_entry, education_entry, excluded_work, another_work],
    )

    heading.assert_called_once_with(pdf, "Experience")
    assert add_entry.call_args_list == [
        call(pdf, work_entry),
        call(pdf, another_work),
    ]


def test_add_skills_section_joins_skill_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf = MagicMock()
    heading = MagicMock()
    monkeypatch.setattr(build_cv, "_add_section_heading", heading)

    skills: list[build_cv.Skill] = [
        {"name": "Python"},
        {"name": "Ansible"},
        {"name": "Podman"},
    ]

    build_cv._add_skills_section(pdf, skills)

    heading.assert_called_once_with(pdf, "Skills")
    pdf.set_font.assert_called_once_with(
        "JetBrainsMono",
        size=build_cv.BODY_FONT_SIZE,
    )
    pdf.multi_cell.assert_called_once_with(
        w=0,
        h=4.5,
        text="Python · Ansible · Podman",
        new_x="LMARGIN",
        new_y="NEXT",
    )


def test_add_contact_line_centres_contact_text_and_creates_links() -> None:
    pdf = MagicMock()
    pdf.w = 210
    pdf.l_margin = 15
    pdf.r_margin = 15
    pdf.get_string_width.side_effect = [20, 5, 30, 5, 25]

    urls: build_cv.Urls = {
        "linkedin": "https://www.linkedin.com/in/marco-ramos/",
        "gitlab": "https://gitlab.com/marco-ramos/",
    }

    build_cv._add_contact_line(pdf, "marco@example.com", urls)

    # Usable width = 210 - 15 - 15 = 180.
    # Contact width = 20 + 5 + 30 + 5 + 25 = 85.
    # Start x = 15 + (180 - 85) / 2 = 62.5.
    pdf.set_x.assert_called_once_with(62.5)

    assert pdf.write.call_args_list == [
        call(h=4.5, text="marco@example.com"),
        call(h=4.5, text=" | "),
        call(
            h=4.5,
            text="linkedin.com/in/marco-ramos",
            link="https://www.linkedin.com/in/marco-ramos/",
        ),
        call(h=4.5, text=" | "),
        call(
            h=4.5,
            text="gitlab.com/marco-ramos",
            link="https://gitlab.com/marco-ramos/",
        ),
    ]
    pdf.ln.assert_called_once_with(5)


def test_build_cv_configures_pdf_renders_sections_and_writes_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    cv_data: build_cv.CVData,
) -> None:
    pdf = MagicMock()
    pdf_class = MagicMock(return_value=pdf)

    output_path = tmp_path / "nested" / "marco_ramos_cv.pdf"
    build_dir = output_path.parent

    load_data = MagicMock(return_value=cv_data)
    contact_line = MagicMock()
    timeline_section = MagicMock()
    skills_section = MagicMock()

    monkeypatch.setattr(build_cv, "FPDF", pdf_class)
    monkeypatch.setattr(build_cv, "load_data", load_data)
    monkeypatch.setattr(build_cv, "_add_contact_line", contact_line)
    monkeypatch.setattr(build_cv, "_add_timeline_section", timeline_section)
    monkeypatch.setattr(build_cv, "_add_skills_section", skills_section)
    monkeypatch.setattr(build_cv, "BUILD", build_dir)
    monkeypatch.setattr(build_cv, "OUTPUT_PATH", output_path)

    build_cv.build_cv()

    load_data.assert_called_once_with(build_cv.DATA)
    pdf_class.assert_called_once_with(format="A4")
    pdf.set_margins.assert_called_once_with(
        build_cv.PAGE_MARGIN,
        build_cv.PAGE_MARGIN,
        build_cv.PAGE_MARGIN,
    )
    pdf.set_auto_page_break.assert_called_once_with(
        auto=True,
        margin=build_cv.PAGE_MARGIN,
    )
    pdf.add_font.assert_has_calls(
        [
            call("JetBrainsMono", fname=build_cv.FONT_REGULAR),
            call("JetBrainsMono", style="B", fname=build_cv.FONT_BOLD),
        ]
    )
    pdf.add_page.assert_called_once_with()

    pdf.set_font.assert_any_call("JetBrainsMono", style="B", size=22)
    pdf.cell.assert_called_once_with(
        w=0,
        h=10,
        text="Marco Ramos",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    contact_line.assert_called_once_with(
        pdf,
        email="marco@example.com",
        urls=cv_data["meta"]["urls"],
    )
    assert timeline_section.call_args_list == [
        call(pdf, "Experience", "work", cv_data["timeline"]),
        call(pdf, "Education", "education", cv_data["timeline"]),
    ]
    skills_section.assert_called_once_with(pdf, cv_data["skills"])

    assert build_dir.is_dir()
    pdf.output.assert_called_once_with(output_path)
