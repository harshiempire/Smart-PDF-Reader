import fitz  # PyMuPDF
import json
import numpy as np
from collections import Counter
from collections import Counter
import os


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


def extract_images(page, page_num, output_dir="extracted_images"):
    """Extract images from the given page and save them."""
    os.makedirs(output_dir, exist_ok=True)
    images_info = []
    
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]  # Image XREF
        base_image = page.parent.extract_image(xref)
        img_bytes = base_image["image"]
        img_ext = base_image["ext"]
        
        img_filename = f"{output_dir}/page_{page_num + 1}_img_{img_index + 1}.{img_ext}"
        with open(img_filename, "wb") as img_file:
            img_file.write(img_bytes)
        
        # Store metadata about the image
        images_info.append({
            "image_path": img_filename,
            "bbox": img[1]  # Image bounding box (x0, y0, x1, y1)
        })
    
    return images_info


def extract_text_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    structured_text = {}

    for page_num, page in enumerate(doc):
        text_dict = page.get_text("dict")  # Extract structured text data
        structured_page = []
        
        # Identify the most common font size on the page (assumed body text size)
        all_font_sizes = [span["size"] for block in text_dict["blocks"] for line in block.get("lines", []) for span in line.get("spans", [])]
        common_font_size = Counter(all_font_sizes).most_common(1)[0][0] if all_font_sizes else 10  # Default fallback
        
        for block in text_dict["blocks"]:
            block_text = []
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text.append(span["text"].strip())
            
            text = " ".join(block_text)
            if text:
                text_type = classify_textblock(block, common_font_size)
                structured_page.append({"type": text_type, "text": text})
        
        # Extract images on the page
        images_info = extract_images(page, page_num)
        
        # Store results for the page
        structured_text[f"Page {page_num + 1}"] = {
            "text_blocks": structured_page,
            "images": images_info
        }
    
    return structured_text


# Run extraction
# pdf_path = "somatosensory.pdf"
# pdf_path = "sample01.pdf"
pdf_path = "1706.03762v7.pdf"
structured_output = extract_text_pymupdf(pdf_path)

# Save output
output_file = "structured_output_pymupdf.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(structured_output, f, indent=4)

print(f"Structured text saved to {output_file}")
