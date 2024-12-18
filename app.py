import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaRecorder
from flask import Flask, render_template
from flask_socketio import SocketIO
from uuid import uuid4
from collections import defaultdict
import os
import aiohttp
import logging
from datetime import datetime

# Set the FLASK_APP environment variable
os.environ['FLASK_APP'] = 'app.py'

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("server")


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Keep track of client connections and peer connections
pcs = defaultdict(list)

# Keep track of rtmp stream
rtmp_stream_url = None
rtmp_process = None
video_track = None

async def broadcast(room, event, data):
    for sid in pcs[room]:
        await socketio.emit(event, data, to=sid)

# Helper function to create a timestamped filename
def timestamp_filename(prefix, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

class MediaTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, frames):
        super().__init__()
        self.frames = frames
        self.frame_counter = 0

    async def recv(self):
        # Get the frame
        if self.frame_counter < len(self.frames):
          frame = self.frames[self.frame_counter]
          self.frame_counter += 1
          return frame
        return None


async def stream_from_rtmp():
  global video_track, rtmp_process
  
  # Create the rtmp link for this instance.
  rtmp_stream_url = 'rtmp://localhost:1935/live/stream' # Using an rtmp endpoint on the same server
  print(f"Starting RTMP Server with Stream URL: {rtmp_stream_url}")
  
  # Open an ffmpeg process to read the rtmp, and convert the frames for use with WebRTC.
  rtmp_process = (
    ffmpeg.input(rtmp_stream_url)
    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    .run_async(pipe_stdout=True)
  )

  frames = []
  while True:
      try:
          frame = await rtmp_process.stdout.read(1920 * 1080 * 3) #Read one frame of 1920x1080, 3 bytes per pixel
          if frame:
            print(f"Got Frame! Size: {len(frame)}")
            frames.append(frame)
          else:
            break
          
      except Exception as e:
         print(f"Error reading frame from ffmpeg: {e}")
         break

  video_track = MediaTrack(frames)
  print("Read all the frames, stopping streaming from RTMP")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
  print('Client connected')

@socketio.on('disconnect')
def disconnect():
  print('Client disconnected')
  #remove connections
  for room in list(pcs):
    if request.sid in pcs[room]:
      pcs[room].remove(request.sid)
  print(f"Clients: {pcs}")

@socketio.on('offer')
async def handle_offer(offer):
  room = "main"
  pc = RTCPeerConnection()
  
  pcs[room].append(request.sid)

  @pc.on("icecandidate")
  async def on_icecandidate(candidate):
    if candidate:
      print("sent ice", candidate.to_json())
      await socketio.emit("ice-candidate", candidate.to_json(), to=request.sid)

  @pc.on("track")
  async def on_track(track):
    print("Got track!", track)
    await broadcast(room, 'track', {'kind':track.kind, 'label':track.label})

    @track.on("ended")
    async def on_ended():
      print("Track ended")
      await broadcast(room, 'track_ended', { 'label':track.label })


  await pc.setRemoteDescription(RTCSessionDescription(sdp=offer['sdp'], type=offer['type']))
  if video_track:
    pc.addTrack(video_track)

  answer = await pc.createAnswer()
  await pc.setLocalDescription(answer)
  
  await socketio.emit("answer", answer.to_json(), to=request.sid)
  print(f"Sent Answer!: {answer.to_json()}")


@socketio.on('ice-candidate')
async def handle_ice_candidate(candidate):
  pc = None
  for room in pcs:
    for sid in pcs[room]:
        if sid == request.sid:
          pc = list(filter(lambda p: p.sid == sid, pcs[room]))[0].peer
          break
  if pc is None:
    print("No peer connection")
    return

  try:
      await pc.addIceCandidate(RTCIceCandidate(candidate))
      print(f'Got ICE: {candidate}')
  except Exception as e:
      print(f'ERROR adding ICE: {e}')



async def start_server():
  global rtmp_process
  # Start the background task
  asyncio.create_task(stream_from_rtmp())
  socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
  if rtmp_process:
      rtmp_process.terminate()
      await rtmp_process.wait()

if __name__ == '__main__':
    asyncio.run(start_server())
