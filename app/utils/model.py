from ultralytics import YOLO
from .pre_processing import upscale_image
from .post_processing import refine_result_boxes, redefine_boxes, recursive_xy_cut
import easyocr
import os
import cv2
import base64
import numpy as np


directory = os.path.join(os.getcwd(), "app", "utils", "weights")

# Load the model
PARAGRAPH_MODEL = YOLO(os.path.join(directory, "paragraph.pt"))  # Double backslashes
READER = easyocr.Reader(["en"])


def read_image(base64_string):
    # Decode the base64 string to binary data
    image_data = base64.b64decode(base64_string)

    # Convert binary data to a NumPy array
    np_arr = np.frombuffer(image_data, dtype=np.uint8)

    # Decode the image array into an OpenCV image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    extracted_text = ""
    img_height, img_width = img.shape[:2]

    paragraph_results = PARAGRAPH_MODEL(
        img, verbose=False, conf=0.1, iou=0.3, agnostic_nms=True
    )

    for p_result in paragraph_results:
        p_boxes = refine_result_boxes(p_result)
        p_bboxes = redefine_boxes(p_boxes)
        p_sorted_indices = recursive_xy_cut(p_bboxes)

        for p_box in p_sorted_indices:
            p_x_min, p_y_min, p_x_max, p_y_max = map(int, p_box)
            p_x_min, p_y_min = max(0, p_x_min), max(0, p_y_min)
            p_x_max, p_y_max = min(img_width, p_x_max), min(img_height, p_y_max)
            cropped_paragraph = img[p_y_min:p_y_max, p_x_min:p_x_max]

            paragraph = READER.readtext(cropped_paragraph)

            extracted_text += f"{' '.join(item[1] for item in paragraph)}\n"

    return extracted_text
