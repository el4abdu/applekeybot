#!/usr/bin/env python3
"""
Test script to verify Chrome driver auto-download functionality
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_chrome_driver():
    """Test Chrome driver auto-download and setup"""
    print("🔧 Testing Chrome driver auto-download...")
    
    try:
        # Auto-install ChromeDriver matching installed Chrome version
        print("📥 Downloading ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless for testing
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Create service and driver
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test basic functionality
        print("🌐 Testing browser functionality...")
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Page title: {title}")
        
        # Get Chrome version
        version = driver.capabilities['browserVersion']
        print(f"✅ Chrome version: {version}")
        
        # Clean up
        driver.quit()
        print("✅ Chrome driver test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Chrome driver test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_chrome_driver()
    sys.exit(0 if success else 1)
