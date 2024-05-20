import os
import time
from PIL import Image
import numpy as np
import onnxruntime
import cv2
from picamera2 import Picamera2
from threading import Thread

class VideoStream:
    """Camera object that controls video streaming from the Picamera2"""
    def __init__(self, resolution=(640, 480), framerate=30):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": resolution, "format": "RGB888"}))
        self.picam2.start()
        self.frame = self.picam2.capture_array()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.picam2.stop()
                return
            self.frame = self.picam2.capture_array()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

def preprocess_image(image, height, width):
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
    image_data = image.astype(np.float32)
    image_data /= 255.0
    image_data -= np.array([0.485, 0.456, 0.406])
    image_data /= np.array([0.229, 0.224, 0.225])
    image_data = np.transpose(image_data, (2, 0, 1))
    image_data = np.expand_dims(image_data, 0)
    return image_data

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def run_inference(session, image, categories):
    output = session.run([], {'input': preprocess_image(image, 224, 224)})[0]
    output = output.flatten()
    output = softmax(output)
    top5_catid = np.argsort(-output)[:5]
    for catid in top5_catid:
        print(categories[catid], output[catid])
    with open("result.txt", "w") as f:
        for catid in top5_catid:
            f.write(categories[catid] + " " + str(output[catid]) + " \r")

if __name__ == "__main__":
    with open("imagenet_classes.txt", "r") as f:
        categories = [s.strip() for s in f.readlines()]
    
    session = onnxruntime.InferenceSession("mobilenet_v2_float.onnx")

    # Retry opening the camera if busy
    max_retries = 5
    for i in range(max_retries):
        try:
            videostream = VideoStream(resolution=(640, 480), framerate=30).start()
            time.sleep(1)
            break
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries} failed: {e}")
            if i == max_retries - 1:
                raise
            time.sleep(5)  # Wait before retrying

    while True:
        frame = videostream.read()
        frame = cv2.flip(frame, 1)
        cv2.imshow('Camera Frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        run_inference(session, frame, categories)

    videostream.stop()
    cv2.destroyAllWindows()
