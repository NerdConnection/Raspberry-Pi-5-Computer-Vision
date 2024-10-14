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

# search all container
containers = client.containers.list(all=True) 

# tfLite_container
tflite_container = next((c for c in containers if c.name == "tflite"), None) 
tflite_container_counter = 0

# onnx_model_container
onnx_model_container = next((c for c in containers if c.name == "onnx"), None)
onnx_model_container_counter = 0


ROOT = os.path.dirname(__file__)
ROOT_STATIC = os.path.join(os.path.dirname(__file__), "static")
ROOT_TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")

async def return_ip(request):
    data = await request.json()
    model_name = data.get("model")
    logging.info(f"======== Requested model: {model_name} ========")
    
    try:
        # Always get the latest container object
        container = client.containers.get(model_name)
        container.reload()  # Refresh the container's state

        # Handle the container based on its status
        if container.status == "exited":
            container.start()
            logging.info(f"{model_name} container started.")
        elif container.status == "running":
            logging.info(f"{model_name} container is already running.")
        else:
            logging.warning(f"{model_name} container status: {container.status}")

    except docker.errors.NotFound:
        logging.error(f"Container {model_name} not found.")
        return web.json_response({"error": f"Container {model_name} not found"}, status=404)
    except Exception as e:
        logging.error(f"Error controlling container: {e}")
        return web.json_response({"error": str(e)}, status=500)
        
    # Executes a command to retrieve the IP address of the Raspberry Pi's 'wlan0' interface
    result = subprocess.run(["ip", "addr", "show", "wlan0"], capture_output=True, text=True)
    output = result.stdout
    for line in output.splitlines():
        if "inet " in line:
            ip_address = line.split()[1].split('/')[0] 
            break
    else:
        ip_address = None 
        
    return web.json_response({"ip": ip_address})


def get_containers():
    return client.containers.list(all=True)


async def return_containers(request):
    containers = get_containers()
    
    # Prepare the response data
    container_data = []
    valid_containers = {"tflite", "onnx"}
    for container in containers:
        if container.name in valid_containers:
            container_info = {
                "name": container.name,
                "status": container.status
            }
            container_data.append(container_info)
    return web.json_response(container_data)


async def stop_container(request):
    data = await request.json()
    container_name = data.get("name")
    try:
        container = client.containers.get(container_name)
        if container.status == "running":
            container.stop()
            return web.json_response({"status": "success", "message": f"{container_name} stopped."})
        else:
            return web.json_response({"status": "error", "message": f"{container_name} is not running."})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})


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
    app.router.add_post("/get-containers", return_containers)
    app.router.add_post("/get-ip", return_ip)
    app.router.add_post("/stop-container", stop_container)
    logging.info(f"======== Running on http://{args.host}:{args.port} ========")
    web.run_app(app, host=args.host, port=args.port)
