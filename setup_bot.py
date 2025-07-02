#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Setup Script
================ 

Interactive setup script for the Telegram Channels Manager Bot.
Helps users configure the bot for first-time use.
=======
سكريبت إعداد بوت إدارة القنوات
"""

import os
import sys
 
import asyncio
import logging
from pathlib import Path
from getpass import getpass

def print_banner():
    """Print setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║               Telegram Channels Manager Bot                  ║
║                      إعداد البوت                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🚀 مرحباً بك في معالج إعداد بوت إدارة القنوات              ║
║                                                              ║
║  سيساعدك هذا المعالج في:                                    ║
║  ✅ تكوين إعدادات Telegram API                             ║
║  ✅ إنشاء ملف البيئة (.env)                                 ║
║  ✅ اختبار الاتصال                                          ║
║  ✅ إعداد قاعدة البيانات                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def get_user_input(prompt: str, required: bool = True, password: bool = False) -> str:
    """Get user input with validation"""
    while True:
        if password:
            value = getpass(f"{prompt}: ")
        else:
            value = input(f"{prompt}: ").strip()
        
        if not required or value:
            return value
        print("❌ هذا الحقل مطلوب. يرجى إدخال قيمة.")

def validate_api_id(api_id: str) -> bool:
    """Validate API ID"""
    try:
        int(api_id)
        return len(api_id) >= 7
    except ValueError:
        return False

def validate_token(token: str) -> bool:
    """Validate bot token format"""
    parts = token.split(':')
    return len(parts) == 2 and len(parts[0]) >= 8 and len(parts[1]) >= 35

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    return phone.startswith('+') and len(phone) >= 10

