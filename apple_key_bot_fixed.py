#!/usr/bin/env python3
"""
Apple Service Key Generator Telegram Bot
Automatically generates redemption keys for Apple services (TV, Music, Arcade, Fitness, News)
"""

import asyncio
import logging
import os
import re
import time
import tempfile
import uuid
import shutil
from datetime import datetime, timedelta
from typing import Dict, Optional, Set
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from retrying import retry

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('apple_key_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7623137573:AAEHiRKpuG1T77cP6hWgyx_bai-G9IuP-0o")
APPLE_REDEEM_URL = "https://redeem.services.apple/card-apple-entertainment-offer-1-2025"

# Rate limiting configuration
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "60"))
user_requests = defaultdict(list)
user_cooldowns = defaultdict(datetime)

# Service button XPaths
SERVICE_BUTTONS = {
    "tv": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[1]/div/div[2]/button',
    "music": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[2]/div/div[2]/button',
    "arcade": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[3]/div/div[2]/button',
    "fitness": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[4]/div/div[2]/button',
    "news": '/html/body/div[1]/main/div/div[1]/div/div/div/div[1]/div[5]/div/div[2]/button',
}

# Service emojis for better UX
SERVICE_EMOJIS = {
    "tv": "📺",
    "music": "🎵",
    "arcade": "🎮",
    "fitness": "💪",
    "news": "📰",
}

