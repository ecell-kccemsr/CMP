# Classroom Management Platform - Setup Guide

## Prerequisites

### Server Requirements
- Ubuntu 20.04 or later
- Minimum 4GB RAM
- 50GB storage
- Open ports (will be configured automatically):
  - 1935 (RTMP)
  - 8080 (HLS)
  - 5000 (FastAPI)
  - 3000 (Dashboard)
  - 9090 (Prometheus)
  - 3001 (Grafana)

### Classroom PC Requirements
- Ubuntu 20.04 or later
- USB webcam or IP camera
- Microphone
- Stable network connection

## Server Setup Guide

1. **System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install git -y
```

2. **Download the Project**
```bash
# Clone the repository
git clone https://github.com/ecell-kccemsr/CMP.git
cd CMP
```

3. **Environment Setup**
```bash
# Copy example environment file
cp example.env .env

# Edit the .env file with your settings
nano .env
```

Required .env changes:
- Change `POSTGRES_PASSWORD`
- Change `SECRET_KEY`
- Change `GRAFANA_ADMIN_PASSWORD`
- Change `ELASTIC_PASSWORD`

4. **Run Setup Script**
```bash
# Make script executable
chmod +x setup_server.sh

# Run setup script
sudo ./setup_server.sh
```

5. **Verify Installation**
- Dashboard: http://your-server-ip:3000
- API Docs: http://your-server-ip:8000/docs
- Grafana: http://your-server-ip:3001
- Prometheus: http://your-server-ip:9090

## Classroom PC Setup Guide

1. **System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install git -y
```

2. **Download the Project**
```bash
# Clone the repository
git clone https://github.com/ecell-kccemsr/CMP.git
cd CMP
```

3. **Check Camera and Audio Devices**
```bash
# List video devices
v4l2-ctl --list-devices

# List audio devices
arecord -l
```

4. **Environment Setup**
```bash
# Copy example environment file
cp example.env .env

# Edit the .env file with your settings
nano .env
```

Required .env changes for classroom:
- Set `VIDEO_DEVICE` (e.g., /dev/video0)
- Set `AUDIO_DEVICE` (e.g., hw:0,0)
- Set `SERVER_RTMP_ADDRESS` to your server's IP
- Set `STREAM_KEY` (get this from the dashboard)

5. **Run Setup Script**
```bash
# Make script executable
chmod +x setup_classroom.sh

# Run setup script
sudo ./setup_classroom.sh
```

## Troubleshooting

### Common Server Issues

1. **Port Access Issues**
```bash
# Check if ports are open
sudo netstat -tulpn | grep -E ':(1935|8080|5000|3000|9090|3001)'

# Check firewall status
sudo ufw status
```

2. **Docker Issues**
```bash
# Check docker service
sudo systemctl status docker

# Check running containers
docker ps

# View container logs
docker-compose logs
```

3. **Stream Issues**
```bash
# Check NGINX logs
docker-compose logs nginx

# Check worker logs
docker-compose logs worker
```

### Common Classroom Issues

1. **Camera Issues**
```bash
# Test camera
ffmpeg -f v4l2 -i /dev/video0 -t 5 test.mp4

# Check permissions
ls -l /dev/video*
```

2. **Audio Issues**
```bash
# Test audio recording
arecord -d 5 -f cd test.wav

# Check audio levels
alsamixer
```

3. **Streaming Issues**
```bash
# Check agent logs
docker-compose -f docker-compose.agent.yml logs

# Test network connection
ping your-server-ip
```

## Support

If you encounter any issues:
1. Check the troubleshooting guide above
2. Check the logs using `docker-compose logs`
3. Create an issue on GitHub with:
   - Error messages
   - System details
   - Steps to reproduce

## Security Notes

1. Always change default passwords in .env
2. Keep your system updated
3. Monitor logs regularly
4. Use strong passwords
5. Backup your data regularly

## Maintenance

### Server Maintenance
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Check logs
docker-compose logs --tail=100

# Backup database
docker-compose exec db pg_dump -U your_user your_db > backup.sql
```

### Classroom Maintenance
```bash
# Update agent
docker-compose -f docker-compose.agent.yml pull
docker-compose -f docker-compose.agent.yml up -d

# Check agent logs
docker-compose -f docker-compose.agent.yml logs --tail=100
```
