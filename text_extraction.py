import base64
import io
import json
import os

import easyocr
import fitz
import numpy as np
import pdf2image
import pdfplumber
import pytesseract
import requests
from PIL import Image

from app import id_to_names


def extract_page_image(pdf_path, page_num):
    """Extract image from PDF page"""
    print(
        f"\nDEBUG: Attempting to extract image from page {page_num + 1} of {pdf_path}"
    )
    try:
        images = pdf2image.convert_from_path(
            pdf_path, first_page=page_num + 1, last_page=page_num + 1
        )
        if not images:
            print(f"DEBUG: No images extracted from page {page_num + 1}")
            return None
        print(f"DEBUG: Successfully extracted image from page {page_num + 1}")
        return images[0]
    except Exception as e:
        print(f"Error extracting page image: {str(e)}")
        return None


def resize_for_ocr(image):
    """Resize image to fit within OCR processing limits while maintaining quality"""
    if image is None:
        print("DEBUG: Cannot resize None image")
        return None
    try:
        # Get current dimensions
        width, height = image.size
        print(f"DEBUG: Original image dimensions: {width}x{height}")

        # Define target dimensions that work well with OCR
        target_dpi = 300  # Standard DPI for OCR
        max_dimension = 4000  # Maximum dimension to ensure good OCR performance
        min_dimension = 1000  # Minimum dimension to maintain text readability

        # Calculate scaling factor based on the larger dimension
        scale = 1.0
        max_side = max(width, height)

        if max_side > max_dimension:
            scale = max_dimension / max_side
        elif max_side < min_dimension:
            scale = min_dimension / max_side

        if scale != 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            print(f"DEBUG: Resizing image to {new_width}x{new_height} for optimal OCR")
            # Resize using high-quality resampling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            print("DEBUG: Image dimensions are optimal for OCR, no resizing needed")

        return image
    except Exception as e:
        print(f"Error resizing image: {str(e)}")
        return None


def crop_image(page_image, bbox):
    """Crop image using bounding box coordinates with improved handling"""
    if page_image is None:
        print("DEBUG: Cannot crop None image")
        return None
    try:
        # Get original dimensions
        width, height = page_image.size
        print(f"DEBUG: Original image dimensions for cropping: {width}x{height}")
        print(f"DEBUG: Cropping with bbox coordinates: {bbox}")

        # Validate bbox coordinates
        if not all(0 <= coord <= 1 for coord in bbox):
            print("DEBUG: Invalid bbox coordinates - must be between 0 and 1")
            return None

        # Calculate crop dimensions in pixels with improved rounding
        x1 = round(bbox[0] * width)
        y1 = round(bbox[1] * height)
        x2 = round(bbox[2] * width)
        y2 = round(bbox[3] * height)

        # Ensure proper ordering of coordinates
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Add adaptive padding based on image size
        padding = (
            min(width, height) // 200
        )  # Adaptive padding (0.5% of smaller dimension)
        padding = max(3, min(padding, 10))  # Ensure padding is between 3 and 10 pixels

        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(width, x2 + padding)
        y2 = min(height, y2 + padding)

        # Create crop box with validated coordinates
        crop_box = (x1, y1, x2, y2)

        # Ensure crop box has valid dimensions and minimum size
        min_dimension = 100  # Minimum size for OCR readability
        if (
            crop_box[2] <= crop_box[0]
            or crop_box[3] <= crop_box[1]
            or crop_box[2] - crop_box[0] < min_dimension // 2
            or crop_box[3] - crop_box[1] < min_dimension // 2
        ):
            print("DEBUG: Invalid or too small crop box dimensions")
            return None

        print(f"DEBUG: Final crop box coordinates: {crop_box}")
        cropped = page_image.crop(crop_box)

        # Resize if needed while maintaining aspect ratio
        crop_width = crop_box[2] - crop_box[0]
        crop_height = crop_box[3] - crop_box[1]

        if crop_width < min_dimension or crop_height < min_dimension:
            # Calculate scale while preserving aspect ratio
            scale = max(min_dimension / crop_width, min_dimension / crop_height)
            new_width = int(crop_width * scale)
            new_height = int(crop_height * scale)
            print(
                f"DEBUG: Resizing small crop to {new_width}x{new_height} for better OCR"
            )
            cropped = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return cropped
    except Exception as e:
        print(f"Error cropping image: {str(e)}")
        return None


