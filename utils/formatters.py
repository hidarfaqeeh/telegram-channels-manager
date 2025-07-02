#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Formatters Module
===============

Collection of text formatting and cleaning functions.
Used for preparing and formatting messages, cleaning text, and applying consistent styling.
"""

import re
import html
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def clean_text(text: str, remove_extra_spaces: bool = True) -> str:
    """
    Clean and normalize text by removing unwanted characters and formatting.
    
    Args:
        text: Text to clean
        remove_extra_spaces: Whether to remove extra spaces
        
    Returns:
        str: Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove null bytes and other control characters
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize Unicode
    try:
        import unicodedata
        cleaned = unicodedata.normalize('NFKC', cleaned)
    except ImportError:
        pass
    
    # Remove extra whitespace
    if remove_extra_spaces:
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def format_message(text: str, 
                  header: str = "", 
                  footer: str = "", 
                  bold_keywords: List[str] = None,
                  italic_keywords: List[str] = None) -> str:
    """
    Format a message with header, footer, and keyword styling.
    
    Args:
        text: Main message text
        header: Header text to prepend
        footer: Footer text to append
        bold_keywords: Keywords to make bold
        italic_keywords: Keywords to make italic
        
    Returns:
        str: Formatted message
    """
    if not text:
        return ""
    
    formatted = clean_text(text)
    
    # Apply keyword formatting
    if bold_keywords:
        for keyword in bold_keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            formatted = pattern.sub(f"**{keyword}**", formatted)
    
    if italic_keywords:
        for keyword in italic_keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            formatted = pattern.sub(f"*{keyword}*", formatted)
    
    # Add header and footer
    parts = []
    if header:
        parts.append(clean_text(header))
    
    parts.append(formatted)
    
    if footer:
        parts.append(clean_text(footer))
    
    return "\n\n".join(filter(None, parts))

def format_telegram_message(text: str, parse_mode: str = "Markdown") -> str:
    """
    Format text for Telegram with proper escaping based on parse mode.
    
    Args:
        text: Text to format
        parse_mode: Telegram parse mode ("Markdown", "MarkdownV2", "HTML")
        
    Returns:
        str: Formatted text ready for Telegram
    """
    if not text:
        return ""
    
    if parse_mode == "HTML":
        return format_html_message(text)
    elif parse_mode == "MarkdownV2":
        return format_markdown_v2_message(text)
    else:  # Default Markdown
        return format_markdown_message(text)

def format_html_message(text: str) -> str:
    """
    Format text for Telegram HTML parse mode.
    
    Args:
        text: Text to format
        
    Returns:
        str: HTML formatted text
    """
    if not text:
        return ""
    
    # Escape HTML characters
    formatted = html.escape(text)
    
    # Convert basic markdown to HTML
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted)  # Bold
    formatted = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted)      # Italic
    formatted = re.sub(r'`(.*?)`', r'<code>\1</code>', formatted)  # Code
    formatted = re.sub(r'```(.*?)```', r'<pre>\1</pre>', formatted, flags=re.DOTALL)  # Code block
    
    return formatted

def format_markdown_message(text: str) -> str:
    """
    Format text for Telegram Markdown parse mode.
    
    Args:
        text: Text to format
        
    Returns:
        str: Markdown formatted text
    """
    if not text:
        return ""
    
    # Escape special characters for Markdown
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    formatted = text
    
    for char in special_chars:
        formatted = formatted.replace(char, f'\\{char}')
    
    return formatted

def format_markdown_v2_message(text: str) -> str:
    """
    Format text for Telegram MarkdownV2 parse mode.
    
    Args:
        text: Text to format
        
    Returns:
        str: MarkdownV2 formatted text
    """
    if not text:
        return ""
    
    # Escape special characters for MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    formatted = text
    
    for char in special_chars:
        formatted = formatted.replace(char, f'\\{char}')
    
    return formatted

