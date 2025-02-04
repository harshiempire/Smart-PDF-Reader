from pdfminer.high_level import extract_text
import json

def extract_text_pdfminer(pdf_path):
    text = extract_text(pdf_path)
    pages = text.split("\f")  # Split into pages

    structured_text = {f"Page {i+1}": [{"type": "Paragraph", "text": page.strip()}] for i, page in enumerate(pages) if page.strip()}
    return structured_text

# Run extraction

pdf_path = "somatosensory.pdf"

structured_output_pdfminer = extract_text_pdfminer(pdf_path)

# Save output
output_file_pdfminer = "structured_output_pdfminer.json"
with open(output_file_pdfminer, "w", encoding="utf-8") as f:
    json.dump(structured_output_pdfminer, f, indent=4)

print(f"Structured text saved to {output_file_pdfminer}")
