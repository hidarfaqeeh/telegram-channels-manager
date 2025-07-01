import re
import json
import logging
from typing import Dict, List, Optional, Any
from utils.helpers import (
    extract_urls, extract_emails, extract_usernames, extract_hashtags,
    remove_emojis, normalize_whitespace, remove_duplicate_lines,
    remove_empty_lines, clean_html_tags
)

logger = logging.getLogger(__name__)

class TextFormatter:
    def __init__(self, db_manager):
        self.db = db_manager
    
    async def format_message_text(self, text: str, channel_id: int) -> str:
        """Format message text according to channel settings"""
        if not text:
            return text
        
        try:
            # Get formatting settings
            formatting_settings = await self.db.get_message_formatting(channel_id)
            if not formatting_settings:
                return text
            
            # Apply text cleaning
            text = await self._clean_text(text, formatting_settings)
            
            # Apply word replacements
            text = await self._apply_word_replacements(text, channel_id)
            
            # Apply text formatting
            text = self._apply_text_formatting(text, formatting_settings.text_format)
            
            return text
            
        except Exception as e:
            logger.error(f"Error formatting text: {e}")
            return text
    
    async def _clean_text(self, text: str, settings) -> str:
        """Apply text cleaning based on settings"""
        original_text = text
        
        try:
            # Clean links
            if settings.clean_links:
                urls = extract_urls(text)
                for url in urls:
                    text = text.replace(url, '')
            
            # Clean emails
            if settings.clean_emails:
                emails = extract_emails(text)
                for email in emails:
                    text = text.replace(email, '')
            
            # Clean usernames
            if settings.clean_usernames:
                usernames = extract_usernames(text)
                for username in usernames:
                    text = text.replace(f'@{username}', '')
            
            # Clean hashtags
            if settings.clean_hashtags:
                hashtags = extract_hashtags(text)
                for hashtag in hashtags:
                    text = text.replace(f'#{hashtag}', '')
            
            # Clean numbers
            if settings.clean_numbers:
                text = re.sub(r'\d+', '', text)
            
            # Clean emojis
            if settings.clean_emojis:
                text = remove_emojis(text)
            
            # Clean punctuation
            if settings.clean_punctuation:
                text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
            
            # Clean HTML tags
            text = clean_html_tags(text)
            
            # Remove custom words
            if settings.remove_words:
                try:
                    remove_words_list = json.loads(settings.remove_words)
                    for word in remove_words_list:
                        text = re.sub(rf'\b{re.escape(word)}\b', '', text, flags=re.IGNORECASE)
                except json.JSONDecodeError:
                    pass
            
            # Normalize spaces
            if settings.normalize_spaces:
                text = normalize_whitespace(text)
            
            # Remove duplicate lines
            if settings.clean_duplicate_lines:
                text = remove_duplicate_lines(text)
            
            # Remove empty lines
            if settings.clean_empty_lines:
                text = remove_empty_lines(text)
            
            # Remove forward tag (simplified implementation)
            if settings.remove_forward_tag:
                # Remove common forward patterns
                forward_patterns = [
                    r'Forwarded from .*?\n',
                    r'توجيه من .*?\n',
                    r'Переслано от .*?\n',
                    r'محول من .*?\n'
                ]
                for pattern in forward_patterns:
                    text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return original_text
    
    async def _apply_word_replacements(self, text: str, channel_id: int) -> str:
        """Apply word replacement rules"""
        try:
            replacements = await self.db.get_word_replacements(channel_id)
            
            for replacement in replacements:
                if replacement.is_active:
                    # Use word boundaries for exact word matching
                    pattern = rf'\b{re.escape(replacement.original_word)}\b'
                    text = re.sub(pattern, replacement.replacement_word, text, flags=re.IGNORECASE)
            
            return text
            
        except Exception as e:
            logger.error(f"Error applying word replacements: {e}")
            return text
    
    def _apply_text_formatting(self, text: str, format_type: str) -> str:
        """Apply text formatting like bold, italic, etc."""
        if not text or format_type == 'original':
            return text
        
        try:
            # Different formatting options
            if format_type == 'bold':
                return f"**{text}**"
            elif format_type == 'italic':
                return f"*{text}*"
            elif format_type == 'underline':
                return f"__{text}__"
            elif format_type == 'strikethrough':
                return f"~~{text}~~"
            elif format_type == 'code':
                return f"`{text}`"
            elif format_type == 'mono':
                return f"```\n{text}\n```"
            elif format_type == 'quote':
                lines = text.split('\n')
                quoted_lines = [f"> {line}" for line in lines]
                return '\n'.join(quoted_lines)
            elif format_type == 'spoiler':
                return f"||{text}||"
            else:
                return text
                
        except Exception as e:
            logger.error(f"Error applying text formatting: {e}")
            return text
    
    async def clean_text_only(self, text: str, cleaning_options: Dict[str, bool]) -> str:
        """Clean text with specific options without database dependency"""
        if not text:
            return text
        
        try:
            # Apply selected cleaning options
            if cleaning_options.get('clean_links', False):
                urls = extract_urls(text)
                for url in urls:
                    text = text.replace(url, '')
            
            if cleaning_options.get('clean_emails', False):
                emails = extract_emails(text)
                for email in emails:
                    text = text.replace(email, '')
            
            if cleaning_options.get('clean_usernames', False):
                usernames = extract_usernames(text)
                for username in usernames:
                    text = text.replace(f'@{username}', '')
            
            if cleaning_options.get('clean_hashtags', False):
                hashtags = extract_hashtags(text)
                for hashtag in hashtags:
                    text = text.replace(f'#{hashtag}', '')
            
            if cleaning_options.get('clean_numbers', False):
                text = re.sub(r'\d+', '', text)
            
            if cleaning_options.get('clean_emojis', False):
                text = remove_emojis(text)
            
            if cleaning_options.get('clean_punctuation', False):
                text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
            
            if cleaning_options.get('normalize_spaces', False):
                text = normalize_whitespace(text)
            
            if cleaning_options.get('clean_duplicate_lines', False):
                text = remove_duplicate_lines(text)
            
            if cleaning_options.get('clean_empty_lines', False):
                text = remove_empty_lines(text)
            
            if cleaning_options.get('remove_forward_tag', False):
                forward_patterns = [
                    r'Forwarded from .*?\n',
                    r'توجيه من .*?\n',
                    r'Переслано от .*?\n',
                    r'محول من .*?\n'
                ]
                for pattern in forward_patterns:
                    text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error in text cleaning: {e}")
            return text
    
    def apply_formatting_only(self, text: str, format_type: str) -> str:
        """Apply only formatting without cleaning"""
        return self._apply_text_formatting(text, format_type)
    
    async def get_cleaning_preview(self, text: str, cleaning_options: Dict[str, bool]) -> Dict[str, str]:
        """Get preview of text cleaning without applying"""
        preview = {
            'original': text,
            'cleaned': await self.clean_text_only(text, cleaning_options)
        }
        
        # Add step-by-step preview
        steps = {}
        current_text = text
        
        if cleaning_options.get('clean_links', False):
            urls = extract_urls(current_text)
            for url in urls:
                current_text = current_text.replace(url, '')
            steps['after_links_removal'] = current_text
        
        if cleaning_options.get('clean_emojis', False):
            current_text = remove_emojis(current_text)
            steps['after_emoji_removal'] = current_text
        
        if cleaning_options.get('normalize_spaces', False):
            current_text = normalize_whitespace(current_text)
            steps['after_normalization'] = current_text
        
        preview['steps'] = steps
        return preview
    
    async def update_formatting_settings(self, channel_id: int, **kwargs) -> bool:
        """Update text formatting settings for a channel"""
        try:
            await self.db.update_message_formatting(channel_id, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to update formatting settings: {e}")
            return False
    
    async def get_formatting_settings(self, channel_id: int) -> Optional[Dict]:
        """Get current formatting settings for a channel"""
        try:
            settings = await self.db.get_message_formatting(channel_id)
            if settings:
                return {
                    'text_format': settings.text_format,
                    'cleaning_options': {
                        'clean_links': settings.clean_links,
                        'clean_emails': settings.clean_emails,
                        'clean_usernames': settings.clean_usernames,
                        'clean_numbers': settings.clean_numbers,
                        'clean_hashtags': settings.clean_hashtags,
                        'clean_emojis': settings.clean_emojis,
                        'clean_captions': settings.clean_captions,
                        'clean_punctuation': settings.clean_punctuation,
                        'clean_duplicate_lines': settings.clean_duplicate_lines,
                        'normalize_spaces': settings.normalize_spaces,
                        'clean_empty_lines': settings.clean_empty_lines,
                        'remove_forward_tag': settings.remove_forward_tag
                    },
                    'remove_words': json.loads(settings.remove_words) if settings.remove_words else []
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get formatting settings: {e}")
            return None
    
    def extract_text_stats(self, text: str) -> Dict[str, Any]:
        """Extract statistics from text"""
        if not text:
            return {
                'character_count': 0,
                'word_count': 0,
                'line_count': 0,
                'url_count': 0,
                'email_count': 0,
                'username_count': 0,
                'hashtag_count': 0,
                'has_emojis': False
            }
        
        return {
            'character_count': len(text),
            'word_count': len(text.split()),
            'line_count': len(text.split('\n')),
            'url_count': len(extract_urls(text)),
            'email_count': len(extract_emails(text)),
            'username_count': len(extract_usernames(text)),
            'hashtag_count': len(extract_hashtags(text)),
            'has_emojis': len(text) != len(remove_emojis(text))
        }