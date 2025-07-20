#!/usr/bin/env python3
"""
Test script for Apple Key Generator Bot
Tests individual components before full deployment
"""

import asyncio
import logging
from apple_key_bot import AppleKeyGenerator, AppleKeyBot

# Configure logging for testing
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

async def test_key_generator():
    """Test the key generation functionality"""
    print("🧪 Testing Apple Key Generator...")
    
    generator = AppleKeyGenerator()
    
    try:
        # Test TV key generation
        print("📺 Testing Apple TV key generation...")
        result = await generator.generate_key("tv")
        
        if result["success"]:
            print(f"✅ TV Key generated: {result['key']}")
        else:
            print(f"❌ TV Key failed: {result['error']}")
        
        # Small delay
        await asyncio.sleep(2)
        
        # Test Music key generation
        print("🎵 Testing Apple Music key generation...")
        result = await generator.generate_key("music")
        
        if result["success"]:
            print(f"✅ Music Key generated: {result['key']}")
        else:
            print(f"❌ Music Key failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        generator.close_driver()
        print("🔧 Driver closed")

def test_url_extraction():
    """Test URL key extraction"""
    print("🧪 Testing URL key extraction...")
    
    generator = AppleKeyGenerator()
    
    # Test URLs
    test_urls = [
        "https://tv.apple.com/includes/commerce/authenticate?returnPath=/redeem?ctx=tv%26code=XTA6F7HXKYMR",
        "https://tv.apple.com/includes/commerce/redeem?ctx=tv&code=XTA6F7HXKYMR",
        "https://tv.apple.com/redeem/?ctx=tv&code=XTA6F7HXKYMR",
        "https://music.apple.com/includes/commerce/redeem?ctx=Music&code=RY9AJFRHXL37&ign-itscg=10300&ign-itsct=AC_MS_Music"
    ]
    
    for url in test_urls:
        key = generator.extract_key_from_url(url)
        print(f"URL: {url}")
        print(f"Extracted Key: {key}")
        print("---")

async def main():
    """Main test function"""
    print("🍎 Apple Key Bot Test Suite 🍎")
    print("=" * 40)
    
    # Test URL extraction (quick test)
    test_url_extraction()
    
    print("\n" + "=" * 40)
    
    # Test key generation (requires browser)
    choice = input("Do you want to test key generation? (y/n): ").lower()
    if choice == 'y':
        await test_key_generator()
    else:
        print("⏭️ Skipping key generation test")
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main())