def create_env_file(config: dict):
    """Create .env file with configuration"""
    env_content = f"""# Telegram API Configuration
# احصل عليها من https://my.telegram.org/apps
API_ID={config['api_id']}
API_HASH={config['api_hash']}

# Bot Tokens
# أنشئ البوتات مع @BotFather على تلغرام
BOT_TOKEN={config['bot_token']}
CONTROL_BOT_TOKEN={config['control_bot_token']}

# User Account
PHONE_NUMBER={config['phone_number']}
SESSION_NAME=userbot_session

# Admin Configuration
# معرفات المديرين مفصولة بفواصل
ADMIN_IDS={config['admin_ids']}

# Database Configuration
DATABASE_URL=sqlite:///bot_database.db

# Bot Settings
DEFAULT_TIMEZONE=UTC
MAX_MESSAGE_LENGTH=4096
MAX_CAPTION_LENGTH=1024

# Message Formatting
DEFAULT_HEADER={config.get('default_header', '🚀 قناة الأخبار')}
DEFAULT_FOOTER={config.get('default_footer', '📱 تابعونا للمزيد')}
DEFAULT_BUTTONS=[]

# Translation Settings
DEFAULT_TRANSLATE_LANGUAGE=ar
TRANSLATE_SERVICE=google

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Rate Limiting
INVITE_ACCEPT_RATE=10
MESSAGE_DELAY=1.0

# Auto-accept Settings
AUTO_ACCEPT_DELAY=300
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ تم إنشاء ملف .env بنجاح")

def setup_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'data', 
        'sessions',
        'media',
        'media/thumbnails',
        'media/temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ تم إنشاء المجلدات المطلوبة")

async def test_connection(config: dict) -> bool:
    """Test bot connection"""
    try:
        print("\n🔗 اختبار الاتصال...")
        
        # Test userbot connection
        from telethon import TelegramClient
        
        client = TelegramClient(
            'test_session',
            int(config['api_id']),
            config['api_hash']
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print("📱 إرسال رمز التحقق...")
            await client.send_code_request(config['phone_number'])
            code = get_user_input("🔢 أدخل رمز التحقق")
            await client.sign_in(config['phone_number'], code)
        
        me = await client.get_me()
        print(f"✅ تم الاتصال بنجاح! مرحباً {me.first_name}")
        
        await client.disconnect()
        
        # Clean up test session
        for file in Path('.').glob('test_session.*'):
            file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ فشل في الاتصال: {e}")
        return False

async def setup_database():
    """Initialize database"""
    try:
        print("\n🗄️ إعداد قاعدة البيانات...")
        
        # Import and initialize database
        sys.path.insert(0, '.')
        from database.database import DatabaseManager
        
        db = DatabaseManager()
        await db.initialize()
        await db.close()
        
        print("✅ تم إعداد قاعدة البيانات بنجاح")
        return True
        
    except Exception as e:
        print(f"❌ فشل في إعداد قاعدة البيانات: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        print("\n📦 تثبيت المتطلبات...")
        
        # Try to install key dependencies
        import subprocess
        import sys
        
        # List of essential packages
        packages = [
            'python-dotenv',
            'telethon',
            'python-telegram-bot',
            'sqlalchemy',
            'aiosqlite',
            'aiofiles',
            'validators',
            'langdetect',
            'requests'
        ]
        
        for package in packages:
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', 
                    package, '--break-system-packages', '--quiet'
                ])
            except subprocess.CalledProcessError:
                print(f"⚠️ فشل في تثبيت {package}")
        
        print("✅ تم تثبيت المتطلبات الأساسية")
        return True
        
    except Exception as e:
        print(f"❌ فشل في تثبيت المتطلبات: {e}")
        return False

async def main():
    """Main setup function"""
    print_banner()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("\n⚠️ ملف .env موجود بالفعل. هل تريد استبداله؟ (y/N): ")
        if overwrite.lower() not in ['y', 'yes', 'نعم']:
            print("❌ تم إلغاء الإعداد")
            return
    
    print("\n📋 يرجى إدخال المعلومات التالية:")
    print("=" * 50)
    
    config = {}
    
    # Get Telegram API credentials
    print("\n🔑 إعدادات Telegram API")
    print("احصل عليها من: https://my.telegram.org/apps")
    
    while True:
        api_id = get_user_input("API ID")
        if validate_api_id(api_id):
            config['api_id'] = api_id
            break
        print("❌ API ID غير صحيح. يجب أن يكون رقماً من 7 خانات على الأقل")
    
    config['api_hash'] = get_user_input("API Hash")
    
    # Get phone number
    print("\n📱 رقم الهاتف")
    while True:
        phone = get_user_input("رقم الهاتف (مع رمز الدولة)")
        if validate_phone(phone):
            config['phone_number'] = phone
            break
        print("❌ رقم الهاتف غير صحيح. يجب أن يبدأ بـ + ورمز الدولة")
    
    # Get bot tokens
    print("\n🤖 توكن البوت")
    print("أنشئ البوتات مع @BotFather على تلغرام")
    
    while True:
        bot_token = get_user_input("BOT TOKEN")
        if validate_token(bot_token):
            config['bot_token'] = bot_token
            break
        print("❌ توكن البوت غير صحيح")
    
    while True:
        control_token = get_user_input("CONTROL BOT TOKEN")
        if validate_token(control_token):
            config['control_bot_token'] = control_token
            break
        print("❌ توكن بوت التحكم غير صحيح")
    
    # Get admin IDs
    print("\n👥 معرفات المديرين")
    admin_ids = get_user_input("معرفات المديرين (مفصولة بفواصل)")
    config['admin_ids'] = admin_ids
    
    # Optional settings
    print("\n⚙️ إعدادات اختيارية")
    config['default_header'] = get_user_input(
        "رأس الرسائل الافتراضي", 
        required=False
    ) or "🚀 قناة الأخبار"
    
    config['default_footer'] = get_user_input(
        "ذيل الرسائل الافتراضي", 
        required=False
    ) or "📱 تابعونا للمزيد"
    
    # Install dependencies
    print("\n" + "=" * 50)
    install_deps = input("📦 هل تريد تثبيت المتطلبات؟ (Y/n): ")
    if install_deps.lower() not in ['n', 'no', 'لا']:
        install_dependencies()
    
    # Create directories
    setup_directories()
    
    # Create .env file
    create_env_file(config)
    
    # Test connection
    print("\n" + "=" * 50)
    test_conn = input("🔗 هل تريد اختبار الاتصال؟ (Y/n): ")
    if test_conn.lower() not in ['n', 'no', 'لا']:
        if await test_connection(config):
            # Setup database
            await setup_database()
        else:
            print("⚠️ فشل اختبار الاتصال. تحقق من الإعدادات")
    
    # Final message
    print("\n" + "=" * 70)
    print("🎉 تم إعداد البوت بنجاح!")
    print("\n📝 الخطوات التالية:")
    print("1. تحقق من ملف .env وتأكد من صحة جميع البيانات")
    print("2. شغل البوت باستخدام: python3 main.py")
    print("3. استخدم بوت التحكم لإدارة القنوات")
    print("\n📚 للمساعدة، راجع ملف README.md")
    print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ تم إلغاء الإعداد بواسطة المستخدم")
    except Exception as e:
        print(f"\n💥 خطأ في الإعداد: {e}")
        sys.exit(1)
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
