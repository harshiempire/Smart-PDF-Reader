import fitz  # PyMuPDF
import json
import numpy as np
from collections import Counter
from scipy.cluster.vq import kmeans, vq

def classify_textblock(block, common_font_size):
    """Classify text block as Title or Paragraph using PyMuPDF metadata."""
    font_sizes = [span["size"] for line in block.get("lines", []) for span in line.get("spans", [])]
    if not font_sizes:
        return "Paragraph"
    
    avg_font_size = np.mean(font_sizes)
    max_font_size = np.max(font_sizes)
    
    # Check if text is bold or italic
    is_bold = any("Bold" in span.get("font", "") for line in block.get("lines", []) for span in line.get("spans", []))
    is_italic = any("Italic" in span.get("font", "") for line in block.get("lines", []) for span in line.get("spans", []))
    
    # Use common font size to determine if it's larger than standard text
    is_large = max_font_size > common_font_size * 1.2  # Title is significantly larger than body text
    
    # Titles are often short, bold, or large
    if is_large or is_bold or is_italic:
        return "Title"
    return "Paragraph"

def detect_columns(blocks, num_columns=2):
    """Detect columns based on x-coordinates using k-means clustering."""
    x_positions = [block["bbox"][0] for block in blocks]  # Get x0 positions
    if len(set(x_positions)) <= 1:
        return [0]  # Single column case
    
    # Use k-means clustering to find column positions
    centroids, _ = kmeans(np.array(x_positions).reshape(-1, 1).astype(float), num_columns)
    column_labels, _ = vq(np.array(x_positions).reshape(-1, 1), centroids)
    
    # Sort by x position to maintain left-to-right order
    sorted_centroids = sorted(centroids.flatten())
    column_map = {centroid: idx for idx, centroid in enumerate(sorted_centroids)}
    return [column_map[centroids[label][0]] for label in column_labels]

def extract_text_pymupdf(pdf_path, num_columns=2):
    doc = fitz.open(pdf_path)
    structured_text = {}

    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict")  # Extract structured text data
        structured_page = []
        
        # Identify the most common font size on the page (assumed body text size)
        all_font_sizes = [span["size"] for block in text_dict["blocks"] for line in block.get("lines", []) for span in line.get("spans", [])]
        common_font_size = Counter(all_font_sizes).most_common(1)[0][0] if all_font_sizes else 10  # Default fallback

        # print(all_font_sizes)
        
        # Detect columns
        column_assignments = detect_columns(text_dict["blocks"], num_columns)
        
        blocks_with_columns = []
        for block, column in zip(text_dict["blocks"], column_assignments):
            block_text = []
            bbox = block["bbox"]
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text.append(span["text"].strip())
            
            text = " ".join(block_text)
            if text:
                text_type = classify_textblock(block, common_font_size)
                blocks_with_columns.append({
                    "type": text_type,
                    "text": text,
                    "column": column,
                    "y": bbox[1]  # Use y0 for sorting within the column
                })
        print(blocks_with_columns)
        # Sort blocks by column and then by y-position within each column
        sorted_blocks = sorted(blocks_with_columns, key=lambda b: (b["column"], b["y"]))
        structured_page = [{"type": b["type"], "text": b["text"]} for b in sorted_blocks]
        
        structured_text[f"Page {page_num + 1}"] = structured_page

    return structured_text


# Run extraction
pdf_path = "somatosensory.pdf"
# pdf_path = "sample01.pdf"
# pdf_path = "1706.03762v7.pdf"
structured_output = extract_text_pymupdf(pdf_path)

# Save output
output_file = "structured_output_pymupdf.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(structured_output, f, indent=4)

print(f"Structured text saved to {output_file}")
