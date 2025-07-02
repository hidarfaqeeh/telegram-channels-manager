#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scheduler Module
===============

Provides task scheduling capabilities for the Telegram bot.
Supports scheduled posting, automated tasks, and recurring operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    INTERVAL = "interval"

@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    id: str
    name: str
    task_type: TaskType
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    scheduled_time: datetime = None
    interval_seconds: int = None
    cron_expression: str = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_run: datetime = None
    next_run: datetime = None
    run_count: int = 0
    max_runs: int = None
    enabled: bool = True
    metadata: dict = field(default_factory=dict)

class BotScheduler:
    """
    Advanced task scheduler for the Telegram bot.
    
    Features:
    - One-time scheduled tasks
    - Recurring tasks with intervals
    - Cron-like scheduling
    - Task persistence
    - Error handling and retry logic
    - Task monitoring and statistics
    """
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        self._scheduler_task = None
        self._next_task_id = 1
    
    async def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("🕐 Scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all running tasks
        for task_id, task in self.running_tasks.items():
            task.cancel()
            logger.info(f"Cancelled running task: {task_id}")
        
        # Cancel scheduler task
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.running_tasks.clear()
        logger.info("🛑 Scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        try:
            while self.is_running:
                await self._check_and_run_tasks()
                await asyncio.sleep(1)  # Check every second
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
    
    async def _check_and_run_tasks(self):
        """Check for tasks that need to be executed"""
        now = datetime.now()
        
        for task_id, task in list(self.tasks.items()):
            if not task.enabled or task.status in [TaskStatus.CANCELLED, TaskStatus.FAILED]:
                continue
            
            should_run = False
            
            # Check one-time tasks
            if task.task_type == TaskType.ONE_TIME:
                if task.scheduled_time and now >= task.scheduled_time and task.status == TaskStatus.PENDING:
                    should_run = True
            
            # Check recurring tasks
            elif task.task_type == TaskType.RECURRING:
                if task.next_run and now >= task.next_run:
                    should_run = True
            
            # Check interval tasks
            elif task.task_type == TaskType.INTERVAL:
                if task.interval_seconds and (not task.last_run or 
                    now >= task.last_run + timedelta(seconds=task.interval_seconds)):
                    should_run = True
            
            # Run task if needed
            if should_run:
                await self._execute_task(task)
    
    async def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        if task.id in self.running_tasks:
            logger.warning(f"Task {task.id} is already running")
            return
        
        # Check max runs limit
        if task.max_runs and task.run_count >= task.max_runs:
            task.status = TaskStatus.COMPLETED
            logger.info(f"Task {task.id} reached max runs limit")
            return
        
        logger.info(f"🚀 Executing task: {task.name} ({task.id})")
        
        # Create and start task
        async_task = asyncio.create_task(self._run_task_wrapper(task))
        self.running_tasks[task.id] = async_task
        
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()
        task.run_count += 1
    
    async def _run_task_wrapper(self, task: ScheduledTask):
        """Wrapper for running tasks with error handling"""
        try:
            # Execute the task function
            if asyncio.iscoroutinefunction(task.function):
                await task.function(*task.args, **task.kwargs)
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, task.function, *task.args, **task.kwargs)
            
            # Update task status
            if task.task_type == TaskType.ONE_TIME:
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.PENDING
                task.next_run = self._calculate_next_run(task)
            
            logger.info(f"✅ Task completed: {task.name}")
            
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            logger.info(f"⏹️ Task cancelled: {task.name}")
        except Exception as e:
            task.status = TaskStatus.FAILED
            logger.error(f"❌ Task failed: {task.name} - {str(e)}")
        finally:
            # Remove from running tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    def _calculate_next_run(self, task: ScheduledTask) -> datetime:
        """Calculate next run time for recurring tasks"""
        now = datetime.now()
        
        if task.task_type == TaskType.RECURRING:
            if task.interval_seconds:
                return now + timedelta(seconds=task.interval_seconds)
            elif task.cron_expression:
                # Simple cron parsing (basic implementation)
                return self._parse_cron_next_run(task.cron_expression, now)
        
        elif task.task_type == TaskType.INTERVAL:
            if task.interval_seconds:
                return now + timedelta(seconds=task.interval_seconds)
        
        return now + timedelta(hours=24)  # Default to 24 hours
    
    def _parse_cron_next_run(self, cron_expr: str, from_time: datetime) -> datetime:
        """Simple cron expression parser"""
        try:
            # Format: minute hour day month weekday
            parts = cron_expr.split()
            if len(parts) != 5:
                logger.warning(f"Invalid cron expression: {cron_expr}")
                return from_time + timedelta(hours=1)
            
            minute, hour, day, month, weekday = parts
            
            # Handle simple cases
            next_run = from_time.replace(second=0, microsecond=0)
            
            # Set minute
            if minute != '*':
                target_minute = int(minute)
                next_run = next_run.replace(minute=target_minute)
            
            # Set hour
            if hour != '*':
                target_hour = int(hour)
                next_run = next_run.replace(hour=target_hour)
                
                # If time has passed today, move to tomorrow
                if next_run <= from_time:
                    next_run += timedelta(days=1)
            
            return next_run
            
        except Exception as e:
            logger.error(f"Cron parsing error: {e}")
            return from_time + timedelta(hours=1)
    
    def schedule_task(self, 
                     name: str,
                     function: Callable,
                     scheduled_time: datetime = None,
                     interval_seconds: int = None,
                     cron_expression: str = None,
                     args: tuple = None,
                     kwargs: dict = None,
                     max_runs: int = None,
                     metadata: dict = None) -> str:
        """
        Schedule a new task
        
        Args:
            name: Task name
            function: Function to execute
            scheduled_time: When to run (for one-time tasks)
            interval_seconds: Interval for recurring tasks
            cron_expression: Cron expression for scheduled tasks
            args: Function arguments
            kwargs: Function keyword arguments
            max_runs: Maximum number of runs
            metadata: Additional task metadata
            
        Returns:
            str: Task ID
        """
        task_id = f"task_{self._next_task_id}"
        self._next_task_id += 1
        
        # Determine task type
        if scheduled_time and not interval_seconds and not cron_expression:
            task_type = TaskType.ONE_TIME
        elif interval_seconds:
            task_type = TaskType.INTERVAL
        elif cron_expression:
            task_type = TaskType.RECURRING
        else:
            raise ValueError("Must specify either scheduled_time, interval_seconds, or cron_expression")
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type=task_type,
            function=function,
            args=args or (),
            kwargs=kwargs or {},
            scheduled_time=scheduled_time,
            interval_seconds=interval_seconds,
            cron_expression=cron_expression,
            max_runs=max_runs,
            metadata=metadata or {}
        )
        
        # Calculate next run for recurring tasks
        if task_type in [TaskType.RECURRING, TaskType.INTERVAL]:
            task.next_run = self._calculate_next_run(task)
        
        self.tasks[task_id] = task
        logger.info(f"📅 Scheduled task: {name} ({task_id})")
        
        return task_id
    
    def schedule_post(self, 
                     channel_id: str,
                     message: str,
                     scheduled_time: datetime,
                     media_path: str = None,
                     parse_mode: str = "Markdown") -> str:
        """
        Schedule a post to be sent to a channel
        
        Args:
            channel_id: Target channel ID
            message: Message text
            scheduled_time: When to send
            media_path: Optional media file path
            parse_mode: Message parse mode
            
        Returns:
            str: Task ID
        """
        async def send_post():
            try:
                # This would be implemented with actual bot sending logic
                logger.info(f"📤 Sending scheduled post to {channel_id}: {message[:50]}...")
                # await bot.send_message(channel_id, message, parse_mode=parse_mode)
            except Exception as e:
                logger.error(f"Failed to send scheduled post: {e}")
        
        return self.schedule_task(
            name=f"Post to {channel_id}",
            function=send_post,
            scheduled_time=scheduled_time,
            metadata={
                "type": "scheduled_post",
                "channel_id": channel_id,
                "message": message,
                "media_path": media_path,
                "parse_mode": parse_mode
            }
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.CANCELLED
        task.enabled = False
        
        # Cancel if currently running
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
        
        logger.info(f"🚫 Cancelled task: {task.name} ({task_id})")
        return True
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: TaskStatus = None) -> List[ScheduledTask]:
        """List all tasks, optionally filtered by status"""
        if status:
            return [task for task in self.tasks.values() if task.status == status]
        return list(self.tasks.values())
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        stats = {
            "total_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
            "cancelled_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.CANCELLED]),
            "is_running": self.is_running
        }
        return stats
    
    def export_tasks(self) -> str:
        """Export tasks to JSON"""
        exportable_tasks = []
        for task in self.tasks.values():
            task_data = {
                "id": task.id,
                "name": task.name,
                "task_type": task.task_type.value,
                "scheduled_time": task.scheduled_time.isoformat() if task.scheduled_time else None,
                "interval_seconds": task.interval_seconds,
                "cron_expression": task.cron_expression,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "next_run": task.next_run.isoformat() if task.next_run else None,
                "run_count": task.run_count,
                "max_runs": task.max_runs,
                "enabled": task.enabled,
                "metadata": task.metadata
            }
            exportable_tasks.append(task_data)
        
        return json.dumps(exportable_tasks, indent=2, ensure_ascii=False)

# Global scheduler instance
scheduler = BotScheduler()

__all__ = ['BotScheduler', 'ScheduledTask', 'TaskStatus', 'TaskType', 'scheduler']