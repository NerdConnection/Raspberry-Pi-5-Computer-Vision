
import os
import cv2
import numpy as np
import importlib.util
import logging
from tflite_runtime.interpreter import Interpreter

def load_model(model_dir, model_name):
    model_path = os.path.join(model_dir, model_name)
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    return interpreter, input_details, output_details

def transform_tflite(image, interpreter, input_details, output_details, labels, min_conf_threshold=0.5):
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    
    # Resize and normalize the image
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height))
    
    # Check if the model expects FLOAT32 input, and normalize accordingly
    input_data = np.expand_dims(image_resized, axis=0)
    
    if input_details[0]['dtype'] == np.float32:
        input_data = np.float32(input_data) / 255.0  # Normalize to 0-1 if needed
    
    # Perform inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    # Get results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    classes = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]
    
    imH, imW, _ = image.shape
    for i in range(len(scores)):
        if (scores[i] > min_conf_threshold) and (scores[i] <= 1.0):
            class_idx = int(classes[i])
            if class_idx >= len(labels):
                logging.warning(f"Invalid class index: {class_idx}. Skipping.")
                continue

            ymin = int(max(1, (boxes[i][0] * imH)))
            xmin = int(max(1, (boxes[i][1] * imW)))
            ymax = int(min(imH, (boxes[i][2] * imH)))
            xmax = int(min(imW, (boxes[i][3] * imW)))
            
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
            label = '%s: %d%%' % (labels[class_idx], int(scores[i] * 100))
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            label_ymin = max(ymin, labelSize[1] + 10)
            cv2.rectangle(image, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
            cv2.putText(image, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    return image


