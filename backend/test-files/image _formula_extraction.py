from PIL import Image
from .cli pix2teximport LatexOCR

img = Image.open('formula_test_image.png')
model = LatexOCR()
print(model(img))