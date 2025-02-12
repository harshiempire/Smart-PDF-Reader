import os
import json
import numpy as np

def process_pdf_pages(pdf_images, bboxes_list, classes_list, scores_list, id_to_names):
    """
    Process multiple PDF pages and generate structured JSON output with reading order detection.
    
    Args:
        pdf_images (list): List of paths to PDF page images
        bboxes_list (list): List of bounding boxes for each page
        classes_list (list): List of class predictions for each page
        scores_list (list): List of confidence scores for each page
        id_to_names (dict): Mapping from class IDs to class names
    
    Returns:
        dict: Structured JSON output containing layout information for all pages
    """
    pages_data = []
    
    def detect_columns(elements, threshold=0.3):
        """Detect columns based on horizontal positions of elements."""
        if not elements:
            return 1
        
        # Get page width from the rightmost element
        page_width = max(element['bbox']['x2'] for element in elements)
        column_assignments = []
        
        for element in elements:
            center_x = (element['bbox']['x1'] + element['bbox']['x2']) / 2
            normalized_x = center_x / page_width
            column_assignments.append(normalized_x)
        
        # Analyze distribution of horizontal positions
        hist, bins = np.histogram(column_assignments, bins=10)
        peaks = [i for i, count in enumerate(hist) if count > len(elements) * threshold]
        return max(1, len(peaks))
    
    def assign_reading_order(elements):
        """Assign reading order considering column layout."""
        if not elements:
            return elements
            
        # Detect number of columns
        num_columns = detect_columns(elements)
        
        if num_columns == 1:
            # Single column: sort by vertical position
            return sorted(elements, key=lambda x: x['bbox']['y1'])
        
        # Multi-column: group elements by column and sort within each column
        page_width = max(element['bbox']['x2'] for element in elements)
        column_width = page_width / num_columns
        
        # Assign elements to columns
        columns = [[] for _ in range(num_columns)]
        for element in elements:
            center_x = (element['bbox']['x1'] + element['bbox']['x2']) / 2
            col_idx = int(center_x / column_width)
            col_idx = min(col_idx, num_columns - 1)  # Ensure valid column index
            columns[col_idx].append(element)
        
        # Sort elements within each column by vertical position
        for column in columns:
            column.sort(key=lambda x: x['bbox']['y1'])
        
        # Combine columns in reading order (left to right)
        ordered_elements = []
        for column in columns:
            ordered_elements.extend(column)
        
        return ordered_elements
    
    for page_idx, (bboxes, classes, scores) in enumerate(zip(bboxes_list, classes_list, scores_list)):
        page_elements = []
        
        for bbox, class_id, score in zip(bboxes, classes, scores):
            # Convert class ID to name
            class_name = id_to_names.get(int(class_id), 'unknown')
            
            # Create element dictionary
            element = {
                'type': class_name,
                'bbox': {
                    'x1': float(bbox[0]),
                    'y1': float(bbox[1]),
                    'x2': float(bbox[2]),
                    'y2': float(bbox[3])
                },
                'confidence': float(score)
            }
            page_elements.append(element)
        
        # Sort elements in reading order
        page_elements = assign_reading_order(page_elements)
        
        # Create page dictionary
        page_data = {
            'page_number': page_idx + 1,
            'elements': page_elements
        }
        pages_data.append(page_data)
    
    # Create final JSON structure
    output = {
        'document_layout': {
            'total_pages': len(pages_data),
            'pages': pages_data
        }
    }
    
    return output

def save_results(output, save_path):
    """
    Save the JSON output to a file.
    
    Args:
        output (dict): The JSON output to save
        save_path (str): Path where to save the JSON file
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)