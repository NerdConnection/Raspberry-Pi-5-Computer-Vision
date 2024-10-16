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

    # Transpose the image to match (channels, height, width)
    input_data = np.transpose(image_resized, (2, 0, 1)).astype(np.float32)

    # Add batch dimension (1, channels, height, width)
    input_data = np.expand_dims(input_data, axis=0) / 255.0

    # Get the input names
    input_name = session.get_inputs()[0].name
    image_shape_name = session.get_inputs()[1].name

    # Prepare the image shape as an input
    imH, imW, _ = image.shape
    image_shape = np.array([imH, imW], dtype=np.float32).reshape(1, 2)

    # Run inference on the ONNX model
    boxes, scores, indices = session.run(None, {input_name: input_data, image_shape_name: image_shape})
    
    # Check if indices are empty
    if len(indices) == 0 or indices[0].size == 0:
        logging.warning("No objects detected.")
        return image

    # Post-processing using the 'indices'
    out_boxes, out_scores, out_classes = [], [], []
    for idx_ in indices[0]:
        if len(idx_) < 3:
            logging.warning(f"Invalid index detected: {idx_}")
            continue

        class_idx = idx_[1]  # Class index
        box_idx = idx_[2]  # Box index
        out_classes.append(class_idx)
        out_scores.append(scores[0, class_idx, box_idx])
        out_boxes.append(boxes[0, box_idx])
    
    # Draw bounding boxes on the original image
    for i in range(len(out_scores)):
        if (out_scores[i] > min_conf_threshold) and (out_scores[i] <= 1.0):
            class_idx = int(out_classes[i])
            if class_idx >= len(labels):
                logging.warning(f"Invalid class index: {class_idx}. Skipping.")
                continue

            # Get the bounding box coordinates
            box = out_boxes[i]
            ymin = int(max(1, (box[0] * imH)))
            xmin = int(max(1, (box[1] * imW)))
            ymax = int(min(imH, (box[2] * imH)))
            xmax = int(min(imW, (box[3] * imW)))
            
            # Draw bounding box
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
            
            # Prepare label
            label = f"{labels[class_idx]}: {int(out_scores[i] * 100)}%"
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            label_ymin = max(ymin, labelSize[1] + 10)
            
            # Draw label background and text
            cv2.rectangle(image, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
            cv2.putText(image, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return image
