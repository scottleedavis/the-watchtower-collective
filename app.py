import eventlet
eventlet.monkey_patch()

import logging
import os
from datetime import datetime
from collections import defaultdict

from flask import Flask, render_template, request
from flask_socketio import SocketIO
from rtmplite3.rtmp import FlashServer, Event
import rtmplite3.multitask as multitask

# Environment variable for Flask if needed
os.environ['FLASK_APP'] = 'app.py'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("server")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Using eventlet for SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

pcs = defaultdict(list)
sid_to_pc = {}
RTMP_PORT = 1935

def timestamp_filename(prefix, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def handle_rtmp_stream(stream):
    print("RTMP stream started")
    try:
        for data in stream:
            # Process RTMP data as needed.
            pass
    except Exception as e:
        print(f"Error receiving RTMP Data: {e}")
    print("RTMP stream ended")

def start_rtmp_server():
    agent = FlashServer()
    agent.root = "./"
    agent.start("0.0.0.0", RTMP_PORT)

    @Event.onPublish
    def on_publish_handler(client, stream):
        handle_rtmp_stream(stream)

    print(f"RTMP server started on port {RTMP_PORT}")

    # Keep multitask.run() active indefinitely
    def dummy_task():
        while True:
            yield multitask.sleep(1)

    multitask.add(dummy_task())
    multitask.run()
    agent.stop()

@app.route('/')
def index():
    # Ensure you have a templates/index.html
    return render_template('index.html')

@socketio.on('connect')
def connect():
    print('Client connected')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')
    for room in list(pcs):
        if request.sid in pcs[room]:
            pcs[room].remove(request.sid)
    if request.sid in sid_to_pc:
        sid_to_pc.pop(request.sid, None)
    print(f"Clients: {pcs}")

@socketio.on('offer')
def handle_offer(offer):
    room = "main"
    pcs[room].append(request.sid)

    # Send a dummy answer since we're not integrating real WebRTC here.
    fake_answer = {
        "type": "answer",
        "sdp": "v=0\r\n..."
    }
    socketio.emit("answer", fake_answer, to=request.sid)
    print("Sent dummy answer")

@socketio.on('ice-candidate')
def handle_ice_candidate(candidate):
    print(f"Received ICE candidate: {candidate}")

if __name__ == '__main__':
    # Start RTMP server in background green thread
    eventlet.spawn_n(start_rtmp_server)

    # Run Flask-SocketIO server without debug mode or reloader
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)
