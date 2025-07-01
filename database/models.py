from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import json

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, unique=True, nullable=False)
    channel_username = Column(String(255), nullable=True)
    channel_title = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Channel settings
    auto_header = Column(Boolean, default=False)
    auto_footer = Column(Boolean, default=False)
    custom_header = Column(Text, nullable=True)
    custom_footer = Column(Text, nullable=True)
    custom_buttons = Column(Text, nullable=True)  # JSON string
    
    # Publishing settings
    delete_and_resend = Column(Boolean, default=False)
    edit_mode = Column(Boolean, default=True)
    
    # Notification settings
    disable_notification = Column(Boolean, default=False)
    disable_web_page_preview = Column(Boolean, default=False)
    
class InviteLink(Base):
    __tablename__ = 'invite_links'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    link_name = Column(String(255), nullable=False)
    invite_link = Column(String(255), nullable=False)
    expire_date = Column(DateTime, nullable=True)
    member_limit = Column(Integer, nullable=True)
    creates_join_request = Column(Boolean, default=False)
    is_revoked = Column(Boolean, default=False)
    member_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChannelAdmin(Base):
    __tablename__ = 'channel_admins'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    username = Column(String(255), nullable=True)
    can_manage_chat = Column(Boolean, default=False)
    can_delete_messages = Column(Boolean, default=False)
    can_manage_video_chats = Column(Boolean, default=False)
    can_restrict_members = Column(Boolean, default=False)
    can_promote_members = Column(Boolean, default=False)
    can_change_info = Column(Boolean, default=False)
    can_invite_users = Column(Boolean, default=False)
    can_post_messages = Column(Boolean, default=False)
    can_edit_messages = Column(Boolean, default=False)
    can_pin_messages = Column(Boolean, default=False)
    can_manage_topics = Column(Boolean, default=False)
    is_anonymous = Column(Boolean, default=False)
    is_restricted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageFilter(Base):
    __tablename__ = 'message_filters'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    
    # Text filters
    blacklist_words = Column(Text, nullable=True)  # JSON array
    whitelist_words = Column(Text, nullable=True)  # JSON array
    enable_blacklist = Column(Boolean, default=False)
    enable_whitelist = Column(Boolean, default=False)
    
    # Media filters
    allow_text = Column(Boolean, default=True)
    allow_photo = Column(Boolean, default=True)
    allow_video = Column(Boolean, default=True)
    allow_audio = Column(Boolean, default=True)
    allow_document = Column(Boolean, default=True)
    allow_sticker = Column(Boolean, default=True)
    allow_animation = Column(Boolean, default=True)
    allow_voice = Column(Boolean, default=True)
    allow_video_note = Column(Boolean, default=True)
    allow_contact = Column(Boolean, default=True)
    allow_location = Column(Boolean, default=True)
    allow_venue = Column(Boolean, default=True)
    allow_poll = Column(Boolean, default=True)
    allow_dice = Column(Boolean, default=True)
    
    # Advanced filters
    block_forwarded = Column(Boolean, default=False)
    block_duplicates = Column(Boolean, default=False)
    block_inline_buttons = Column(Boolean, default=False)
    admin_only = Column(Boolean, default=False)
    block_links = Column(Boolean, default=False)
    
    # Language filter
    allowed_languages = Column(Text, nullable=True)  # JSON array
    blocked_languages = Column(Text, nullable=True)  # JSON array
    
    # Length filter
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)
    
    # Time filters
    working_days = Column(Text, nullable=True)  # JSON array [0-6]
    working_hours = Column(Text, nullable=True)  # JSON array [0-23]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MessageFormatting(Base):
    __tablename__ = 'message_formatting'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    
    # Text formatting
    text_format = Column(String(50), default='original')  # original, bold, italic, etc.
    
    # Text cleaning
    clean_links = Column(Boolean, default=False)
    clean_emails = Column(Boolean, default=False)
    clean_usernames = Column(Boolean, default=False)
    clean_numbers = Column(Boolean, default=False)
    clean_hashtags = Column(Boolean, default=False)
    clean_emojis = Column(Boolean, default=False)
    clean_captions = Column(Boolean, default=False)
    clean_punctuation = Column(Boolean, default=False)
    clean_duplicate_lines = Column(Boolean, default=False)
    normalize_spaces = Column(Boolean, default=False)
    clean_empty_lines = Column(Boolean, default=False)
    remove_forward_tag = Column(Boolean, default=False)
    
    # Custom word removal
    remove_words = Column(Text, nullable=True)  # JSON array
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScheduledPost(Base):
    __tablename__ = 'scheduled_posts'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    message_data = Column(Text, nullable=False)  # JSON with message content
    scheduled_time = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class WordReplacement(Base):
    __tablename__ = 'word_replacements'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    original_word = Column(String(255), nullable=False)
    replacement_word = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TranslationSettings(Base):
    __tablename__ = 'translation_settings'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    enable_translation = Column(Boolean, default=False)
    target_language = Column(String(10), default='ar')
    translation_service = Column(String(50), default='google')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AutoAcceptSettings(Base):
    __tablename__ = 'auto_accept_settings'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    enable_auto_accept = Column(Boolean, default=False)
    accept_delay = Column(Integer, default=300)  # seconds
    max_accepts_per_minute = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotSettings(Base):
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(255), unique=True, nullable=False)
    setting_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)