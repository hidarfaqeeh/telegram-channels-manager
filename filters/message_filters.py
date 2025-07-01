import re
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, time
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaContact, MessageMediaGeo, MessageMediaPoll
from telethon.tl.types import MessageMediaWebPage, MessageMediaVenue, MessageMediaGame, MessageMediaInvoice, MessageMediaGeoLive
from langdetect import detect, DetectorFactory
from utils.helpers import extract_urls, extract_usernames, contains_emoji, get_text_language

logger = logging.getLogger(__name__)

# Set seed for consistent language detection
DetectorFactory.seed = 0

class MessageFilterManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.language_cache = {}
        
    async def should_filter_message(self, message: Message, channel_id: int) -> tuple[bool, str]:
        """
        Check if message should be filtered
        Returns: (should_filter, reason)
        """
        try:
            # Get filter settings for channel
            filter_settings = await self.db.get_message_filter(channel_id)
            if not filter_settings:
                return False, ""
            
            # Check each filter
            filters = [
                self._check_media_filter,
                self._check_text_filters,
                self._check_forwarded_filter,
                self._check_duplicate_filter,
                self._check_inline_buttons_filter,
                self._check_admin_filter,
                self._check_links_filter,
                self._check_language_filter,
                self._check_length_filter,
                self._check_time_filter
            ]
            
            for filter_func in filters:
                should_filter, reason = await filter_func(message, filter_settings)
                if should_filter:
                    return True, reason
            
            return False, ""
            
        except Exception as e:
            logger.error(f"Error in message filtering: {e}")
            return False, "filter_error"
    
    async def _check_media_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check media type filters"""
        if not message.media:
            # Text message
            if not settings.allow_text:
                return True, "text_not_allowed"
            return False, ""
        
        media_type = type(message.media).__name__
        media_checks = {
            'MessageMediaPhoto': settings.allow_photo,
            'MessageMediaDocument': self._check_document_type(message, settings),
            'MessageMediaContact': settings.allow_contact,
            'MessageMediaGeo': settings.allow_location,
            'MessageMediaGeoLive': settings.allow_location,
            'MessageMediaVenue': settings.allow_venue,
            'MessageMediaPoll': settings.allow_poll,
            'MessageMediaWebPage': True,  # Usually allowed
            'MessageMediaGame': True,
            'MessageMediaInvoice': True
        }
        
        if media_type in media_checks:
            if not media_checks[media_type]:
                return True, f"{media_type}_not_allowed"
        
        return False, ""
    
    def _check_document_type(self, message: Message, settings) -> bool:
        """Check specific document type"""
        if not isinstance(message.media, MessageMediaDocument):
            return True
        
        document = message.media.document
        if not document or not document.attributes:
            return settings.allow_document
        
        # Check document attributes to determine type
        for attr in document.attributes:
            attr_type = type(attr).__name__
            
            if attr_type == 'DocumentAttributeVideo':
                if attr.round_message:
                    return settings.allow_video_note
                else:
                    return settings.allow_video
            elif attr_type == 'DocumentAttributeAudio':
                if attr.voice:
                    return settings.allow_voice
                else:
                    return settings.allow_audio
            elif attr_type == 'DocumentAttributeAnimated':
                return settings.allow_animation
            elif attr_type == 'DocumentAttributeSticker':
                return settings.allow_sticker
        
        return settings.allow_document
    
    async def _check_text_filters(self, message: Message, settings) -> tuple[bool, str]:
        """Check blacklist and whitelist filters"""
        if not message.text:
            return False, ""
        
        text = message.text.lower()
        
        # Check blacklist
        if settings.enable_blacklist and settings.blacklist_words:
            try:
                blacklist = json.loads(settings.blacklist_words)
                for word in blacklist:
                    if word.lower() in text:
                        return True, f"blacklisted_word: {word}"
            except json.JSONDecodeError:
                pass
        
        # Check whitelist
        if settings.enable_whitelist and settings.whitelist_words:
            try:
                whitelist = json.loads(settings.whitelist_words)
                found_whitelisted = False
                for word in whitelist:
                    if word.lower() in text:
                        found_whitelisted = True
                        break
                
                if not found_whitelisted:
                    return True, "not_in_whitelist"
            except json.JSONDecodeError:
                pass
        
        return False, ""
    
    async def _check_forwarded_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check if forwarded messages should be filtered"""
        if settings.block_forwarded and message.forward:
            return True, "forwarded_message"
        return False, ""
    
    async def _check_duplicate_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check for duplicate messages (simplified implementation)"""
        if not settings.block_duplicates:
            return False, ""
        
        # This is a simplified implementation
        # In a real scenario, you'd store message hashes and check against them
        return False, ""
    
    async def _check_inline_buttons_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check for inline keyboard buttons"""
        if settings.block_inline_buttons and message.reply_markup:
            from telethon.tl.types import ReplyInlineMarkup
            if isinstance(message.reply_markup, ReplyInlineMarkup):
                return True, "inline_buttons"
        return False, ""
    
    async def _check_admin_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check if only admins can post"""
        if not settings.admin_only:
            return False, ""
        
        # This would need to be implemented with actual admin checking
        # For now, we'll assume the message is allowed
        return False, ""
    
    async def _check_links_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check for links and usernames"""
        if not settings.block_links or not message.text:
            return False, ""
        
        text = message.text
        
        # Check for URLs
        urls = extract_urls(text)
        if urls:
            return True, "contains_urls"
        
        # Check for usernames
        usernames = extract_usernames(text)
        if usernames:
            return True, "contains_usernames"
        
        return False, ""
    
    async def _check_language_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check language filters"""
        if not message.text:
            return False, ""
        
        if not (settings.allowed_languages or settings.blocked_languages):
            return False, ""
        
        try:
            # Detect language
            text = message.text
            if len(text) < 10:  # Too short for reliable detection
                return False, ""
            
            detected_lang = get_text_language(text)
            if not detected_lang:
                return False, ""
            
            # Check allowed languages
            if settings.allowed_languages:
                try:
                    allowed = json.loads(settings.allowed_languages)
                    if detected_lang not in allowed:
                        return True, f"language_not_allowed: {detected_lang}"
                except json.JSONDecodeError:
                    pass
            
            # Check blocked languages
            if settings.blocked_languages:
                try:
                    blocked = json.loads(settings.blocked_languages)
                    if detected_lang in blocked:
                        return True, f"language_blocked: {detected_lang}"
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
        
        return False, ""
    
    async def _check_length_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check message length filters"""
        if not message.text:
            return False, ""
        
        text_length = len(message.text)
        
        if settings.min_length and text_length < settings.min_length:
            return True, f"too_short: {text_length} < {settings.min_length}"
        
        if settings.max_length and text_length > settings.max_length:
            return True, f"too_long: {text_length} > {settings.max_length}"
        
        return False, ""
    
    async def _check_time_filter(self, message: Message, settings) -> tuple[bool, str]:
        """Check working days and hours"""
        now = datetime.now()
        
        # Check working days (0 = Monday, 6 = Sunday)
        if settings.working_days:
            try:
                working_days = json.loads(settings.working_days)
                if now.weekday() not in working_days:
                    return True, f"not_working_day: {now.weekday()}"
            except json.JSONDecodeError:
                pass
        
        # Check working hours
        if settings.working_hours:
            try:
                working_hours = json.loads(settings.working_hours)
                if now.hour not in working_hours:
                    return True, f"not_working_hour: {now.hour}"
            except json.JSONDecodeError:
                pass
        
        return False, ""
    
    async def get_filter_stats(self, channel_id: int) -> Dict[str, int]:
        """Get filtering statistics (this would need to be implemented with proper tracking)"""
        return {
            'total_messages': 0,
            'filtered_messages': 0,
            'media_filtered': 0,
            'text_filtered': 0,
            'forwarded_filtered': 0,
            'duplicate_filtered': 0,
            'buttons_filtered': 0,
            'admin_filtered': 0,
            'links_filtered': 0,
            'language_filtered': 0,
            'length_filtered': 0,
            'time_filtered': 0
        }
    
    async def update_filter_settings(self, channel_id: int, **kwargs) -> bool:
        """Update filter settings for a channel"""
        try:
            await self.db.update_message_filter(channel_id, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to update filter settings: {e}")
            return False
    
    async def get_filter_settings(self, channel_id: int) -> Optional[Dict]:
        """Get current filter settings for a channel"""
        try:
            settings = await self.db.get_message_filter(channel_id)
            if settings:
                return {
                    'blacklist_words': json.loads(settings.blacklist_words) if settings.blacklist_words else [],
                    'whitelist_words': json.loads(settings.whitelist_words) if settings.whitelist_words else [],
                    'enable_blacklist': settings.enable_blacklist,
                    'enable_whitelist': settings.enable_whitelist,
                    'media_filters': {
                        'text': settings.allow_text,
                        'photo': settings.allow_photo,
                        'video': settings.allow_video,
                        'audio': settings.allow_audio,
                        'document': settings.allow_document,
                        'sticker': settings.allow_sticker,
                        'animation': settings.allow_animation,
                        'voice': settings.allow_voice,
                        'video_note': settings.allow_video_note,
                        'contact': settings.allow_contact,
                        'location': settings.allow_location,
                        'venue': settings.allow_venue,
                        'poll': settings.allow_poll,
                        'dice': settings.allow_dice
                    },
                    'advanced_filters': {
                        'block_forwarded': settings.block_forwarded,
                        'block_duplicates': settings.block_duplicates,
                        'block_inline_buttons': settings.block_inline_buttons,
                        'admin_only': settings.admin_only,
                        'block_links': settings.block_links
                    },
                    'language_filter': {
                        'allowed_languages': json.loads(settings.allowed_languages) if settings.allowed_languages else [],
                        'blocked_languages': json.loads(settings.blocked_languages) if settings.blocked_languages else []
                    },
                    'length_filter': {
                        'min_length': settings.min_length,
                        'max_length': settings.max_length
                    },
                    'time_filter': {
                        'working_days': json.loads(settings.working_days) if settings.working_days else list(range(7)),
                        'working_hours': json.loads(settings.working_hours) if settings.working_hours else list(range(24))
                    }
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get filter settings: {e}")
            return None