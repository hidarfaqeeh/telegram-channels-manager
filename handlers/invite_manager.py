#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Invite Manager Handler
=====================

Handles all invite link management operations including:
- Creating and managing invite links
- Monitoring invite link usage
- Auto-generating invite links
- Link expiration management
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError
from telethon.tl.functions.messages import ExportChatInviteRequest, EditExportedChatInviteRequest
from telethon.tl.types import ChatInviteExported

from database.database import DatabaseManager

logger = logging.getLogger(__name__)

class InviteManager:
    """
    Advanced invite link management handler for Telegram channels.
    
    Features:
    - Create and revoke invite links
    - Set expiration dates and usage limits
    - Monitor link usage statistics
    - Auto-generate links for new channels
    - Bulk link management
    """
    
    def __init__(self, client: TelegramClient, db: DatabaseManager):
        self.client = client
        self.db = db
        self.active_links: Dict[int, List[Dict]] = {}  # channel_id -> list of links
    
    async def create_invite_link(self, 
                               channel_id: int,
                               link_name: str = "Default Link",
                               expire_date: Optional[datetime] = None,
                               usage_limit: Optional[int] = None,
                               request_needed: bool = False) -> Dict[str, Any]:
        """
        Create a new invite link for a channel
        
        Args:
            channel_id: Channel ID
            link_name: Name for the invite link
            expire_date: When the link should expire
            usage_limit: Maximum number of uses
            request_needed: Whether admin approval is required
            
        Returns:
            Dict with operation result
        """
        try:
            # Get channel entity
            channel = await self.client.get_entity(channel_id)
            
            # Create invite link
            result = await self.client(ExportChatInviteRequest(
                peer=channel,
                expire_date=expire_date,
                usage_limit=usage_limit,
                request_needed=request_needed,
                title=link_name
            ))
            
            if isinstance(result, ChatInviteExported):
                # Save to database
                invite_link = await self.db.create_invite_link(
                    channel_id=channel_id,
                    link_name=link_name,
                    invite_link=result.link,
                    expire_date=expire_date,
                    member_limit=usage_limit,
                    creates_join_request=request_needed
                )
                
                # Add to memory
                if channel_id not in self.active_links:
                    self.active_links[channel_id] = []
                
                link_info = {
                    'id': invite_link.id,
                    'name': link_name,
                    'link': result.link,
                    'expire_date': expire_date,
                    'usage_limit': usage_limit,
                    'request_needed': request_needed,
                    'usage_count': 0,
                    'created_at': datetime.now()
                }
                self.active_links[channel_id].append(link_info)
                
                logger.info(f"✅ Created invite link '{link_name}' for channel {channel_id}")
                
                return {
                    'success': True,
                    'link': result.link,
                    'link_id': invite_link.id,
                    'name': link_name
                }
            
            return {
                'success': False,
                'error': 'Failed to create invite link'
            }
            
        except ChatAdminRequiredError:
            return {
                'success': False,
                'error': 'Admin rights required to create invite links'
            }
        except Exception as e:
            logger.error(f"Error creating invite link: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def revoke_invite_link(self, link_id: int) -> Dict[str, Any]:
        """
        Revoke an invite link
        
        Args:
            link_id: Database ID of the link to revoke
            
        Returns:
            Dict with operation result
        """
        try:
            # Revoke in database
            success = await self.db.revoke_invite_link(link_id)
            
            if success:
                # Remove from memory
                for channel_id, links in self.active_links.items():
                    self.active_links[channel_id] = [
                        link for link in links if link['id'] != link_id
                    ]
                
                logger.info(f"✅ Revoked invite link {link_id}")
                
                return {
                    'success': True,
                    'message': 'Invite link revoked successfully'
                }
            
            return {
                'success': False,
                'error': 'Link not found or already revoked'
            }
            
        except Exception as e:
            logger.error(f"Error revoking invite link {link_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_channel_invite_links(self, channel_id: int) -> List[Dict]:
        """
        Get all active invite links for a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            List of invite link information
        """
        try:
            links = await self.db.get_invite_links(channel_id)
            result = []
            
            for link in links:
                link_info = {
                    'id': link.id,
                    'name': link.link_name,
                    'link': link.invite_link,
                    'expire_date': link.expire_date,
                    'usage_limit': link.member_limit,
                    'request_needed': link.creates_join_request,
                    'usage_count': link.usage_count,
                    'created_at': link.created_at,
                    'is_revoked': link.is_revoked
                }
                result.append(link_info)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting invite links for channel {channel_id}: {e}")
            return []
    
    async def auto_create_invite_link(self, channel_id: int, channel_title: str) -> Optional[str]:
        """
        Auto-create a default invite link for a new channel
        
        Args:
            channel_id: Channel ID
            channel_title: Channel title for link name
            
        Returns:
            Invite link URL or None if failed
        """
        try:
            link_name = f"Auto - {channel_title}"
            
            result = await self.create_invite_link(
                channel_id=channel_id,
                link_name=link_name,
                expire_date=None,  # No expiration
                usage_limit=None,  # No limit
                request_needed=False
            )
            
            if result['success']:
                logger.info(f"✅ Auto-created invite link for channel {channel_id}")
                return result['link']
            
            return None
            
        except Exception as e:
            logger.error(f"Error auto-creating invite link: {e}")
            return None
    
    async def create_temporary_invite_link(self, 
                                         channel_id: int,
                                         hours: int = 24,
                                         usage_limit: int = 10) -> Dict[str, Any]:
        """
        Create a temporary invite link with expiration
        
        Args:
            channel_id: Channel ID
            hours: Hours until expiration
            usage_limit: Maximum uses
            
        Returns:
            Dict with operation result
        """
        expire_date = datetime.now() + timedelta(hours=hours)
        link_name = f"Temporary {hours}h"
        
        return await self.create_invite_link(
            channel_id=channel_id,
            link_name=link_name,
            expire_date=expire_date,
            usage_limit=usage_limit,
            request_needed=False
        )
    
    async def create_approval_invite_link(self, 
                                        channel_id: int,
                                        link_name: str = "Approval Required") -> Dict[str, Any]:
        """
        Create an invite link that requires admin approval
        
        Args:
            channel_id: Channel ID
            link_name: Name for the link
            
        Returns:
            Dict with operation result
        """
        return await self.create_invite_link(
            channel_id=channel_id,
            link_name=link_name,
            expire_date=None,
            usage_limit=None,
            request_needed=True
        )
    
    async def cleanup_expired_links(self) -> int:
        """
        Remove expired invite links
        
        Returns:
            Number of links cleaned up
        """
        try:
            now = datetime.now()
            cleaned_count = 0
            
            for channel_id, links in self.active_links.items():
                expired_links = []
                
                for link in links:
                    expire_date = link.get('expire_date')
                    if expire_date and expire_date <= now:
                        expired_links.append(link['id'])
                
                for link_id in expired_links:
                    await self.revoke_invite_link(link_id)
                    cleaned_count += 1
            
            logger.info(f"✅ Cleaned up {cleaned_count} expired invite links")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired links: {e}")
            return 0
    
    async def get_invite_link_stats(self, channel_id: int) -> Dict[str, Any]:
        """
        Get statistics for invite links of a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dict with statistics
        """
        try:
            links = await self.get_channel_invite_links(channel_id)
            
            stats = {
                'total_links': len(links),
                'active_links': len([l for l in links if not l['is_revoked']]),
                'expired_links': 0,
                'approval_links': len([l for l in links if l['request_needed']]),
                'total_usage': sum(l['usage_count'] for l in links),
                'most_used_link': None,
                'newest_link': None
            }
            
            # Count expired links
            now = datetime.now()
            for link in links:
                if link['expire_date'] and link['expire_date'] <= now:
                    stats['expired_links'] += 1
            
            # Find most used link
            if links:
                most_used = max(links, key=lambda x: x['usage_count'])
                stats['most_used_link'] = {
                    'name': most_used['name'],
                    'usage_count': most_used['usage_count']
                }
                
                # Find newest link
                newest = max(links, key=lambda x: x['created_at'])
                stats['newest_link'] = {
                    'name': newest['name'],
                    'created_at': newest['created_at']
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting invite link stats: {e}")
            return {}
    
    async def bulk_create_invite_links(self, 
                                     channel_id: int,
                                     count: int = 5,
                                     prefix: str = "Bulk") -> List[Dict]:
        """
        Create multiple invite links at once
        
        Args:
            channel_id: Channel ID
            count: Number of links to create
            prefix: Prefix for link names
            
        Returns:
            List of created links
        """
        try:
            created_links = []
            
            for i in range(count):
                link_name = f"{prefix} {i+1}"
                
                result = await self.create_invite_link(
                    channel_id=channel_id,
                    link_name=link_name,
                    expire_date=None,
                    usage_limit=None,
                    request_needed=False
                )
                
                if result['success']:
                    created_links.append(result)
                else:
                    logger.warning(f"Failed to create bulk link {i+1}: {result.get('error')}")
            
            logger.info(f"✅ Created {len(created_links)} bulk invite links for channel {channel_id}")
            return created_links
            
        except Exception as e:
            logger.error(f"Error creating bulk invite links: {e}")
            return []
    
    async def load_active_links(self):
        """Load active invite links from database on startup"""
        try:
            # This would require a method to get all active links from DB
            # For now, we'll initialize empty and load as needed
            self.active_links = {}
            logger.info("✅ Initialized invite manager")
            
        except Exception as e:
            logger.error(f"Error loading active links: {e}")
    
    async def monitor_link_usage(self, channel_id: int):
        """
        Monitor invite link usage for a channel
        This would be called periodically to update usage statistics
        
        Args:
            channel_id: Channel ID to monitor
        """
        try:
            # Get current links from Telegram
            channel = await self.client.get_entity(channel_id)
            
            # Here you would implement logic to check link usage
            # This requires additional Telegram API calls that may not be available
            # For now, we'll just log that monitoring is active
            
            logger.debug(f"Monitoring invite links for channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error monitoring link usage: {e}")
    
    async def export_invite_links(self, channel_id: int) -> str:
        """
        Export invite links to a formatted string
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Formatted string with all links
        """
        try:
            links = await self.get_channel_invite_links(channel_id)
            
            if not links:
                return "No invite links found for this channel."
            
            export_text = f"📋 Invite Links Export\n"
            export_text += f"Channel ID: {channel_id}\n"
            export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            export_text += f"Total Links: {len(links)}\n\n"
            
            for i, link in enumerate(links, 1):
                export_text += f"{i}. {link['name']}\n"
                export_text += f"   Link: {link['link']}\n"
                export_text += f"   Created: {link['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
                export_text += f"   Usage: {link['usage_count']}"
                
                if link['usage_limit']:
                    export_text += f"/{link['usage_limit']}"
                export_text += "\n"
                
                if link['expire_date']:
                    export_text += f"   Expires: {link['expire_date'].strftime('%Y-%m-%d %H:%M')}\n"
                
                if link['request_needed']:
                    export_text += f"   ⚠️ Requires Approval\n"
                
                if link['is_revoked']:
                    export_text += f"   ❌ Revoked\n"
                
                export_text += "\n"
            
            return export_text
            
        except Exception as e:
            logger.error(f"Error exporting invite links: {e}")
            return f"Error exporting links: {str(e)}"