def extract_formula_text(cropped_image):
    """Extract mathematical formula text using OCR"""
    print("\nDEBUG: Starting formula text extraction")
    try:
        if cropped_image is None:
            print("DEBUG: Cannot extract formula from None image")
            return None

        # Resize image if needed
        print("DEBUG: Resizing image for formula OCR")
        resized_image = resize_for_ocr(cropped_image)
        if resized_image is None:
            print("DEBUG: Failed to resize image for formula OCR")
            return None

        print("DEBUG: Configuring Tesseract for formula recognition")
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:()[]{}+-=<>/*^_\\"\' \n -c preserve_interword_spaces=1 -c textord_heavy_nr=1 -c textord_min_linesize=2.5'
        extracted_text = pytesseract.image_to_string(
            resized_image, config=custom_config, lang="eng"
        )
        if extracted_text:
            print(
                f"DEBUG: Successfully extracted formula text: {extracted_text[:50]}..."
            )
        else:
            print("DEBUG: No text extracted from formula image")
        return extracted_text.strip() if extracted_text else None

    except Exception as e:
        print(f"Error in formula extraction: {str(e)}")
        return None


def extract_table_text(cropped_image):
    """Extract text from table using Tesseract with table-optimized settings"""
    print("\nDEBUG: Starting table text extraction")
    try:
        if cropped_image is None:
            print("DEBUG: Cannot extract table from None image")
            return None

        print("DEBUG: Resizing image for table OCR")
        resized_image = resize_for_ocr(cropped_image)
        if resized_image is None:
            print("DEBUG: Failed to resize image for table OCR")
            return None

        print("DEBUG: Using Tesseract for table recognition")
        custom_config = r"--oem 3 --psm 6 -c preserve_interword_spaces=1"
        extracted_text = pytesseract.image_to_string(
            resized_image, config=custom_config
        )

        if extracted_text:
            print(
                f"DEBUG: Successfully extracted table text with Tesseract: {extracted_text[:50]}..."
            )
        else:
            print("DEBUG: No text extracted from table image")
        return extracted_text.strip() if extracted_text else None

    except Exception as e:
        print(f"Error in table extraction: {str(e)}")
        return None


def extract_text_with_easyocr(cropped_image):
    """Extract text from regular content using EasyOCR"""
    print("\nDEBUG: Starting EasyOCR text extraction")
    try:
        if cropped_image is None:
            print("DEBUG: Cannot extract text from None image")
            return None
        # Resize image if needed
        print("DEBUG: Resizing image for EasyOCR")
        resized_image = resize_for_ocr(cropped_image)
        if resized_image is None:
            print("DEBUG: Failed to resize image for EasyOCR")
            return None

        print("DEBUG: Initializing EasyOCR reader")
        reader = easyocr.Reader(["en"], gpu=False)
        # Convert PIL Image to numpy array for EasyOCR
        text_image_np = np.array(resized_image)
        print("DEBUG: Running EasyOCR text detection")
        # Perform OCR with optimized parameters
        results = reader.readtext(
            text_image_np,
            paragraph=True,
            batch_size=1,
            min_size=10,
            contrast_ths=0.1,
            adjust_contrast=0.5,
            text_threshold=0.7,
            link_threshold=0.4,
            low_text=0.4,
            detail=0,
        )
        extracted_text = " ".join(results)
        if extracted_text:
            print(f"DEBUG: Successfully extracted text: {extracted_text[:50]}...")
        else:
            print("DEBUG: No text extracted by EasyOCR")
        return extracted_text.strip() if extracted_text else None
    except Exception as e:
        print(f"Error in text extraction: {str(e)}")
        return None


def sort_elements_by_reading_order(elements, page_width, page_height):
    """Sort elements by reading order (top-to-bottom, left-to-right within columns)"""
    if not elements:
        return []

    # Calculate element densities for better column detection
    x_centers = [
        ((elem["bbox"]["x1"] + elem["bbox"]["x2"]) / 2) / page_width
        for elem in elements
    ]

    # Use histogram to identify column centers
    hist, bin_edges = np.histogram(x_centers, bins=20)
    peaks = []
    threshold = max(hist) * 0.3  # Adjust threshold for column detection

    for i in range(1, len(hist) - 1):
        if hist[i] > threshold and hist[i] >= hist[i - 1] and hist[i] >= hist[i + 1]:
            column_center = (bin_edges[i] + bin_edges[i + 1]) / 2
            peaks.append(column_center)

    # If no clear columns detected, check for regular spacing
    if len(peaks) <= 1:
        # Check if elements form regular columns
        x_starts = sorted(set([elem["bbox"]["x1"] for elem in elements]))
        x_gaps = [x_starts[i + 1] - x_starts[i] for i in range(len(x_starts) - 1)]

        if x_gaps:
            avg_gap = sum(x_gaps) / len(x_gaps)
            std_gap = np.std(x_gaps)

            # If gaps are regular (low standard deviation), use them for column detection
            if std_gap < avg_gap * 0.3:  # Threshold for gap regularity
                peaks = [
                    x / page_width for x in x_starts if x > page_width * 0.1
                ]  # Ignore margins

    # Assign elements to columns
    columns = [[] for _ in range(max(1, len(peaks)))]

    for elem in elements:
        center_x = (elem["bbox"]["x1"] + elem["bbox"]["x2"]) / 2
        # Find closest column
        if peaks:
            col_idx = min(
                range(len(peaks)), key=lambda i: abs(center_x / page_width - peaks[i])
            )
            columns[col_idx].append(elem)
        else:
            columns[0].append(elem)

    # Sort elements within each column by vertical position
    for column in columns:
        column.sort(key=lambda x: x["bbox"]["y1"])

    # Merge columns left-to-right
    sorted_elements = []
    for column in columns:
        sorted_elements.extend(column)

    return sorted_elements


def get_text(json_output, page_images):
    """Extract text from different document elements using specialized approaches"""
    print("\nDEBUG: Starting text extraction")
    print(
        f"DEBUG: Total pages to process: {json_output['document_layout']['total_pages']}"
    )
    extracted_content = []

    for page_idx, page_image in enumerate(page_images):
        print(f"\nDEBUG: Processing page {page_idx + 1}")
        if page_image is None:
            print(f"DEBUG: Skipping page {page_idx + 1} due to missing image")
            continue

        page_content = []
        width, height = page_image.size
        elements = json_output["document_layout"]["pages"][page_idx]["elements"]
        print(f"DEBUG: Found {len(elements)} elements on page {page_idx + 1}")

        # Sort elements by reading order
        elements = sort_elements_by_reading_order(elements, width, height)
        print("DEBUG: Elements sorted by reading order")

        # Filter out overlapping elements and handle duplicates
        filtered_elements = []
        processed_areas = []

        # Sort elements by confidence and area
        sorted_elements = sorted(
            elements,
            key=lambda x: (
                x.get("confidence", 0),
                (x["bbox"]["x2"] - x["bbox"]["x1"])
                * (x["bbox"]["y2"] - x["bbox"]["y1"]),
            ),
            reverse=True,
        )

        for elem in sorted_elements:
            # Calculate current element area
            curr_bbox = elem["bbox"]
            significant_overlap = False

            # Check overlap with previously processed areas
            for prev_area in processed_areas:
                x1 = max(curr_bbox["x1"], prev_area[0])
                y1 = max(curr_bbox["y1"], prev_area[1])
                x2 = min(curr_bbox["x2"], prev_area[2])
                y2 = min(curr_bbox["y2"], prev_area[3])

                if x1 < x2 and y1 < y2:
                    overlap_area = (x2 - x1) * (y2 - y1)
                    curr_area = (curr_bbox["x2"] - curr_bbox["x1"]) * (
                        curr_bbox["y2"] - curr_bbox["y1"]
                    )

                    # If more than 30% overlap, consider it significant
                    if overlap_area / curr_area > 0.3:
                        significant_overlap = True
                        break

            if not significant_overlap:
                filtered_elements.append(elem)
                processed_areas.append(
                    (curr_bbox["x1"], curr_bbox["y1"], curr_bbox["x2"], curr_bbox["y2"])
                )

        # Sort elements by vertical position for better context
        filtered_elements.sort(key=lambda x: (x["bbox"]["y1"], x["bbox"]["x1"]))

        # Track previous element type for context
        prev_element_type = None

        for element_idx, element in enumerate(elements):
            element_type = element["type"].lower()
            bbox = element["bbox"]
            print(
                f"\nDEBUG: Processing element {element_idx + 1}/{len(elements)} of type: {element_type}"
            )

            # Additional validation for bbox coordinates
            if not all(
                isinstance(v, (int, float))
                for v in [bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]]
            ):
                print(f"DEBUG: Invalid bbox coordinates for element {element_idx + 1}")
                continue

            # Ensure bbox coordinates are within image bounds and have minimum size
            min_size = 20  # Minimum size in pixels
            width, height = page_image.size

            # Validate and adjust bbox coordinates
            bbox["x1"] = max(0, min(bbox["x1"], width))
            bbox["y1"] = max(0, min(bbox["y1"], height))
            bbox["x2"] = max(bbox["x1"] + min_size, min(bbox["x2"], width))
            bbox["y2"] = max(bbox["y1"] + min_size, min(bbox["y2"], height))

            # Additional validation for figure captions
            if element_type in ["figure_caption", "caption"]:
                # Ensure caption has reasonable height (not too tall)
                caption_height = bbox["y2"] - bbox["y1"]
                if (
                    caption_height > height * 0.2
                ):  # Caption shouldn't be more than 20% of page height
                    bbox["y2"] = bbox["y1"] + min(caption_height, height * 0.2)

            # Normalize bbox coordinates to 0-1 range
            bbox_tuple = (
                bbox["x1"] / width,
                bbox["y1"] / height,
                bbox["x2"] / width,
                bbox["y2"] / height,
            )

            # Validate bbox dimensions
            if bbox_tuple[2] <= bbox_tuple[0] or bbox_tuple[3] <= bbox_tuple[1]:
                print(f"DEBUG: Invalid bbox dimensions for element {element_idx + 1}")
                continue

            # Crop image for the current element
            cropped_image = crop_image(page_image, bbox_tuple)
            cropped_image_filename = (
                f"cropped_images/{element_type}_{element_idx + 1}.png"
            )
            cropped_image.save(cropped_image_filename)
            if cropped_image is None:
                print(f"DEBUG: Failed to crop image for element {element_idx + 1}")
                continue

            extracted_text = None

            # Context-aware element type handling
            if element_type == "table":
                print("DEBUG: Using Tesseract for table extraction")
                extracted_text = extract_table_text(cropped_image)
            elif element_type in ["isolate_formula", "formula_caption", "formula"]:
                print("DEBUG: Using formula extraction method")
                extracted_text = extract_formula_text(cropped_image)
                if not extracted_text:
                    print("DEBUG: Formula extraction failed, falling back to Tesseract")
                    extracted_text = extract_table_text(cropped_image)
            elif element_type in ["title", "section", "heading"]:
                # Enhanced title validation with improved spacing and context checks
                is_valid_title = False
                if (
                    page_idx == 0 and bbox["y1"] < height * 0.25
                ):  # Main title at top of first page, increased threshold
                    is_valid_title = True
                elif (
                    bbox["y1"] < height * 0.2
                ):  # Section titles at top of other pages, increased threshold
                    is_valid_title = True
                elif (
                    prev_element_type != "title" and len(elements) > element_idx + 1
                ):  # Check spacing
                    next_element = elements[element_idx + 1]
                    spacing = next_element["bbox"]["y1"] - bbox["y2"]
                    # Consider both spacing and relative position
                    if (
                        spacing > height * 0.015
                        and bbox["y2"] - bbox["y1"] < height * 0.1
                    ):
                        is_valid_title = True
                # Additional check for standalone titles
                elif bbox["y2"] - bbox["y1"] < height * 0.08 and element_idx > 0:
                    prev_element = elements[element_idx - 1]
                    prev_spacing = bbox["y1"] - prev_element["bbox"]["y2"]
                    if prev_spacing > height * 0.02:
                        is_valid_title = True

                if is_valid_title:
                    print("DEBUG: Using EasyOCR for title/heading extraction")
                    extracted_text = extract_text_with_easyocr(cropped_image)
                else:
                    print("DEBUG: Reclassifying title element as plain text")
                    element_type = "plain_text"
                    extracted_text = extract_text_with_easyocr(cropped_image)
            elif element_type in ["figure", "figure_caption", "caption"]:
                print("DEBUG: Using specialized settings for figure caption")
                if prev_element_type == "figure":
                    extracted_text = extract_table_text(cropped_image)
                else:
                    print(
                        "DEBUG: Caption without figure, using general text extraction"
                    )
                    extracted_text = extract_text_with_easyocr(cropped_image)
            else:
                print("DEBUG: Using EasyOCR for general text extraction")
                extracted_text = extract_text_with_easyocr(cropped_image)
                if not extracted_text:
                    print("DEBUG: EasyOCR failed, falling back to Tesseract")
                    extracted_text = extract_table_text(cropped_image)

            if extracted_text:
                print(
                    f"DEBUG: Successfully extracted text for element {element_idx + 1}"
                )
                print(
                    f"DEBUG: Element type: {element_type}, Text preview: {extracted_text[:50]}..."
                )
            else:
                print(f"DEBUG: No text extracted for element {element_idx + 1}")

            page_content.append(
                {"type": element_type, "text": extracted_text, "bbox": bbox}
            )

            # Update previous element type
            prev_element_type = element_type

        print(f"DEBUG: Completed processing page {page_idx + 1}")
        extracted_content.append(
            {"page_number": page_idx + 1, "elements": page_content}
        )

    print("\nDEBUG: Text extraction completed for all pages")
    return {
        "total_pages": json_output["document_layout"]["total_pages"],
        "pages": extracted_content,
    }
