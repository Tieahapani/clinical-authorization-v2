import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from extract_text import extract_pages

SAMPLE_PDF = Path(__file__).resolve().parent.parent / "samples" / "sample.pdf"


def test_extract_pages_returns_four_pages():
    pages = extract_pages(str(SAMPLE_PDF))
    assert len(pages) == 4


def test_page_numbers_are_sequential():
    pages = extract_pages(str(SAMPLE_PDF))
    assert [p["page_number"] for p in pages] == [1, 2, 3, 4]


def test_expected_text_on_correct_page():
    pages = extract_pages(str(SAMPLE_PDF))
    assert "REFERRAL LETTER" in pages[0]["text"]
    assert "Motor strength" in pages[1]["text"]
    assert "ibuprofen" in pages[2]["text"]
    assert "Physical therapy" in pages[3]["text"]
