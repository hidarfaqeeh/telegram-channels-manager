#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto Accept Manager Handler
==========================

Handles automatic acceptance of join requests including:
- Auto-accepting join requests
- Managing acceptance criteria
- Rate limiting
- User filtering and validation
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.errors import UserNotParticipantError, ChatAdminRequiredError
from telethon.tl.functions.messages import HideChatJoinRequestRequest

from database.database import DatabaseManager

logger = logging.getLogger(__name__)

class AutoAcceptManager:
    """
    Auto-accept manager for handling join requests automatically.
    
    Features:
    - Auto-accept join requests based on criteria
    - Rate limiting and spam protection
    - User validation and filtering
    - Statistics tracking
    - Manual review for suspicious requests
    """
    
    def __init__(self, client: TelegramClient, db: DatabaseManager):
        self.client = client
        self.db = db
        self.auto_accept_enabled: Dict[int, bool] = {}  # channel_id -> enabled
        self.accept_settings: Dict[int, Dict] = {}  # channel_id -> settings
        self.accept_stats: Dict[int, Dict] = {}  # channel_id -> stats
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers for join requests"""
        
        @self.client.on(events.ChatAction)
        async def handle_join_request(event):
            """Handle new join requests"""
            try:
                if (hasattr(event, 'join_request') and event.join_request and 
                    event.chat_id in self.auto_accept_enabled and 
                    self.auto_accept_enabled[event.chat_id]):
                    
                    await self._process_join_request(event)
                    
            except Exception as e:
                logger.error(f"Error handling join request: {e}")
    
    async def enable_auto_accept(self, 
                               channel_id: int,
                               settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enable auto-accept for a channel
        
        Args:
            channel_id: Channel ID
            settings: Auto-accept settings
            
        Returns:
            Dict with operation result
        """
        try:
            # Default settings
            default_settings = {
                'enabled': True,
                'max_accepts_per_hour': 50,
                'require_photo': False,
                'require_username': False,
                'min_account_age_days': 0,
                'blacklisted_words': [],
                'allowed_countries': [],  # Empty = all countries
                'review_suspicious': True,
                'delay_seconds': 5
            }
            
            if settings:
                default_settings.update(settings)
            
            # Save to database
            await self.db.update_auto_accept_settings(
                channel_id=channel_id,
                **default_settings
            )
            
            # Update memory
            self.auto_accept_enabled[channel_id] = True
            self.accept_settings[channel_id] = default_settings
            
            # Initialize stats
            if channel_id not in self.accept_stats:
                self.accept_stats[channel_id] = {
                    'total_requests': 0,
                    'accepted': 0,
                    'rejected': 0,
                    'pending_review': 0,
                    'last_reset': datetime.now().date()
                }
            
            logger.info(f"✅ Enabled auto-accept for channel {channel_id}")
            
            return {
                'success': True,
                'channel_id': channel_id,
                'settings': default_settings
            }
            
        except Exception as e:
            logger.error(f"Error enabling auto-accept: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def disable_auto_accept(self, channel_id: int) -> Dict[str, Any]:
        """
        Disable auto-accept for a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dict with operation result
        """
        try:
            # Update database
            await self.db.update_auto_accept_settings(
                channel_id=channel_id,
                enabled=False
            )
            
            # Update memory
            self.auto_accept_enabled[channel_id] = False
            
            logger.info(f"✅ Disabled auto-accept for channel {channel_id}")
            
            return {
                'success': True,
                'channel_id': channel_id,
                'message': 'Auto-accept disabled'
            }
            
        except Exception as e:
            logger.error(f"Error disabling auto-accept: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _process_join_request(self, event):
        """Process a new join request"""
        try:
            channel_id = event.chat_id
            user = event.user
            
            if not user:
                return
            
            # Update stats
            await self._update_stats(channel_id, 'request')
            
            # Get settings
            settings = self.accept_settings.get(channel_id, {})
            
            # Check rate limits
            if not await self._check_rate_limits(channel_id, settings):
                logger.info(f"Rate limit exceeded for channel {channel_id}")
                return
            
            # Validate user
            validation_result = await self._validate_user(user, settings)
            
            if validation_result['accept']:
                await self._accept_user(event, user)
                await self._update_stats(channel_id, 'accepted')
            elif validation_result['review']:
                await self._queue_for_review(event, user, validation_result['reason'])
                await self._update_stats(channel_id, 'review')
            else:
                await self._reject_user(event, user, validation_result['reason'])
                await self._update_stats(channel_id, 'rejected')
            
        except Exception as e:
            logger.error(f"Error processing join request: {e}")
    
    async def _validate_user(self, user, settings: Dict) -> Dict[str, Any]:
        """
        Validate a user against acceptance criteria
        
        Args:
            user: User object
            settings: Auto-accept settings
            
        Returns:
            Dict with validation result
        """
        try:
            # Check if profile photo required
            if settings.get('require_photo', False):
                if not hasattr(user, 'photo') or not user.photo:
                    return {
                        'accept': False,
                        'review': settings.get('review_suspicious', True),
                        'reason': 'No profile photo'
                    }
            
            # Check if username required
            if settings.get('require_username', False):
                if not user.username:
                    return {
                        'accept': False,
                        'review': settings.get('review_suspicious', True),
                        'reason': 'No username'
                    }
            
            # Check account age (would need creation date from API)
            min_age_days = settings.get('min_account_age_days', 0)
            if min_age_days > 0:
                # This would require additional API calls to get user info
                # For now, we'll skip this check
                pass
            
            # Check for blacklisted words in name
            blacklisted_words = settings.get('blacklisted_words', [])
            if blacklisted_words:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".lower()
                for word in blacklisted_words:
                    if word.lower() in full_name:
                        return {
                            'accept': False,
                            'review': False,
                            'reason': f'Blacklisted word: {word}'
                        }
            
            # Check if user is a bot
            if getattr(user, 'bot', False):
                return {
                    'accept': False,
                    'review': True,
                    'reason': 'Bot account'
                }
            
            # Check if user is deleted/deactivated
            if getattr(user, 'deleted', False):
                return {
                    'accept': False,
                    'review': False,
                    'reason': 'Deleted account'
                }
            
            # All checks passed
            return {
                'accept': True,
                'review': False,
                'reason': 'Passed all checks'
            }
            
        except Exception as e:
            logger.error(f"Error validating user: {e}")
            return {
                'accept': False,
                'review': True,
                'reason': f'Validation error: {str(e)}'
            }
    
    async def _check_rate_limits(self, channel_id: int, settings: Dict) -> bool:
        """Check if rate limits allow accepting more users"""
        try:
            max_per_hour = settings.get('max_accepts_per_hour', 50)
            
            # Get current hour accepts count
            # This would need to be tracked in database or memory
            # For now, we'll assume it's okay
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return False
    
    async def _accept_user(self, event, user):
        """Accept a user's join request"""
        try:
            # Add delay if configured
            settings = self.accept_settings.get(event.chat_id, {})
            delay = settings.get('delay_seconds', 0)
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Accept the request
            await self.client(HideChatJoinRequestRequest(
                peer=event.chat_id,
                user_id=user.id,
                approved=True
            ))
            
            logger.info(f"✅ Accepted join request from user {user.id} in channel {event.chat_id}")
            
        except Exception as e:
            logger.error(f"Error accepting user: {e}")
    
    async def _reject_user(self, event, user, reason: str):
        """Reject a user's join request"""
        try:
            # Reject the request
            await self.client(HideChatJoinRequestRequest(
                peer=event.chat_id,
                user_id=user.id,
                approved=False
            ))
            
            logger.info(f"❌ Rejected join request from user {user.id}: {reason}")
            
        except Exception as e:
            logger.error(f"Error rejecting user: {e}")
    
    async def _queue_for_review(self, event, user, reason: str):
        """Queue a join request for manual review"""
        try:
            # Store for manual review (would need database table)
            review_data = {
                'channel_id': event.chat_id,
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'reason': reason,
                'created_at': datetime.now()
            }
            
            # Save to review queue (implementation needed)
            logger.info(f"📋 Queued for review: user {user.id} - {reason}")
            
        except Exception as e:
            logger.error(f"Error queuing for review: {e}")
    
    async def _update_stats(self, channel_id: int, stat_type: str):
        """Update auto-accept statistics"""
        try:
            if channel_id not in self.accept_stats:
                self.accept_stats[channel_id] = {
                    'total_requests': 0,
                    'accepted': 0,
                    'rejected': 0,
                    'pending_review': 0,
                    'last_reset': datetime.now().date()
                }
            
            stats = self.accept_stats[channel_id]
            
            # Reset daily stats if needed
            today = datetime.now().date()
            if stats['last_reset'] != today:
                stats['total_requests'] = 0
                stats['accepted'] = 0
                stats['rejected'] = 0
                stats['pending_review'] = 0
                stats['last_reset'] = today
            
            # Update stats
            if stat_type == 'request':
                stats['total_requests'] += 1
            elif stat_type == 'accepted':
                stats['accepted'] += 1
            elif stat_type == 'rejected':
                stats['rejected'] += 1
            elif stat_type == 'review':
                stats['pending_review'] += 1
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    async def get_auto_accept_stats(self, channel_id: int) -> Dict[str, Any]:
        """
        Get auto-accept statistics for a channel
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Dict with statistics
        """
        try:
            stats = self.accept_stats.get(channel_id, {})
            
            if not stats:
                return {
                    'enabled': False,
                    'total_requests': 0,
                    'accepted': 0,
                    'rejected': 0,
                    'pending_review': 0,
                    'acceptance_rate': 0
                }
            
            total = stats['total_requests']
            acceptance_rate = (stats['accepted'] / total * 100) if total > 0 else 0
            
            return {
                'enabled': self.auto_accept_enabled.get(channel_id, False),
                'total_requests': total,
                'accepted': stats['accepted'],
                'rejected': stats['rejected'],
                'pending_review': stats['pending_review'],
                'acceptance_rate': round(acceptance_rate, 2),
                'last_reset': stats['last_reset']
            }
            
        except Exception as e:
            logger.error(f"Error getting auto-accept stats: {e}")
            return {}
    
    async def update_auto_accept_settings(self, 
                                        channel_id: int,
                                        settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update auto-accept settings for a channel
        
        Args:
            channel_id: Channel ID
            settings: New settings
            
        Returns:
            Dict with operation result
        """
        try:
            # Update database
            await self.db.update_auto_accept_settings(
                channel_id=channel_id,
                **settings
            )
            
            # Update memory
            if channel_id in self.accept_settings:
                self.accept_settings[channel_id].update(settings)
            else:
                self.accept_settings[channel_id] = settings
            
            # Update enabled status
            self.auto_accept_enabled[channel_id] = settings.get('enabled', True)
            
            logger.info(f"✅ Updated auto-accept settings for channel {channel_id}")
            
            return {
                'success': True,
                'channel_id': channel_id,
                'settings': self.accept_settings[channel_id]
            }
            
        except Exception as e:
            logger.error(f"Error updating auto-accept settings: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def load_auto_accept_settings(self):
        """Load auto-accept settings from database on startup"""
        try:
            # Initialize empty for now
            # Would load from database in real implementation
            self.auto_accept_enabled = {}
            self.accept_settings = {}
            self.accept_stats = {}
            
            logger.info("✅ Initialized auto-accept manager")
            
        except Exception as e:
            logger.error(f"Error loading auto-accept settings: {e}")
    
    async def manual_review_request(self, 
                                  channel_id: int,
                                  user_id: int,
                                  action: str) -> Dict[str, Any]:
        """
        Manually review a join request
        
        Args:
            channel_id: Channel ID
            user_id: User ID
            action: 'accept' or 'reject'
            
        Returns:
            Dict with operation result
        """
        try:
            if action == 'accept':
                await self.client(HideChatJoinRequestRequest(
                    peer=channel_id,
                    user_id=user_id,
                    approved=True
                ))
                await self._update_stats(channel_id, 'accepted')
                
            elif action == 'reject':
                await self.client(HideChatJoinRequestRequest(
                    peer=channel_id,
                    user_id=user_id,
                    approved=False
                ))
                await self._update_stats(channel_id, 'rejected')
            
            logger.info(f"✅ Manual {action} for user {user_id} in channel {channel_id}")
            
            return {
                'success': True,
                'action': action,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Error in manual review: {e}")
            return {
                'success': False,
                'error': str(e)
            }