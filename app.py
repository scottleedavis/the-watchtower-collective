import asyncio
import logging
import os
import ffmpeg
from datetime import datetime
from collections import defaultdict

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from flask import Flask, render_template
from flask_socketio import SocketIO

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
video_track = None

RTMP_PORT = 1935

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
      
async def handle_rtmp_connection(reader, writer):
    global video_track
    
    print(f"Got rtmp connection!")
    
    try:
        handshake_c0c1 = await reader.readexactly(1537)  # Receive 1537 bytes handshake C0+C1
        
        handshake_s0s1s2 = b'\x03' + handshake_c0c1[1:1537] # Respond with S0, S1, S2
        writer.write(handshake_s0s1s2)
        await writer.drain()
        
        handshake_c2 = await reader.readexactly(1536) # read client C2
        
        print(f"Starting RTMP Stream Reading")

        frames = []
        while True:
            try:
                # Read chunk header (1 byte)
                header = await reader.readexactly(1)
                if not header:
                    break
                
                # Extract the channel ID
                channel_id = ord(header) & 0x3F
                
                # Read the basic header
                basic_header_bytes = 1;
                if (ord(header) & 0x3F) == 0:
                    basic_header_bytes = 2;
                    basic_header = await reader.readexactly(1);
                elif (ord(header) & 0x3F) == 1:
                    basic_header_bytes = 3;
                    basic_header = await reader.readexactly(2);
                
                # Read the chunk message header
                message_header = await reader.readexactly(3)
                
                # Extract the length
                length = (ord(message_header[0]) << 16) + (ord(message_header[1]) << 8) + ord(message_header[2])
                                
                # Read the message data
                data = await reader.readexactly(length)

                if data:
                        process = (
                        ffmpeg
                            .input('pipe:', format='flv')
                            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                            .run_async(pipe_stdin=True, pipe_stdout=True)
                        )
                        out, err = await process.communicate(input=data)
                        if out:
                            print(f"Got frame! Size: {len(out)}")
                            frames.append(out)
                        else:
                            print(f"Error processing frame: {err}")
                            
                else:
                    break
            except Exception as e:
                print(f"Error receiving RTMP Data: {e}")
                break
                
        video_track = MediaTrack(frames)
        print(f"Finished RTMP Stream for connection")


    except Exception as e:
         print(f"Error handling RTMP connection: {e}")
    finally:
        writer.close()

async def rtmp_server(host="0.0.0.0", port=RTMP_PORT):
    server = await asyncio.start_server(handle_rtmp_connection, host, port)
    print(f"RTMP server started on {host}:{port}")
    async with server:
       await server.serve_forever()
    print(f"Rtmp server stopped")

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
   # Start the background task
    await rtmp_server()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    asyncio.run(start_server())