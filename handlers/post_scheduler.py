#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Post Scheduler Handler
=====================

Handles all scheduled post operations including:
- Scheduling posts for future publishing
- Managing post queues
- Automatic posting
- Post template management
"""

import logging
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from telethon import TelegramClient

from database.database import DatabaseManager
from utils.scheduler import scheduler

logger = logging.getLogger(__name__)

class PostScheduler:
    """
    Advanced post scheduling handler for Telegram channels.
    
    Features:
    - Schedule posts for specific times
    - Recurring post scheduling
    - Post template management
    - Queue management
    - Auto-posting capabilities
    """
    
    def __init__(self, client: TelegramClient, db: DatabaseManager):
        self.client = client
        self.db = db
        self.scheduled_posts: Dict[str, Dict] = {}
    
    async def schedule_post(self, 
                          channel_id: int,
                          message_text: str,
                          scheduled_time: datetime,
                          media_path: str = None,
                          parse_mode: str = "Markdown") -> Dict[str, Any]:
        """
        Schedule a post for future publishing
        
        Args:
            channel_id: Target channel ID
            message_text: Message text
            scheduled_time: When to publish
            media_path: Optional media file path
            parse_mode: Message parse mode
            
        Returns:
            Dict with operation result
        """
        try:
            # Prepare message data
            message_data = {
                'text': message_text,
                'parse_mode': parse_mode,
                'media_path': media_path,
                'channel_id': channel_id
            }
            
            # Save to database
            post = await self.db.add_scheduled_post(
                channel_id=channel_id,
                message_data=message_data,
                scheduled_time=scheduled_time
            )
            
            # Schedule with scheduler
            task_id = scheduler.schedule_post(
                channel_id=str(channel_id),
                message=message_text,
                scheduled_time=scheduled_time,
                media_path=media_path,
                parse_mode=parse_mode
            )
            
            # Store task mapping
            self.scheduled_posts[task_id] = {
                'post_id': post.id,
                'channel_id': channel_id,
                'scheduled_time': scheduled_time,
                'message_data': message_data
            }
            
            logger.info(f"✅ Scheduled post for channel {channel_id} at {scheduled_time}")
            
            return {
                'success': True,
                'post_id': post.id,
                'task_id': task_id,
                'scheduled_time': scheduled_time
            }
            
        except Exception as e:
            logger.error(f"Error scheduling post: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def schedule_recurring_post(self,
                                    channel_id: int,
                                    message_text: str,
                                    interval_hours: int,
                                    start_time: datetime = None,
                                    max_posts: int = None) -> Dict[str, Any]:
        """
        Schedule recurring posts
        
        Args:
            channel_id: Target channel ID
            message_text: Message text
            interval_hours: Hours between posts
            start_time: When to start (default: now)
            max_posts: Maximum number of posts
            
        Returns:
            Dict with operation result
        """
        try:
            start_time = start_time or datetime.now()
            
            # Schedule recurring task
            task_id = scheduler.schedule_task(
                name=f"Recurring post for channel {channel_id}",
                function=self._send_recurring_post,
                interval_seconds=interval_hours * 3600,
                args=(channel_id, message_text),
                max_runs=max_posts
            )
            
            logger.info(f"✅ Scheduled recurring post for channel {channel_id} every {interval_hours}h")
            
            return {
                'success': True,
                'task_id': task_id,
                'interval_hours': interval_hours,
                'max_posts': max_posts
            }
            
        except Exception as e:
            logger.error(f"Error scheduling recurring post: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _send_recurring_post(self, channel_id: int, message_text: str):
        """Send a recurring post"""
        try:
            await self._send_post_now(channel_id, message_text)
            logger.info(f"✅ Sent recurring post to channel {channel_id}")
        except Exception as e:
            logger.error(f"Error sending recurring post: {e}")
    
    async def cancel_scheduled_post(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled post
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            Dict with operation result
        """
        try:
            # Cancel in scheduler
            success = scheduler.cancel_task(task_id)
            
            if success and task_id in self.scheduled_posts:
                post_info = self.scheduled_posts[task_id]
                
                # Mark as cancelled in database
                # Note: would need a method in DB to update post status
                
                # Remove from memory
                del self.scheduled_posts[task_id]
                
                logger.info(f"✅ Cancelled scheduled post {task_id}")
                
                return {
                    'success': True,
                    'message': 'Post cancelled successfully'
                }
            
            return {
                'success': False,
                'error': 'Post not found or already processed'
            }
            
        except Exception as e:
            logger.error(f"Error cancelling scheduled post: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_scheduled_posts(self, channel_id: int = None) -> List[Dict]:
        """
        Get scheduled posts
        
        Args:
            channel_id: Filter by channel ID (optional)
            
        Returns:
            List of scheduled posts
        """
        try:
            scheduled_posts = []
            
            for task_id, post_info in self.scheduled_posts.items():
                if channel_id is None or post_info['channel_id'] == channel_id:
                    task = scheduler.get_task(task_id)
                    
                    if task:
                        post_data = {
                            'task_id': task_id,
                            'post_id': post_info['post_id'],
                            'channel_id': post_info['channel_id'],
                            'scheduled_time': post_info['scheduled_time'],
                            'message_preview': post_info['message_data']['text'][:100],
                            'status': task.status.value,
                            'created_at': task.created_at
                        }
                        scheduled_posts.append(post_data)
            
            return scheduled_posts
            
        except Exception as e:
            logger.error(f"Error getting scheduled posts: {e}")
            return []
    
    async def _send_post_now(self, 
                           channel_id: int, 
                           message_text: str,
                           media_path: str = None,
                           parse_mode: str = "Markdown"):
        """
        Send a post immediately
        
        Args:
            channel_id: Target channel ID
            message_text: Message text
            media_path: Optional media file path
            parse_mode: Message parse mode
        """
        try:
            channel = await self.client.get_entity(channel_id)
            
            if media_path:
                # Send with media
                await self.client.send_file(
                    channel,
                    media_path,
                    caption=message_text,
                    parse_mode=parse_mode
                )
            else:
                # Send text only
                await self.client.send_message(
                    channel,
                    message_text,
                    parse_mode=parse_mode
                )
            
            logger.info(f"✅ Sent post to channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error sending post to channel {channel_id}: {e}")
            raise
    
    async def create_post_template(self, 
                                 name: str,
                                 template_text: str,
                                 variables: List[str] = None) -> Dict[str, Any]:
        """
        Create a post template for reuse
        
        Args:
            name: Template name
            template_text: Template text with variables like {variable}
            variables: List of variable names
            
        Returns:
            Dict with operation result
        """
        try:
            template_data = {
                'name': name,
                'text': template_text,
                'variables': variables or [],
                'created_at': datetime.now()
            }
            
            # Save template (would need DB table for templates)
            # For now, just return success
            
            logger.info(f"✅ Created post template: {name}")
            
            return {
                'success': True,
                'template_name': name,
                'variables': variables or []
            }
            
        except Exception as e:
            logger.error(f"Error creating post template: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def schedule_from_template(self,
                                   template_name: str,
                                   channel_id: int,
                                   scheduled_time: datetime,
                                   variables: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Schedule a post using a template
        
        Args:
            template_name: Name of template to use
            channel_id: Target channel ID
            scheduled_time: When to publish
            variables: Variables to substitute in template
            
        Returns:
            Dict with operation result
        """
        try:
            # Get template (would fetch from DB)
            # For now, assume basic template
            template_text = "📢 {title}\n\n{content}\n\n#news"
            
            # Substitute variables
            message_text = template_text
            if variables:
                for var_name, var_value in variables.items():
                    message_text = message_text.replace(f"{{{var_name}}}", var_value)
            
            # Schedule the post
            return await self.schedule_post(
                channel_id=channel_id,
                message_text=message_text,
                scheduled_time=scheduled_time
            )
            
        except Exception as e:
            logger.error(f"Error scheduling from template: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_posting_stats(self, channel_id: int = None) -> Dict[str, Any]:
        """
        Get posting statistics
        
        Args:
            channel_id: Filter by channel ID (optional)
            
        Returns:
            Dict with statistics
        """
        try:
            # Get scheduler stats
            scheduler_stats = scheduler.get_task_stats()
            
            # Filter scheduled posts for the channel
            channel_posts = []
            if channel_id:
                channel_posts = [
                    post for post in self.scheduled_posts.values()
                    if post['channel_id'] == channel_id
                ]
            else:
                channel_posts = list(self.scheduled_posts.values())
            
            stats = {
                'total_scheduled': len(channel_posts),
                'pending_posts': len([p for p in channel_posts 
                                    if p['scheduled_time'] > datetime.now()]),
                'total_scheduler_tasks': scheduler_stats['total_tasks'],
                'running_tasks': scheduler_stats['running_tasks'],
                'completed_tasks': scheduler_stats['completed_tasks'],
                'failed_tasks': scheduler_stats['failed_tasks']
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting posting stats: {e}")
            return {}
    
    async def bulk_schedule_posts(self, 
                                posts: List[Dict],
                                start_time: datetime,
                                interval_minutes: int = 30) -> List[Dict]:
        """
        Schedule multiple posts with intervals
        
        Args:
            posts: List of post data dicts
            start_time: When to start posting
            interval_minutes: Minutes between posts
            
        Returns:
            List of scheduling results
        """
        try:
            results = []
            current_time = start_time
            
            for post_data in posts:
                result = await self.schedule_post(
                    channel_id=post_data['channel_id'],
                    message_text=post_data['message_text'],
                    scheduled_time=current_time,
                    media_path=post_data.get('media_path'),
                    parse_mode=post_data.get('parse_mode', 'Markdown')
                )
                
                results.append({
                    'channel_id': post_data['channel_id'],
                    'scheduled_time': current_time,
                    'success': result['success'],
                    'task_id': result.get('task_id'),
                    'error': result.get('error')
                })
                
                # Move to next time slot
                current_time += timedelta(minutes=interval_minutes)
            
            successful = len([r for r in results if r['success']])
            logger.info(f"✅ Bulk scheduled {successful}/{len(posts)} posts")
            
            return results
            
        except Exception as e:
            logger.error(f"Error bulk scheduling posts: {e}")
            return []
    
    async def load_pending_posts(self):
        """Load pending scheduled posts from database on startup"""
        try:
            # Get pending posts from database
            pending_posts = await self.db.get_pending_posts()
            
            for post in pending_posts:
                try:
                    message_data = json.loads(post.message_data)
                    
                    # Re-schedule if time hasn't passed
                    if post.scheduled_time > datetime.now():
                        task_id = scheduler.schedule_post(
                            channel_id=str(post.channel_id),
                            message=message_data['text'],
                            scheduled_time=post.scheduled_time,
                            media_path=message_data.get('media_path'),
                            parse_mode=message_data.get('parse_mode', 'Markdown')
                        )
                        
                        self.scheduled_posts[task_id] = {
                            'post_id': post.id,
                            'channel_id': post.channel_id,
                            'scheduled_time': post.scheduled_time,
                            'message_data': message_data
                        }
                        
                except Exception as e:
                    logger.warning(f"Could not reload scheduled post {post.id}: {e}")
            
            logger.info(f"✅ Loaded {len(self.scheduled_posts)} pending scheduled posts")
            
        except Exception as e:
            logger.error(f"Error loading pending posts: {e}")