class AppleKeyGenerator:
    """Handles Apple service key generation using Selenium"""
    
    def __init__(self):
        self.driver = None
        self.user_data_dir = None
        
    def _find_chromedriver_executable(self, base_path: str) -> str:
        """Find the correct chromedriver executable in the downloaded directory"""
        import glob
        import stat
        
        logger.info(f"Searching for chromedriver executable starting from: {base_path}")
        
        # If base_path is a file, get its directory
        if os.path.isfile(base_path):
            search_dir = os.path.dirname(base_path)
        else:
            search_dir = base_path
        
        logger.info(f"Searching in directory: {search_dir}")
        
        # Search recursively for chromedriver executable
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                # Check if filename matches chromedriver patterns
                if file == 'chromedriver' or file == 'chromedriver.exe':
                    candidate = os.path.join(root, file)
                    logger.info(f"Checking candidate: {candidate}")
                    
                    # Skip THIRD_PARTY_NOTICES files
                    if 'THIRD_PARTY_NOTICES' in candidate:
                        logger.info(f"Skipping THIRD_PARTY_NOTICES file: {candidate}")
                        continue
                    
                    # Check if file exists and is executable
                    if os.path.isfile(candidate):
                        try:
                            st = os.stat(candidate)
                            logger.info(f"File {candidate} - size: {st.st_size}")
                            
                            if st.st_size > 1000:  # ChromeDriver should be larger than 1KB
                                # Make sure it's executable
                                os.chmod(candidate, st.st_mode | stat.S_IEXEC)
                                logger.info(f"Found valid chromedriver executable: {candidate}")
                                return candidate
                        except Exception as e:
                            logger.warning(f"Could not check file stats for {candidate}: {e}")
        
        # If we still haven't found it, try a more aggressive search
        logger.warning("Standard search failed, trying aggressive search...")
        
        # Use find command if available (Linux/Unix)
        try:
            import subprocess
            result = subprocess.run(
                ['find', search_dir, '-name', 'chromedriver', '-type', 'f'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                candidates = result.stdout.strip().split('\n')
                for candidate in candidates:
                    if 'THIRD_PARTY_NOTICES' not in candidate and os.path.getsize(candidate) > 1000:
                        os.chmod(candidate, 0o755)
                        logger.info(f"Found chromedriver via find command: {candidate}")
                        return candidate
        except Exception as e:
            logger.warning(f"Find command failed: {e}")
        
        raise FileNotFoundError(f"Could not find chromedriver executable in {search_dir}")

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with private browsing and no cookies"""
        try:
            logger.info("Setting up Chrome driver with auto-download...")
            
            # Auto-install ChromeDriver matching installed Chrome version
            raw_driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver downloaded to: {raw_driver_path}")
            
            # Find the correct executable (fixes Linux path issues)
            driver_path = self._find_chromedriver_executable(raw_driver_path)
            logger.info(f"Using ChromeDriver executable: {driver_path}")
            
            service = Service(driver_path)
            
            # Chrome options for private browsing and production
            chrome_options = Options()
            
            # Create unique user data directory to avoid conflicts
            temp_dir = tempfile.gettempdir()
            unique_id = str(uuid.uuid4())[:8]
            user_data_dir = os.path.join(temp_dir, f"chrome_user_data_{unique_id}")
            self.user_data_dir = user_data_dir
            
            # Privacy and security options
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            logger.info(f"Using unique user data directory: {user_data_dir}")
            
            # User agent to avoid detection
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Production/server options (enabled based on environment)
            if os.getenv("CHROME_HEADLESS", "false").lower() == "true":
                chrome_options.add_argument("--headless")
                logger.info("Running Chrome in headless mode")
            
            if os.getenv("CHROME_NO_SANDBOX", "false").lower() == "true":
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                logger.info("Running Chrome with no-sandbox mode")
            
            # Additional stability options
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Create driver instance
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_window_size(1920, 1080)
            
            # Execute script to avoid detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info(f"Chrome driver setup successful - Version: {self.driver.capabilities['browserVersion']}")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            if self.driver:
                self.driver.quit()
            raise
    
    def extract_key_from_url(self, url: str) -> Optional[str]:
        """Extract redemption key from Apple service URL"""
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Look for 'code' parameter in URL
            if 'code' in query_params:
                key = query_params['code'][0]
                logger.info(f"Extracted key: {key}")
                return key
            
            # Alternative: extract from URL path if code is in path
            code_match = re.search(r'code=([A-Z0-9]+)', url)
            if code_match:
                key = code_match.group(1)
                logger.info(f"Extracted key from path: {key}")
                return key
                
            return None
                
        except Exception as e:
            logger.error(f"Failed to extract key from URL {url}: {e}")
            return None

    def generate_key(self, service: str) -> Dict[str, str]:
        """Generate redemption key for specified Apple service"""
        result = {
            "success": False,
            "key": None,
            "service": service,
            "error": None
        }
        
        try:
            if service not in SERVICE_BUTTONS:
                result["error"] = f"Unknown service: {service}"
                return result
            
            # Setup driver
            if not self.driver:
                self.setup_driver()
            
            logger.info(f"Generating key for {service.upper()} service")
            
            # Navigate to Apple redeem page
            self.driver.get(APPLE_REDEEM_URL)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)
            
            # Find and click the service button
            button_xpath = SERVICE_BUTTONS[service]
            button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
            
            logger.info(f"Clicking {service} button")
            button.click()
            
            # Wait for redirect and capture the new URL
            wait.until(lambda driver: driver.current_url != APPLE_REDEEM_URL)
            
            # Get the final URL after redirect
            final_url = self.driver.current_url
            logger.info(f"Redirected to: {final_url}")
            
            # Extract key from URL
            key = self.extract_key_from_url(final_url)
            
            if key:
                result["success"] = True
                result["key"] = key
                logger.info(f"Successfully generated {service} key: {key}")
            else:
                result["error"] = "Could not extract key from redirect URL"
                
        except TimeoutException:
            result["error"] = "Timeout waiting for page elements"
            logger.error(f"Timeout error for {service}")
            
        except WebDriverException as e:
            result["error"] = f"WebDriver error: {str(e)}"
            logger.error(f"WebDriver error for {service}: {e}")
            
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error for {service}: {e}")
        
        return result

    def close_driver(self):
        """Close the Chrome driver and cleanup temporary directories"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing Chrome driver: {e}")
            finally:
                self.driver = None
        
        # Cleanup temporary user data directory
        if self.user_data_dir and os.path.exists(self.user_data_dir):
            try:
                shutil.rmtree(self.user_data_dir, ignore_errors=True)
                logger.info(f"Cleaned up temporary directory: {self.user_data_dir}")
            except Exception as e:
                logger.warning(f"Could not cleanup temporary directory {self.user_data_dir}: {e}")
            finally:
                self.user_data_dir = None

class AppleKeyBot:
    """Telegram bot for Apple key generation"""
    
    def __init__(self):
        self.key_generator = AppleKeyGenerator()
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("generate", self.generate_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
🍎 **Welcome to Apple Key Generator Bot!** 🍎

I can generate redemption keys for Apple services:
📺 Apple TV+
🎵 Apple Music
🎮 Apple Arcade
💪 Apple Fitness+
📰 Apple News+

**Commands:**
/generate - Generate keys for Apple services
/help - Show this help message

Click the button below to get started!
        """
        
        keyboard = [[InlineKeyboardButton("🚀 Generate Keys", callback_data="show_services")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🍎 **Apple Key Generator Bot Help** 🍎

**Available Commands:**
/start - Start the bot and see welcome message
/generate - Generate keys for Apple services
/help - Show this help message

**How it works:**
1. Click "Generate Keys" button
2. Choose a specific service or generate all keys
3. Wait for the bot to process your request
4. Receive your redemption key(s)

**Supported Services:**
📺 Apple TV+ - Entertainment streaming
🎵 Apple Music - Music streaming
🎮 Apple Arcade - Gaming subscription
💪 Apple Fitness+ - Workout classes
📰 Apple News+ - News and magazines

**Note:** Keys are single-use and may expire after some time.
        """
        
        keyboard = [[InlineKeyboardButton("🚀 Generate Keys", callback_data="show_services")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def generate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate command"""
        await self.show_service_menu(update)
    
    async def show_service_menu(self, update: Update):
        """Show service selection menu"""
        menu_text = """
🍎 **Choose Apple Service** 🍎

Select which service you'd like to generate a key for:
        """
        
        keyboard = []
        for service, emoji in SERVICE_EMOJIS.items():
            service_name = service.replace('_', ' ').title()
            keyboard.append([InlineKeyboardButton(f"{emoji} Apple {service_name}", callback_data=f"generate_{service}")])
        
        keyboard.append([InlineKeyboardButton("🎯 Generate All Keys", callback_data="generate_all")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                menu_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                menu_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "show_services":
            await self.show_service_menu(update)
        elif query.data.startswith("generate_"):
            service = query.data.replace("generate_", "")
            if service == "all":
                await self.generate_all_keys(update)
            else:
                await self.generate_single_key(update, service)
        elif query.data == "cancel":
            await query.edit_message_text("❌ Operation cancelled.")
    
    async def generate_single_key(self, update: Update, service: str):
        """Generate key for a single service"""
        query = update.callback_query
        emoji = SERVICE_EMOJIS.get(service, "🔑")
        service_name = service.replace('_', ' ').title()
        
        # Show processing message
        await query.edit_message_text(f"🔄 Generating {emoji} Apple {service_name} key...\nPlease wait...")
        
        try:
            # Generate key
            result = self.key_generator.generate_key(service)
            
            if result["success"]:
                response_text = f"""
✅ **{emoji} Apple {service_name} Key Generated!**

🔑 **Your Key:** `{result['key']}`

**How to use:**
1. Copy the key above
2. Go to your Apple device
3. Open the {service_name} app
4. Look for "Redeem" option
5. Enter your key

*Note: Keys are single-use and may expire.*
                """
                
                keyboard = [[InlineKeyboardButton("🔄 Generate Another", callback_data="show_services")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    response_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                error_text = f"""
❌ **Failed to generate {emoji} Apple {service_name} key**

**Error:** {result.get('error', 'Unknown error')}

Please try again later.
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Try Again", callback_data=f"generate_{service}")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="show_services")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    error_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"Error in generate_single_key: {e}")
            await query.edit_message_text(
                f"❌ An unexpected error occurred: {str(e)}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="show_services")]])
            )
        finally:
            # Always close driver after use
            self.key_generator.close_driver()
    
    async def generate_all_keys(self, update: Update):
        """Generate keys for all services"""
        query = update.callback_query
        
        # Show processing message
        await query.edit_message_text("🔄 Generating keys for all Apple services...\nThis may take a few minutes...")
        
        success_keys = []
        failed_services = []
        
        for service, emoji in SERVICE_EMOJIS.items():
            service_name = service.replace('_', ' ').title()
            
            try:
                result = self.key_generator.generate_key(service)
                
                if result["success"]:
                    success_keys.append(f"{emoji} Apple {service_name}: `{result['key']}`")
                else:
                    failed_services.append(f"{emoji} Apple {service_name}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                failed_services.append(f"{emoji} Apple {service_name}: {str(e)}")
            
            # Close driver between services to avoid conflicts
            self.key_generator.close_driver()
        
        # Create response message
        response_text = "🍎 *All Keys Generation Complete* 🍎\n\n"
        
        if success_keys:
            response_text += "✅ *Successfully Generated:*\n" + "\n".join(success_keys) + "\n\n"
        
        if failed_services:
            response_text += "❌ *Failed to Generate:*\n" + "\n".join(failed_services) + "\n\n"
        
        response_text += "*Note:* Keys are single-use and expire after some time."
        
        keyboard = [[InlineKeyboardButton("🔄 Generate Again", callback_data="show_services")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            response_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def run(self):
        """Run the bot"""
        logger.info("Starting Apple Key Generator Bot...")
        
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Bot is running! Press Ctrl+C to stop.")
            
            # Keep the bot running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            await self.application.stop()
            self.key_generator.close_driver()

def main():
    """Main function"""
    try:
        bot = AppleKeyBot()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
