#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl import functions

logger = logging.getLogger(__name__)

class AutoAcceptManager:
    def __init__(self, db, client: TelegramClient):
        self.db = db
        self.client = client
        self.pending_requests = {}
    
    async def schedule_auto_accept(self, channel_id: int, user_id: int, delay_seconds: int):
        """Schedule auto accept for a user"""
        try:
            accept_time = datetime.now() + timedelta(seconds=delay_seconds)
            
            if channel_id not in self.pending_requests:
                self.pending_requests[channel_id] = []
            
            self.pending_requests[channel_id].append({
                'user_id': user_id,
                'accept_time': accept_time
            })
            
            logger.info(f"Scheduled auto accept for user {user_id} in channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling auto accept: {e}")
    
    async def process_pending_requests(self):
        """Process all pending auto accept requests"""
        try:
            current_time = datetime.now()
            
            for channel_id, requests in self.pending_requests.items():
                entity = await self.client.get_entity(channel_id)
                
                # Process requests that are due
                for request in requests[:]:
                    if current_time >= request['accept_time']:
                        try:
                            await self.client(functions.messages.HideChatJoinRequestRequest(
                                peer=entity,
                                user_id=request['user_id'],
                                approved=True
                            ))
                            
                            logger.info(f"Auto accepted user {request['user_id']} in channel {channel_id}")
                            requests.remove(request)
                            
                        except Exception as e:
                            logger.error(f"Error auto accepting user {request['user_id']}: {e}")
                            requests.remove(request)
                        
                        await asyncio.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Error processing pending requests: {e}")
    
    async def get_pending_join_requests(self, channel_id: int) -> List[Dict[str, Any]]:
        """Get pending join requests for channel"""
        try:
            entity = await self.client.get_entity(channel_id)
            
            requests = await self.client(functions.messages.GetChatJoinRequestsRequest(
                peer=entity,
                offset_date=None,
                offset_user=None,
                limit=100
            ))
            
            pending_requests = []
            for user in requests.users:
                pending_requests.append({
                    'user_id': user.id,
                    'username': getattr(user, 'username', None),
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', ''),
                    'request_date': getattr(user, 'date', None)
                })
            
            return pending_requests
            
        except Exception as e:
            logger.error(f"Error getting pending requests for channel {channel_id}: {e}")
            return []