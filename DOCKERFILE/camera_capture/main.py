from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
picam2.preview_configuration.main.size = (800,800)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

count = 0

while True:
    im = picam2.capture_array()
    print("hi")
    filename = f'image_{count:04d}.jpg'
    cv2.imwrite(filename, im)
    print(f"Saved {filename}")
        
    count += 1
    time.sleep(1)


cv2.destroyAllWindows()
