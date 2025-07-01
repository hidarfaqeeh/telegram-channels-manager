#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram Channels Manager Bot
==========================

بوت تلغرام متقدم لإدارة القنوات مع ميزات:
- إدارة القنوات المتقدمة
- فلترة الرسائل الذكية
- تنسيق وتنظيف النصوص
- الترجمة التلقائية
- النشر المجدول
- إدارة روابط الدعوة
- قبول الطلبات التلقائي
- إدارة المشرفين

المطور: مجهول
الإصدار: 1.0.0
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import config
from userbot import TelegramUserBot, main as userbot_main
from control_bot import start_control_bot, stop_control_bot

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the application"""
    logger.info("🚀 Starting Telegram Channels Manager Bot...")
    
    # Check configuration
    if not validate_config():
        logger.error("❌ Configuration validation failed")
        sys.exit(1)
    
    userbot_task = None
    control_bot_task = None
    
    try:
        # Start both bots concurrently
        logger.info("🤖 Starting UserBot and Control Bot...")
        
        # Create tasks for both bots
        userbot_task = asyncio.create_task(userbot_main())
        control_bot_task = asyncio.create_task(start_control_bot())
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}")
            userbot_task.cancel()
            control_bot_task.cancel()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Wait for both tasks
        await asyncio.gather(userbot_task, control_bot_task)
        
    except KeyboardInterrupt:
        logger.info("⌨️ Received KeyboardInterrupt")
    except asyncio.CancelledError:
        logger.info("🛑 Tasks cancelled")
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        
        # Cancel tasks if they're still running
        if userbot_task and not userbot_task.done():
            userbot_task.cancel()
            try:
                await userbot_task
            except asyncio.CancelledError:
                pass
        
        if control_bot_task and not control_bot_task.done():
            control_bot_task.cancel()
            try:
                await control_bot_task
            except asyncio.CancelledError:
                pass
        
        # Stop control bot
        try:
            await stop_control_bot()
        except Exception as e:
            logger.error(f"Error stopping control bot: {e}")
        
        logger.info("✅ Cleanup completed")

def validate_config():
    """Validate configuration"""
    required_config = [
        'API_ID', 'API_HASH', 'BOT_TOKEN', 'PHONE_NUMBER', 
        'CONTROL_BOT_TOKEN', 'ADMIN_IDS'
    ]
    
    missing_config = []
    
    for key in required_config:
        value = getattr(config, key, None)
        if not value or (isinstance(value, list) and len(value) == 0):
            missing_config.append(key)
    
    if missing_config:
        logger.error(f"❌ Missing required configuration: {', '.join(missing_config)}")
        logger.error("📝 Please check your .env file and ensure all required variables are set")
        return False
    
    # Validate API_ID is integer
    try:
        int(config.API_ID)
    except (ValueError, TypeError):
        logger.error("❌ API_ID must be a valid integer")
        return False
    
    # Validate ADMIN_IDS are integers
    if config.ADMIN_IDS:
        try:
            for admin_id in config.ADMIN_IDS:
                int(admin_id)
        except (ValueError, TypeError):
            logger.error("❌ ADMIN_IDS must be valid integers")
            return False
    
    logger.info("✅ Configuration validation passed")
    return True

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

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import telethon
        import telegram
        import sqlalchemy
        import aiofiles
        import aiohttp
        import langdetect
        import deep_translator
        logger.info("✅ All dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("📦 Please install all required dependencies using: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'sessions']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")

if __name__ == "__main__":
    # Print banner
    print_banner()
    
    # Create necessary directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("⚠️ .env file not found")
        logger.info("📝 Please copy .env.example to .env and configure your settings")
        
        # Copy example file if it exists
        example_file = Path('.env.example')
        if example_file.exists():
            import shutil
            shutil.copy('.env.example', '.env')
            logger.info("📄 Created .env file from .env.example")
            logger.info("✏️ Please edit .env file with your actual configuration")
        
        sys.exit(1)
    
    try:
        # Run the main application
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"💀 Fatal error: {e}")
        sys.exit(1)