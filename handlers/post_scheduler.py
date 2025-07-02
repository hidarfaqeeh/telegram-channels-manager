#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from telethon import TelegramClient

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self, db, client: TelegramClient):
        self.db = db
        self.client = client
    
    async def schedule_post(self, channel_id: int, message_data: Dict[str, Any], 
                          scheduled_time: datetime) -> bool:
        """Schedule a post for later"""
        try:
            await self.db.add_scheduled_post(
                channel_id=channel_id,
                message_data=message_data,
                scheduled_time=scheduled_time
            )
            
            logger.info(f"Scheduled post for channel {channel_id} at {scheduled_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling post: {e}")
            return False
    
    async def send_scheduled_post(self, post_id: int, channel_id: int, message_data: Dict[str, Any]) -> bool:
        """Send a scheduled post"""
        try:
            entity = await self.client.get_entity(channel_id)
            
            await self.client.send_message(
                entity,
                message_data.get('text', ''),
                file=message_data.get('file'),
                parse_mode=message_data.get('parse_mode', 'html')
            )
            
            await self.db.mark_post_sent(post_id)
            logger.info(f"Sent scheduled post {post_id} to channel {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending scheduled post {post_id}: {e}")
            return False