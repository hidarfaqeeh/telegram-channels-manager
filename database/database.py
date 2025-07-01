from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import asyncio
import logging
from typing import Optional, List, Dict, Any
from .models import Base, Channel, InviteLink, ChannelAdmin, MessageFilter, MessageFormatting, ScheduledPost, WordReplacement, TranslationSettings, AutoAcceptSettings, BotSettings
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        
    async def init_db(self):
        """Initialize database connection and create tables"""
        try:
            # Create async engine for async operations
            if self.database_url.startswith('sqlite'):
                self.async_engine = create_async_engine(
                    self.database_url.replace('sqlite://', 'sqlite+aiosqlite://'),
                    echo=False
                )
            else:
                self.async_engine = create_async_engine(self.database_url, echo=False)
                
            # Create sync engine for sync operations
            self.engine = create_engine(
                self.database_url.replace('sqlite+aiosqlite://', 'sqlite://'),
                echo=False
            )
            
            # Create session makers
            self.AsyncSessionLocal = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            
            # Create all tables
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def get_async_session(self) -> AsyncSession:
        """Get async database session"""
        async with self.AsyncSessionLocal() as session:
            yield session
    
    def get_sync_session(self) -> Session:
        """Get sync database session"""
        return self.SessionLocal()
    
    # Channel Management Methods
    async def add_channel(self, channel_id: int, username: str = None, title: str = "Unknown Channel") -> Channel:
        """Add a new channel to database"""
        async with self.AsyncSessionLocal() as session:
            try:
                # Check if channel already exists
                existing = await session.get(Channel, channel_id)
                if existing:
                    existing.channel_username = username
                    existing.channel_title = title
                    existing.is_active = True
                    existing.updated_at = datetime.utcnow()
                    await session.commit()
                    return existing
                
                # Create new channel
                channel = Channel(
                    channel_id=channel_id,
                    channel_username=username,
                    channel_title=title
                )
                session.add(channel)
                await session.commit()
                await session.refresh(channel)
                return channel
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to add channel {channel_id}: {e}")
                raise
    
    async def remove_channel(self, channel_id: int) -> bool:
        """Remove a channel from database"""
        async with self.AsyncSessionLocal() as session:
            try:
                channel = await session.get(Channel, channel_id)
                if channel:
                    channel.is_active = False
                    await session.commit()
                    return True
                return False
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to remove channel {channel_id}: {e}")
                return False
    
    async def get_channel(self, channel_id: int) -> Optional[Channel]:
        """Get channel by ID"""
        async with self.AsyncSessionLocal() as session:
            return await session.get(Channel, channel_id)
    
    async def get_active_channels(self) -> List[Channel]:
        """Get all active channels"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM channels WHERE is_active = true"
            )
            return result.fetchall()
    
    # Invite Link Management
    async def create_invite_link(self, channel_id: int, link_name: str, invite_link: str, 
                               expire_date: datetime = None, member_limit: int = None,
                               creates_join_request: bool = False) -> InviteLink:
        """Create a new invite link"""
        async with self.AsyncSessionLocal() as session:
            try:
                link = InviteLink(
                    channel_id=channel_id,
                    link_name=link_name,
                    invite_link=invite_link,
                    expire_date=expire_date,
                    member_limit=member_limit,
                    creates_join_request=creates_join_request
                )
                session.add(link)
                await session.commit()
                await session.refresh(link)
                return link
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to create invite link: {e}")
                raise
    
    async def get_invite_links(self, channel_id: int) -> List[InviteLink]:
        """Get all invite links for a channel"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM invite_links WHERE channel_id = ? AND is_revoked = false",
                (channel_id,)
            )
            return result.fetchall()
    
    async def revoke_invite_link(self, link_id: int) -> bool:
        """Revoke an invite link"""
        async with self.AsyncSessionLocal() as session:
            try:
                link = await session.get(InviteLink, link_id)
                if link:
                    link.is_revoked = True
                    await session.commit()
                    return True
                return False
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to revoke invite link {link_id}: {e}")
                return False
    
    # Message Filter Management
    async def get_message_filter(self, channel_id: int) -> Optional[MessageFilter]:
        """Get message filter settings for a channel"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM message_filters WHERE channel_id = ?",
                (channel_id,)
            )
            return result.fetchone()
    
    async def update_message_filter(self, channel_id: int, **kwargs) -> MessageFilter:
        """Update message filter settings"""
        async with self.AsyncSessionLocal() as session:
            try:
                # Get existing filter or create new one
                result = await session.execute(
                    "SELECT * FROM message_filters WHERE channel_id = ?",
                    (channel_id,)
                )
                filter_obj = result.fetchone()
                
                if not filter_obj:
                    filter_obj = MessageFilter(channel_id=channel_id)
                    session.add(filter_obj)
                
                # Update attributes
                for key, value in kwargs.items():
                    if hasattr(filter_obj, key):
                        setattr(filter_obj, key, value)
                
                filter_obj.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(filter_obj)
                return filter_obj
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update message filter for channel {channel_id}: {e}")
                raise
    
    # Message Formatting Management
    async def get_message_formatting(self, channel_id: int) -> Optional[MessageFormatting]:
        """Get message formatting settings for a channel"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM message_formatting WHERE channel_id = ?",
                (channel_id,)
            )
            return result.fetchone()
    
    async def update_message_formatting(self, channel_id: int, **kwargs) -> MessageFormatting:
        """Update message formatting settings"""
        async with self.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    "SELECT * FROM message_formatting WHERE channel_id = ?",
                    (channel_id,)
                )
                formatting = result.fetchone()
                
                if not formatting:
                    formatting = MessageFormatting(channel_id=channel_id)
                    session.add(formatting)
                
                for key, value in kwargs.items():
                    if hasattr(formatting, key):
                        setattr(formatting, key, value)
                
                formatting.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(formatting)
                return formatting
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update message formatting for channel {channel_id}: {e}")
                raise
    
    # Word Replacement Management
    async def add_word_replacement(self, channel_id: int, original: str, replacement: str) -> WordReplacement:
        """Add a word replacement rule"""
        async with self.AsyncSessionLocal() as session:
            try:
                word_replacement = WordReplacement(
                    channel_id=channel_id,
                    original_word=original,
                    replacement_word=replacement
                )
                session.add(word_replacement)
                await session.commit()
                await session.refresh(word_replacement)
                return word_replacement
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to add word replacement: {e}")
                raise
    
    async def get_word_replacements(self, channel_id: int) -> List[WordReplacement]:
        """Get all word replacements for a channel"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM word_replacements WHERE channel_id = ? AND is_active = true",
                (channel_id,)
            )
            return result.fetchall()
    
    async def remove_word_replacement(self, replacement_id: int) -> bool:
        """Remove a word replacement rule"""
        async with self.AsyncSessionLocal() as session:
            try:
                replacement = await session.get(WordReplacement, replacement_id)
                if replacement:
                    replacement.is_active = False
                    await session.commit()
                    return True
                return False
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to remove word replacement {replacement_id}: {e}")
                return False
    
    # Scheduled Posts Management
    async def add_scheduled_post(self, channel_id: int, message_data: dict, scheduled_time: datetime) -> ScheduledPost:
        """Add a scheduled post"""
        async with self.AsyncSessionLocal() as session:
            try:
                post = ScheduledPost(
                    channel_id=channel_id,
                    message_data=json.dumps(message_data),
                    scheduled_time=scheduled_time
                )
                session.add(post)
                await session.commit()
                await session.refresh(post)
                return post
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to add scheduled post: {e}")
                raise
    
    async def get_pending_posts(self) -> List[ScheduledPost]:
        """Get all pending scheduled posts"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM scheduled_posts WHERE is_sent = false AND scheduled_time <= ?",
                (datetime.utcnow(),)
            )
            return result.fetchall()
    
    async def mark_post_sent(self, post_id: int) -> bool:
        """Mark a scheduled post as sent"""
        async with self.AsyncSessionLocal() as session:
            try:
                post = await session.get(ScheduledPost, post_id)
                if post:
                    post.is_sent = True
                    await session.commit()
                    return True
                return False
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to mark post {post_id} as sent: {e}")
                return False
    
    # Translation Settings
    async def get_translation_settings(self, channel_id: int) -> Optional[TranslationSettings]:
        """Get translation settings for a channel"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM translation_settings WHERE channel_id = ?",
                (channel_id,)
            )
            return result.fetchone()
    
    async def update_translation_settings(self, channel_id: int, **kwargs) -> TranslationSettings:
        """Update translation settings"""
        async with self.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    "SELECT * FROM translation_settings WHERE channel_id = ?",
                    (channel_id,)
                )
                settings = result.fetchone()
                
                if not settings:
                    settings = TranslationSettings(channel_id=channel_id)
                    session.add(settings)
                
                for key, value in kwargs.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
                
                settings.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(settings)
                return settings
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update translation settings for channel {channel_id}: {e}")
                raise
    
    # Auto Accept Settings
    async def get_auto_accept_settings(self, channel_id: int) -> Optional[AutoAcceptSettings]:
        """Get auto accept settings for a channel"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT * FROM auto_accept_settings WHERE channel_id = ?",
                (channel_id,)
            )
            return result.fetchone()
    
    async def update_auto_accept_settings(self, channel_id: int, **kwargs) -> AutoAcceptSettings:
        """Update auto accept settings"""
        async with self.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    "SELECT * FROM auto_accept_settings WHERE channel_id = ?",
                    (channel_id,)
                )
                settings = result.fetchone()
                
                if not settings:
                    settings = AutoAcceptSettings(channel_id=channel_id)
                    session.add(settings)
                
                for key, value in kwargs.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
                
                settings.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(settings)
                return settings
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to update auto accept settings for channel {channel_id}: {e}")
                raise
    
    # Bot Settings
    async def get_setting(self, key: str) -> Optional[str]:
        """Get a bot setting"""
        async with self.AsyncSessionLocal() as session:
            result = await session.execute(
                "SELECT setting_value FROM bot_settings WHERE setting_key = ?",
                (key,)
            )
            row = result.fetchone()
            return row[0] if row else None
    
    async def set_setting(self, key: str, value: str) -> None:
        """Set a bot setting"""
        async with self.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    "SELECT * FROM bot_settings WHERE setting_key = ?",
                    (key,)
                )
                setting = result.fetchone()
                
                if setting:
                    setting.setting_value = value
                    setting.updated_at = datetime.utcnow()
                else:
                    setting = BotSettings(setting_key=key, setting_value=value)
                    session.add(setting)
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to set setting {key}: {e}")
                raise
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()