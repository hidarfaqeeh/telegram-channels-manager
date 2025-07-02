#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Starter Script
==================
سكريبت بدء تشغيل بوت إدارة القنوات
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """Check if all requirements are met"""
    try:
        import telethon
        import telegram
        import sqlalchemy
        import aiofiles
        import aiohttp
        import langdetect
        import deep_translator
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install dependencies: pip install -r requirements.txt")
        return False

def check_config():
    """Check configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Please copy .env.example to .env and configure your settings")
        return False
    
    try:
        import config
        
        required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'PHONE_NUMBER', 'CONTROL_BOT_TOKEN']
        missing_vars = []
        
        for var in required_vars:
            value = getattr(config, var, None)
            if not value:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing configuration variables: {', '.join(missing_vars)}")
            print("📝 Please configure these variables in your .env file")
            return False
        
        return True
        
    except ImportError:
        print("❌ Could not import config module")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'sessions', 'backups']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                 Telegram Channels Manager Bot               ║
║                      بوت إدارة القنوات                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🚀 Advanced Telegram Channels Management Bot               ║
║                                                              ║
║  ✅ Channel Management                                       ║
║  ✅ Advanced Message Filtering                              ║
║  ✅ Text Formatting & Cleaning                              ║
║  ✅ Automatic Translation                                    ║
║  ✅ Scheduled Publishing                                     ║
║  ✅ Invite Links Management                                  ║
║  ✅ Auto Accept Requests                                     ║
║  ✅ Admin Management                                         ║
║                                                              ║
║  Version: 1.0.0                                             ║
║  Developer: Anonymous                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main entry point"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    try:
        # Import and run main
        from main import main as bot_main
        await bot_main()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"💀 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"💀 Fatal error: {e}")
        sys.exit(1)