def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        List[str]: List of found URLs
    """
    if not text:
        return []
    
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    return url_pattern.findall(text)

def remove_urls(text: str, replacement: str = "") -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Text to process
        replacement: Text to replace URLs with
        
    Returns:
        str: Text with URLs removed
    """
    if not text:
        return ""
    
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    return url_pattern.sub(replacement, text).strip()

def extract_mentions(text: str) -> List[str]:
    """
    Extract @mentions from text.
    
    Args:
        text: Text to extract mentions from
        
    Returns:
        List[str]: List of found mentions (without @)
    """
    if not text:
        return []
    
    mention_pattern = re.compile(r'@([a-zA-Z0-9_]{1,32})')
    return mention_pattern.findall(text)

def remove_mentions(text: str, replacement: str = "") -> str:
    """
    Remove @mentions from text.
    
    Args:
        text: Text to process
        replacement: Text to replace mentions with
        
    Returns:
        str: Text with mentions removed
    """
    if not text:
        return ""
    
    mention_pattern = re.compile(r'@[a-zA-Z0-9_]{1,32}')
    return mention_pattern.sub(replacement, text).strip()

def extract_hashtags(text: str) -> List[str]:
    """
    Extract #hashtags from text.
    
    Args:
        text: Text to extract hashtags from
        
    Returns:
        List[str]: List of found hashtags (without #)
    """
    if not text:
        return []
    
    hashtag_pattern = re.compile(r'#([a-zA-Z0-9_]{1,50})')
    return hashtag_pattern.findall(text)

def remove_hashtags(text: str, replacement: str = "") -> str:
    """
    Remove #hashtags from text.
    
    Args:
        text: Text to process
        replacement: Text to replace hashtags with
        
    Returns:
        str: Text with hashtags removed
    """
    if not text:
        return ""
    
    hashtag_pattern = re.compile(r'#[a-zA-Z0-9_]{1,50}')
    return hashtag_pattern.sub(replacement, text).strip()

def truncate_text(text: str, max_length: int = 4096, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def word_count(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        int: Number of words
    """
    if not text:
        return 0
    
    return len(re.findall(r'\b\w+\b', text))

def char_count(text: str, include_spaces: bool = True) -> int:
    """
    Count characters in text.
    
    Args:
        text: Text to count characters in
        include_spaces: Whether to include spaces in count
        
    Returns:
        int: Number of characters
    """
    if not text:
        return 0
    
    if include_spaces:
        return len(text)
    else:
        return len(re.sub(r'\s', '', text))

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    index = 0
    size = float(size_bytes)
    
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    
    return f"{size:.1f} {units[index]}"

def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to convert
        
    Returns:
        str: Slugified text
    """
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    
    return slug.strip('-')

def capitalize_words(text: str, exceptions: List[str] = None) -> str:
    """
    Capitalize words in text with exceptions.
    
    Args:
        text: Text to capitalize
        exceptions: Words that should not be capitalized
        
    Returns:
        str: Text with capitalized words
    """
    if not text:
        return ""
    
    exceptions = exceptions or ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    
    words = text.split()
    result = []
    
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in exceptions:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    
    return ' '.join(result)

def remove_emojis(text: str) -> str:
    """
    Remove emojis from text.
    
    Args:
        text: Text to process
        
    Returns:
        str: Text without emojis
    """
    if not text:
        return ""
    
    # Unicode ranges for emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub(r'', text)

def extract_emojis(text: str) -> List[str]:
    """
    Extract emojis from text.
    
    Args:
        text: Text to extract emojis from
        
    Returns:
        List[str]: List of found emojis
    """
    if not text:
        return []
    
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    return emoji_pattern.findall(text)

__all__ = [
    'clean_text', 'format_message', 'format_telegram_message',
    'format_html_message', 'format_markdown_message', 'format_markdown_v2_message',
    'extract_urls', 'remove_urls', 'extract_mentions', 'remove_mentions',
    'extract_hashtags', 'remove_hashtags', 'truncate_text', 'word_count',
    'char_count', 'format_file_size', 'format_duration', 'slugify',
    'capitalize_words', 'remove_emojis', 'extract_emojis'
]