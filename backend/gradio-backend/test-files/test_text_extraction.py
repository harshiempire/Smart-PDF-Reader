import os
import numpy as np
from PIL import Image
import pytesseract
import easyocr
import torch
from text_extraction import resize_for_ocr, crop_image, extract_table_text, extract_formula_text, extract_text_with_easyocr
from app import recognize_image, id_to_names
from doclayout_yolo import YOLO

# Initialize model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load YOLOv10 model with correct weights
from doclayout_yolo import YOLOv10
model_path = os.path.join(os.path.dirname(__file__), "models", "DocLayout-YOLO-DocStructBench", "doclayout_yolo_docstructbench_imgsz1024.pt")

# Check if model file exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}. Please ensure you have downloaded the model file and placed it in the correct location.")

model = YOLOv10(model_path)  # load the official model

# Pass model to recognize_image function
def test_text_extraction(image_path):
    """Test text extraction with given image using dynamic bounding box detection"""
    print(f"\nTesting text extraction with image: {image_path}")
    
    try:
        # Create directory for saving cropped images
        output_dir = 'cropped_regions'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Load test image
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return None
            
        # Open and convert image to RGB
        image = Image.open(image_path).convert('RGB')
        print(f"Image loaded successfully. Dimensions: {image.size}")
        
        # Get bounding boxes using document layout detection
        img_array = np.array(image)
        detection_results = recognize_image(img_array, model=model, conf_threshold=0.5, iou_threshold=0.5)  # Pass model here
        
        if detection_results is None:
            print("Error: Failed to detect layout regions")
            return None
        
        boxes = detection_results['bboxes']
        classes = detection_results['classes']
        scores = detection_results['scores']
        
        results = []
        
        # Process each detected region
        for box, class_id, score in zip(boxes, classes, scores):
            region_type = id_to_names[int(class_id)]
            bbox = [float(box[0])/image.size[0], float(box[1])/image.size[1], 
                   float(box[2])/image.size[0], float(box[3])/image.size[1]]  # Convert tensors to float and normalize coordinates
            
            print(f"\nProcessing {region_type} region with confidence {score:.2f}")
            print(f"Bounding box coordinates: {bbox}")
            
            # Crop the region
            cropped_image = crop_image(image, bbox)
            if cropped_image is None:
                print("Error: Failed to crop image")
                continue
                
            # Save cropped image
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            crop_filename = f"{output_dir}/{base_name}_{region_type}_{score:.2f}_{bbox[0]:.2f}_{bbox[1]:.2f}.png"
            cropped_image.save(crop_filename)
            print(f"Saved cropped image: {crop_filename}")
            
            # Extract text based on region type
            text = None
            if region_type in ['table', 'table_caption', 'table_footnote']:
                text = extract_table_text(cropped_image)
            elif region_type in ['isolate_formula', 'formula_caption']:
                text = extract_formula_text(cropped_image)
            else:  # For title, plain text, figure_caption
                text = extract_text_with_easyocr(cropped_image)
            
            results.append({
                'region_type': region_type,
                'confidence': float(score),
                'bbox': bbox,
                'text': text
            })
        
        return results
        
    except Exception as e:
        print(f"Error in test_text_extraction: {str(e)}")
        return None

def main():
    # Example usage with a test image from assets
    test_image = '/Users/harshithalle/Smart-PDF-reader/tmp/0ac948d59657ebe3a8c28477661bd282321f56f1319df0254c54a4bb1e89da3d/H._S._M._Coxeter_Samuel_L._Greitzer_Geometry_Rez-lib.org.pdf_160 1.jpg'  # Update with actual test image path
    
    results = test_text_extraction(test_image)
    if results:
        print("\nExtraction Results:")
        for result in results:
            print(f"\n{result['region_type']} (confidence: {result['confidence']:.2f}):")
            print(f"Text: {result['text'] if result['text'] else 'No text extracted'}")

if __name__ == '__main__':
    main()