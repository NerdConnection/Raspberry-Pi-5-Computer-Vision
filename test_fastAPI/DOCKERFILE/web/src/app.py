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
import docker
import requests
from PIL import Image
import io
import httpx

# For control docker container
client = docker.from_env()
containers = client.containers.list(all=True) # search all container
# tfLite_container
tflite_container = next((c for c in containers if c.name == "tflite"), None) 

ROOT = os.path.dirname(__file__)
ROOT_STATIC = os.path.join(os.path.dirname(__file__), "static")
ROOT_TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")
pcs = {}


class PiCameraTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, transform):
        super().__init__()
        self.transform = transform

    async def recv(self):
        if self.transform == "tfLite":
            async with httpx.AsyncClient() as client:
                response = await client.get("http://tflite:8000/get_frame/")
            img_bytes = io.BytesIO(response.content)
            img = Image.open(img_bytes)
            img_np = np.array(img)


            pts = time.time() * 1000000
            new_frame = av.VideoFrame.from_ndarray(img_np, format='rgba')
            new_frame.pts = int(pts)
            new_frame.time_base = Fraction(1, 1000000)
            return new_frame


async def on_connectionstatechange(pc_id, pc, model):
    logging.info(f"Connection state for {pc_id} is {pc.connectionState}")
    if pc.connectionState == "failed":
        logging.error(f"Connection {pc_id} failed. Closing connection.")
        await pc.close()
        pcs.pop(pc_id, None)
        
    elif pc.connectionState == "closed":
        logging.info(f"Connection {pc_id} closed. Removing from pcs.")
        pcs.pop(pc_id, None)
        if model == "tfLite":
            if tflite_container.status == "running":
                tflite_container.stop()
                logging.info("Stopped container 'tflite'")
            else:
                logging.info("Container 'tflite' is not running")

    elif pc.connectionState == "connecting":
        if model == "tfLite":
            # If container is not running, start it
            if tflite_container.status != "running":
                tflite_container.start()
                logging.info("Started container 'tflite'")
            else:
                logging.info("Container 'tflite' is already running")
                

async def webrtc(request):
    logging.info("Received WebRTC request")
    try:
        params = await request.json()
        if params["type"] == "request":
            pc = RTCPeerConnection()
            pc_id = f"PeerConnection({uuid.uuid4()})"
            pcs[pc_id] = pc
            pc.on("connectionstatechange")(lambda: asyncio.create_task(on_connectionstatechange(pc_id, pc, params["video_transform"])))
            
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

