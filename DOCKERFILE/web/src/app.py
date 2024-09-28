import argparse
import asyncio
import json
import logging
import os
import aiohttp
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
import docker
import subprocess

# For control docker container
client = docker.from_env()
containers = client.containers.list(all=True) # search all container

# tfLite_container
tflite_container = next((c for c in containers if c.name == "tflite"), None) 
tflite_container_counter = 0



ROOT = os.path.dirname(__file__)
ROOT_STATIC = os.path.join(os.path.dirname(__file__), "static")
ROOT_TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")

async def return_ip(request):
    data = await request.json()
    model_name = data.get("model")
    
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
    parser = argparse.ArgumentParser(description="RatRig V-Core VAOC (WebRTC camera-streamer)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP server (default: 8080)")
    parser.add_argument("--verbose", "-v", action="count")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/get-ip", return_ip)
    logging.info(f"======== Running on http://{args.host}:{args.port} ========")
    web.run_app(app, host=args.host, port=args.port)
