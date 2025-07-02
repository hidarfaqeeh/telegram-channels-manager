#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validators Module
===============

Collection of validation functions for various data types and formats.
Used throughout the bot for input validation and data integrity checks.
"""

import re
import logging
from typing import Optional, Union, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Regex patterns
URL_PATTERN = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

PHONE_PATTERN = re.compile(
    r'^[\+]?[1-9][\d]{0,15}$'
)

USERNAME_PATTERN = re.compile(
    r'^[a-zA-Z0-9_]{1,32}$'
)

CHANNEL_ID_PATTERN = re.compile(
    r'^-100\d{10,}$'
)

def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.
    
    Args:
        url: String to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and URL_PATTERN.match(url) is not None
    except Exception:
        return False

def is_valid_email(email: str) -> bool:
    """
    Validate if a string is a valid email address.
    
    Args:
        email: String to validate
        
    Returns:
        bool: True if valid email, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    return EMAIL_PATTERN.match(email) is not None

def is_valid_phone(phone: str) -> bool:
    """
    Validate if a string is a valid phone number.
    
    Args:
        phone: String to validate
        
    Returns:
        bool: True if valid phone number, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common separators
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    return PHONE_PATTERN.match(clean_phone) is not None

def is_valid_username(username: str) -> bool:
    """
    Validate if a string is a valid Telegram username.
    
    Args:
        username: String to validate
        
    Returns:
        bool: True if valid username, False otherwise
    """
    if not username or not isinstance(username, str):
        return False
    
    # Remove @ if present
    clean_username = username.lstrip('@')
    
    return USERNAME_PATTERN.match(clean_username) is not None

def is_valid_channel_id(channel_id: Union[str, int]) -> bool:
    """
    Validate if a value is a valid Telegram channel ID.
    
    Args:
        channel_id: Channel ID to validate
        
    Returns:
        bool: True if valid channel ID, False otherwise
    """
    if not channel_id:
        return False
    
    channel_str = str(channel_id)
    
    # Check for supergroup/channel format
    if CHANNEL_ID_PATTERN.match(channel_str):
        return True
    
    # Check for regular negative ID
    try:
        channel_int = int(channel_str)
        return channel_int < 0
    except ValueError:
        return False

def is_valid_user_id(user_id: Union[str, int]) -> bool:
    """
    Validate if a value is a valid Telegram user ID.
    
    Args:
        user_id: User ID to validate
        
    Returns:
        bool: True if valid user ID, False otherwise
    """
    if not user_id:
        return False
    
    try:
        user_int = int(user_id)
        return user_int > 0
    except ValueError:
        return False

def is_valid_message_text(text: str, max_length: int = 4096) -> bool:
    """
    Validate if text is suitable for a Telegram message.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        
    Returns:
        bool: True if valid message text, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    
    return len(text.strip()) > 0 and len(text) <= max_length

def is_valid_file_size(size_bytes: int, max_size_mb: int = 50) -> bool:
    """
    Validate if file size is within acceptable limits.
    
    Args:
        size_bytes: File size in bytes
        max_size_mb: Maximum size in MB
        
    Returns:
        bool: True if valid size, False otherwise
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return 0 < size_bytes <= max_size_bytes

def is_valid_language_code(lang_code: str) -> bool:
    """
    Validate if string is a valid language code.
    
    Args:
        lang_code: Language code to validate
        
    Returns:
        bool: True if valid language code, False otherwise
    """
    if not lang_code or not isinstance(lang_code, str):
        return False
    
    # Common language codes
    valid_codes = {
        'en', 'ar', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja',
        'ko', 'hi', 'tr', 'fa', 'ur', 'bn', 'id', 'ms', 'th', 'vi'
    }
    
    return lang_code.lower() in valid_codes

def is_valid_timezone(timezone: str) -> bool:
    """
    Validate if string is a valid timezone.
    
    Args:
        timezone: Timezone string to validate
        
    Returns:
        bool: True if valid timezone, False otherwise
    """
    if not timezone or not isinstance(timezone, str):
        return False
    
    try:
        import pytz
        return timezone in pytz.all_timezones
    except ImportError:
        # Fallback to basic validation
        common_timezones = {
            'UTC', 'GMT', 'EST', 'PST', 'CST', 'MST',
            'Asia/Dubai', 'Asia/Riyadh', 'Asia/Baghdad',
            'Europe/London', 'Europe/Paris', 'Europe/Berlin'
        }
        return timezone in common_timezones

def is_valid_cron_expression(cron_expr: str) -> bool:
    """
    Basic validation for cron expressions.
    
    Args:
        cron_expr: Cron expression to validate
        
    Returns:
        bool: True if valid cron expression, False otherwise
    """
    if not cron_expr or not isinstance(cron_expr, str):
        return False
    
    parts = cron_expr.strip().split()
    
    # Standard cron has 5 parts (minute, hour, day, month, weekday)
    if len(parts) != 5:
        return False
    
    # Basic pattern matching for each part
    patterns = [
        r'^(\*|[0-5]?\d)(\/\d+)?$',  # minute
        r'^(\*|[01]?\d|2[0-3])(\/\d+)?$',  # hour
        r'^(\*|[1-2]?\d|3[01])(\/\d+)?$',  # day
        r'^(\*|[1-9]|1[0-2])(\/\d+)?$',  # month
        r'^(\*|[0-6])(\/\d+)?$'  # weekday
    ]
    
    for i, part in enumerate(parts):
        if not re.match(patterns[i], part):
            return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return "untitled"
    
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    
    # Trim underscores from start and end
    sanitized = sanitized.strip('_')
    
    # Ensure minimum length
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized[:255]  # Limit to 255 characters

def validate_admin_permissions(permissions: dict) -> bool:
    """
    Validate admin permissions dictionary.
    
    Args:
        permissions: Dictionary of permissions
        
    Returns:
        bool: True if valid permissions, False otherwise
    """
    if not isinstance(permissions, dict):
        return False
    
    valid_permissions = {
        'can_change_info', 'can_post_messages', 'can_edit_messages',
        'can_delete_messages', 'can_invite_users', 'can_restrict_members',
        'can_pin_messages', 'can_promote_members', 'can_manage_video_chats',
        'can_manage_chat', 'is_anonymous'
    }
    
    for perm in permissions:
        if perm not in valid_permissions:
            return False
        if not isinstance(permissions[perm], bool):
            return False
    
    return True

def validate_filter_settings(settings: dict) -> bool:
    """
    Validate filter settings dictionary.
    
    Args:
        settings: Filter settings to validate
        
    Returns:
        bool: True if valid settings, False otherwise
    """
    if not isinstance(settings, dict):
        return False
    
    required_keys = {'enabled', 'blacklist_words', 'whitelist_words', 'media_types'}
    
    if not all(key in settings for key in required_keys):
        return False
    
    if not isinstance(settings['enabled'], bool):
        return False
    
    if not isinstance(settings['blacklist_words'], list):
        return False
    
    if not isinstance(settings['whitelist_words'], list):
        return False
    
    if not isinstance(settings['media_types'], dict):
        return False
    
    return True

# Legacy function names for backwards compatibility
url = is_valid_url
email = is_valid_email

__all__ = [
    'is_valid_url', 'is_valid_email', 'is_valid_phone', 'is_valid_username',
    'is_valid_channel_id', 'is_valid_user_id', 'is_valid_message_text',
    'is_valid_file_size', 'is_valid_language_code', 'is_valid_timezone',
    'is_valid_cron_expression', 'sanitize_filename', 'validate_admin_permissions',
    'validate_filter_settings', 'url', 'email'
]