from fastapi import FastAPI
from picamera2 import Picamera2
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import numpy as np

cam = Picamera2()
cam.configure(cam.create_video_configuration())
cam.start()

app = FastAPI()

@app.get("/get_frame/")
async def get_frame():
    img_array = cam.capture_array()
    img = Image.fromarray(img_array)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    return StreamingResponse(img_bytes, media_type="image/png")
