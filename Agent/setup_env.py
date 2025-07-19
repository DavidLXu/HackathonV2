#!/usr/bin/env python3
"""
Setup script for Smart Fridge Environment
"""

import os
import sys

def setup_environment():
    """Setup environment variables"""
    print("🔧 Smart Fridge Environment Setup")
    print("=" * 50)
    
    # Check if API key is already set
    api_key = os.getenv('DASHSCOPE_API_KEY')
    
    if api_key:
        print("✅ DASHSCOPE_API_KEY is already set")
        print(f"   Current key: {api_key[:10]}...{api_key[-4:]}")
        return True
    
    print("❌ DASHSCOPE_API_KEY is not set")
    print("\n📋 Setup Instructions:")
    print("1. Get your API key from: https://dashscope.console.aliyun.com/")
    print("2. Set the environment variable:")
    print("   export DASHSCOPE_API_KEY='your_api_key_here'")
    print("\n   Or create a .env file with:")
    print("   DASHSCOPE_API_KEY=your_api_key_here")
    
    # Ask user if they want to set it now
    response = input("\nWould you like to set the API key now? (y/n): ").lower().strip()
    
    if response == 'y':
        api_key = input("Enter your DashScope API key: ").strip()
        if api_key:
            # Set environment variable for current session
            os.environ['DASHSCOPE_API_KEY'] = api_key
            print("✅ API key set for current session")
            print("   Note: This will only persist for the current terminal session.")
            print("   For permanent setup, add to your shell profile or create a .env file")
            return True
        else:
            print("❌ No API key provided")
            return False
    else:
        print("⚠️  Please set the API key before running the application")
        return False

def test_connection():
    """Test the API connection"""
    print("\n🧪 Testing API Connection...")
    
    try:
        import dashscope
        from smart_fridge_qwen import SmartFridgeQwenAgent
        
        # This will raise an error if API key is not set
        fridge = SmartFridgeQwenAgent()
        print("✅ API connection successful!")
        return True
        
    except ValueError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    if setup_environment():
        test_connection()
    else:
        print("\n🔧 Manual Setup Required:")
        print("1. Set DASHSCOPE_API_KEY environment variable")
        print("2. Run this script again to test the connection")
        sys.exit(1) 