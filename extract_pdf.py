import json
import argparse
from extract_text import extract_multi_column_text

parser = argparse.ArgumentParser(description="Extract structured text from PDFs")
parser.add_argument("pdf_path", help="Path to the PDF file")
args = parser.parse_args()

structured_output = extract_multi_column_text(args.pdf_path)

# Save output
output_file = "output.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(structured_output, f, indent=4)

print(f"Structured text saved to {output_file}")
