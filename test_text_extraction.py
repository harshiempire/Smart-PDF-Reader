import os
import numpy as np
from PIL import Image
import pytesseract
import easyocr
from text_extraction import resize_for_ocr, crop_image, extract_table_text, extract_formula_text, extract_text_with_easyocr

def test_text_extraction(image_path, bbox):
    """Test text extraction with given image and bounding box"""
    print(f"\nTesting text extraction with image: {image_path}")
    print(f"Using bounding box coordinates: {bbox}")
    
    try:
        # Load test image
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return None
            
        # Open and convert image to RGB
        image = Image.open(image_path).convert('RGB')
        print(f"Image loaded successfully. Dimensions: {image.size}")
        
        # Test cropping
        print("\nTesting image cropping...")
        cropped_image = crop_image(image, bbox)
        if cropped_image is None:
            print("Error: Failed to crop image")
            return None
        
        # Save cropped image for inspection
        crop_output_path = 'test_crop.png'
        cropped_image.save(crop_output_path)
        print(f"Cropped image saved to {crop_output_path}")
        
        # Test different extraction methods
        print("\nTesting text extraction methods...")
        
        # Test table extraction
        print("\n1. Testing table extraction:")
        table_text = extract_table_text(cropped_image)
        print(f"Table extraction result: {table_text}")
        
        # Test formula extraction
        print("\n2. Testing formula extraction:")
        formula_text = extract_formula_text(cropped_image)
        print(f"Formula extraction result: {formula_text}")
        
        # Test EasyOCR extraction
        print("\n3. Testing EasyOCR extraction:")
        easyocr_text = extract_text_with_easyocr(cropped_image)
        print(f"EasyOCR extraction result: {easyocr_text}")
        
        return {
            'table_text': table_text,
            'formula_text': formula_text,
            'easyocr_text': easyocr_text
        }
        
    except Exception as e:
        print(f"Error in test_text_extraction: {str(e)}")
        return None

def main():
    # Example usage with a test image from assets
    test_image = 'assets/example/textbook.jpg'  # Update with actual test image path
    
    # Test with different types of bounding boxes
    test_cases = [
        {
            'name': 'Full image',
            'bbox': (0.0, 0.0, 1.0, 1.0)  # Normalized coordinates for full image
        },
        {
            'name': 'Center region',
            'bbox': (0.25, 0.25, 0.75, 0.75)  # Center quarter of the image
        },
        {
            'name': 'Small region',
            'bbox': (0.4, 0.4, 0.6, 0.6)  # Small central region
        }
    ]
    
    for case in test_cases:
        print(f"\n=== Testing {case['name']} ===")
        results = test_text_extraction(test_image, case['bbox'])
        if results:
            print(f"\nResults for {case['name']}:")
            for method, text in results.items():
                print(f"{method}: {'Text extracted successfully' if text else 'No text extracted'}")

if __name__ == '__main__':
    main()