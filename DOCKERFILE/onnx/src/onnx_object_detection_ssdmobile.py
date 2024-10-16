import os
import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont, ImageColor
import matplotlib.pyplot as plt

def load_model(model_dir, model_name):
    model_path = os.path.join(model_dir, model_name)
    session = ort.InferenceSession(model_path)
    return session

def draw_detection(draw, d, c, labels, font):
    width, height = draw.im.size
    # Multiply with height and width to get pixel values
    top = d[0] * height
    left = d[1] * width
    bottom = d[2] * height
    right = d[3] * width
    top = max(0, np.floor(top + 0.5).astype('int32'))
    left = max(0, np.floor(left + 0.5).astype('int32'))
    bottom = min(height, np.floor(bottom + 0.5).astype('int32'))
    right = min(width, np.floor(right + 0.5).astype('int32'))
    
    label = labels[c]
    label_size = draw.textsize(label, font=font)
    
    if top - label_size[1] >= 0:
        text_origin = tuple(np.array([left, top - label_size[1]]))
    else:
        text_origin = tuple(np.array([left, top + 1]))
    
    color = ImageColor.getrgb("red")
    thickness = 0
    draw.rectangle([left + thickness, top + thickness, right - thickness, bottom - thickness],
                   outline=color)
    draw.text(text_origin, label, fill=color, font=font)

def transform_onnx(image, session, labels, min_conf_threshold=0.5):
    # Convert image to RGB using PIL
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    
    # Load a font, you can change the font file path as needed
    font = ImageFont.load_default()

    # Convert to numpy array
    img_data = np.array(image_pil).astype(np.uint8)
    input_data = np.expand_dims(img_data, axis=0)

    # Get the input names
    input_name = session.get_inputs()[0].name

    # Run inference on the ONNX model
    outputs = session.run(None, {input_name: input_data})

    # Adjust the number of outputs based on the actual model output
    if len(outputs) == 3:
        detection_boxes, detection_scores, detection_classes = outputs
    else:
        num_detections, detection_boxes, detection_scores, detection_classes = outputs

    imH, imW, _ = image.shape

    # Loop over the results - each returned tensor is a batch
    batch_size = num_detections.shape[0]
    for batch in range(0, batch_size):
        num_detect = int(num_detections[batch])

        for detection in range(0, num_detect):
            score = detection_scores[batch][detection]
            
            if score > min_conf_threshold:
                c = int(detection_classes[batch][detection])
                d = detection_boxes[batch][detection]
                draw_detection(draw, d, c, labels, font)

    return image_pil  # Return PIL image instead of OpenCV image
