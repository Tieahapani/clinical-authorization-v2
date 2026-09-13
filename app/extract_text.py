"""
Milestone 2: extract PDF text into a reusable data structure, and save
it as JSON so it can be inspected on disk.

extract_pages() returns a list of page dicts - JSON-shaped data that
other code (tests, future criteria matching) can use directly.

No policy logic, no AI, no database - just extraction.
"""

import json
import pymupdf

PDF_PATH = "samples/sample.pdf"
OUTPUT_PATH = "output/sample_pages.json"


def extract_pages(pdf_path):
    doc = pymupdf.open(pdf_path)

    pages = []
    for page_number, page in enumerate(doc.pages(), start=1):
        pages.append({
            "page_number": page_number,
            "text": page.get_text(),
        })

    doc.close()
    return pages


def main():
    pages = extract_pages(PDF_PATH)

    for page in pages:
        print(f"--- Page {page['page_number']} ---")
        print(page["text"])

    with open(OUTPUT_PATH, "w") as f:
        json.dump(pages, f, indent=2)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
