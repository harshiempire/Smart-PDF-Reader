import os
from typing import List

from backend.models import (
    DocumentSchema,
    SegmentSchema,
    PositionInfo,
    ProcessingStatus,
    SegmentType,
)
from backend.db import DBClient

# Dynamically load the PDF processing utilities from the gradio-backend folder.
import importlib.util
import sys

_APP_DIR = os.path.join(os.path.dirname(__file__), "gradio-backend")
spec = importlib.util.spec_from_file_location(
    "gradio_app", os.path.join(_APP_DIR, "app.py")
)
_gradio_app = importlib.util.module_from_spec(spec)
sys.path.insert(0, _APP_DIR)
spec.loader.exec_module(_gradio_app)  # type: ignore
process_pdf = _gradio_app.process_pdf


def _map_segment_type(segment_name: str) -> SegmentType:
    """Map raw detection labels to SegmentType enum."""
    name = segment_name.lower()
    if name in {"title", "section", "heading"}:
        return SegmentType.TITLE
    if name in {"figure", "isolate_formula"}:
        return SegmentType.FIGURE
    if name in {"table"}:
        return SegmentType.TABLE
    if "caption" in name or "footnote" in name:
        return SegmentType.CAPTION
    return SegmentType.PARAGRAPH


async def process_and_store_document(
    pdf_path: str,
    user_id: str,
    conf_threshold: float = 0.25,
    iou_threshold: float = 0.45,
) -> str:
    """Process a PDF file and store segments in the database.

    This function performs layout detection and OCR on the given PDF and stores
    the resulting document and segment records in MongoDB using the schemas
    defined in ``models.py``.
    """

    # Run the detection + OCR pipeline from gradio-backend
    visualizations, json_output = process_pdf(pdf_path, conf_threshold, iou_threshold)
    if json_output is None:
        raise RuntimeError("PDF processing failed")

    # Collect basic document info
    file_stats = os.stat(pdf_path)
    document = DocumentSchema(
        filename=os.path.basename(pdf_path),
        pages=json_output["document_layout"]["total_pages"],
        processing_status=ProcessingStatus.COMPLETED,
        user_id=user_id,
        file_size=file_stats.st_size,
    )

    client = await DBClient.getInstance()
    if client is None:
        raise RuntimeError("Database connection failed")
    db = client.get_default_database()
    documents_col = db["documents"]
    segments_col = db["segments"]

    result = await documents_col.insert_one(document.dict(by_alias=True, exclude={"id"}))
    document_id = result.inserted_id

    # Store segments
    segments: List[SegmentSchema] = []
    text_pages = json_output.get("text_content", {}).get("pages", [])
    for page in text_pages:
        page_number = page.get("page_number", 0)
        for element in page.get("elements", []):
            bbox = element.get("bbox", {})
            page_width = 1.0
            page_height = 1.0
            pos = PositionInfo(
                x=bbox.get("x1", 0.0),
                y=bbox.get("y1", 0.0),
                width=bbox.get("x2", 0.0) - bbox.get("x1", 0.0),
                height=bbox.get("y2", 0.0) - bbox.get("y1", 0.0),
                page_width=page_width,
                page_height=page_height,
            )
            seg = SegmentSchema(
                document_id=document_id,
                page_number=page_number,
                text_content=element.get("text", ""),
                position_info=pos,
                segment_type=_map_segment_type(element.get("type", "")),
            )
            segments.append(seg)

    if segments:
        await segments_col.insert_many(
            [s.dict(by_alias=True, exclude={"id"}) for s in segments]
        )

    return str(document_id)
