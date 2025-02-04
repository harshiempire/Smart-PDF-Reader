import pdfplumber
import numpy as np

def detect_columns(page):
    words = page.extract_words()
    x_positions = [word['x0'] for word in words]  # Extract X-coordinates

    # Find column gaps using clustering
    x_sorted = sorted(x_positions)
    column_gaps = np.diff(x_sorted)
    
    # Define column breaks using mean + standard deviation as a threshold
    threshold = np.mean(column_gaps) + np.std(column_gaps)
    column_boundaries = [x for x, gap in zip(x_sorted, column_gaps) if gap > threshold]
    
    return column_boundaries

def extract_multi_column_text(pdf_path):
    structured_text = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            column_boundaries = detect_columns(page)
            words = page.extract_words()
            
            # Organize words into columns
            columns = [[] for _ in range(len(column_boundaries) + 1)]
            
            for word in words:
                x = word["x0"]
                for i, boundary in enumerate(column_boundaries):
                    if x < boundary:
                        columns[i].append(word)
                        break
                else:
                    columns[-1].append(word)

            # Sort words in each column by Y-position (top to bottom)
            for col in columns:
                col.sort(key=lambda w: w["top"])

            # Merge text in correct reading order
            structured_text[f"Page {page_num + 1}"] = [
                " ".join([w["text"] for w in col]) for col in columns
            ]
    
    return structured_text

pdf_path = "somatosensory.pdf"  # Replace with your PDF file
structured_output = extract_multi_column_text(pdf_path)

# Print output in structured format
import json
print(json.dumps(structured_output, indent=4))
