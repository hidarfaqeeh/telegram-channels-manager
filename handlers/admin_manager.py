#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Admin Manager Handler
====================

Handles all admin management operations including:
- Managing channel administrators
- Permission management
- Admin role assignment
- Admin activity monitoring
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError, UserNotParticipantError
from telethon.tl.functions.channels import EditAdminRequest, GetParticipantRequest
from telethon.tl.types import ChatAdminRights, User

from database.database import DatabaseManager

logger = logging.getLogger(__name__)

class AdminManager:
    """
    Advanced admin management handler for Telegram channels.
    
    Features:
    - Add/remove channel administrators
    - Manage admin permissions
    - Monitor admin activities
    - Role-based access control
    - Admin statistics tracking
    """
    
    def __init__(self, client: TelegramClient, db: DatabaseManager):
        self.client = client
        self.db = db
        self.channel_admins: Dict[int, List[Dict]] = {}  # channel_id -> admin list
    
    async def add_admin(self, 
                       channel_id: int,
                       user_id: int,
                       permissions: Dict[str, bool] = None) -> Dict[str, Any]:
        """
        Add a new administrator to a channel
        
        Args:
            channel_id: Channel ID
            user_id: User ID to promote
            permissions: Admin permissions dict
            
        Returns:
            Dict with operation result
        """
        try:
            # Default permissions
            default_permissions = {
                'change_info': True,
                'post_messages': True,
                'edit_messages': True,
                'delete_messages': True,
                'ban_users': True,
                'invite_users': True,
                'pin_messages': True,
                'add_admins': False,
                'manage_call': False
            }
            
            if permissions:
                default_permissions.update(permissions)
            
            # Create admin rights
            admin_rights = ChatAdminRights(
                change_info=default_permissions['change_info'],
                post_messages=default_permissions['post_messages'],
                edit_messages=default_permissions['edit_messages'],
                delete_messages=default_permissions['delete_messages'],
                ban_users=default_permissions['ban_users'],
                invite_users=default_permissions['invite_users'],
                pin_messages=default_permissions['pin_messages'],
                add_admins=default_permissions['add_admins'],
                manage_call=default_permissions['manage_call']
            )
            
            # Get channel and user entities
            channel = await self.client.get_entity(channel_id)
            user = await self.client.get_entity(user_id)
            
            # Promote user
            await self.client(EditAdminRequest(
                channel=channel,
                user_id=user,
                admin_rights=admin_rights,
                rank="Administrator"
            ))
            
            # Save to database
            await self.db.add_channel_admin(
                channel_id=channel_id,
                user_id=user_id,
                permissions=default_permissions
            )
            
            # Update memory
            if channel_id not in self.channel_admins:
                self.channel_admins[channel_id] = []
            
            admin_info = {
                'user_id': user_id,
                'username': getattr(user, 'username', None),
                'first_name': getattr(user, 'first_name', 'Unknown'),
                'permissions': default_permissions,
                'added_at': datetime.now(),
                'is_active': True
            }
            self.channel_admins[channel_id].append(admin_info)
            
            logger.info(f"✅ Added admin {user_id} to channel {channel_id}")
            
            return {
                'success': True,
                'user_id': user_id,
                'username': getattr(user, 'username', None),
                'permissions': default_permissions
            }
            
        except ChatAdminRequiredError:
            return {
                'success': False,
                'error': 'Bot needs admin rights to manage administrators'
            }
        except Exception as e:
            logger.error(f"Error adding admin: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def remove_admin(self, channel_id: int, user_id: int) -> Dict[str, Any]:
        """
        Remove administrator from a channel
        
        Args:
            channel_id: Channel ID
            user_id: User ID to demote
            
        Returns:
            Dict with operation result
        """
        try:
            # Get channel and user entities
            channel = await self.client.get_entity(channel_id)
            user = await self.client.get_entity(user_id)
            
            # Remove admin rights
            await self.client(EditAdminRequest(
                channel=channel,
                user_id=user,
                admin_rights=ChatAdminRights(),  # Empty rights = remove admin
                rank=""
            ))
            
            # Remove from database
            await self.db.remove_channel_admin(channel_id, user_id)
            
            # Update memory
            if channel_id in self.channel_admins:
                self.channel_admins[channel_id] = [
                    admin for admin in self.channel_admins[channel_id]
                    if admin['user_id'] != user_id
                ]
            
            logger.info(f"✅ Removed admin {user_id} from channel {channel_id}")
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'Admin removed successfully'
            }
            
        except ChatAdminRequiredError:
            return {
                'success': False,
                'error': 'Bot needs admin rights to manage administrators'
            }
        except Exception as e:
            logger.error(f"Error removing admin: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_channel_admins(self, channel_id: int) -> List[Dict]:
        """
        Get all administrators of a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            List of admin information
        """
        try:
            # Get from Telegram API
            channel = await self.client.get_entity(channel_id)
            
            admins = []
            async for participant in self.client.iter_participants(channel, filter='admin'):
                if isinstance(participant, User):
                    admin_info = {
                        'user_id': participant.id,
                        'username': participant.username,
                        'first_name': participant.first_name or 'Unknown',
                        'last_name': participant.last_name or '',
                        'is_bot': participant.bot,
                        'is_verified': getattr(participant, 'verified', False),
                        'is_premium': getattr(participant, 'premium', False)
                    }
                    admins.append(admin_info)
            
            return admins
            
        except Exception as e:
            logger.error(f"Error getting channel admins: {e}")
            return []
    
    async def update_admin_permissions(self, 
                                     channel_id: int,
                                     user_id: int,
                                     permissions: Dict[str, bool]) -> Dict[str, Any]:
        """
        Update administrator permissions
        
        Args:
            channel_id: Channel ID
            user_id: User ID
            permissions: New permissions dict
            
        Returns:
            Dict with operation result
        """
        try:
            # Create admin rights
            admin_rights = ChatAdminRights(
                change_info=permissions.get('change_info', False),
                post_messages=permissions.get('post_messages', False),
                edit_messages=permissions.get('edit_messages', False),
                delete_messages=permissions.get('delete_messages', False),
                ban_users=permissions.get('ban_users', False),
                invite_users=permissions.get('invite_users', False),
                pin_messages=permissions.get('pin_messages', False),
                add_admins=permissions.get('add_admins', False),
                manage_call=permissions.get('manage_call', False)
            )
            
            # Get entities
            channel = await self.client.get_entity(channel_id)
            user = await self.client.get_entity(user_id)
            
            # Update permissions
            await self.client(EditAdminRequest(
                channel=channel,
                user_id=user,
                admin_rights=admin_rights,
                rank="Administrator"
            ))
            
            # Update database
            await self.db.update_admin_permissions(channel_id, user_id, permissions)
            
            # Update memory
            if channel_id in self.channel_admins:
                for admin in self.channel_admins[channel_id]:
                    if admin['user_id'] == user_id:
                        admin['permissions'] = permissions
                        break
            
            logger.info(f"✅ Updated permissions for admin {user_id} in channel {channel_id}")
            
            return {
                'success': True,
                'user_id': user_id,
                'permissions': permissions
            }
            
        except Exception as e:
            logger.error(f"Error updating admin permissions: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_admin_stats(self, channel_id: int) -> Dict[str, Any]:
        """
        Get administrator statistics for a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dict with statistics
        """
        try:
            admins = await self.get_channel_admins(channel_id)
            
            stats = {
                'total_admins': len(admins),
                'bot_admins': len([a for a in admins if a.get('is_bot', False)]),
                'verified_admins': len([a for a in admins if a.get('is_verified', False)]),
                'premium_admins': len([a for a in admins if a.get('is_premium', False)]),
                'admins_with_username': len([a for a in admins if a.get('username')]),
                'recent_additions': 0  # Would need database tracking for this
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            return {}
    
    async def check_admin_permissions(self, 
                                    channel_id: int, 
                                    user_id: int,
                                    required_permission: str) -> bool:
        """
        Check if a user has a specific admin permission
        
        Args:
            channel_id: Channel ID
            user_id: User ID to check
            required_permission: Permission to check
            
        Returns:
            bool: True if user has permission
        """
        try:
            channel = await self.client.get_entity(channel_id)
            
            # Get participant info
            participant = await self.client(GetParticipantRequest(
                channel=channel,
                participant=user_id
            ))
            
            if hasattr(participant.participant, 'admin_rights'):
                admin_rights = participant.participant.admin_rights
                return getattr(admin_rights, required_permission, False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking admin permissions: {e}")
            return False
    
    async def load_channel_admins(self):
        """Load channel admins from database on startup"""
        try:
            # Initialize empty for now
            self.channel_admins = {}
            logger.info("✅ Initialized admin manager")
            
        except Exception as e:
            logger.error(f"Error loading channel admins: {e}")
    
    async def bulk_add_admins(self, 
                            channel_id: int,
                            user_ids: List[int],
                            permissions: Dict[str, bool] = None) -> List[Dict]:
        """
        Add multiple administrators at once
        
        Args:
            channel_id: Channel ID
            user_ids: List of user IDs to promote
            permissions: Admin permissions to assign
            
        Returns:
            List of operation results
        """
        try:
            results = []
            
            for user_id in user_ids:
                result = await self.add_admin(channel_id, user_id, permissions)
                results.append({
                    'user_id': user_id,
                    'success': result['success'],
                    'error': result.get('error')
                })
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
            
            successful = len([r for r in results if r['success']])
            logger.info(f"✅ Bulk added {successful}/{len(user_ids)} admins to channel {channel_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error bulk adding admins: {e}")
            return []
    
    async def export_admins_list(self, channel_id: int) -> str:
        """
        Export administrators list to formatted string
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Formatted string with admin list
        """
        try:
            admins = await self.get_channel_admins(channel_id)
            
            if not admins:
                return "No administrators found for this channel."
            
            export_text = f"👥 Administrators Export\n"
            export_text += f"Channel ID: {channel_id}\n"
            export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            export_text += f"Total Admins: {len(admins)}\n\n"
            
            for i, admin in enumerate(admins, 1):
                export_text += f"{i}. {admin['first_name']}"
                if admin['last_name']:
                    export_text += f" {admin['last_name']}"
                
                if admin['username']:
                    export_text += f" (@{admin['username']})"
                
                export_text += f"\n   ID: {admin['user_id']}\n"
                
                if admin['is_bot']:
                    export_text += "   🤖 Bot\n"
                if admin['is_verified']:
                    export_text += "   ✅ Verified\n"
                if admin['is_premium']:
                    export_text += "   ⭐ Premium\n"
                
                export_text += "\n"
            
            return export_text
            
        except Exception as e:
            logger.error(f"Error exporting admins list: {e}")
            return f"Error exporting admins: {str(e)}"