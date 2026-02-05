#!/bin/bash

# Solana AI Trader Installation Script
# This script automates the setup process on Linux servers

set -e  # Exit on error

echo "=================================="
echo "Solana AI Trader Installation"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root or with sudo"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    print_error "Cannot detect operating system"
    exit 1
fi

print_success "Detected OS: $OS"

# Install system dependencies
echo ""
echo "Installing system dependencies..."

if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    apt-get update
    apt-get install -y python3.11 python3.11-venv python3-pip git nginx certbot
    print_success "System dependencies installed"

elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
    yum install -y python311 python311-pip git nginx certbot
    print_success "System dependencies installed"

else
    print_warning "Unsupported OS: $OS"
    print_warning "Please install Python 3.11, pip, git, and nginx manually"
fi

# Create dedicated user
echo ""
echo "Creating dedicated user..."

if ! id "trader" &>/dev/null; then
    useradd -m -s /bin/bash trader
    print_success "User 'trader' created"
else
    print_warning "User 'trader' already exists"
fi

# Set installation directory
INSTALL_DIR="/home/trader/solana-ai-trader"

# Clone or update repository
echo ""
echo "Setting up application files..."

if [ -d "$INSTALL_DIR" ]; then
    print_warning "Directory already exists, updating..."
    cd $INSTALL_DIR
    # git pull
else
    mkdir -p $INSTALL_DIR
    # git clone <repository_url> $INSTALL_DIR
    chown -R trader:trader $INSTALL_DIR
    print_success "Application directory created"
fi

# Create Python virtual environment
echo ""
echo "Creating Python virtual environment..."

cd $INSTALL_DIR/backend
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."

mkdir -p $INSTALL_DIR/backend/logs
mkdir -p $INSTALL_DIR/backend/data
mkdir -p $INSTALL_DIR/logs
chown -R trader:trader $INSTALL_DIR/backend/logs
chown -R trader:trader $INSTALL_DIR/backend/data
chown -R trader:trader $INSTALL_DIR/logs
print_success "Directories created"

# Setup environment file
echo ""
echo "Setting up environment configuration..."

if [ ! -f "$INSTALL_DIR/backend/.env" ]; then
    cp $INSTALL_DIR/backend/.env.example $INSTALL_DIR/backend/.env
    chown trader:trader $INSTALL_DIR/backend/.env
    print_success "Environment file created"
    print_warning "Please edit $INSTALL_DIR/backend/.env with your configuration"
else
    print_warning "Environment file already exists"
fi

# Setup systemd service
echo ""
echo "Setting up systemd service..."

cp $INSTALL_DIR/deploy/solana-ai-trader.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable solana-ai-trader
print_success "Systemd service installed"

# Setup nginx (optional)
echo ""
read -p "Do you want to setup nginx reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp $INSTALL_DIR/deploy/nginx.conf /etc/nginx/nginx.conf
    systemctl reload nginx
    print_success "Nginx configured"
fi

# Print summary
echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration:"
echo "   nano $INSTALL_DIR/backend/.env"
echo ""
echo "2. Start the service:"
echo "   systemctl start solana-ai-trader"
echo ""
echo "3. Check service status:"
echo "   systemctl status solana-ai-trader"
echo ""
echo "4. View logs:"
echo "   journalctl -u solana-ai-trader -f"
echo "   tail -f $INSTALL_DIR/logs/output.log"
echo ""
echo "5. Access web dashboard:"
echo "   http://localhost:8000"
echo ""
echo "For more information, see README.md"
echo ""
