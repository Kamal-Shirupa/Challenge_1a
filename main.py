import fitz  # PyMuPDF
import json
import re

# Keywords to ignore while detecting headings or titles
IGNORE_WORDS = [
    "title", "title of the article", "abstract", "contents", "index",
    "references", "appendix", "acknowledgments", "introduction", "chapter",
    "section", "figure", "table", "page", "footer", "header"
]

def clean_text(text):
    text = text.strip()
    text = re.sub(r'[:\-.\s]+$', '', text)
    return text

def is_centered(block, page_width):
    bbox = block["bbox"]
    return (bbox[0] < page_width / 4) and (bbox[2] > 3 * page_width / 4)

def extract_outline_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    headings = []
    title = "Unknown Title"

    for page_num, page in enumerate(doc, start=1):
        page_width = page.rect.width
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue

            block_text = " ".join(
                " ".join(span["text"].strip() for span in line["spans"]) for line in block["lines"]
            ).strip()

            if not block_text:
                continue

            first_span = block["lines"][0]["spans"][0]
            font_size = first_span["size"]
            is_bold = "bold" in first_span["font"].lower()
            is_italic = "italic" in first_span["font"].lower()

            # Title detection (first page only)
            if page_num == 1 and title == "Unknown Title":
                if (font_size > 20 and is_centered(block, page_width) and
                    len(block_text.split()) <= 10 and
                    block_text.lower() not in IGNORE_WORDS):
                    title = clean_text(block_text)
                    continue

            # Heading filtering
            if (font_size < 8 or
                len(block_text.split()) > 10 or
                block_text.lower() in IGNORE_WORDS or
                re.match(r'^[\d\s\.]+$', block_text) or
                block_text.endswith((".", ":", ";"))):
                continue

            headings.append({
                "text": clean_text(block_text),
                "font_size": font_size,
                "bold": is_bold,
                "italic": is_italic,
                "page": page_num
            })

    # Assign heading levels based on font size
    unique_sizes = sorted({h["font_size"] for h in headings}, reverse=True)
    size_to_level = {}
    if len(unique_sizes) >= 1: size_to_level[unique_sizes[0]] = "H1"
    if len(unique_sizes) >= 2: size_to_level[unique_sizes[1]] = "H2"
    if len(unique_sizes) >= 3: size_to_level[unique_sizes[2]] = "H3"

    outline = []
    for h in headings:
        level = size_to_level.get(h["font_size"])
        if not level:
            continue
        outline.append({
            "level": level,
            "text": h["text"],
            "page": h["page"]
        })

    return {
        "title": title if title else "Unknown Title",
        "outline": outline
    }

# Sample run
if __name__ == "__main__":
    pdf_file = "/content/MINI PROJECT KAMAL.pdf"  # Change as needed
    result = extract_outline_from_pdf(pdf_file)
    print(json.dumps(result, indent=4))
