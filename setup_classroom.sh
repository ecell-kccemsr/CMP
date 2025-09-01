#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${YELLOW}[*] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[+] $1${NC}"
}

print_error() {
    echo -e "${RED}[-] $1${NC}"
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

# Check for Docker
print_status "Checking for Docker installation..."
if ! command -v docker &> /dev/null; then
    print_status "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    if [ $? -eq 0 ]; then
        print_success "Docker installed successfully"
    else
        print_error "Failed to install Docker"
        exit 1
    fi
else
    print_success "Docker is already installed"
fi

# Check for Docker Compose
print_status "Checking for Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_status "Docker Compose not found. Installing Docker Compose..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d '"' -f 4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    if [ $? -eq 0 ]; then
        print_success "Docker Compose installed successfully"
    else
        print_error "Failed to install Docker Compose"
        exit 1
    fi
else
    print_success "Docker Compose is already installed"
fi

# Check for video and audio devices
print_status "Checking for video and audio devices..."
if [ ! -e /dev/video0 ]; then
    print_error "No video device found at /dev/video0"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Setting up classroom configuration..."
    
    # Function to validate IP address format
    validate_ip() {
        local ip=$1
        if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
            for i in {1..4}; do
                if [ $(echo "$ip" | cut -d. -f$i) -gt 255 ]; then
                    return 1
                fi
            done
            return 0
        else
            return 1
        fi
    }

    # Function to check server connectivity
    check_server() {
        local ip=$1
        print_status "Testing connection to server at $ip..."
        
        # Check RTMP port
        nc -zv $ip 1935 &>/dev/null
        if [ $? -eq 0 ]; then
            print_success "Successfully connected to RTMP port (1935)"
            return 0
        else
            print_error "Could not connect to RTMP port (1935)"
            return 1
        fi
    }

    # Get server IP with validation
    while true; do
        read -p "Enter the streaming server IP address: " SERVER_IP
        if validate_ip "$SERVER_IP"; then
            if check_server "$SERVER_IP"; then
                SERVER_RTMP_ADDRESS="rtmp://$SERVER_IP/live"
                break
            else
                print_error "Could not connect to server. Please verify the IP and ensure the server is running."
                read -p "Would you like to try again? [Y/n]: " retry
                if [[ $retry =~ ^[Nn]$ ]]; then
                    print_error "Setup cancelled"
                    exit 1
                fi
            fi
        else
            print_error "Invalid IP address format. Please enter a valid IPv4 address."
        fi
    done
    
    # Prompt for stream key
    while true; do
        read -p "Enter the stream key provided by your administrator: " STREAM_KEY
        if [[ -n "$STREAM_KEY" ]]; then
            break
        else
            print_error "Stream key cannot be empty"
        fi
    done
    
    # Detect video device
    VIDEO_DEVICE="/dev/video0"
    if [ ! -e "$VIDEO_DEVICE" ]; then
        read -p "Enter the video device path: " VIDEO_DEVICE
    fi
    
    # Detect audio device
    AUDIO_DEVICE="/dev/audio1"
    if [ ! -e "$AUDIO_DEVICE" ]; then
        read -p "Enter the audio device path: " AUDIO_DEVICE
    fi
    
    cat > .env << EOF
SERVER_RTMP_ADDRESS=$SERVER_RTMP_ADDRESS
STREAM_KEY=$STREAM_KEY
VIDEO_DEVICE=$VIDEO_DEVICE
AUDIO_DEVICE=$AUDIO_DEVICE
EOF
    
    print_success "Created .env file with configuration"
else
    print_status ".env file already exists, skipping creation"
fi

# Start the classroom agent
print_status "Starting classroom agent..."
docker-compose -f docker-compose.agent.yml pull
docker-compose -f docker-compose.agent.yml up -d

if [ $? -eq 0 ]; then
    print_success "Classroom agent setup completed successfully!"
    echo -e "\nAgent is now running and streaming to: $SERVER_RTMP_ADDRESS"
    echo -e "\nTo view logs, run: docker-compose -f docker-compose.agent.yml logs -f"
    echo -e "To stop the agent, run: docker-compose -f docker-compose.agent.yml down"
else
    print_error "Failed to start classroom agent"
    exit 1
fi
