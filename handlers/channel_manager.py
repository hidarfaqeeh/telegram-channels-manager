#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Channel Manager Handler
======================

Handles all channel management operations including:
- Adding/removing channels
- Managing channel settings
- Monitoring channel activities
- Handling channel events
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat, User, MessageActionChatJoinedByLink
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError

from database.database import DatabaseManager
from filters.message_filters import MessageFilterManager
from formatters.text_formatter import TextFormatter

logger = logging.getLogger(__name__)

class ChannelManager:
    """
    Advanced channel management handler for Telegram channels.
    
    Features:
    - Channel discovery and management
    - Message filtering and formatting
    - Channel statistics tracking
    - User activity monitoring
    - Channel settings management
    """
    
    def __init__(self, client: TelegramClient, db: DatabaseManager):
        self.client = client
        self.db = db
        self.filter_manager = MessageFilterManager()
        self.text_formatter = TextFormatter()
        self.managed_channels: Dict[int, Dict] = {}
        self.channel_stats: Dict[int, Dict] = {}
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers for channel activities"""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            """Handle new messages in managed channels"""
            try:
                if event.is_channel and event.chat_id in self.managed_channels:
                    await self._process_channel_message(event)
            except Exception as e:
                logger.error(f"Error handling new message: {e}")
        
        @self.client.on(events.ChatAction)
        async def handle_chat_action(event):
            """Handle chat actions (joins, leaves, etc.)"""
            try:
                if event.is_channel and event.chat_id in self.managed_channels:
                    await self._process_chat_action(event)
            except Exception as e:
                logger.error(f"Error handling chat action: {e}")
    
    async def add_channel(self, channel_identifier: str) -> Dict[str, Any]:
        """
        Add a new channel to management
        
        Args:
            channel_identifier: Channel username or ID
            
        Returns:
            Dict with operation result
        """
        try:
            # Get channel entity
            channel = await self.client.get_entity(channel_identifier)
            
            if not isinstance(channel, Channel):
                return {
                    'success': False,
                    'error': 'Provided identifier is not a channel'
                }
            
            # Check if we have admin rights
            try:
                permissions = await self.client.get_permissions(channel)
                if not permissions.is_admin:
                    logger.warning(f"No admin permissions for channel {channel.id}")
            except Exception as e:
                logger.warning(f"Could not check permissions: {e}")
            
            # Add to database
            await self.db.add_channel(
                channel_id=channel.id,
                username=channel.username,
                title=channel.title
            )
            
            # Add to managed channels
            self.managed_channels[channel.id] = {
                'entity': channel,
                'title': channel.title,
                'username': channel.username,
                'added_at': datetime.now(),
                'message_count': 0,
                'last_activity': None
            }
            
            # Initialize channel stats
            self.channel_stats[channel.id] = {
                'messages_today': 0,
                'messages_week': 0,
                'messages_month': 0,
                'members_joined_today': 0,
                'members_left_today': 0,
                'last_reset': datetime.now().date()
            }
            
            logger.info(f"✅ Added channel: {channel.title} ({channel.id})")
            
            return {
                'success': True,
                'channel_id': channel.id,
                'title': channel.title,
                'username': channel.username
            }
            
        except ChannelPrivateError:
            return {
                'success': False,
                'error': 'Channel is private or bot was banned'
            }
        except Exception as e:
            logger.error(f"Error adding channel {channel_identifier}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def remove_channel(self, channel_id: int) -> bool:
        """
        Remove a channel from management
        
        Args:
            channel_id: Channel ID to remove
            
        Returns:
            bool: Success status
        """
        try:
            # Remove from database
            success = await self.db.remove_channel(channel_id)
            
            if success:
                # Remove from memory
                self.managed_channels.pop(channel_id, None)
                self.channel_stats.pop(channel_id, None)
                logger.info(f"✅ Removed channel: {channel_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error removing channel {channel_id}: {e}")
            return False
    
    async def get_managed_channels(self) -> List[Dict]:
        """Get list of all managed channels"""
        try:
            channels = await self.db.get_active_channels()
            result = []
            
            for channel in channels:
                channel_info = {
                    'id': channel.channel_id,
                    'title': channel.channel_title,
                    'username': channel.channel_username,
                    'is_active': channel.is_active,
                    'added_at': channel.created_at,
                    'stats': self.channel_stats.get(channel.channel_id, {})
                }
                result.append(channel_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting managed channels: {e}")
            return []
    
    async def _process_channel_message(self, event):
        """Process new message in managed channel"""
        try:
            channel_id = event.chat_id
            message = event.message
            
            # Update statistics
            await self._update_channel_stats(channel_id, 'message')
            
            # Update last activity
            if channel_id in self.managed_channels:
                self.managed_channels[channel_id]['last_activity'] = datetime.now()
                self.managed_channels[channel_id]['message_count'] += 1
            
            # Apply message filters if enabled
            filter_settings = await self.db.get_message_filter(channel_id)
            if filter_settings and filter_settings.enabled:
                await self._apply_message_filters(event, filter_settings)
            
            # Apply text formatting if enabled
            formatting_settings = await self.db.get_message_formatting(channel_id)
            if formatting_settings and formatting_settings.enabled:
                await self._apply_text_formatting(event, formatting_settings)
            
        except Exception as e:
            logger.error(f"Error processing channel message: {e}")
    
    async def _process_chat_action(self, event):
        """Process chat action in managed channel"""
        try:
            channel_id = event.chat_id
            
            # Track member joins/leaves
            if hasattr(event, 'user_joined') and event.user_joined:
                await self._update_channel_stats(channel_id, 'member_joined')
            elif hasattr(event, 'user_left') and event.user_left:
                await self._update_channel_stats(channel_id, 'member_left')
            
        except Exception as e:
            logger.error(f"Error processing chat action: {e}")
    
    async def _apply_message_filters(self, event, filter_settings):
        """Apply message filters to the event"""
        try:
            message_text = event.message.text or ""
            
            # Check with filter manager
            filter_result = await self.filter_manager.filter_message(event.message)
            
            if not filter_result.passed:
                logger.info(f"Message filtered: {filter_result.reason}")
                
                # Delete message if configured
                if filter_settings.delete_filtered:
                    try:
                        await event.delete()
                        logger.info(f"Deleted filtered message in channel {event.chat_id}")
                    except Exception as e:
                        logger.error(f"Could not delete message: {e}")
            
        except Exception as e:
            logger.error(f"Error applying message filters: {e}")
    
    async def _apply_text_formatting(self, event, formatting_settings):
        """Apply text formatting to the message"""
        try:
            if not event.message.text:
                return
            
            original_text = event.message.text
            
            # Apply text formatting
            formatted_text = await self.text_formatter.format_message(
                text=original_text,
                settings={
                    'add_header': formatting_settings.add_header,
                    'add_footer': formatting_settings.add_footer,
                    'header_text': formatting_settings.header_text,
                    'footer_text': formatting_settings.footer_text,
                    'clean_text': formatting_settings.clean_text,
                    'fix_spacing': formatting_settings.fix_spacing
                }
            )
            
            # Edit message if text changed
            if formatted_text != original_text:
                try:
                    await event.edit(formatted_text)
                    logger.info(f"Applied text formatting in channel {event.chat_id}")
                except Exception as e:
                    logger.error(f"Could not edit message: {e}")
            
        except Exception as e:
            logger.error(f"Error applying text formatting: {e}")
    
    async def _update_channel_stats(self, channel_id: int, stat_type: str):
        """Update channel statistics"""
        try:
            if channel_id not in self.channel_stats:
                self.channel_stats[channel_id] = {
                    'messages_today': 0,
                    'messages_week': 0,
                    'messages_month': 0,
                    'members_joined_today': 0,
                    'members_left_today': 0,
                    'last_reset': datetime.now().date()
                }
            
            stats = self.channel_stats[channel_id]
            
            # Reset daily stats if needed
            today = datetime.now().date()
            if stats['last_reset'] != today:
                stats['members_joined_today'] = 0
                stats['members_left_today'] = 0
                stats['messages_today'] = 0
                stats['last_reset'] = today
            
            # Update stats
            if stat_type == 'message':
                stats['messages_today'] += 1
                stats['messages_week'] += 1
                stats['messages_month'] += 1
            elif stat_type == 'member_joined':
                stats['members_joined_today'] += 1
            elif stat_type == 'member_left':
                stats['members_left_today'] += 1
            
        except Exception as e:
            logger.error(f"Error updating channel stats: {e}")
    
    async def get_channel_stats(self, channel_id: int) -> Dict[str, Any]:
        """Get statistics for a specific channel"""
        try:
            if channel_id not in self.channel_stats:
                return {}
            
            stats = self.channel_stats[channel_id].copy()
            
            # Add channel info
            if channel_id in self.managed_channels:
                channel_info = self.managed_channels[channel_id]
                stats.update({
                    'title': channel_info.get('title'),
                    'username': channel_info.get('username'),
                    'total_messages': channel_info.get('message_count', 0),
                    'last_activity': channel_info.get('last_activity')
                })
            
            # Get member count
            try:
                channel = await self.client.get_entity(channel_id)
                if hasattr(channel, 'participants_count'):
                    stats['member_count'] = channel.participants_count
            except Exception:
                stats['member_count'] = 'Unknown'
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting channel stats for {channel_id}: {e}")
            return {}
    
    async def load_managed_channels(self):
        """Load managed channels from database on startup"""
        try:
            channels = await self.db.get_active_channels()
            
            for channel in channels:
                try:
                    # Get channel entity
                    entity = await self.client.get_entity(channel.channel_id)
                    
                    self.managed_channels[channel.channel_id] = {
                        'entity': entity,
                        'title': channel.channel_title,
                        'username': channel.channel_username,
                        'added_at': channel.created_at,
                        'message_count': 0,
                        'last_activity': None
                    }
                    
                    # Initialize stats
                    self.channel_stats[channel.channel_id] = {
                        'messages_today': 0,
                        'messages_week': 0,
                        'messages_month': 0,
                        'members_joined_today': 0,
                        'members_left_today': 0,
                        'last_reset': datetime.now().date()
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not load channel {channel.channel_id}: {e}")
            
            logger.info(f"✅ Loaded {len(self.managed_channels)} managed channels")
            
        except Exception as e:
            logger.error(f"Error loading managed channels: {e}")
    
    async def cleanup_inactive_channels(self, days: int = 30):
        """Remove channels that have been inactive for specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            inactive_channels = []
            
            for channel_id, info in self.managed_channels.items():
                last_activity = info.get('last_activity')
                if not last_activity or last_activity < cutoff_date:
                    inactive_channels.append(channel_id)
            
            for channel_id in inactive_channels:
                await self.remove_channel(channel_id)
                logger.info(f"Removed inactive channel: {channel_id}")
            
            return len(inactive_channels)
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive channels: {e}")
            return 0