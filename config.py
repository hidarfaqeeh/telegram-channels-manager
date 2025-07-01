import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '')
SESSION_NAME = os.getenv('SESSION_NAME', 'userbot_session')

# Admin settings
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []
CONTROL_BOT_TOKEN = os.getenv('CONTROL_BOT_TOKEN', '')

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')

# Bot settings
DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'UTC')
MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '4096'))
MAX_CAPTION_LENGTH = int(os.getenv('MAX_CAPTION_LENGTH', '1024'))

# Message formatting settings
DEFAULT_HEADER = os.getenv('DEFAULT_HEADER', '')
DEFAULT_FOOTER = os.getenv('DEFAULT_FOOTER', '')
DEFAULT_BUTTONS = os.getenv('DEFAULT_BUTTONS', '[]')

# Filter settings
DEFAULT_BLACKLIST_WORDS = []
DEFAULT_WHITELIST_WORDS = []
DEFAULT_MEDIA_FILTERS = {
    'text': True,
    'photo': True,
    'video': True,
    'audio': True,
    'document': True,
    'sticker': True,
    'animation': True,
    'voice': True,
    'video_note': True,
    'contact': True,
    'location': True,
    'venue': True,
    'poll': True,
    'dice': True
}

# Translation settings
DEFAULT_TRANSLATE_LANGUAGE = os.getenv('DEFAULT_TRANSLATE_LANGUAGE', 'ar')
TRANSLATE_SERVICE = os.getenv('TRANSLATE_SERVICE', 'google')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Rate limiting
INVITE_ACCEPT_RATE = int(os.getenv('INVITE_ACCEPT_RATE', '10'))  # per minute
MESSAGE_DELAY = float(os.getenv('MESSAGE_DELAY', '1.0'))  # seconds

# Working hours and days
DEFAULT_WORKING_HOURS = list(range(24))  # All hours by default
DEFAULT_WORKING_DAYS = list(range(7))   # All days by default

# Auto-accept settings
AUTO_ACCEPT_DELAY = int(os.getenv('AUTO_ACCEPT_DELAY', '300'))  # 5 minutes default