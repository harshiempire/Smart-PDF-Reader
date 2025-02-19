bbox = {
  "document_layout": {
    "total_pages": 1,
    "pages": [
      {
        "page_number": 1,
        "elements": [
          {
            "type": "title",
            "bbox": {
              "x1": 299.020751953125,
              "y1": 321.13018798828125,
              "x2": 1480.6043701171875,
              "y2": 569.3958740234375
            },
            "confidence": 0.3583584725856781
          },
          {
            "type": "title",
            "bbox": {
              "x1": 299.4757995605469,
              "y1": 323.0918884277344,
              "x2": 1063.1259765625,
              "y2": 464.0020751953125
            },
            "confidence": 0.7568033933639526
          },
          {
            "type": "title",
            "bbox": {
              "x1": 299.1059265136719,
              "y1": 481.9646301269531,
              "x2": 1480.6168212890625,
              "y2": 567.1762084960938
            },
            "confidence": 0.5990617871284485
          },
          {
            "type": "plain text",
            "bbox": {
              "x1": 297.5455322265625,
              "y1": 630.6560668945312,
              "x2": 1700,
              "y2": 1319.3267822265625
            },
            "confidence": 0.9839761257171631
          },
          {
            "type": "plain text",
            "bbox": {
              "x1": 295.5846862792969,
              "y1": 1381.1341552734375,
              "x2": 1700,
              "y2": 1879.984619140625
            },
            "confidence": 0.9836615920066833
          },
          {
            "type": "plain text",
            "bbox": {
              "x1": 296.44561767578125,
              "y1": 1944.2392578125,
              "x2": 1700,
              "y2": 2200
            },
            "confidence": 0.9829394817352295
          },
          {
            "type": "plain text",
            "bbox": {
              "x1": 296.3824768066406,
              "y1": 2200,
              "x2": 1700,
              "y2": 2220
            },
            "confidence": 0.9821754097938538
          }
        ]
      }
    ]
  },
}
bbox_1 = bbox["document_layout"]["pages"][0]["elements"][0]["bbox"]
# import easyocr
from pdf2image import convert_from_path
import cv2

pages = convert_from_path('basic-text.pdf', 500)
for count,page in enumerate(pages):
    page.save(f"page{count}.jpg", "JPEG")
    # image_width = page.width
    # image_height = page.height
    # # box_xmin, box_ymin, box_xmax, box_ymax = bbox_1
    # box_xmin = int(bbox_1['x1']) 
    # box_xmax = int(bbox_1['x2']) 
    # box_ymin = int(bbox_1['y1']) 
    # box_ymax = int(bbox_1['y2']) 


    # print(box_xmin, box_ymin, box_xmax, box_ymax)
    # if  int( box_xmin ) < 0:
    #     box_xmin = 0
                        
    # if int( box_ymin ) < 0:
    #     box_ymin = 0

    # if int( box_xmax ) > image_width:
    #     box_xmax = image_width

    # if int( box_ymax ) > image_height:
    #     box_ymax = image_height

    # img = cv2.imread("page0.jpg", cv2.IMREAD_GRAYSCALE) 
    # crop = img[box_xmin:box_ymax, box_ymin:box_xmax]
    # cv2.imwrite("crop.jpg", crop)    