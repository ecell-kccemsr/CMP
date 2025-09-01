import os
import time
import subprocess
import logging
from typing import Optional
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingAgent:
    def __init__(self):
        # Load configuration from environment variables
        self.server_rtmp_address = os.getenv("SERVER_RTMP_ADDRESS", "rtmp://localhost/live")
        self.stream_key = os.getenv("STREAM_KEY")
        self.video_device = os.getenv("VIDEO_DEVICE", "/dev/video0")
        self.audio_device = os.getenv("AUDIO_DEVICE", "default")
        self.audio_channels = int(os.getenv("AUDIO_CHANNELS", "2"))
        self.audio_rate = int(os.getenv("AUDIO_RATE", "44100"))
        self.video_input_format = os.getenv("VIDEO_INPUT_FORMAT", "v4l2")
        self.sync_offset = float(os.getenv("SYNC_OFFSET_MS", "0")) / 1000  # Convert ms to seconds
        
        # Streaming process
        self.process: Optional[subprocess.Popen] = None
        self.retry_count = 0
        self.max_retries = 10
        
        # Validate devices
        self._validate_devices()
        
        if not self.stream_key:
            raise ValueError("STREAM_KEY environment variable must be set")

    def _validate_devices(self):
        """Validate video and audio devices"""
        # Check video device
        if not os.path.exists(self.video_device):
            raise ValueError(f"Video device {self.video_device} not found")
            
        # Check audio device using arecord
        try:
            subprocess.run(
                ["arecord", "-L"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError:
            logger.error("ALSA audio subsystem not available")
            raise ValueError("Audio system not properly configured")
            
        # Test audio device
        try:
            subprocess.run(
                ["arecord", "-d", "1", "-f", "cd", "-D", self.audio_device, "/dev/null"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Audio device test failed: {e.stderr.decode()}")
            raise ValueError(f"Audio device {self.audio_device} not working properly")

    def _get_audio_mapping(self) -> str:
        """Get the audio channel mapping configuration"""
        if self.audio_channels == 1:
            return "pan=mono|c0=c0"
        return "anull"  # Pass through for stereo

    def calculate_backoff_time(self) -> float:
        """Calculate exponential backoff time with jitter"""
        base_delay = min(300, 2 ** self.retry_count)  # Cap at 300 seconds
        jitter = random.uniform(0, 0.1 * base_delay)  # 10% jitter
        return base_delay + jitter

    def start_stream(self) -> bool:
        """Start the streaming process using FFmpeg"""
        command = [
            "ffmpeg",
            # Global options
            "-thread_queue_size", "512",  # Increase queue size for inputs
            "-use_wallclock_as_timestamps", "1",  # Use wallclock for sync
            
            # Input options - video
            "-f", self.video_input_format,
            "-i", self.video_device,
            
            # Input options - audio
            "-f", "alsa",
            "-thread_queue_size", "512",
            "-ac", str(self.audio_channels),
            "-ar", str(self.audio_rate),
            "-i", self.audio_device,
            
            # Video encoding
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-b:v", "2500k",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-pix_fmt", "yuv420p",
            "-g", "60",
            "-keyint_min", "60",
            "-sc_threshold", "0",  # Disable scene change detection
            "-filter_complex", "[0:v]format=yuv420p,scale=-2:720[v]",  # Ensure consistent format and resolution
            
            # Audio encoding
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", str(self.audio_rate),
            "-af", self._get_audio_mapping(),
            "-async", "1",  # Audio sync method
            "-vsync", "1",  # Video sync method
            
            # Sync offset if needed
            "-itsoffset", str(self.sync_offset),
            
            # Output mapping
            "-map", "[v]",    # Mapped video
            "-map", "1:a",    # Mapped audio
            
            # Output options
            "-f", "flv",
            "-flvflags", "no_duration_filesize",  # Better live streaming
            f"{self.server_rtmp_address}/{self.stream_key}"
        ]

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("Streaming process started")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming process: {str(e)}")
            return False

    def stop_stream(self):
        """Stop the streaming process"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logger.info("Streaming process stopped")

    def monitor_stream(self):
        """Monitor the streaming process and handle errors"""
        import re
        
        # Patterns to match in FFmpeg output
        sync_pattern = re.compile(r'speed=(\d+\.\d+)x.*drop=(\d+)')
        audio_pattern = re.compile(r'Audio: .* (\d+) Hz')
        
        while True:
            if not self.process or self.process.poll() is not None:
                logger.warning("Stream process ended unexpectedly")
                
                # Calculate backoff time
                backoff_time = self.calculate_backoff_time()
                logger.info(f"Waiting {backoff_time:.2f} seconds before retry")
                time.sleep(backoff_time)
                
                # Increment retry counter
                self.retry_count += 1
                
                if self.retry_count > self.max_retries:
                    logger.error("Maximum retry attempts reached")
                    break
                
                # Attempt to restart the stream
                if self.start_stream():
                    logger.info("Stream restarted successfully")
                    self.retry_count = 0  # Reset retry counter on successful restart
                else:
                    logger.error("Failed to restart stream")
                    continue
            
            # Check process status
            if self.process:
                # Check for process output/errors
                error = self.process.stderr.readline().decode().strip()
                if error:
                    # Check for sync issues
                    sync_match = sync_pattern.search(error)
                    if sync_match:
                        speed, drops = sync_match.groups()
                        if float(speed) < 0.95 or float(speed) > 1.05:
                            logger.warning(f"Stream speed outside normal range: {speed}x")
                        if int(drops) > 0:
                            logger.warning(f"Detected {drops} dropped frames")
                    
                    # Check for audio sample rate mismatches
                    audio_match = audio_pattern.search(error)
                    if audio_match and int(audio_match.group(1)) != self.audio_rate:
                        logger.warning(f"Audio sample rate mismatch: expected {self.audio_rate}Hz")
                    
                    # Log general FFmpeg output
                    if "Non-monotonous DTS" in error or "Timestamps are unset" in error:
                        logger.warning("Detected A/V sync issues")
                    elif "error" in error.lower():
                        logger.error(f"FFmpeg error: {error}")
                    else:
                        logger.debug(f"FFmpeg output: {error}")
            
            time.sleep(1)  # Prevent tight loop

    def run(self):
        """Main run loop"""
        logger.info("Starting classroom streaming agent")
        
        try:
            if self.start_stream():
                self.monitor_stream()
            else:
                logger.error("Failed to start initial stream")
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.stop_stream()
            logger.info("Classroom streaming agent stopped")

if __name__ == "__main__":
    agent = StreamingAgent()
    agent.run()
