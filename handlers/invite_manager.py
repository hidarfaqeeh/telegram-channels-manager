#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl import functions
from telethon.tl.types import ChatInviteExported
from telethon.errors import FloodWaitError, ChatAdminRequiredError

logger = logging.getLogger(__name__)

class InviteManager:
    def __init__(self, db, client: TelegramClient):
        self.db = db
        self.client = client
        
    async def create_invite_link(self, channel_id: int, link_name: str, 
                               expire_date: Optional[datetime] = None,
                               member_limit: Optional[int] = None,
                               creates_join_request: bool = False) -> Optional[str]:
        """Create a new invite link for channel"""
        try:
            entity = await self.client.get_entity(channel_id)
            
            # Create invite link
            invite = await self.client(
                functions.messages.ExportChatInviteRequest(
                    peer=entity,
                    expire_date=expire_date,
                    usage_limit=member_limit,
                    request_needed=creates_join_request
                )
            )
            
            if isinstance(invite, ChatInviteExported):
                await self.db.create_invite_link(
                    channel_id=channel_id,
                    link_name=link_name,
                    invite_link=invite.link,
                    expire_date=expire_date,
                    member_limit=member_limit,
                    creates_join_request=creates_join_request
                )
                
                logger.info(f"Created invite link for channel {channel_id}: {link_name}")
                return invite.link
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating invite link for channel {channel_id}: {e}")
            return None
    
    async def revoke_invite_link(self, channel_id: int, invite_link: str) -> bool:
        """Revoke an invite link"""
        try:
            entity = await self.client.get_entity(channel_id)
            
            # Revoke the link
            await self.client(
                functions.messages.EditExportedChatInviteRequest(
                    peer=entity,
                    link=invite_link,
                    revoked=True
                )
            )
            
            # Update database
            # Note: You'll need to add this method to database.py
            # await self.db.revoke_invite_link_by_url(invite_link)
            
            logger.info(f"Revoked invite link for channel {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking invite link for channel {channel_id}: {e}")
            return False
    
    async def get_channel_invite_links(self, channel_id: int) -> List[Dict[str, Any]]:
        """Get all invite links for a channel"""
        try:
            return await self.db.get_invite_links(channel_id)
        except Exception as e:
            logger.error(f"Error getting invite links for channel {channel_id}: {e}")
            return []
    
    async def get_invite_link_stats(self, channel_id: int, invite_link: str) -> Dict[str, Any]:
        """Get statistics for a specific invite link"""
        try:
            entity = await self.client.get_entity(channel_id)
            
            # Get invite link importers
            importers = await self.client(
                functions.messages.GetChatInviteImportersRequest(
                    peer=entity,
                    link=invite_link,
                    offset_date=None,
                    offset_user=None,
                    limit=100
                )
            )
            
            stats = {
                'total_importers': importers.count,
                'importers': []
            }
            
            for user in importers.users:
                stats['importers'].append({
                    'user_id': user.id,
                    'username': getattr(user, 'username', None),
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', ''),
                    'join_date': getattr(user, 'date', None)
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting invite link stats: {e}")
            return {}
    
    async def cleanup_expired_links(self, channel_id: int) -> int:
        """Clean up expired invite links"""
        try:
            current_links = await self.get_channel_invite_links(channel_id)
            cleaned_count = 0
            
            for link_info in current_links:
                # Check if link is expired
                if link_info.get('expire_date'):
                    if datetime.now() > link_info['expire_date']:
                        success = await self.revoke_invite_link(channel_id, link_info['link'])
                        if success:
                            cleaned_count += 1
                
                # Check if usage limit reached
                elif link_info.get('usage_limit'):
                    if link_info.get('usage', 0) >= link_info['usage_limit']:
                        success = await self.revoke_invite_link(channel_id, link_info['link'])
                        if success:
                            cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired links for channel {channel_id}")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired links: {e}")
            return 0
    
    async def monitor_invite_usage(self, channel_id: int) -> Dict[str, Any]:
        """Monitor invite link usage and generate report"""
        try:
            links = await self.get_channel_invite_links(channel_id)
            
            total_links = len(links)
            active_links = sum(1 for link in links if not link.get('revoked', False))
            expired_links = sum(1 for link in links if link.get('expire_date') and datetime.now() > link['expire_date'])
            
            total_usage = sum(link.get('usage', 0) for link in links)
            
            # Get most used link
            most_used = max(links, key=lambda x: x.get('usage', 0)) if links else None
            
            report = {
                'channel_id': channel_id,
                'total_links': total_links,
                'active_links': active_links,
                'expired_links': expired_links,
                'total_usage': total_usage,
                'most_used_link': {
                    'link': most_used.get('link', '') if most_used else '',
                    'usage': most_used.get('usage', 0) if most_used else 0
                },
                'monitoring_time': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error monitoring invite usage for channel {channel_id}: {e}")
            return {}
    
    async def create_temporary_link(self, channel_id: int, duration_hours: int = 24, member_limit: int = 50) -> Optional[str]:
        """Create a temporary invite link"""
        expire_date = datetime.now() + timedelta(hours=duration_hours)
        
        return await self.create_invite_link(
            channel_id=channel_id,
            link_name=f"temp_link_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            expire_date=expire_date,
            member_limit=member_limit,
            creates_join_request=False
        )
    
    async def bulk_create_links(self, channel_id: int, count: int, **kwargs) -> List[str]:
        """Create multiple invite links at once"""
        links = []
        
        for i in range(count):
            link_name = f"bulk_link_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            link = await self.create_invite_link(
                channel_id=channel_id,
                link_name=link_name,
                **kwargs
            )
            
            if link:
                links.append(link)
                
            # Rate limiting
            await asyncio.sleep(0.5)
        
        logger.info(f"Created {len(links)} bulk invite links for channel {channel_id}")
        return links