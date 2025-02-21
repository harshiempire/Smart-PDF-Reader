from img2table.document import Image
from img2table.ocr import TesseractOCR

ocr = TesseractOCR(n_threads=1, lang="eng")

# Instantiation of the image
img = Image(src="best_test_table.png")

# Table identification

# Table extraction
extracted_tables = img.extract_tables(
ocr=ocr,
                                      implicit_rows=False,
                                      borderless_tables=False,
                                      min_confidence=50
            )
# Result of table identification
print(extracted_tables[0].df.to_numpy())

# #output
# [ExtractedTable(title=None, bbox=(10, 8, 745, 314),shape=(6, 3)),
#  ExtractedTable(title=None, bbox=(936, 9, 1129, 111),shape=(2, 2))]

# [['Type\nsize\n(pts.)' 'Regular' 'Bold' 'Italic']
#  ['10\n24' 'Table captions," table superscripts' None None]
#  ['10\n24'
#   'Section titles, references, tables,\ntable first letters in table\ncaptions," figure captions,\nfootnotes, text subscripts, and\nsuperscripts'
#   None None]
#  ['10\n24' None 'Abstract' None]
#  ['10\n24'
#   '‘Authors affiliations, main text,\nequations, first letters in section\ntitles*'
#   None 'Subheading']
#  ['10\n24' 'Authors’ names' None None]
#  ['10\n24' 'Paper title' None None]]