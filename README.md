# 🍎 Apple Key Generator Telegram Bot

An automated Telegram bot that generates redemption keys for Apple services including Apple TV+, Apple Music, Apple Arcade, Apple Fitness+, and Apple News+.

## 🚀 Features

- **Multi-Service Support**: Generate keys for all major Apple services
- **Private Browsing**: Uses incognito mode with no cookies for clean sessions
- **Auto ChromeDriver**: Automatically installs and matches your Chrome version
- **24/7 Operation**: Designed for continuous operation on AWS Ubuntu
- **Beautiful UI**: Intuitive Telegram interface with emojis and inline keyboards
- **Error Handling**: Robust error handling and retry mechanisms
- **Batch Generation**: Generate keys for all services at once

## 📋 Supported Apple Services

| Service | Description | Emoji |
|---------|-------------|-------|
| Apple TV+ | Entertainment streaming | 📺 |
| Apple Music | Music streaming | 🎵 |
| Apple Arcade | Gaming subscription | 🎮 |
| Apple Fitness+ | Workout classes | 💪 |
| Apple News+ | News and magazines | 📰 |

## 🛠️ Installation

### Local Development (Windows)

1. **Clone the repository**
   ```bash
   cd "c:\Users\HP\Documents\dev3\ubuntu apple key"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python apple_key_bot.py
   ```

### Production Deployment (Ubuntu/AWS)

1. **Upload files to your Ubuntu server**
   ```bash
   scp -r * ubuntu@your-server-ip:/home/ubuntu/apple-key-bot/
   ```

2. **SSH into your server**
   ```bash
   ssh ubuntu@your-server-ip
   cd /home/ubuntu/apple-key-bot
   ```

3. **Run deployment script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

The deployment script will:
- Install Python 3 and pip
- Install Google Chrome and dependencies
- Create a virtual environment
- Install Python packages
- Set up systemd service for 24/7 operation
- Configure headless Chrome operation

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and main menu |
| `/generate` | Show service selection menu |
| `/help` | Display help information |

## 🔧 Configuration

### Environment Variables (.env)

```env
BOT_TOKEN=7623137573:AAEHiRKpuG1T77cP6hWgyx_bai-G9IuP-0o
APPLE_REDEEM_URL=https://redeem.services.apple/card-apple-entertainment-offer-1-2025
HEADLESS_MODE=false
LOG_LEVEL=INFO
```

### Service Button XPaths

The bot uses specific XPath selectors to click service buttons:

```python
SERVICE_BUTTONS = {
    "tv": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[1]/div/div[2]/button',
    "music": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]/button',
    "arcade": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[3]/div/div[2]/button',
    "fitness": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[4]/div/div[2]/button',
    "news": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[5]/div/div[2]/button',
}
```

## 🏗️ Architecture

### Core Components

1. **AppleKeyGenerator**: Handles Selenium automation
   - Sets up Chrome driver with private browsing
   - Navigates to Apple redemption page
   - Clicks service buttons
   - Extracts keys from redirect URLs

2. **AppleKeyBot**: Manages Telegram bot interactions
   - Handles commands and callbacks
   - Provides user-friendly interface
   - Manages key generation workflow

### Key Generation Process

1. Open private Chrome browser session
2. Navigate to Apple redemption page
3. Click the selected service button
4. Wait for redirect to service-specific URL
5. Extract redemption key from URL parameters
6. Return key to user via Telegram

## 🔍 How It Works

1. **User Interaction**: User sends `/start` or `/generate` command
2. **Service Selection**: Bot displays inline keyboard with service options
3. **Browser Automation**: Selenium opens private Chrome session
4. **Page Navigation**: Bot navigates to Apple redemption page
5. **Button Click**: Clicks the appropriate service button
6. **URL Capture**: Captures redirect URL containing the key
7. **Key Extraction**: Extracts key using regex/URL parsing
8. **Result Delivery**: Sends key back to user via Telegram

## 📊 System Requirements

### Minimum Requirements
- Python 3.8+
- Google Chrome browser
- 2GB RAM
- 1GB disk space
- Stable internet connection

### Recommended for Production
- Ubuntu 20.04+ LTS
- 4GB RAM
- 2 CPU cores
- 10GB disk space
- AWS EC2 t3.small or larger

## 🚦 Service Management (Ubuntu)

```bash
# Check bot status
sudo systemctl status apple-key-bot.service

# View real-time logs
sudo journalctl -u apple-key-bot.service -f

# Restart the bot
sudo systemctl restart apple-key-bot.service

# Stop the bot
sudo systemctl stop apple-key-bot.service

# Start the bot
sudo systemctl start apple-key-bot.service
```

## 🛡️ Security Features

- **Private Browsing**: Uses incognito mode to prevent cookie tracking
- **No Data Storage**: Keys are not stored, only generated and delivered
- **Environment Variables**: Sensitive data stored in .env file
- **Error Handling**: Comprehensive error handling prevents crashes
- **Rate Limiting**: Built-in delays between requests

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver Version Mismatch**
   - Solution: The bot auto-installs matching ChromeDriver version

2. **Timeout Errors**
   - Solution: Increase timeout values in WebDriverWait

3. **XPath Not Found**
   - Solution: Check if Apple changed their page structure

4. **Bot Not Responding**
   - Solution: Check systemd service status and logs

### Debug Mode

To enable debug logging, modify the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

- **Key Generation Time**: 10-30 seconds per service
- **Batch Generation**: 2-5 minutes for all services
- **Memory Usage**: ~200MB per Chrome instance
- **CPU Usage**: Low when idle, moderate during generation

## 🔄 Updates and Maintenance

The bot is designed to be self-maintaining with:
- Auto ChromeDriver updates
- Robust error handling
- Service restart on failures
- Comprehensive logging

## 📞 Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u apple-key-bot.service -f`
2. Verify Chrome installation: `google-chrome --version`
3. Test bot token: Send a message to your bot
4. Check network connectivity to Apple services

## 📄 License

This project is for educational purposes. Please respect Apple's terms of service and use responsibly.

---

**🤖 Bot Token**: `7623137573:AAEHiRKpuG1T77cP6hWgyx_bai-G9IuP-0o`

**🌐 Apple Redeem URL**: `https://redeem.services.apple/card-apple-entertainment-offer-1-2025`
#   a p p l e k e y b o t  
 