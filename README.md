# Educational Live Streaming Platform

A comprehensive educational live streaming platform designed for remote and hybrid learning environments, featuring real-time video streaming, interactive dashboards, and extensive monitoring capabilities.

## Architecture Overview

### Server Components

1. **FastAPI Backend**: RESTful API for authentication, classroom management, and stream coordination
2. **NGINX RTMP Server**: Handles incoming RTMP streams and HLS conversion
3. **FFmpeg Workers**: Process video streams and handle format conversion
4. **React Dashboard**: Modern web interface for stream management and monitoring
5. **Monitoring Stack**: Comprehensive system monitoring with Prometheus and Grafana

### Classroom Components

1. **Classroom Agent**: Manages video capture and streaming
2. **FFmpeg Client**: Handles local video encoding and RTMP streaming

## Quick Start

### Server Deployment

```bash
# Single command setup
sudo ./setup_server.sh
```

### Classroom Setup

```bash
# Single command setup
sudo ./setup_classroom.sh
```

## System Requirements

### Server Requirements

- Ubuntu 20.04 or later
- Minimum 4GB RAM
- 50GB storage
- Open ports:
  - 1935 (RTMP Ingest)
  - 8080 (HLS Streaming)
  - 5000 (FastAPI)
  - 3000 (Dashboard)
  - 9090 (Prometheus)
  - 3001 (Grafana)

### Classroom Requirements

- Ubuntu 20.04 or later
- USB webcam or capture device
- Stable network connection
- FFmpeg and Python 3.8+

## Detailed Setup

### Server Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/streaming-platform.git
cd streaming-platform
```

2. Run the setup script:

```bash
sudo ./setup_server.sh
```

The setup script will:

- Install and configure UFW firewall
- Install Docker and Docker Compose
- Set up all required services
- Configure network interfaces
- Start the monitoring stack

### Classroom Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/streaming-platform.git
cd streaming-platform
```

2. Run the setup script:

```bash
sudo ./setup_classroom.sh
```

The setup script will:

- Validate server connectivity
- Install required dependencies
- Configure video devices
- Set up the streaming agent
- Verify the connection

## Configuration

### Server Configuration

- `.env`: Environment variables

  ```ini
  POSTGRES_USER=streaming_user
  POSTGRES_PASSWORD=secure_password
  POSTGRES_DB=streaming_platform
  REDIS_HOST=redis
  SECRET_KEY=your_secret_key
  ```

- `docker-compose.yml`: Service configuration

  ```yaml
  # Configure service resources
  api:
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: 1G
  ```

- `nginx.conf`: NGINX settings
  ```nginx
  # Configure HLS segment duration
  hls_fragment 4s;
  hls_playlist_length 60s;
  ```

### Classroom Configuration

- `.env`: Device settings
  ```ini
  VIDEO_DEVICE=/dev/video0
  AUDIO_DEVICE=hw:0,0
  STREAM_QUALITY=high
  ```

## Troubleshooting Guide

### Common Issues

1. **RTMP Connection Fails**

   ```bash
   # Check NGINX RTMP port
   netstat -an | grep 1935
   # Check NGINX logs
   docker-compose logs nginx
   ```

2. **Video Device Issues**

   ```bash
   # List video devices
   v4l2-ctl --list-devices
   # Test video capture
   ffmpeg -f v4l2 -i /dev/video0 -t 5 test.mp4
   ```

3. **Docker Issues**

   ```bash
   # Restart services
   docker-compose down
   docker-compose up -d
   # Check logs
   docker-compose logs --tail=100
   ```

4. **Dashboard Access**
   ```bash
   # Check if service is running
   docker-compose ps dashboard
   # Check logs
   docker-compose logs dashboard
   ```

### Monitoring

1. **Access Points**

   - Dashboard: `http://server-ip:3000`
   - API Docs: `http://server-ip:5000/docs`
   - Grafana: `http://server-ip:3001`
   - Prometheus: `http://server-ip:9090`

2. **Key Metrics**

   - Stream Health
   - Network Bandwidth
   - System Resources
   - Error Rates

3. **Log Access**
   ```bash
   # API logs
   docker-compose logs api
   # NGINX logs
   docker-compose logs nginx
   # Classroom agent logs
   journalctl -u classroom-agent
   ```

## Security Best Practices

1. **Network Security**

   - Keep firewall rules minimal
   - Use SSL/TLS in production
   - Regularly update passwords

2. **System Security**

   - Regular security updates
   - Monitor system logs
   - Implement authentication

3. **Data Security**
   - Regular backups
   - Encrypted storage
   - Access control

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

For issues and support:

1. Check the troubleshooting guide
2. Search existing issues
3. Create a new issue with:
   - System details
   - Error logs
   - Steps to reproduce
