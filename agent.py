import asyncio
import json
import logging
import os
import ffmpeg
import torch
from io import BytesIO
from PIL import Image
from collections import defaultdict
from transformers import pipeline
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.media import MediaStreamTrack
import google.generativeai as genai
import cv2
import argparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agent")

# Load environment variables
gemini_api_key = os.environ.get("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")

# Setup image captioning model
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device {device}")
image_to_text = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base", device=0 if device == "cuda" else -1)

# Initialize the Gemini model
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel('gemini-pro-vision')

def load_agent_personalities():
    try:
        with open("agent_personalities.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("agent_personalities.json not found.")
        exit(1)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in agent_personalities.json.")
        exit(1)

agent_personalities = load_agent_personalities()

async def get_response_from_gemini(prompt, image_bytes):
    try:
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = await gemini_model.generate_content([prompt, image_part])

        if response and response.text:
            return response.text
        else:
            return "Gemini API returned an empty response."
    except Exception as e:
        logger.error(f"Error using Gemini: {e}")
        return "Error processing with Gemini API."

async def process_video_frame(frame, width, height, agent_type):
    try:
        # Convert raw frame to JPEG
        process = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}')
            .output('pipe:', format='image2', vframes=1, vcodec='mjpeg')
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )
        out, err = await process.communicate(input=frame)

        # Process the image
        image = Image.open(BytesIO(out))
        caption = image_to_text(image)[0]['generated_text']
        logger.info(f"Generated Caption: {caption}")

        # Convert image to bytes for Gemini
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()

        # LLM call
        prompt = f"You are an observer for a live video feed. Describe what is happening. Context is in the caption: {caption}."
        response = await get_response_from_gemini(prompt, image_bytes)
        logger.info(f"LLM Response: {response}")

        # Agent formatting
        agent_data = agent_personalities.get(agent_type)
        if agent_data:
           message = f"--- Agent: {agent_type} Report ---\nPersonality: {agent_data['personality']}\nFocus: {agent_data['focus']}\nAnalysis: {response}\n"
           logger.info(message)
        else:
           logger.info(response)

    except Exception as e:
       logger.error(f"Error Processing Frame: {e}")

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, agent_type):
        super().__init__()
        self.track = track
        self.agent_type = agent_type

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_rgb()
        width, height = img.width, img.height
        frame_bytes = img.to_ndarray(format="rgb24")

        # Process frame asynchronously
        asyncio.create_task(process_video_frame(frame_bytes, width, height, self.agent_type))
        return frame

# Global variables to track PeerConnection and agent_type
active_pc = None
agent_type = None

async def handle_webrtc_offer(offer_sdp, offer_type="offer", ice_candidates=None):
    """
    Handle a WebRTC offer, create a PeerConnection, process tracks, and return SDP answer.
    """
    global active_pc, agent_type
    ice_candidates = ice_candidates or []

    pc = RTCPeerConnection()
    active_pc = pc

    @pc.on("track")
    def on_track(track):
        logger.info(f"Received track: {track.kind}")
        if track.kind == 'video':
            local_track = VideoTransformTrack(track, agent_type)
            pc.addTrack(local_track)
        else:
            logger.info(f"Received non-video track: {track.kind}")

    # Set remote description from offer
    await pc.setRemoteDescription(RTCSessionDescription(sdp=offer_sdp, type=offer_type))

    # Add ICE candidates
    for c in ice_candidates:
        candidate = c.get("candidate")
        sdpMid = c.get("sdpMid")
        sdpMLineIndex = c.get("sdpMLineIndex")
        if candidate:
            await pc.addIceCandidate(RTCIceCandidate(candidate, sdpMid, sdpMLineIndex))

    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    }

async def add_ice_candidate(candidate, sdpMid, sdpMLineIndex):
    global active_pc
    if active_pc is None:
        logger.error("No active peer connection to add ICE candidate to.")
        return
    await active_pc.addIceCandidate(RTCIceCandidate(candidate, sdpMid, sdpMLineIndex))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run an agent with a specific type.")
    parser.add_argument('--agent_type', type=str, required=True, help='The type of agent to run.')
    args = parser.parse_args()

    if args.agent_type not in agent_personalities:
        logger.error(f"Invalid agent type: {args.agent_type}")
        exit(1)

    agent_type = args.agent_type
    logger.info(f"Agent {agent_type} loaded and ready.")
    # Keep running
    asyncio.get_event_loop().run_forever()
