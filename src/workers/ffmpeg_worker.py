import json
import subprocess
import time
import os
from redis import Redis
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Stream configuration
HLS_OUTPUT_DIR = os.getenv("HLS_OUTPUT_DIR", "/var/www/streaming/hls")
DVR_WINDOW_SIZE = 120  # 2 minutes in seconds

class FFmpegWorker:
    def __init__(self):
        self.redis_client = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        self.processes = {}

    def process_stream(self, rtmp_key: str, stream_id: str):
        input_url = f"rtmp://localhost/live/{rtmp_key}"
        output_path = f"{HLS_OUTPUT_DIR}/{stream_id}"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)

        # FFmpeg command for HLS output with DVR window
        command = [
            "ffmpeg",
            "-i", input_url,
            "-c:v", "copy",              # Copy video codec
            "-c:a", "aac",              # Convert audio to AAC
            "-b:a", "128k",             # Audio bitrate
            "-f", "hls",                # HLS output format
            "-hls_time", "2",           # Segment duration
            "-hls_list_size", str(DVR_WINDOW_SIZE // 2),  # Number of segments to keep
            "-hls_flags", "delete_segments",  # Delete old segments
            "-hls_segment_filename", f"{output_path}/%03d.ts",  # Segment filename pattern
            f"{output_path}/playlist.m3u8"  # Playlist file
        ]

        try:
            # Start FFmpeg process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes[stream_id] = process
            
            # Update stream status in Redis
            self.redis_client.publish(
                "stream_status_updates",
                json.dumps({
                    "stream_id": stream_id,
                    "status": "active",
                    "timestamp": datetime.utcnow().isoformat()
                })
            )
            
            return True
        except Exception as e:
            logger.error(f"Error starting stream {stream_id}: {str(e)}")
            return False

    def stop_stream(self, stream_id: str):
        if stream_id in self.processes:
            process = self.processes[stream_id]
            process.terminate()
            process.wait()
            del self.processes[stream_id]
            
            # Update stream status in Redis
            self.redis_client.publish(
                "stream_status_updates",
                json.dumps({
                    "stream_id": stream_id,
                    "status": "stopped",
                    "timestamp": datetime.utcnow().isoformat()
                })
            )

    def run(self):
        logger.info("FFmpeg worker started")
        while True:
            try:
                # Check for new stream requests in Redis queue
                stream_request = self.redis_client.rpop("stream_requests")
                if stream_request:
                    request_data = json.loads(stream_request)
                    rtmp_key = request_data.get("rtmp_key")
                    stream_id = request_data.get("stream_id")
                    
                    if rtmp_key and stream_id:
                        self.process_stream(rtmp_key, stream_id)
                
                # Check for stop requests
                stop_request = self.redis_client.rpop("stream_stop_requests")
                if stop_request:
                    request_data = json.loads(stop_request)
                    stream_id = request_data.get("stream_id")
                    if stream_id:
                        self.stop_stream(stream_id)
                
                time.sleep(1)  # Prevent tight loop
                
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    worker = FFmpegWorker()
    worker.run()
