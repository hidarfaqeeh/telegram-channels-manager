import re
import json
import asyncio
import logging
from typing import Union, List, Dict, Any, Optional
from datetime import datetime, timedelta
from telethon.tl.types import User, Chat, Channel
import validators
import emoji

logger = logging.getLogger(__name__)

def is_admin(user_id: int, admin_ids: List[int]) -> bool:
    """Check if user is admin"""
    return user_id in admin_ids

def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def parse_time_string(time_str: str) -> Optional[int]:
    """Parse time string like '5m', '2h', '30s' to seconds"""
    time_str = time_str.lower().strip()
    
    # Regular expression to match time patterns
    pattern = r'(\d+)([smhd])'
    matches = re.findall(pattern, time_str)
    
    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'd':
            total_seconds += value * 86400
    
    return total_seconds if total_seconds > 0 else None

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def extract_usernames(text: str) -> List[str]:
    """Extract usernames from text"""
    username_pattern = r'@([a-zA-Z0-9_]{5,32})'
    return re.findall(username_pattern, text)

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    hashtag_pattern = r'#(\w+)'
    return re.findall(hashtag_pattern, text)

def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text"""
    phone_pattern = r'[\+]?[1-9]?[0-9]{7,14}'
    return re.findall(phone_pattern, text)

def clean_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    clean_pattern = re.compile('<.*?>')
    return re.sub(clean_pattern, '', text)

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text"""
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with single newline
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def remove_duplicate_lines(text: str) -> str:
    """Remove duplicate lines from text"""
    lines = text.split('\n')
    seen = set()
    unique_lines = []
    
    for line in lines:
        if line.strip() not in seen:
            seen.add(line.strip())
            unique_lines.append(line)
    
    return '\n'.join(unique_lines)

def remove_empty_lines(text: str) -> str:
    """Remove empty lines from text"""
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def split_message(text: str, max_length: int = 4096) -> List[str]:
    """Split long message into multiple parts"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    for line in text.split('\n'):
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part.rstrip())
                current_part = line + '\n'
            else:
                # Line is too long, split it by words
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= max_length:
                        current_line += word + ' '
                    else:
                        if current_line:
                            parts.append(current_line.rstrip())
                            current_line = word + ' '
                        else:
                            # Word is too long, truncate it
                            parts.append(word[:max_length])
                            current_line = ""
                if current_line:
                    current_part = current_line + '\n'
    
    if current_part:
        parts.append(current_part.rstrip())
    
    return parts

def get_entity_info(entity) -> Dict[str, Any]:
    """Get information about Telegram entity"""
    info = {
        'id': entity.id,
        'type': type(entity).__name__,
        'title': None,
        'username': None,
        'first_name': None,
        'last_name': None
    }
    
    if isinstance(entity, User):
        info['first_name'] = entity.first_name
        info['last_name'] = entity.last_name
        info['username'] = entity.username
    elif isinstance(entity, (Chat, Channel)):
        info['title'] = entity.title
        info['username'] = getattr(entity, 'username', None)
    
    return info

def create_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create a text progress bar"""
    if total == 0:
        return "█" * width
    
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    percentage = (current / total) * 100
    return f"{bar} {percentage:.1f}%"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def safe_json_loads(json_str: str, default=None):
    """Safely load JSON string"""
    try:
        return json.loads(json_str) if json_str else default
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj, default=None) -> str:
    """Safely dump object to JSON string"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return json.dumps(default) if default is not None else "{}"

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    return validators.url(url) is True

def is_valid_email(email: str) -> bool:
    """Check if email is valid"""
    return validators.email(email) is True

def contains_emoji(text: str) -> bool:
    """Check if text contains emoji"""
    return any(char in emoji.UNICODE_EMOJI['en'] for char in text)

def remove_emojis(text: str) -> str:
    """Remove emojis from text"""
    return ''.join(char for char in text if char not in emoji.UNICODE_EMOJI['en'])

def get_text_language(text: str) -> Optional[str]:
    """Detect text language using simple heuristics"""
    try:
        from langdetect import detect
        return detect(text)
    except:
        return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename

def format_user_mention(user_id: int, name: str) -> str:
    """Format user mention"""
    return f"[{name}](tg://user?id={user_id})"

def parse_button_data(button_data: str) -> List[List[Dict[str, str]]]:
    """Parse button data from string format"""
    try:
        # Expected format: "Text1|URL1,Text2|URL2;Text3|URL3"
        # Semicolon separates rows, comma separates buttons in row, pipe separates text and URL
        
        rows = []
        if not button_data.strip():
            return rows
        
        for row_data in button_data.split(';'):
            row = []
            for button_data in row_data.split(','):
                if '|' in button_data:
                    text, url = button_data.split('|', 1)
                    row.append({'text': text.strip(), 'url': url.strip()})
            if row:
                rows.append(row)
        
        return rows
    except Exception as e:
        logger.error(f"Failed to parse button data: {e}")
        return []

async def async_retry(func, max_retries: int = 3, delay: float = 1.0, *args, **kwargs):
    """Retry async function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(delay * (2 ** attempt))

def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert datetime between timezones"""
    try:
        import pytz
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        # Localize the datetime to source timezone
        localized_dt = from_timezone.localize(dt)
        # Convert to target timezone
        converted_dt = localized_dt.astimezone(to_timezone)
        return converted_dt
    except Exception as e:
        logger.error(f"Failed to convert timezone: {e}")
        return dt

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def get_command_args(text: str, command: str) -> List[str]:
    """Extract arguments from command"""
    if not text.startswith(f'/{command}'):
        return []
    
    args_text = text[len(f'/{command}'):].strip()
    return args_text.split() if args_text else []

def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} دقيقة"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours} ساعة {minutes} دقيقة" if minutes > 0 else f"{hours} ساعة"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days} يوم {hours} ساعة" if hours > 0 else f"{days} يوم"