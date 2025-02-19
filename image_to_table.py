from img2table.document import Image
from img2table.ocr import TesseractOCR

ocr = TesseractOCR(n_threads=1, lang="eng")

# Instantiation of the image
img = Image(src="table_14.png")

# Table identification

# Table extraction
extracted_tables = img.extract_tables(
ocr=ocr,
                                      implicit_rows=False,
                                      borderless_tables=True,
                                      min_confidence=50
            )
# Result of table identification
print(extracted_tables[0].df.to_numpy())

# #output
# [ExtractedTable(title=None, bbox=(10, 8, 745, 314),shape=(6, 3)),
#  ExtractedTable(title=None, bbox=(936, 9, 1129, 111),shape=(2, 2))]