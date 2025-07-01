#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import traceback

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Import local modules
import config
from userbot import bot_instance
from utils.helpers import is_admin, format_duration, split_message

# Configure logging
logger = logging.getLogger(__name__)

class TelegramControlBot:
    def __init__(self):
        self.application = None
        self.userbot = bot_instance
        
    async def start(self):
        """Start the control bot"""
        try:
            logger.info("Starting Control Bot...")
            
            # Create application
            self.application = Application.builder().token(config.CONTROL_BOT_TOKEN).build()
            
            # Register handlers
            self._register_handlers()
            
            # Set commands
            await self._set_commands()
            
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Control Bot started successfully!")
            
        except Exception as e:
            logger.error(f"Failed to start control bot: {e}")
            raise
    
    async def stop(self):
        """Stop the control bot"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        logger.info("Control Bot stopped")
    
    def _register_handlers(self):
        """Register all command and callback handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Channel management
        self.application.add_handler(CommandHandler("channels", self.channels_command))
        self.application.add_handler(CommandHandler("addchannel", self.add_channel_command))
        self.application.add_handler(CommandHandler("removechannel", self.remove_channel_command))
        
        # Message management
        self.application.add_handler(CommandHandler("post", self.post_command))
        self.application.add_handler(CommandHandler("schedule", self.schedule_command))
        
        # Settings
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("filters", self.filters_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for text input
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler))
        
        logger.info("Control bot handlers registered")
    
    async def _set_commands(self):
        """Set bot commands for the menu"""
        commands = [
            BotCommand("start", "🚀 بدء البوت"),
            BotCommand("help", "❓ المساعدة"),
            BotCommand("status", "📊 حالة البوت"),
            BotCommand("stats", "📈 الإحصائيات"),
            BotCommand("channels", "📺 إدارة القنوات"),
            BotCommand("post", "📤 نشر منشور"),
            BotCommand("schedule", "⏰ جدولة منشور"),
            BotCommand("settings", "⚙️ الإعدادات"),
            BotCommand("filters", "🔍 الفلاتر"),
        ]
        
        await self.application.bot.set_my_commands(commands)
    
    def _check_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return is_admin(user_id, config.ADMIN_IDS)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._check_admin(update.effective_user.id):
            await update.message.reply_text("❌ غير مصرح لك باستخدام هذا البوت")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("📊 حالة البوت", callback_data="status"),
                InlineKeyboardButton("📈 الإحصائيات", callback_data="stats")
            ],
            [
                InlineKeyboardButton("📺 إدارة القنوات", callback_data="channels"),
                InlineKeyboardButton("📤 نشر منشور", callback_data="post")
            ],
            [
                InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings"),
                InlineKeyboardButton("🔍 الفلاتر", callback_data="filters")
            ],
            [
                InlineKeyboardButton("❓ المساعدة", callback_data="help")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🤖 **مرحباً بك في لوحة تحكم بوت إدارة القنوات**

هذا البوت يساعدك في إدارة قنواتك بشكل متقدم مع ميزات:

✅ إدارة القنوات (إضافة/حذف/قائمة)
✅ فلترة الرسائل المتقدمة
✅ تنسيق وتنظيف النصوص
✅ الترجمة التلقائية
✅ النشر المجدول
✅ إدارة روابط الدعوة
✅ قبول الطلبات التلقائي
✅ إدارة المشرفين

اختر من القائمة أدناه للبدء:
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        help_text = """
📚 **دليل استخدام البوت**

**أوامر إدارة القنوات:**
• `/channels` - عرض قائمة القنوات المُدارة
• `/addchannel <معرف القناة>` - إضافة قناة جديدة
• `/removechannel <معرف القناة>` - حذف قناة

**أوامر النشر:**
• `/post <معرف القناة> <النص>` - نشر منشور مباشر
• `/schedule <معرف القناة> <الوقت> <النص>` - جدولة منشور

**أوامر المراقبة:**
• `/status` - حالة البوت الحالية
• `/stats` - إحصائيات مفصلة

**أوامر الإعدادات:**
• `/settings` - إعدادات البوت العامة
• `/filters` - إعدادات فلاتر الرسائل

**تنسيق الوقت للجدولة:**
• `5m` = 5 دقائق
• `2h` = ساعتين
• `1d` = يوم واحد
• `2023-12-25 15:30` = تاريخ ووقت محدد

**معرفات القنوات:**
• يمكن استخدام اسم المستخدم: `@channel_username`
• أو المعرف الرقمي: `-1001234567890`
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        if not self.userbot:
            await update.message.reply_text("❌ UserBot غير متصل")
            return
        
        stats = self.userbot.get_bot_stats()
        
        status_text = f"""
📊 **حالة البوت**

🔹 **الحالة:** {'🟢 يعمل' if stats['is_running'] else '🔴 متوقف'}
🔹 **وقت التشغيل:** {stats['uptime_formatted']}
🔹 **القنوات المُدارة:** {stats['managed_channels']}
🔹 **الرسائل المعالجة:** {stats['messages_processed']:,}
🔹 **الرسائل المُوجهة:** {stats['messages_forwarded']:,}
🔹 **الرسائل المفلترة:** {stats['messages_filtered']:,}

⏰ **وقت البدء:** {stats['start_time'][:19] if stats['start_time'] else 'غير معروف'}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        if not self.userbot:
            await update.message.reply_text("❌ UserBot غير متصل")
            return
        
        try:
            channels = await self.userbot.get_managed_channels()
            stats = self.userbot.get_bot_stats()
            
            stats_text = f"""
📈 **إحصائيات مفصلة**

📊 **إحصائيات عامة:**
• مدة التشغيل: {stats['uptime_formatted']}
• الرسائل المعالجة: {stats['messages_processed']:,}
• الرسائل المُوجهة: {stats['messages_forwarded']:,}
• الرسائل المفلترة: {stats['messages_filtered']:,}

📺 **القنوات المُدارة ({len(channels)}):**
"""
            
            for channel in channels[:10]:  # Show first 10 channels
                stats_text += f"• {channel['title']} ({channel.get('participant_count', 0):,} عضو)\n"
            
            if len(channels) > 10:
                stats_text += f"... و {len(channels) - 10} قناة أخرى"
            
            keyboard = [
                [InlineKeyboardButton("🔄 تحديث", callback_data="stats")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                stats_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في الحصول على الإحصائيات: {str(e)}")
    
    async def channels_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /channels command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        if not self.userbot:
            await update.message.reply_text("❌ UserBot غير متصل")
            return
        
        try:
            channels = await self.userbot.get_managed_channels()
            
            if not channels:
                text = "📺 لا توجد قنوات مُدارة حالياً\n\nاستخدم `/addchannel @channel_username` لإضافة قناة"
            else:
                text = f"📺 **القنوات المُدارة ({len(channels)}):**\n\n"
                
                for i, channel in enumerate(channels, 1):
                    username = f"@{channel['username']}" if channel['username'] else "بدون معرف"
                    text += f"{i}. **{channel['title']}**\n"
                    text += f"   • المعرف: `{channel['id']}`\n"
                    text += f"   • اسم المستخدم: {username}\n"
                    text += f"   • الأعضاء: {channel.get('participant_count', 0):,}\n\n"
            
            keyboard = [
                [
                    InlineKeyboardButton("➕ إضافة قناة", callback_data="add_channel"),
                    InlineKeyboardButton("➖ حذف قناة", callback_data="remove_channel")
                ],
                [InlineKeyboardButton("🔄 تحديث", callback_data="channels")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Split message if too long
            messages = split_message(text, 4000)
            for i, msg in enumerate(messages):
                if i == len(messages) - 1:  # Last message gets the keyboard
                    await update.message.reply_text(
                        msg,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
                    
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في الحصول على القنوات: {str(e)}")
    
    async def add_channel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addchannel command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الرجاء تحديد معرف القناة\n"
                "مثال: `/addchannel @channel_username`\n"
                "أو: `/addchannel -1001234567890`"
            )
            return
        
        channel_identifier = context.args[0]
        
        try:
            success = await self.userbot.add_channel(channel_identifier)
            
            if success:
                await update.message.reply_text(f"✅ تم إضافة القناة بنجاح: {channel_identifier}")
            else:
                await update.message.reply_text(f"❌ فشل في إضافة القناة: {channel_identifier}")
                
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في إضافة القناة: {str(e)}")
    
    async def remove_channel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removechannel command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ الرجاء تحديد معرف القناة\n"
                "مثال: `/removechannel -1001234567890`"
            )
            return
        
        try:
            channel_id = int(context.args[0])
            success = await self.userbot.remove_channel(channel_id)
            
            if success:
                await update.message.reply_text(f"✅ تم حذف القناة بنجاح: {channel_id}")
            else:
                await update.message.reply_text(f"❌ فشل في حذف القناة: {channel_id}")
                
        except ValueError:
            await update.message.reply_text("❌ معرف القناة يجب أن يكون رقماً")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في حذف القناة: {str(e)}")
    
    async def post_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /post command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        await update.message.reply_text(
            "📤 **نشر منشور**\n\n"
            "قم بإرسال رسالة بالتنسيق التالي:\n"
            "`معرف_القناة|النص_المراد_نشره`\n\n"
            "مثال:\n"
            "`-1001234567890|مرحباً بكم في قناتنا!`"
        )
    
    async def schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /schedule command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        await update.message.reply_text(
            "⏰ **جدولة منشور**\n\n"
            "قم بإرسال رسالة بالتنسيق التالي:\n"
            "`معرف_القناة|الوقت|النص`\n\n"
            "أمثلة للوقت:\n"
            "• `5m` - بعد 5 دقائق\n"
            "• `2h` - بعد ساعتين\n"
            "• `2023-12-25 15:30` - في وقت محدد\n\n"
            "مثال:\n"
            "`-1001234567890|1h|سيتم النشر بعد ساعة`"
        )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        keyboard = [
            [
                InlineKeyboardButton("📝 تنسيق النصوص", callback_data="text_formatting"),
                InlineKeyboardButton("🔤 الترجمة", callback_data="translation")
            ],
            [
                InlineKeyboardButton("📋 Headers/Footers", callback_data="headers_footers"),
                InlineKeyboardButton("🔄 استبدال الكلمات", callback_data="word_replacement")
            ],
            [
                InlineKeyboardButton("⏰ قبول الطلبات", callback_data="auto_accept"),
                InlineKeyboardButton("🔗 روابط الدعوة", callback_data="invite_links")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ **إعدادات البوت**\n\nاختر الإعداد الذي تريد تعديله:",
            reply_markup=reply_markup
        )
    
    async def filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /filters command"""
        if not self._check_admin(update.effective_user.id):
            return
        
        keyboard = [
            [
                InlineKeyboardButton("📝 فلتر النصوص", callback_data="text_filters"),
                InlineKeyboardButton("📁 فلتر الوسائط", callback_data="media_filters")
            ],
            [
                InlineKeyboardButton("🔗 فلتر الروابط", callback_data="link_filters"),
                InlineKeyboardButton("🌐 فلتر اللغات", callback_data="language_filters")
            ],
            [
                InlineKeyboardButton("⏰ فلتر الوقت", callback_data="time_filters"),
                InlineKeyboardButton("📏 فلتر الطول", callback_data="length_filters")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔍 **فلاتر الرسائل**\n\nاختر نوع الفلتر الذي تريد إعداده:",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not self._check_admin(query.from_user.id):
            await query.edit_message_text("❌ غير مصرح لك باستخدام هذا البوت")
            return
        
        data = query.data
        
        try:
            if data == "status":
                await self.handle_status_callback(query)
            elif data == "stats":
                await self.handle_stats_callback(query)
            elif data == "channels":
                await self.handle_channels_callback(query)
            elif data == "help":
                await self.handle_help_callback(query)
            else:
                await query.edit_message_text(f"🚧 هذه الميزة قيد التطوير: {data}")
                
        except Exception as e:
            logger.error(f"Error in button callback {data}: {e}")
            await query.edit_message_text(f"❌ خطأ في تنفيذ العملية: {str(e)}")
    
    async def handle_status_callback(self, query):
        """Handle status button callback"""
        if not self.userbot:
            await query.edit_message_text("❌ UserBot غير متصل")
            return
        
        stats = self.userbot.get_bot_stats()
        
        status_text = f"""
📊 **حالة البوت**

🔹 **الحالة:** {'🟢 يعمل' if stats['is_running'] else '🔴 متوقف'}
🔹 **وقت التشغيل:** {stats['uptime_formatted']}
🔹 **القنوات المُدارة:** {stats['managed_channels']}
🔹 **الرسائل المعالجة:** {stats['messages_processed']:,}
🔹 **الرسائل المُوجهة:** {stats['messages_forwarded']:,}
🔹 **الرسائل المفلترة:** {stats['messages_filtered']:,}

⏰ **وقت البدء:** {stats['start_time'][:19] if stats['start_time'] else 'غير معروف'}

🔄 آخر تحديث: {datetime.now().strftime('%H:%M:%S')}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_stats_callback(self, query):
        """Handle stats button callback"""
        # Similar to stats_command but for callback
        await self.stats_command(query, None)
    
    async def handle_channels_callback(self, query):
        """Handle channels button callback"""
        # Similar to channels_command but for callback
        await self.channels_command(query, None)
    
    async def handle_help_callback(self, query):
        """Handle help button callback"""
        await self.help_command(query, None)
    
    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for posting and scheduling"""
        if not self._check_admin(update.effective_user.id):
            return
        
        text = update.message.text
        
        # Check if it's a post command
        if '|' in text:
            parts = text.split('|', 2)
            
            if len(parts) == 2:
                # Direct post: channel_id|text
                await self._handle_direct_post(update, parts[0].strip(), parts[1].strip())
            elif len(parts) == 3:
                # Scheduled post: channel_id|time|text
                await self._handle_scheduled_post(update, parts[0].strip(), parts[1].strip(), parts[2].strip())
    
    async def _handle_direct_post(self, update: Update, channel_id_str: str, text: str):
        """Handle direct posting"""
        try:
            channel_id = int(channel_id_str)
            
            # Send message through userbot
            if self.userbot and self.userbot.client:
                await self.userbot.client.send_message(channel_id, text)
                await update.message.reply_text(f"✅ تم نشر المنشور في القناة {channel_id}")
            else:
                await update.message.reply_text("❌ UserBot غير متصل")
                
        except ValueError:
            await update.message.reply_text("❌ معرف القناة يجب أن يكون رقماً")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في النشر: {str(e)}")
    
    async def _handle_scheduled_post(self, update: Update, channel_id_str: str, time_str: str, text: str):
        """Handle scheduled posting"""
        try:
            channel_id = int(channel_id_str)
            
            # Parse time
            scheduled_time = self._parse_schedule_time(time_str)
            if not scheduled_time:
                await update.message.reply_text("❌ تنسيق الوقت غير صحيح")
                return
            
            # Add to database
            message_data = {'text': text, 'parse_mode': 'html'}
            
            if self.userbot:
                await self.userbot.db.add_scheduled_post(channel_id, message_data, scheduled_time)
                await update.message.reply_text(
                    f"✅ تم جدولة المنشور للنشر في {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            else:
                await update.message.reply_text("❌ UserBot غير متصل")
                
        except ValueError:
            await update.message.reply_text("❌ معرف القناة يجب أن يكون رقماً")
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في الجدولة: {str(e)}")
    
    def _parse_schedule_time(self, time_str: str) -> Optional[datetime]:
        """Parse schedule time string"""
        try:
            time_str = time_str.lower().strip()
            
            # Parse relative time (5m, 2h, 1d)
            if time_str.endswith('m'):
                minutes = int(time_str[:-1])
                return datetime.now() + timedelta(minutes=minutes)
            elif time_str.endswith('h'):
                hours = int(time_str[:-1])
                return datetime.now() + timedelta(hours=hours)
            elif time_str.endswith('d'):
                days = int(time_str[:-1])
                return datetime.now() + timedelta(days=days)
            else:
                # Try to parse absolute time
                return datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                
        except (ValueError, IndexError):
            return None

# Global control bot instance
control_bot_instance = None

async def start_control_bot():
    """Start the control bot"""
    global control_bot_instance
    
    try:
        control_bot_instance = TelegramControlBot()
        await control_bot_instance.start()
    except Exception as e:
        logger.error(f"Failed to start control bot: {e}")
        raise

async def stop_control_bot():
    """Stop the control bot"""
    global control_bot_instance
    
    if control_bot_instance:
        await control_bot_instance.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_control_bot())
    except KeyboardInterrupt:
        logger.info("Control bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start control bot: {e}")
        sys.exit(1)