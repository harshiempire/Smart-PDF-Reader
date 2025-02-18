import os

os.environ["GRADIO_TEMP_DIR"] = "./tmp"

import io
import json
import sys
import tempfile

import gradio as gr
import numpy as np
import PyPDF2
import torch
import torchvision
from huggingface_hub import snapshot_download
from PIL import Image

from pdf_processor import process_pdf_pages, save_results
from visualization import visualize_bbox

# == download weights ==
model_dir = snapshot_download(
    "juliozhao/DocLayout-YOLO-DocStructBench",
    local_dir="./models/DocLayout-YOLO-DocStructBench",
)
# == select device ==
device = "cuda" if torch.cuda.is_available() else "cpu"

id_to_names = {
    0: "title",
    1: "plain text",
    2: "abandon",
    3: "figure",
    4: "figure_caption",
    5: "table",
    6: "table_caption",
    7: "table_footnote",
    8: "isolate_formula",
    9: "formula_caption",
}


def process_pdf(pdf_path, conf_threshold, iou_threshold):
    print(f"DEBUG: Received PDF path: {pdf_path}")
    print(
        f"DEBUG: File exists check: {os.path.exists(pdf_path) if pdf_path else False}"
    )

    if not pdf_path:
        print("Error: PDF path is None or empty")
        return [], None
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file does not exist at path: {pdf_path}")
        return [], None
    if not pdf_path.lower().endswith(".pdf"):
        print(f"Error: File is not a PDF: {pdf_path}")
        return [], None

    visualizations = []
    pdf_images = []
    model_outputs = {"bboxes": [], "classes": [], "scores": []}

    try:
        print(f"DEBUG: Opening PDF file: {pdf_path}")
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(
                f"DEBUG: PDF loaded successfully. Number of pages: {len(pdf_reader.pages)}"
            )

            if len(pdf_reader.pages) == 0:
                print("Error: PDF file is empty")
                return [], None

            for page_num in range(len(pdf_reader.pages)):
                try:
                    print(f"\nDEBUG: Processing page {page_num + 1}")
                    page = pdf_reader.pages[page_num]

                    with tempfile.NamedTemporaryFile(
                        suffix=".png", delete=False
                    ) as tmp_file:
                        try:
                            from pdf2image import convert_from_bytes

                            print(f"DEBUG: Converting page {page_num + 1} to image")
                            try:
                                # Extract page content as bytes
                                page_content = io.BytesIO()
                                writer = PyPDF2.PdfWriter()
                                writer.add_page(page)
                                writer.write(page_content)
                                page_content.seek(0)

                                # Convert PDF bytes to image
                                images = convert_from_bytes(
                                    page_content.getvalue(),
                                    dpi=300,
                                    thread_count=2,
                                    grayscale=False,
                                    size=(None, None),
                                    use_pdftocairo=True,
                                )
                                if not images:
                                    print(
                                        f"Warning: Could not convert page {page_num + 1} to image"
                                    )
                                    continue
                                print(
                                    f"DEBUG: Page {page_num + 1} converted successfully"
                                )
                            except Exception as conv_error:
                                print(
                                    f"Error converting page {page_num + 1} to image: {str(conv_error)}"
                                )
                                continue

                            page_image = images[0]
                            page_image.save(tmp_file.name)
                            print(
                                f"DEBUG: Saved page {page_num + 1} as temporary image"
                            )

                            img = np.array(page_image)
                            processed_result = recognize_image(
                                img, conf_threshold, iou_threshold
                            )
                            if processed_result is not None:
                                visualizations.append(processed_result["visualization"])
                                pdf_images.append(tmp_file.name)
                                model_outputs["bboxes"].append(
                                    processed_result["bboxes"]
                                )
                                model_outputs["classes"].append(
                                    processed_result["classes"]
                                )
                                model_outputs["scores"].append(
                                    processed_result["scores"]
                                )
                                print(
                                    f"DEBUG: Successfully processed page {page_num + 1}"
                                )
                        except Exception as page_error:
                            print(
                                f"Error processing page {page_num + 1}: {str(page_error)}"
                            )
                            continue
                        finally:
                            if os.path.exists(tmp_file.name):
                                os.unlink(tmp_file.name)
                except Exception as page_error:
                    print(f"Error processing page {page_num + 1}: {str(page_error)}")
                    continue

        # Generate structured JSON output
        if pdf_images and model_outputs["bboxes"]:
            json_output = process_pdf_pages(
                pdf_images,
                model_outputs["bboxes"],
                model_outputs["classes"],
                model_outputs["scores"],
                id_to_names,
            )

            json_text_output = input()

        else:
            json_output = None

        return visualizations, json_output
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return [], None


