#!/usr/bin/env python3
"""
Test script to verify Chrome driver auto-download functionality
"""

import os
import sys
import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def find_chromedriver_executable(base_path: str) -> str:
    """Find the correct chromedriver executable in the downloaded directory"""
    # Common chromedriver executable names
    possible_names = ['chromedriver', 'chromedriver.exe']
    
    # First, check if the base_path is already the correct executable
    if os.path.isfile(base_path) and os.access(base_path, os.X_OK):
        if not base_path.endswith(('THIRD_PARTY_NOTICES', '.txt', '.md')):
            return base_path
    
    # If base_path is a directory or wrong file, search for the executable
    search_dir = os.path.dirname(base_path) if os.path.isfile(base_path) else base_path
    
    # Search recursively for chromedriver executable
    for root, dirs, files in os.walk(search_dir):
        for name in possible_names:
            candidate = os.path.join(root, name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                # Verify it's not a text file
                try:
                    with open(candidate, 'rb') as f:
                        header = f.read(4)
                        if header.startswith(b'\x7fELF') or header.startswith(b'MZ'):  # Linux/Windows executable
                            print(f"✅ Found chromedriver executable: {candidate}")
                            return candidate
                except:
                    continue
    
    # Fallback: use glob to find chromedriver files
    patterns = [
        os.path.join(search_dir, '**/chromedriver'),
        os.path.join(search_dir, '**/chromedriver.exe')
    ]
    
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            if os.access(match, os.X_OK) and not match.endswith(('THIRD_PARTY_NOTICES', '.txt', '.md')):
                print(f"✅ Found chromedriver via glob: {match}")
                return match
    
    raise FileNotFoundError(f"Could not find chromedriver executable in {search_dir}")

def test_chrome_driver():
    """Test Chrome driver auto-download and setup"""
    print("🔧 Testing Chrome driver auto-download...")
    
    try:
        # Auto-install ChromeDriver matching installed Chrome version
        print("📥 Downloading ChromeDriver...")
        raw_driver_path = ChromeDriverManager().install()
        print(f"📁 ChromeDriver downloaded to: {raw_driver_path}")
        
        # Find the correct executable (fixes Linux path issues)
        driver_path = find_chromedriver_executable(raw_driver_path)
        print(f"✅ Using ChromeDriver executable: {driver_path}")
        
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
