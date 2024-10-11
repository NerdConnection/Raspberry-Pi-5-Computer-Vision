import os
import cv2
import numpy as np
import onnxruntime as ort
import logging
from PIL import Image

logging.basicConfig(level=logging.INFO)

def load_model(model_dir, model_name):
    model_path = os.path.join(model_dir, model_name)
    session = ort.InferenceSession(model_path)
    return session

def transform_onnx(image, session, labels, min_conf_threshold=0.5):
    # Convert image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize image to the fixed input size (416, 416) required by the Tiny-YOLOv3 model
    input_size = (416, 416)
    image_resized = cv2.resize(image_rgb, input_size)

    # Normalize the image
    image_normalized = image_resized / 255.0

    # Transpose the image to match (channels, height, width)
    input_data = np.transpose(image_normalized, (2, 0, 1)).astype(np.float32)

    # Add batch dimension (1, channels, height, width)
    input_data = np.expand_dims(input_data, axis=0) 

    # Get the input names
    input_name = session.get_inputs()[0].name
    image_shape_name = session.get_inputs()[1].name

    # Prepare the image shape as an input
    imH, imW, _ = image.shape
    image_shape = np.array([imH, imW], dtype=np.float32).reshape(1, 2)

    # Run inference on the ONNX model
    outputs = session.run(None, {input_name: input_data, image_shape_name: image_shape})

    # Postprocess outputs
    boxes = []
    confidences = []
    class_ids = []

    detected_objects = []  

    for detection in outputs[0][0]:
        scores = detection[5:]
        if scores.size == 0:
            continue
        else :
            logging.info("fuck")


        class_id = np.argmax(scores)
        confidence = scores[class_id]

        if confidence > min_conf_threshold:  
            box = detection[0:4] * np.array([imW, imH, imW, imH])
            (center_x, center_y, width, height) = box.astype("int")
            x = int(center_x - (width / 2))
            y = int(center_y - (height / 2))
            boxes.append([x, y, int(width), int(height)])
            confidences.append(float(confidence))
            class_ids.append(class_id)

            detected_objects.append((labels[class_id], confidence))

    if detected_objects:
        logging.info(f"Detected {len(detected_objects)} objects:")
        for obj_name, conf in detected_objects:
            logging.info(f"Object: {obj_name}, Confidence: {conf:.2f}")
    else:
        logging.info("No objects detected.")

    for (box, confidence, class_id) in zip(boxes, confidences, class_ids):
        (x, y, w, h) = box
        color = (0, 255, 0)  # Green for box
        label = f"{labels[class_id]}: {confidence:.2f}"
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return image
