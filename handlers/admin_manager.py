#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Optional, List, Dict, Any
from telethon import TelegramClient
from telethon.tl import functions
from telethon.tl.types import ChatAdminRights

logger = logging.getLogger(__name__)

class AdminManager:
    def __init__(self, db, client: TelegramClient):
        self.db = db
        self.client = client
    
    async def promote_user(self, channel_id: int, user_id: int, rights: Dict[str, bool]) -> bool:
        """Promote user to admin"""
        try:
            entity = await self.client.get_entity(channel_id)
            user = await self.client.get_entity(user_id)
            
            admin_rights = ChatAdminRights(
                change_info=rights.get('can_change_info', False),
                post_messages=rights.get('can_post_messages', False),
                edit_messages=rights.get('can_edit_messages', False),
                delete_messages=rights.get('can_delete_messages', False),
                ban_users=rights.get('can_ban_users', False),
                invite_users=rights.get('can_invite_users', False),
                pin_messages=rights.get('can_pin_messages', False),
                add_admins=rights.get('can_add_admins', False),
                anonymous=rights.get('is_anonymous', False),
                manage_call=rights.get('can_manage_call', False),
                other=rights.get('other', False)
            )
            
            await self.client(functions.channels.EditAdminRequest(
                channel=entity,
                user_id=user,
                admin_rights=admin_rights,
                rank=rights.get('rank', '')
            ))
            
            logger.info(f"Promoted user {user_id} in channel {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error promoting user {user_id} in channel {channel_id}: {e}")
            return False
    
    async def demote_user(self, channel_id: int, user_id: int) -> bool:
        """Demote admin user"""
        try:
            entity = await self.client.get_entity(channel_id)
            user = await self.client.get_entity(user_id)
            
            await self.client(functions.channels.EditAdminRequest(
                channel=entity,
                user_id=user,
                admin_rights=ChatAdminRights(),
                rank=''
            ))
            
            logger.info(f"Demoted user {user_id} in channel {channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error demoting user {user_id} in channel {channel_id}: {e}")
            return False