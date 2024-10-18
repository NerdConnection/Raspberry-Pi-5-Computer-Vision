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
from aiortc.contrib.media import MediaStreamTrack, MediaRelay
import cv2
import tflite_object_detection
import subprocess

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
        self.transform = transform  # model selected by user

        # Load the appropriate model and labels based on user selection
        if self.transform == "efficientdet":
            self.model_name = 'efficientdet.tflite'
        elif self.transform == "ssd-mobilenet-v1":
            self.model_name = 'ssd-mobilenet-v1.tflite'
        else:
            raise ValueError(f"Unsupported model type: {self.transform}")
        # Load the TensorFlow Lite model once during initialization
        self.interpreter, self.input_details, self.output_details = tflite_object_detection.load_model(OBJECT_MODEL_DIR, self.model_name)


    async def recv(self):
        img = cam.capture_array()

        # Transform the image using the TensorFlow Lite model
        processed_image = tflite_object_detection.transform_tflite(
            img, self.interpreter, self.input_details, self.output_details, labels
        )

        # Convert image to RGB format if it is in RGBA
        if processed_image.shape[2] == 4:
            processed_image = cv2.cvtColor(processed_image, cv2.COLOR_RGBA2RGB)

        # Create a new VideoFrame
        new_frame = av.VideoFrame.from_ndarray(processed_image, format='rgb24')

        # Set PTS (Presentation Time Stamp) for frame synchronization
        pts = time.time() * 1000000
        new_frame.pts = int(pts)
        new_frame.time_base = Fraction(1, 1000000)

        return new_frame


async def on_connectionstatechange(pc_id, pc, model):
    logging.info(f"Connection state for {pc_id} is {pc.connectionState}")
    if pc.connectionState == "failed":
        logging.error(f"Connection {pc_id} failed. Closing connection.")
        
        for sender in pc.getSenders():
            if sender.track:
                sender.track.stop()
        
        await pc.close()
        pcs.pop(pc_id, None)
        
    elif pc.connectionState == "closed":
        logging.info(f"Connection {pc_id} closed. Removing from pcs.")

        for sender in pc.getSenders():
            if sender.track:
                sender.track.stop()

        await pc.close()
        pcs.pop(pc_id, None)

    elif pc.connectionState == "connecting":
        logging.info("connecting container 'tflite'")
                

efficientdet_track = PiCameraTrack(transform="efficientdet")
mobilenet_track = PiCameraTrack(transform="ssd-mobilenet-v1")

async def webrtc(request):
    logging.info("Received WebRTC request")
    try:
        params = await request.json()
        if params["type"] == "request":
            pc = RTCPeerConnection()
            pc_id = f"PeerConnection({uuid.uuid4()})"
            pcs[pc_id] = pc
            pc.on("connectionstatechange")(lambda: asyncio.create_task(on_connectionstatechange(pc_id, pc, params["video_transform"])))
            
            if params["video_transform"] == "efficientdet":
                pc.addTrack(efficientdet_track)
            elif params["video_transform"] == "ssd-mobilenet-v1":
                pc.addTrack(mobilenet_track)
            
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


async def return_ip(request):
    data = await request.json()
    # Executes a command to retrieve the IP address of the Raspberry Pi's 'wlan0' interface
    result = subprocess.run(["ip", "addr", "show", "wlan0"], capture_output=True, text=True)
    output = result.stdout
    for line in output.splitlines():
        if "inet " in line:
            ip_address = line.split()[1].split('/')[0] 
            break
    else:
        ip_address = None 
        
    logging.info(f"======== wlan0 IP: {ip_address} ========")
    return web.json_response({"ip": ip_address})
    
async def index(request):
    content = open(os.path.join(ROOT_TEMPLATES, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT_STATIC, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Raspberry Pi WebRTC Camera Streamer")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=80, help="Port for HTTP server (default: 8080)")
    parser.add_argument("--verbose", "-v", action="count")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/webrtc", webrtc)
    app.router.add_post("/get-ip", return_ip)
    logging.info(f"======== Running on http://{args.host}:{args.port} ========")
    web.run_app(app, host=args.host, port=args.port)

