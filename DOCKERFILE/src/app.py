import argparse
import asyncio
import json
import logging
import os
import uuid
import time
import av
import numpy as np
import importlib.util
from fractions import Fraction
from picamera2 import Picamera2
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaStreamTrack
import cv2
import tflite_object_detection

ROOT = os.path.dirname(__file__)
ROOT_STATIC = os.path.join(os.path.dirname(__file__), "static")
ROOT_TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")

cam = Picamera2()
cam.configure(cam.create_video_configuration())
cam.start()
pcs = {}

# TensorFlow Lite model and label map initialization
OBJECT_MODEL_DIR = "src/TFLite_model/object_detection/"
LABELMAP_NAME = "labels.txt" # using coco dataset label 2017

# Load the label map
with open(os.path.join("src", LABELMAP_NAME), 'r') as f:
    labels = [line.strip() for line in f.readlines()]
if labels[0] == '???':
    del(labels[0])




class PiCameraTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, transform):
        super().__init__()
        self.transform = transform  # 클라이언트에서 요청한 AI 모델명

    # video track에 추가되는 프레임 생성 recv함수 
    async def recv(self):
        img = cam.capture_array()

        if self.transform == "tfLite": ###### NEED TO CHANGE TO MODEL NAME (OBJECT DETECTION)
            # Load the TensorFlow Lite model
            interpreter, input_details, output_details = tflite_object_detection.load_model(OBJECT_MODEL_DIR,'efficientdet.tflite') ####### CHANGE 'MODEL NAME' WITH EXTRA [ELIF] TO SELECT ONTHER OBJECT DETECTION MODEL 

            # Transform the image using the TensorFlow Lite model
            processed_image = tflite_object_detection.transform_tflite(img, interpreter, input_details, output_details, labels)

            # Convert image to RGB format if it is in RGBA
            if processed_image.shape[2] == 4:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGBA2RGB)

            new_frame = av.VideoFrame.from_ndarray(processed_image, format='rgb24')
        else:
            # Load the TensorFlow Lite model
            interpreter, input_details, output_details = tflite_object_detection.load_model(OBJECT_MODEL_DIR,'ssd-mobilenet-v1.tflite') ####### CHANGE 'MODEL NAME' WITH EXTRA [ELIF] TO SELECT ONTHER OBJECT DETECTION MODEL 

            # Transform the image using the TensorFlow Lite model
            processed_image = tflite_object_detection.transform_tflite(img, interpreter, input_details, output_details, labels)

            # Convert image to RGB format if it is in RGBA
            if processed_image.shape[2] == 4:
                processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGBA2RGB)

            new_frame = av.VideoFrame.from_ndarray(processed_image, format='rgb24')

        pts = time.time() * 1000000
        new_frame.pts = int(pts)
        new_frame.time_base = Fraction(1, 1000000)
        return new_frame


async def webrtc(request):
    logging.info("Received WebRTC request")
    try:
        params = await request.json()
        if params["type"] == "request":
            pc = RTCPeerConnection()
            pc_id = f"PeerConnection({uuid.uuid4()})"
            pcs[pc_id] = pc

            @pc.on("connectionstatechange")
            async def on_connectionstatechange():
                print(f"Connection state is {pc.connectionState}")
                if pc.connectionState == "failed":
                    await pc.close()
                    pcs.pop(pc_id, None)

            cam_track = PiCameraTrack(transform=params["video_transform"])
            pc.addTrack(cam_track)
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)

            await asyncio.sleep(0)  # Allow other tasks to run

            while pc.iceGatheringState != "complete":
                await asyncio.sleep(0.1)

            return web.Response(
                content_type="application/json",
                text=json.dumps({
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type,
                    "id": pc_id,
                    "iceServers": []
                }),
            )
        elif params["type"] == "answer":
            pc = pcs.get(params["id"])

            if not pc:
                return web.Response(
                    content_type="application/json",
                    text=json.dumps({"error": "PeerConnection not found"}),
                    status=404,
                )

            await pc.setRemoteDescription(RTCSessionDescription(sdp=params["sdp"], type=params["type"]))

            return web.Response(content_type="application/json", text=json.dumps({}))

    except Exception as e:
        logging.error(f"Error during WebRTC handling: {e}")
        return web.Response(content_type="application/json", text=json.dumps({"error": str(e)}), status=500)


async def on_shutdown(app):
    coros = [pc.close() for pc in pcs.values()]
    await asyncio.gather(*coros)
    pcs.clear()


async def index(request):
    content = open(os.path.join(ROOT_TEMPLATES, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT_STATIC, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Raspberry Pi WebRTC Camera Streamer")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP server (default: 8080)")
    parser.add_argument("--verbose", "-v", action="count")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/webrtc", webrtc)
    logging.info(f"======== Running on http://{args.host}:{args.port} ========")
    web.run_app(app, host=args.host, port=args.port)