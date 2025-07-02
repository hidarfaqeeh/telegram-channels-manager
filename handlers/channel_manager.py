#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError, UserNotParticipantError

logger = logging.getLogger(__name__)

class ChannelManager:
    def __init__(self, db, client: TelegramClient):
        self.db = db
        self.client = client
        
    async def get_channel_info(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed channel information"""
        try:
            entity = await self.client.get_entity(channel_id)
            
            if not isinstance(entity, (Channel, Chat)):
                return None
                
            # Get participant count
            participants = await self.client.get_participants(entity, limit=0)
            
            # Get admins
            admins = []
            try:
                async for admin in self.client.iter_participants(entity, filter='admins'):
                    admins.append({
                        'id': admin.id,
                        'username': getattr(admin, 'username', None),
                        'first_name': getattr(admin, 'first_name', ''),
                        'last_name': getattr(admin, 'last_name', '')
                    })
            except Exception as e:
                logger.warning(f"Could not get admins for {channel_id}: {e}")
                
            return {
                'id': entity.id,
                'title': entity.title,
                'username': getattr(entity, 'username', None),
                'description': getattr(entity, 'about', ''),
                'participant_count': participants.total,
                'admins': admins,
                'is_private': getattr(entity, 'megagroup', False),
                'is_channel': isinstance(entity, Channel),
                'is_verified': getattr(entity, 'verified', False),
                'is_scam': getattr(entity, 'scam', False),
                'is_fake': getattr(entity, 'fake', False),
                'created_date': getattr(entity, 'date', None)
            }
            
        except Exception as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return None
    
    async def check_channel_permissions(self, channel_id: int) -> Dict[str, bool]:
        """Check bot permissions in channel"""
        try:
            entity = await self.client.get_entity(channel_id)
            me = await self.client.get_me()
            
            # Get our permissions
            permissions = await self.client.get_permissions(entity, me)
            
            return {
                'can_send_messages': permissions.send_messages if permissions else False,
                'can_edit_messages': permissions.edit_messages if permissions else False,
                'can_delete_messages': permissions.delete_messages if permissions else False,
                'can_ban_users': permissions.ban_users if permissions else False,
                'can_invite_users': permissions.invite_users if permissions else False,
                'can_pin_messages': permissions.pin_messages if permissions else False,
                'can_add_admins': permissions.add_admins if permissions else False,
                'can_manage_call': permissions.manage_call if permissions else False,
                'is_admin': permissions.is_admin if permissions else False,
                'is_creator': permissions.is_creator if permissions else False
            }
            
        except Exception as e:
            logger.error(f"Error checking permissions for {channel_id}: {e}")
            return {}
    
    async def get_channel_statistics(self, channel_id: int) -> Dict[str, Any]:
        """Get channel statistics"""
        try:
            entity = await self.client.get_entity(channel_id)
            
            # Get recent messages for activity analysis
            messages = []
            async for message in self.client.iter_messages(entity, limit=100):
                messages.append(message)
            
            # Calculate statistics
            total_messages = len(messages)
            
            # Message types count
            text_messages = sum(1 for msg in messages if msg.text)
            media_messages = sum(1 for msg in messages if msg.media)
            forwarded_messages = sum(1 for msg in messages if msg.forward)
            
            # Recent activity (last 24 hours)
            recent_activity = 0
            if messages:
                last_24h = datetime.now() - messages[0].date
                if last_24h.days == 0:
                    for msg in messages:
                        if (datetime.now() - msg.date).days == 0:
                            recent_activity += 1
                        else:
                            break
            
            return {
                'total_messages_analyzed': total_messages,
                'text_messages': text_messages,
                'media_messages': media_messages,
                'forwarded_messages': forwarded_messages,
                'recent_activity_24h': recent_activity,
                'last_message_date': messages[0].date if messages else None,
                'average_message_length': sum(len(msg.text or '') for msg in messages) / total_messages if total_messages > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics for {channel_id}: {e}")
            return {}
    
    async def cleanup_channel_messages(self, channel_id: int, criteria: Dict[str, Any]) -> int:
        """Clean up channel messages based on criteria"""
        try:
            entity = await self.client.get_entity(channel_id)
            deleted_count = 0
            
            # Check permissions first
            permissions = await self.check_channel_permissions(channel_id)
            if not permissions.get('can_delete_messages', False):
                logger.warning(f"No permission to delete messages in {channel_id}")
                return 0
            
            # Get messages to delete based on criteria
            messages_to_delete = []
            
            async for message in self.client.iter_messages(entity, limit=criteria.get('limit', 100)):
                should_delete = False
                
                # Check deletion criteria
                if criteria.get('delete_empty', False) and not message.text and not message.media:
                    should_delete = True
                
                if criteria.get('delete_short', False) and message.text and len(message.text) < criteria.get('min_length', 10):
                    should_delete = True
                
                if criteria.get('delete_forwarded', False) and message.forward:
                    should_delete = True
                
                if criteria.get('delete_media_only', False) and message.media and not message.text:
                    should_delete = True
                
                if criteria.get('keywords') and message.text:
                    for keyword in criteria['keywords']:
                        if keyword.lower() in message.text.lower():
                            should_delete = True
                            break
                
                if should_delete:
                    messages_to_delete.append(message.id)
                    
                    # Delete in batches
                    if len(messages_to_delete) >= 100:
                        await self.client.delete_messages(entity, messages_to_delete)
                        deleted_count += len(messages_to_delete)
                        messages_to_delete = []
                        await asyncio.sleep(1)  # Rate limiting
            
            # Delete remaining messages
            if messages_to_delete:
                await self.client.delete_messages(entity, messages_to_delete)
                deleted_count += len(messages_to_delete)
            
            logger.info(f"Deleted {deleted_count} messages from channel {channel_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up channel {channel_id}: {e}")
            return 0
    
    async def backup_channel_messages(self, channel_id: int, limit: int = 1000) -> List[Dict[str, Any]]:
        """Backup channel messages"""
        try:
            entity = await self.client.get_entity(channel_id)
            messages_backup = []
            
            async for message in self.client.iter_messages(entity, limit=limit):
                message_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'sender_id': message.sender_id,
                    'is_forwarded': bool(message.forward),
                    'has_media': bool(message.media),
                    'media_type': str(type(message.media).__name__) if message.media else None,
                    'views': getattr(message, 'views', 0),
                    'forwards': getattr(message, 'forwards', 0),
                    'replies': getattr(message.replies, 'replies', 0) if message.replies else 0
                }
                
                # Add forward info if exists
                if message.forward:
                    message_data['forward_info'] = {
                        'from_id': message.forward.from_id,
                        'from_name': message.forward.from_name,
                        'date': message.forward.date.isoformat() if message.forward.date else None
                    }
                
                messages_backup.append(message_data)
            
            logger.info(f"Backed up {len(messages_backup)} messages from channel {channel_id}")
            return messages_backup
            
        except Exception as e:
            logger.error(f"Error backing up channel {channel_id}: {e}")
            return []
    
    async def monitor_channel_activity(self, channel_id: int) -> Dict[str, Any]:
        """Monitor channel activity and generate report"""
        try:
            # Get channel info
            channel_info = await self.get_channel_info(channel_id)
            if not channel_info:
                return {}
            
            # Get statistics
            stats = await self.get_channel_statistics(channel_id)
            
            # Get permissions
            permissions = await self.check_channel_permissions(channel_id)
            
            # Combine all information
            report = {
                'channel_info': channel_info,
                'statistics': stats,
                'permissions': permissions,
                'monitoring_time': datetime.now().isoformat(),
                'status': 'active' if stats.get('recent_activity_24h', 0) > 0 else 'inactive'
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error monitoring channel {channel_id}: {e}")
            return {}