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

# Install and configure UFW
print_status "Setting up firewall rules..."
if ! command -v ufw &> /dev/null; then
    print_status "Installing UFW firewall..."
    apt-get update
    apt-get install -y ufw
fi

# Configure firewall rules
ufw default deny incoming
ufw default allow outgoing

# Allow necessary ports
print_status "Configuring firewall rules..."
ufw allow ssh
ufw allow 1935/tcp  # RTMP Ingest
ufw allow 8080/tcp  # HLS Streaming
ufw allow 5000/tcp  # FastAPI API
ufw allow 3000/tcp  # Frontend Dashboard & Grafana
ufw allow 9090/tcp  # Prometheus

# Enable UFW
print_status "Enabling UFW..."
ufw --force enable
print_success "Firewall configured successfully"

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

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    
    # Generate random password and secret key
    POSTGRES_PASSWORD=$(openssl rand -base64 16)
    SECRET_KEY=$(openssl rand -base64 32)
    
    cat > .env << EOF
POSTGRES_USER=streaming_user
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=streaming_platform
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
SECRET_KEY=$SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=30
HLS_OUTPUT_DIR=/var/www/streaming/hls
EOF
    
    print_success "Created .env file with secure random credentials"
else
    print_status ".env file already exists, skipping creation"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p /var/www/streaming/hls
chmod -R 777 /var/www/streaming/hls

# Pull and start containers
print_status "Starting containers..."
docker-compose pull
docker-compose up -d

if [ $? -eq 0 ]; then
    print_success "Server setup completed successfully!"
    echo -e "\nServer is now running at http://localhost:8000"
    echo "API documentation is available at http://localhost:8000/docs"
    echo -e "\nMake sure to:"
    echo "1. Update your firewall rules to allow ports 80 and 8000"
    echo "2. Set up SSL/TLS for production use"
    echo "3. Secure your PostgreSQL and Redis instances"
else
    print_error "Failed to start containers"
    exit 1
fi
