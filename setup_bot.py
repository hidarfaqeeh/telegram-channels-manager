#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Setup Script
================
سكريبت إعداد بوت إدارة القنوات
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_requirements():
    """Install required packages"""
    try:
        logger.info("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'sessions', 'backups']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")

def setup_environment():
    """Setup environment file"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        logger.info("📄 Created .env file from .env.example")
        logger.warning("⚠️ Please edit .env file with your actual configuration")
        return False
    elif not env_file.exists():
        logger.error("❌ .env file not found and no .env.example available")
        return False
    
    return True

def check_config():
    """Check configuration"""
    try:
        import config
        
        required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'PHONE_NUMBER', 'CONTROL_BOT_TOKEN']
        missing_vars = []
        
        for var in required_vars:
            value = getattr(config, var, None)
            if not value:
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing configuration variables: {', '.join(missing_vars)}")
            logger.info("📝 Please configure these variables in your .env file")
            return False
        
        logger.info("✅ Configuration check passed")
        return True
        
    except ImportError:
        logger.error("❌ Could not import config module")
        return False

def setup_database():
    """Setup database"""
    try:
        import asyncio
        from database import Database
        import config
        
        async def init_db():
            db = Database(config.DATABASE_URL)
            await db.init_db()
            await db.close()
            logger.info("✅ Database initialized successfully")
        
        asyncio.run(init_db())
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting Bot Setup...")
    
    # Create directories
    create_directories()
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        logger.info("📝 Please configure your .env file and run setup again")
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    logger.info("🎉 Bot setup completed successfully!")
    logger.info("🚀 You can now run the bot with: python main.py")

if __name__ == "__main__":
    main()