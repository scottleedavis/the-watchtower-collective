import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from aiortc.contrib.media import MediaStreamTrack
import socketio
import logging
import os
import ffmpeg
from PIL import Image
from io import BytesIO
from transformers import pipeline
import torch
from collections import defaultdict
import cv2
import google.generativeai as genai
import argparse


# Set the API key as an environment variable
gemini_api_key = os.environ.get("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agent")

# Set the namespace
namespace = "/agent"

# Setup our connection
sio = socketio.AsyncClient(logger=True, engineio_logger=True)

# Keep track of the connections
pcs = defaultdict(list)

async def broadcast(room, event, data):
    for sid in pcs[room]:
        await sio.emit(event, data, to=sid)


#Setup the image captioning models:
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device {device}")
image_to_text = pipeline("image-to-text",model="Salesforce/blip-image-captioning-base", device=device)


# Initialize the Gemini model
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-pro-vision')

# Install: pip install aiortc, ffmpeg-python, transformers, accelerate, torch, opencv-python, google-generativeai
import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, MediaStreamTrack
from aiortc.contrib.media import MediaStreamTrack
import socketio
import logging
import os
import ffmpeg
from PIL import Image
from io import BytesIO
from transformers import pipeline
import torch
from collections import defaultdict
import cv2
import google.generativeai as genai
import argparse


# Set the API key as an environment variable
gemini_api_key = os.environ.get("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agent")

# Set the namespace
namespace = "/agent"

# Setup our connection
sio = socketio.AsyncClient(logger=True, engineio_logger=True)

# Keep track of the connections
pcs = defaultdict(list)

async def broadcast(room, event, data):
    for sid in pcs[room]:
        await sio.emit(event, data, to=sid)


#Setup the image captioning models:
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device {device}")
image_to_text = pipeline("image-to-text",model="Salesforce/blip-image-captioning-base", device=device)


# Initialize the Gemini model
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-pro-vision')

# Model setup for the LLM.
async def get_response_from_gemini(prompt, image_bytes):
    try:
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = await gemini_model.generate_content([prompt, image_part])

        if response and response.text:
             return response.text
        else:
            return "Gemini API returned an empty response."
    except Exception as e:
        print(f"Error using Gemini: {e}")
        return "Error processing with Gemini API."


# Load agent personalities from the JSON file
def load_agent_personalities():
    try:
        with open("agent_personalities.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: agent_personalities.json not found.")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in agent_personalities.json.")
        exit(1)

agent_personalities = load_agent_personalities()

# Model setup for the LLM.
async def get_response_from_gemini(prompt, image_bytes):
    try:
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = await gemini_model.generate_content([prompt, image_part])

        if response and response.text:
             return response.text
        else:
            return "Gemini API returned an empty response."
    except Exception as e:
        print(f"Error using Gemini: {e}")
        return "Error processing with Gemini API."

async def process_video_frame(frame, track, agent_type):
    try:
        # 1. Decode
        # print("Processing Frame")
        process = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{track.width}x{track.height}')
            .output('pipe:', format='image2', vframes=1, vcodec='mjpeg')
            .run_async(pipe_stdin=True, pipe_stdout=True)
        )
        out, err = await process.communicate(input=frame)

        # 2. Image Processing
        image = Image.open(BytesIO(out))
        
        # 3. Image analysis via captioning,
        caption = image_to_text(image)[0]['generated_text']
        print(f"Generated Caption: {caption}")
        
        #Convert the image to bytes for Gemini
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()

        # 4. Send to LLM, and then broadcast the result
        prompt = f"You are an observer for a live video feed. Describe what is happening. Context is provided in the generated caption. Caption: {caption}."
        response = await get_response_from_gemini(prompt, image_bytes)
        print(f"LLM Response: {response}")
        
        #Broadcast results with the correct metadata for the agent type.
        agent_data = agent_personalities.get(agent_type)
        if agent_data:
           message = f"--- Agent: {agent_type} Report ---\nPersonality: {agent_data['personality']}\nFocus: {agent_data['focus']}\nAnalysis: {response}\n"
           await broadcast("main", 'message', {'message':message, 'sender':agent_type})
        else:
           await broadcast("main", 'message', {'message':response, 'sender':track.id})

    except Exception as e:
       print(f"Error Processing Frame: {e}")


@sio.on('connect', namespace=namespace)
async def connect():
    logger.info('Connected to server')

@sio.on('disconnect', namespace=namespace)
async def disconnect():
    logger.info('Disconnected from server')
    for room in list(pcs):
      if sio.sid in pcs[room]:
        pcs[room].remove(sio.sid)

@sio.on('track', namespace=namespace)
async def handle_track(data):
    room = "main"
    track_id = data["label"]
    print("Got track!", data)

    pc = RTCPeerConnection()
    pcs[room].append(pc)

    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
       if candidate:
           await sio.emit("ice-candidate", candidate.to_json(), to=sio.sid, namespace=namespace)

    @pc.on("track")
    async def on_track(track):
       print("Got track in peer connection!", track)
       if track.kind == 'video':
            @track.on("frame")
            async def on_frame(frame):
              await process_video_frame(frame, track, args.agent_type)

    await pc.addTransceiver(kind=data['kind'], direction='recvonly')

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    await sio.emit('offer', offer.to_json(), to=sio.sid, namespace=namespace)
    print(f"Sent Answer to client!: {offer.to_json()}")
    

@sio.on('answer', namespace=namespace)
async def handle_answer(answer):
    pc = None
    for room in pcs:
       for pc_connection in pcs[room]:
           if pc_connection.connection_id == request.sid:
                pc = pc_connection
                break
    if pc is None:
        print("no peer connection")
        return

    await pc.setRemoteDescription(RTCSessionDescription(sdp=answer['sdp'], type=answer['type']))


@sio.on('ice-candidate', namespace=namespace)
async def handle_ice_candidate(candidate):
   pc = None
   for room in pcs:
       for pc_connection in pcs[room]:
           if pc_connection.connection_id == request.sid:
                pc = pc_connection
                break
   if pc is None:
        print("no peer connection")
        return
   try:
      await pc.addIceCandidate(RTCIceCandidate(candidate))
      print(f'Got ICE: {candidate}')
   except Exception as e:
      print(f'Error adding ICE candidate: {e}')



async def start_agent():
    await sio.connect('http://localhost:5000', namespaces=[namespace])
    await sio.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run an agent with a specific type.")
    parser.add_argument('--agent_type', type=str, required=True, help='The type of agent to run.')
    args = parser.parse_args()
    
    if args.agent_type not in agent_personalities:
       print(f"Invalid agent type: {args.agent_type}")
       exit(1)
    
    asyncio.run(start_agent())