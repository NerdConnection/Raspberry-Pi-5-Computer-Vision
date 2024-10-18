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
    
    # Get image dimensions
    imH, imW, _ = image_rgb.shape

    # Prepare input data for the ONNX model
    image_data = np.array(image_rgb).reshape(imH, imW, 3)
    
    # Add batch dimension (batch_size, height, width, channels)
    input_data = np.expand_dims(image_data.astype(np.uint8), axis=0)

    # Get the correct input name from the ONNX model
    input_name = session.get_inputs()[0].name  # Automatically get the input name from the model

    # Get the correct output names from the ONNX model
    output_names = [output.name for output in session.get_outputs()]  # Automatically get output names

    # Run inference on the ONNX model using the correct input and output names
    result = session.run(output_names, {input_name: input_data})
    
    detection_boxes, detection_classes, detection_scores, num_detections = result

    # Draw bounding boxes on the original image
    for i in range(len(detection_scores[0])):
        score = detection_scores[0][i]
        
        # Ensure score is a scalar value, not an array
        if isinstance(score, np.ndarray):
            score = score[0]  # Take the first element if it's an array

        if score > min_conf_threshold:
            class_idx = detection_classes[0][i] if isinstance(detection_classes[0], np.ndarray) else detection_classes[i]
            
            # Ensure class_idx is a scalar value
            if isinstance(class_idx, np.ndarray):
                class_idx = class_idx[0]  # Take the first element if it's an array
                
            class_idx = int(class_idx)

            if class_idx >= len(labels):
                continue

            ymin = int(max(1, detection_boxes[0][i][0] * imH))
            xmin = int(max(1, detection_boxes[0][i][1] * imW))
            ymax = int(min(imH, detection_boxes[0][i][2] * imH))
            xmax = int(min(imW, detection_boxes[0][i][3] * imW))

            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
            label = f"{labels[class_idx]}: {int(score * 100)}%"
            cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return image