def recognize_image(input_img, conf_threshold, iou_threshold):
    print("Starting image recognition...")
    print(
        f"Input image shape: {input_img.shape if hasattr(input_img, 'shape') else 'Not a numpy array'}"
    )
    print(f"Confidence threshold: {conf_threshold}, IOU threshold: {iou_threshold}")

    det_res = model.predict(
        input_img,
        imgsz=1024,
        conf=conf_threshold,
        device=device,
    )[0]
    print("\nDetection results:")
    print(f"Number of detections: {len(det_res)}")

    boxes = det_res.__dict__["boxes"].xyxy
    classes = det_res.__dict__["boxes"].cls
    scores = det_res.__dict__["boxes"].conf

    indices = torchvision.ops.nms(
        boxes=torch.Tensor(boxes),
        scores=torch.Tensor(scores),
        iou_threshold=iou_threshold,
    )
    boxes, scores, classes = boxes[indices], scores[indices], classes[indices]

    if len(boxes.shape) == 1:
        boxes = np.expand_dims(boxes, 0)
        scores = np.expand_dims(scores, 0)
        classes = np.expand_dims(classes, 0)

    # Create visualization
    vis_result = visualize_bbox(input_img, boxes, classes, scores, id_to_names)

    # Add detection results to the output
    vis_result["bboxes"] = boxes
    vis_result["classes"] = classes
    vis_result["scores"] = scores

    return vis_result


def gradio_reset():
    return gr.update(value=None), gr.update(value=None)


if __name__ == "__main__":
    root_path = os.path.abspath(os.getcwd())
    # == load model ==
    from doclayout_yolo import YOLOv10

    print(f"Using device: {device}")
    model = YOLOv10(
        os.path.join(
            os.path.dirname(__file__),
            "models",
            "DocLayout-YOLO-DocStructBench",
            "doclayout_yolo_docstructbench_imgsz1024.pt",
        )
    )  # load an official model

    with open("header.html", "r") as file:
        header = file.read()
    with gr.Blocks() as demo:
        gr.HTML(header)

        with gr.Row():
            with gr.Column():

                with gr.Tab("Image Input"):
                    input_img = gr.Image(label=" ", interactive=True)
                    with gr.Row():
                        clear_img = gr.Button(value="Clear")
                        predict_img = gr.Button(
                            value="Detect", interactive=True, variant="primary"
                        )

                with gr.Tab("PDF Input"):
                    input_pdf = gr.File(
                        label="Upload PDF", file_types=[".pdf"], type="filepath"
                    )
                    with gr.Row():
                        clear_pdf = gr.Button(value="Clear")
                        predict_pdf = gr.Button(
                            value="Detect", interactive=True, variant="primary"
                        )

                with gr.Row():
                    conf_threshold = gr.Slider(
                        label="Confidence Threshold",
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=0.25,
                    )

                with gr.Row():
                    iou_threshold = gr.Slider(
                        label="NMS IOU Threshold",
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=0.45,
                    )

                with gr.Accordion("Examples:"):
                    example_root = os.path.join(
                        os.path.dirname(__file__), "assets", "example"
                    )
                    gr.Examples(
                        examples=[
                            os.path.join(example_root, _)
                            for _ in os.listdir(example_root)
                            if _.endswith("jpg")
                        ],
                        inputs=[input_img],
                    )
            with gr.Column():
                output_gallery = gr.Gallery(
                    label="Detection Results",
                    show_label=True,
                    elem_id="gallery",
                    columns=2,
                    height="auto",
                )
                output_json = gr.JSON(label="JSON Output", visible=True)

        clear_img.click(
            gradio_reset, inputs=None, outputs=[input_img, output_gallery, output_json]
        )
        clear_pdf.click(
            gradio_reset, inputs=None, outputs=[input_pdf, output_gallery, output_json]
        )
        predict_img.click(
            recognize_image,
            inputs=[input_img, conf_threshold, iou_threshold],
            outputs=[output_gallery],
        )
        predict_pdf.click(
            process_pdf,
            inputs=[input_pdf, conf_threshold, iou_threshold],
            outputs=[output_gallery, output_json],
        )

    demo.launch(server_name="0.0.0.0", server_port=7860, debug=True, share=True)

