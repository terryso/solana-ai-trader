#!/bin/bash

# Solana AI Trader Update Script

set -e

INSTALL_DIR="/home/trader/solana-ai-trader"

echo "=================================="
echo "Solana AI Trader Update"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root or with sudo"
    exit 1
fi

# Stop service
echo "Stopping service..."
systemctl stop solana-ai-trader

# Backup current version
echo "Creating backup..."
BACKUP_DIR="$INSTALL_DIR.backup.$(date +%Y%m%d_%H%M%S)"
cp -r $INSTALL_DIR $BACKUP_DIR
echo "Backup created at: $BACKUP_DIR"

# Update code
echo "Updating code..."
cd $INSTALL_DIR
# git pull

# Update dependencies
echo "Updating dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
echo "Restarting service..."
systemctl start solana-ai-trader

# Clean old backups (keep last 5)
echo "Cleaning old backups..."
ls -dt $INSTALL_DIR.backup.* | tail -n +6 | xargs rm -rf

echo ""
echo "Update complete!"
echo "Service status:"
systemctl status solana-ai-trader --no-pager
