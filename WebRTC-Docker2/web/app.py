from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import docker

app = Flask(__name__)
socketio = SocketIO(app)
client = docker.from_env()

@socketio.on('start_container')
def start_container(data):
    container_id = data['container_id']
    container = client.containers.get(container_id)
    container.start()
    emit('container_status', {'message': 'Container started successfully'})

@socketio.on('stop_container')
def stop_container(data):
    container_id = data['container_id']
    container = client.containers.get(container_id)
    container.stop()
    emit('container_status', {'message': 'Container stopped successfully'})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
