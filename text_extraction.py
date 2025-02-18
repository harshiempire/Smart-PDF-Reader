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


def get_final_ocr(json_output):

    final_ocr_output = {}
    instance_of_page
    for i in range(json_output["total_pages"]):

        elements = json_output[i]
        for data in elements:
            type_of_image = data.type
            ocr_text = get_text_from_bbox(instance_of_page, data.bbox, type_of_image)
            return


def get_text_from_bbox(instance_of_page, bbox, type_of_image):
    if type_of_image == "table":
        use_pymupdf()
