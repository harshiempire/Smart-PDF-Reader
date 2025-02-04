import pdfplumber
import numpy as np
import json

def classify_textblock(textblock):
    """Classify text block as Title or Paragraph based on font size and style."""
    if not textblock:
        return "Paragraph"  # Default classification

    font_sizes = [word["size"] for word in textblock if "size" in word]
    if not font_sizes:
        return "Paragraph"

    avg_font_size = np.mean(font_sizes)
    max_font_size = np.max(font_sizes)  # Some titles may have a large single word

    is_bold = any("Bold" in word.get("fontname", "") for word in textblock)
    is_italic = any(not word.get("upright", True) for word in textblock)

    # Define dynamic font size threshold (adjust based on PDF)
    font_threshold = np.percentile(font_sizes, 75)  # Top 25% of sizes are likely titles

    # Classification logic
    if max_font_size >= font_threshold or is_bold or is_italic:
        return "Title"
    
    return "Paragraph"

def extract_text_and_structure(pdf_path):
    structured_text = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["size", "fontname", "upright"])
            if page_num == 0:
                print({f"page-{page_num}":words})

            if not words:
                continue

            structured_page = []
            current_block = []
            prev_bottom = None  # Track Y position for spacing analysis

            for word in words:
                if prev_bottom is not None:
                    space_gap = word["top"] - prev_bottom
                    if space_gap > 1:  # Adjust this threshold as needed
                        if current_block:
                            structured_page.append({
                                "type": classify_textblock(current_block),
                                "text": " ".join([w["text"] for w in current_block])
                            })
                            current_block = []

                current_block.append(word)
                prev_bottom = word["bottom"]

            # Add last text block
            if current_block:
                structured_page.append({
                    "type": classify_textblock(current_block),
                    "text": " ".join([w["text"] for w in current_block])
                })

            structured_text[f"Page {page_num + 1}"] = structured_page

    return structured_text

# Run extraction
# pdf_path = "somatosensory.pdf"
# pdf_path = "sample.pdf"
pdf_path = "1706.03762v7.pdf"
structured_output = extract_text_and_structure(pdf_path)

# Save output
output_file = "structured_output.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(structured_output, f, indent=4)

print(f"Structured text saved to {output_file}")
