import logging
from rtmp import *

# Config
LogLevel = logging.INFO

# Configure logging level and format
logging.basicConfig(level=LogLevel, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_video(payload):
    print("video...")#payload)

def process_audio(payload):
    print("audio...")#payload)

rtmp_server = RTMPServer(video=process_video,audio=process_audio)
asyncio.run(rtmp_server.start_server())
