#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from telethon import TelegramClient, events
from telethon.tl.types import Message, Channel, Chat, User
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import schedule
import json

# Import local modules
import config
from database.database import DatabaseManager
from filters.message_filters import MessageFilterManager
from formatters.text_formatter import TextFormatter
from utils.helpers import is_admin, format_duration, split_message, get_entity_info
from handlers.channel_manager import ChannelManager
from handlers.invite_manager import InviteManager
from handlers.admin_manager import AdminManager
from handlers.post_scheduler import PostScheduler
from handlers.auto_accept import AutoAcceptManager
from handlers.translator import TranslationManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TelegramUserBot:
    def __init__(self):
        # Initialize Telegram client
        self.client = TelegramClient(
            config.SESSION_NAME,
            config.API_ID,
            config.API_HASH
        )
        
        # Initialize database
        self.db = DatabaseManager(config.DATABASE_URL)
        
        # Initialize managers
        self.filter_manager = None
        self.text_formatter = None
        self.channel_manager = None
        self.invite_manager = None
        self.admin_manager = None
        self.post_scheduler = None
        self.auto_accept_manager = None
        self.translation_manager = None
        
        # Bot state
        self.is_running = False
        self.managed_channels = {}
        
        # Statistics
        self.stats = {
            'messages_processed': 0,
            'messages_forwarded': 0,
            'messages_filtered': 0,
            'start_time': None
        }
    
    async def start(self):
        """Start the userbot"""
        try:
            logger.info("Starting Telegram UserBot...")
            
            # Initialize database
            await self.db.init_db()
            logger.info("Database initialized")
            
            # Initialize managers
            self.filter_manager = MessageFilterManager(self.db)
            self.text_formatter = TextFormatter(self.db)
            self.channel_manager = ChannelManager(self.client, self.db)
            self.invite_manager = InviteManager(self.client, self.db)
            self.admin_manager = AdminManager(self.client, self.db)
            self.post_scheduler = PostScheduler(self.client, self.db)
            self.auto_accept_manager = AutoAcceptManager(self.client, self.db)
            self.translation_manager = TranslationManager()
            
            # Connect to Telegram
            await self.client.start(phone=config.PHONE_NUMBER)
            logger.info("Connected to Telegram")
            
            # Load managed channels
            await self._load_managed_channels()
            
            # Setup event handlers
            self._setup_event_handlers()
            
            # Start background tasks
            asyncio.create_task(self._background_tasks())
            
            self.is_running = True
            self.stats['start_time'] = datetime.now()
            
            logger.info("UserBot started successfully!")
            
            # Keep the bot running
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Failed to start userbot: {e}")
            raise
    
    async def stop(self):
        """Stop the userbot"""
        logger.info("Stopping UserBot...")
        self.is_running = False
        
        if self.client.is_connected():
            await self.client.disconnect()
        
        if self.db:
            await self.db.close()
        
        logger.info("UserBot stopped")
    
    async def _load_managed_channels(self):
        """Load managed channels from database"""
        try:
            channels = await self.db.get_active_channels()
            for channel in channels:
                self.managed_channels[channel.channel_id] = {
                    'title': channel.channel_title,
                    'username': channel.channel_username,
                    'settings': channel
                }
            
            logger.info(f"Loaded {len(self.managed_channels)} managed channels")
            
        except Exception as e:
            logger.error(f"Failed to load managed channels: {e}")
    
    def _setup_event_handlers(self):
        """Setup Telethon event handlers"""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            """Handle new messages"""
            try:
                # Only process messages from managed channels
                if event.chat_id not in self.managed_channels:
                    return
                
                message = event.message
                self.stats['messages_processed'] += 1
                
                # Check if message should be filtered
                should_filter, reason = await self.filter_manager.should_filter_message(
                    message, event.chat_id
                )
                
                if should_filter:
                    logger.info(f"Message filtered in {event.chat_id}: {reason}")
                    self.stats['messages_filtered'] += 1
                    
                    # Delete message if configured
                    channel_settings = self.managed_channels[event.chat_id]['settings']
                    if channel_settings.delete_and_resend:
                        await message.delete()
                    
                    return
                
                # Process message (format, translate, etc.)
                await self._process_message(message, event.chat_id)
                
            except Exception as e:
                logger.error(f"Error handling new message: {e}")
        
        @self.client.on(events.ChatAction)
        async def handle_chat_action(event):
            """Handle chat actions like new members"""
            try:
                if event.user_joined or event.user_added:
                    # Handle new member
                    await self._handle_new_member(event)
                
            except Exception as e:
                logger.error(f"Error handling chat action: {e}")
        
        logger.info("Event handlers registered")
    
    async def _process_message(self, message: Message, channel_id: int):
        """Process a message (format, translate, add headers/footers)"""
        try:
            channel_settings = self.managed_channels[channel_id]['settings']
            
            # Get original message text
            original_text = message.text or ""
            processed_text = original_text
            
            # Apply text formatting
            if original_text:
                processed_text = await self.text_formatter.format_message_text(
                    original_text, channel_id
                )
            
            # Add header
            if channel_settings.auto_header and channel_settings.custom_header:
                processed_text = f"{channel_settings.custom_header}\n\n{processed_text}"
            
            # Add footer
            if channel_settings.auto_footer and channel_settings.custom_footer:
                processed_text = f"{processed_text}\n\n{channel_settings.custom_footer}"
            
            # Translate if enabled
            translation_settings = await self.db.get_translation_settings(channel_id)
            if translation_settings and translation_settings.enable_translation:
                processed_text = await self.translation_manager.translate_text(
                    processed_text, translation_settings.target_language
                )
            
            # Check if text changed
            if processed_text != original_text:
                if channel_settings.edit_mode:
                    # Edit the message
                    await message.edit(processed_text)
                    logger.info(f"Message edited in channel {channel_id}")
                elif channel_settings.delete_and_resend:
                    # Delete and resend
                    await message.delete()
                    await self.client.send_message(channel_id, processed_text)
                    logger.info(f"Message deleted and resent in channel {channel_id}")
                
                self.stats['messages_forwarded'] += 1
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _handle_new_member(self, event):
        """Handle new member joining"""
        try:
            channel_id = event.chat_id
            if channel_id not in self.managed_channels:
                return
            
            # Check auto-accept settings
            auto_accept_settings = await self.db.get_auto_accept_settings(channel_id)
            if auto_accept_settings and auto_accept_settings.enable_auto_accept:
                # Schedule auto-accept
                await self.auto_accept_manager.schedule_auto_accept(
                    channel_id, event.user_id, auto_accept_settings.accept_delay
                )
            
        except Exception as e:
            logger.error(f"Error handling new member: {e}")
    
    async def _background_tasks(self):
        """Run background tasks"""
        while self.is_running:
            try:
                # Process scheduled posts
                await self._process_scheduled_posts()
                
                # Process auto-accept queue
                await self._process_auto_accept()
                
                # Update statistics
                await self._update_statistics()
                
                # Sleep for a bit
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in background tasks: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_scheduled_posts(self):
        """Process scheduled posts"""
        try:
            pending_posts = await self.db.get_pending_posts()
            
            for post in pending_posts:
                try:
                    # Parse message data
                    message_data = json.loads(post.message_data)
                    
                    # Send the message
                    await self.client.send_message(
                        post.channel_id,
                        message_data.get('text', ''),
                        file=message_data.get('file'),
                        parse_mode=message_data.get('parse_mode', 'html')
                    )
                    
                    # Mark as sent
                    await self.db.mark_post_sent(post.id)
                    
                    logger.info(f"Scheduled post sent to channel {post.channel_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to send scheduled post {post.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing scheduled posts: {e}")
    
    async def _process_auto_accept(self):
        """Process auto-accept queue"""
        try:
            await self.auto_accept_manager.process_pending_requests()
        except Exception as e:
            logger.error(f"Error processing auto-accept: {e}")
    
    async def _update_statistics(self):
        """Update bot statistics"""
        try:
            uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta()
            
            # Log statistics periodically
            if uptime.total_seconds() % 3600 < 30:  # Every hour
                logger.info(f"Bot Statistics - Uptime: {format_duration(int(uptime.total_seconds()))}, "
                          f"Messages Processed: {self.stats['messages_processed']}, "
                          f"Messages Forwarded: {self.stats['messages_forwarded']}, "
                          f"Messages Filtered: {self.stats['messages_filtered']}")
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    # Channel Management Methods
    async def add_channel(self, channel_identifier: str) -> bool:
        """Add a new channel to management"""
        try:
            entity = await self.client.get_entity(channel_identifier)
            
            if isinstance(entity, (Channel, Chat)):
                channel = await self.db.add_channel(
                    entity.id,
                    getattr(entity, 'username', None),
                    entity.title
                )
                
                self.managed_channels[entity.id] = {
                    'title': entity.title,
                    'username': getattr(entity, 'username', None),
                    'settings': channel
                }
                
                logger.info(f"Added channel: {entity.title} ({entity.id})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add channel {channel_identifier}: {e}")
            return False
    
    async def remove_channel(self, channel_id: int) -> bool:
        """Remove a channel from management"""
        try:
            success = await self.db.remove_channel(channel_id)
            if success and channel_id in self.managed_channels:
                del self.managed_channels[channel_id]
                logger.info(f"Removed channel: {channel_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove channel {channel_id}: {e}")
            return False
    
    async def get_managed_channels(self) -> List[Dict[str, Any]]:
        """Get list of managed channels"""
        channels = []
        for channel_id, info in self.managed_channels.items():
            try:
                # Get additional info from Telegram
                entity = await self.client.get_entity(channel_id)
                participant_count = await self.client.get_participants(entity, limit=0)
                
                channels.append({
                    'id': channel_id,
                    'title': info['title'],
                    'username': info['username'],
                    'participant_count': participant_count.total,
                    'settings': info['settings']
                })
                
            except Exception as e:
                logger.error(f"Error getting channel info for {channel_id}: {e}")
                channels.append({
                    'id': channel_id,
                    'title': info['title'],
                    'username': info['username'],
                    'participant_count': 0,
                    'settings': info['settings']
                })
        
        return channels
    
    def get_bot_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        uptime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta()
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': format_duration(int(uptime.total_seconds())),
            'managed_channels': len(self.managed_channels),
            'messages_processed': self.stats['messages_processed'],
            'messages_forwarded': self.stats['messages_forwarded'],
            'messages_filtered': self.stats['messages_filtered'],
            'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None
        }

# Global bot instance
bot_instance = None

async def main():
    """Main function"""
    global bot_instance
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        if bot_instance:
            asyncio.create_task(bot_instance.stop())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create and start bot
        bot_instance = TelegramUserBot()
        await bot_instance.start()
        
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if bot_instance:
            await bot_instance.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)