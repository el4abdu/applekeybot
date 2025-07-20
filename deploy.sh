#!/bin/bash
# Apple Key Bot Deployment Script for Ubuntu/AWS
# This script sets up the bot environment and dependencies

echo "🍎 Apple Key Bot Deployment Script 🍎"
echo "======================================"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip if not already installed
echo "🐍 Installing Python 3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install Chrome browser
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# Install additional dependencies for Chrome
echo "🔧 Installing Chrome dependencies..."
sudo apt install -y xvfb unzip wget curl

# Create virtual environment
echo "🏗️ Creating Python virtual environment..."
python3 -m venv apple_bot_env
source apple_bot_env/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/apple-key-bot.service > /dev/null <<EOF
[Unit]
Description=Apple Key Generator Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/apple_bot_env/bin
ExecStart=$(pwd)/apple_bot_env/bin/python apple_key_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set up Chrome for headless operation
echo "🖥️ Configuring Chrome for headless operation..."
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

# Enable and start the service
echo "🚀 Enabling and starting the bot service..."
sudo systemctl daemon-reload
sudo systemctl enable apple-key-bot.service
sudo systemctl start apple-key-bot.service

# Check service status
echo "📊 Checking service status..."
sudo systemctl status apple-key-bot.service

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔧 Useful commands:"
echo "  Check status: sudo systemctl status apple-key-bot.service"
echo "  View logs: sudo journalctl -u apple-key-bot.service -f"
echo "  Restart bot: sudo systemctl restart apple-key-bot.service"
echo "  Stop bot: sudo systemctl stop apple-key-bot.service"
echo ""
echo "🤖 Your Apple Key Bot is now running 24/7!"
echo "Test it by sending /start to your Telegram bot."
