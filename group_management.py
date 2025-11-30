#!/usr/bin/env python3
"""
👥 GROUP MANAGEMENT
Ultimate Group King Bot - Group Settings, Welcome, Rules, Locks
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import html
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import (
    DEFAULT_GROUP_CONFIG, LOCKABLE_ITEMS, EMOJIS, 
    COMMAND_CATEGORIES, OWNER_ID
)
from database import Database

# Conversation states
SETTING_WELCOME, SETTING_RULES, SETTING_GOODBYE = range(3)

class GroupManagement:
    """Handles all group management features"""
    
    def __init__(self):
        self.pending_settings = {}  # For multi-step conversations
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is admin"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if user_id == OWNER_ID:
            return True
        
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except:
            return False
    
    def get_user_mention(self, user) -> str:
        """Get formatted user mention"""
        if user.username:
            return f"@{user.username}"
        else:
            return f"[{html.escape(user.first_name)}](tg://user?id={user.id})"
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group settings menu"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command!")
            return
        
        chat_id = update.effective_chat.id
        settings = db.get_group_settings(chat_id)
        
        # Create settings menu
        keyboard = [
            [
                InlineKeyboardButton("👋 Welcome", callback_data="settings_welcome"),
                InlineKeyboardButton("👋 Goodbye", callback_data="settings_goodbye")
            ],
            [
                InlineKeyboardButton("📜 Rules", callback_data="settings_rules"),
                InlineKeyboardButton("🔒 Locks", callback_data="settings_locks")
            ],
            [
                InlineKeyboardButton("⚙️ General", callback_data="settings_general"),
                InlineKeyboardButton("🔊 Anti-Spam", callback_data="settings_antispam")
            ],
            [
                InlineKeyboardButton("📋 Tasks", callback_data="settings_tasks"),
                InlineKeyboardButton("🤖 AI", callback_data="settings_ai")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="settings_stats"),
                InlineKeyboardButton("💾 Backup", callback_data="settings_backup")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings_text = f"""⚙️ **GROUP SETTINGS** ⚙️

📝 **Current Status:**
👋 Welcome: {'✅ ON' if settings.get('welcome_enabled') else '❌ OFF'}
👋 Goodbye: {'✅ ON' if settings.get('goodbye_enabled') else '❌ OFF'}
📜 Rules: {'✅ Set' if settings.get('rules_text') else '❌ Not set'}
🔒 Locks: {sum(settings.get('locks', {}).values())} active
📋 Tasks: {'✅ ON' if settings.get('task_system_active') else '❌ OFF'}
🤖 AI: {'✅ ON' if settings.get('smart_detection') else '❌ OFF'}

Choose an option to manage settings:"""
        
        await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings menu callbacks"""
        query = update.callback_query
        await query.answer()
        
        chat_id = update.effective_chat.id
        settings = db.get_group_settings(chat_id)
        
        if query.data == "settings_welcome":
            await self._show_welcome_settings(query, settings)
        elif query.data == "settings_goodbye":
            await self._show_goodbye_settings(query, settings)
        elif query.data == "settings_rules":
            await self._show_rules_settings(query, settings)
        elif query.data == "settings_locks":
            await self._show_locks_settings(query, settings)
        elif query.data == "settings_general":
            await self._show_general_settings(query, settings)
        elif query.data == "settings_antispam":
            await self._show_antispam_settings(query, settings)
        elif query.data == "settings_tasks":
            await self._show_tasks_settings(query, settings)
        elif query.data == "settings_ai":
            await self._show_ai_settings(query, settings)
        elif query.data == "settings_stats":
            await self._show_stats_settings(query, settings)
        elif query.data == "settings_backup":
            await self._show_backup_settings(query, settings)
        elif query.data.startswith("toggle_"):
            await self._toggle_setting(query, settings)
        elif query.data.startswith("lock_"):
            await self._toggle_lock(query, settings)
    
    async def _show_welcome_settings(self, query, settings):
        """Show welcome settings"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"👋 {'Disable' if settings.get('welcome_enabled') else 'Enable'}",
                    callback_data="toggle_welcome_enabled"
                )
            ],
            [
                InlineKeyboardButton("✏️ Edit Message", callback_data="edit_welcome"),
                InlineKeyboardButton("🔄 Reset", callback_data="reset_welcome")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = settings.get('welcome_text', DEFAULT_GROUP_CONFIG['welcome_text'])
        
        text = f"""👋 **WELCOME SETTINGS** 👋

Status: {'✅ Enabled' if settings.get('welcome_enabled') else '❌ Disabled'}

Current message:
```
{welcome_text}
```

**Variables available:**
- `{{mention}}` - User mention
- `{{chat}}` - Chat name
- `{{count}}` - Member count"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_goodbye_settings(self, query, settings):
        """Show goodbye settings"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"👋 {'Disable' if settings.get('goodbye_enabled') else 'Enable'}",
                    callback_data="toggle_goodbye_enabled"
                )
            ],
            [
                InlineKeyboardButton("✏️ Edit Message", callback_data="edit_goodbye"),
                InlineKeyboardButton("🔄 Reset", callback_data="reset_goodbye")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        goodbye_text = settings.get('goodbye_text', DEFAULT_GROUP_CONFIG['goodbye_text'])
        
        text = f"""👋 **GOODBYE SETTINGS** 👋

Status: {'✅ Enabled' if settings.get('goodbye_enabled') else '❌ Disabled'}

Current message:
```
{goodbye_text}
```

**Variables available:**
- `{{mention}}` - User mention
- `{{chat}}` - Chat name"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_rules_settings(self, query, settings):
        """Show rules settings"""
        keyboard = [
            [
                InlineKeyboardButton("✏️ Edit Rules", callback_data="edit_rules"),
                InlineKeyboardButton("🔄 Reset", callback_data="reset_rules")
            ],
            [
                InlineKeyboardButton("📢 Show Rules", callback_data="show_rules"),
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        rules_text = settings.get('rules_text', DEFAULT_GROUP_CONFIG['rules_text'])
        
        text = f"""📜 **RULES SETTINGS** 📜

Current rules:
```
{rules_text}
```

**Formatting:**
- Markdown supported
- Use `**bold**` for emphasis
- Use `*italic*` for style"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_locks_settings(self, query, settings):
        """Show locks settings"""
        locks = settings.get('locks', {})
        
        # Create lock buttons
        lock_buttons = []
        for i in range(0, len(LOCKABLE_ITEMS), 2):
            row = []
            for item in LOCKABLE_ITEMS[i:i+2]:
                status = "🔒" if locks.get(item, False) else "🔓"
                row.append(InlineKeyboardButton(f"{status} {item}", callback_data=f"lock_{item}"))
            lock_buttons.append(row)
        
        lock_buttons.append([
            InlineKeyboardButton("🔓 Unlock All", callback_data="unlock_all"),
            InlineKeyboardButton("🔒 Lock All", callback_data="lock_all")
        ])
        lock_buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
        ])
        
        reply_markup = InlineKeyboardMarkup(lock_buttons)
        
        active_locks = sum(locks.values())
        
        text = f"""🔒 **LOCK SETTINGS** 🔒

Active locks: {active_locks}/{len(LOCKABLE_ITEMS)}

**Lock Types:**
- **messages** - Text messages
- **media** - Photos, videos, etc.
- **stickers** - Stickers
- **gifs** - GIF files
- **voice** - Voice messages
- **links** - URLs/links
- **forwards** - Forwarded messages
- **commands** - Bot commands
- **bots** - Bot messages
- **inline** - Inline queries

Click to toggle locks:"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_general_settings(self, query, settings):
        """Show general settings"""
        keyboard = [
            [
                InlineKeyboardButton("⚠️ Warnings", callback_data="edit_warnings"),
                InlineKeyboardButton("🔧 Auto Action", callback_data="edit_auto_action")
            ],
            [
                InlineKeyboardButton("🌊 Flood Limit", callback_data="edit_flood"),
                InlineKeyboardButton("📊 Log Channel", callback_data="edit_log_channel")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""⚙️ **GENERAL SETTINGS** ⚙️

⚠️ **Max Warnings:** {settings.get('max_warnings', 3)}
🔧 **Auto Action:** {settings.get('auto_action', 'mute').upper()}
🌊 **Flood Limit:** {settings.get('flood_limit', 5)} msgs/min
📊 **Log Channel:** {settings.get('log_channel', 'Not set')}

**Auto Actions:**
- **mute** - Mute user
- **kick** - Kick user  
- **ban** - Ban user"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_antispam_settings(self, query, settings):
        """Show anti-spam settings"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🤖 Captcha {'ON' if settings.get('captcha_enabled') else 'OFF'}",
                    callback_data="toggle_captcha"
                ),
                InlineKeyboardButton(
                    f"✅ Approval {'ON' if settings.get('approval_mode') else 'OFF'}",
                    callback_data="toggle_approval"
                )
            ],
            [
                InlineKeyboardButton("🛡️ Filters", callback_data="edit_filters"),
                InlineKeyboardButton("🚫 Blacklist", callback_data="edit_blacklist")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""🔊 **ANTI-SPAM SETTINGS** 🔊

🤖 **Captcha:** {'✅ Enabled' if settings.get('captcha_enabled') else '❌ Disabled'}
✅ **Approval Mode:** {'✅ Enabled' if settings.get('approval_mode') else '❌ Disabled'}
🛡️ **Filters:** {len(settings.get('filters', {}))} active
🚫 **Blacklist:** {len(settings.get('blacklist', []))} words

**Protection Levels:**
- **low** - Basic protection
- **medium** - Standard protection  
- **high** - Maximum protection"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_tasks_settings(self, query, settings):
        """Show task system settings"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"📋 Tasks {'ON' if settings.get('task_system_active') else 'OFF'}",
                    callback_data="toggle_tasks"
                )
            ],
            [
                InlineKeyboardButton("💎 EXP Required", callback_data="edit_exp_required"),
                InlineKeyboardButton("⏰ Admin Duration", callback_data="edit_admin_duration")
            ],
            [
                InlineKeyboardButton("🏆 View Tasks", callback_data="view_tasks"),
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""📋 **TASK SYSTEM SETTINGS** 📋

📋 **Status:** {'✅ Enabled' if settings.get('task_system_active') else '❌ Disabled'}
💎 **EXP for Admin:** {settings.get('exp_to_admin', 500)}
⏰ **Admin Duration:** {settings.get('admin_duration', 2)} minutes

**EXP Thresholds:**
- 500 EXP = 2 min admin
- 1000 EXP = 5 min admin
- 5000 EXP = 30 min admin
- 10000 EXP = 2 hours admin"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_ai_settings(self, query, settings):
        """Show AI settings"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🧠 Smart Detection {'ON' if settings.get('smart_detection') else 'OFF'}",
                    callback_data="toggle_smart_detection"
                )
            ],
            [
                InlineKeyboardButton("🤖 AI Model", callback_data="edit_ai_model"),
                InlineKeyboardButton("🔧 AI Settings", callback_data="edit_ai_settings")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""🤖 **AI SETTINGS** 🤖

🧠 **Smart Detection:** {'✅ Enabled' if settings.get('smart_detection') else '❌ Disabled'}

**Features:**
- Commands without `/`
- Natural language processing
- Context understanding
- Auto-correction

**Example:**
- "ban rahul" → /ban rahul
- "weather delhi" → /weather delhi
- "mute @user 5m" → /mute @user 5m"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_stats_settings(self, query, settings):
        """Show statistics"""
        chat_id = update.callback_query.message.chat.id
        
        # Get statistics
        # from database import db  # DISABLED FOR TESTING
        stats = db.get_database_stats()
        
        # Get group-specific stats
        group_stats = db.get_statistics(chat_id, days=7)
        
        # Count messages in last 7 days
        message_count = len([s for s in group_stats if s['stat_type'] == 'messages'])
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Detailed Stats", callback_data="detailed_stats"),
                InlineKeyboardButton("📈 Analytics", callback_data="analytics")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""📊 **GROUP STATISTICS** 📊

📈 **Last 7 Days:**
- Messages: {message_count}
- Commands: {len([s for s in group_stats if s['stat_type'] == 'commands'])}
- Warnings: {len([s for s in group_stats if s['stat_type'] == 'warnings'])}

🌍 **Global Stats:**
- Total Users: {stats.get('users', 0)}
- Total Groups: {stats.get('groups', 0)}
- Total Tasks: {stats.get('tasks', 0)}
- Database Size: {stats.get('file_size_mb', 0)} MB"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _show_backup_settings(self, query, settings):
        """Show backup settings"""
        keyboard = [
            [
                InlineKeyboardButton("💾 Create Backup", callback_data="create_backup"),
                InlineKeyboardButton("📥 Restore Backup", callback_data="restore_backup")
            ],
            [
                InlineKeyboardButton("📋 View Backups", callback_data="view_backups"),
                InlineKeyboardButton("⬅️ Back", callback_data="settings_main")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""💾 **BACKUP & RESTORE** 💾

**Backup includes:**
- Group settings
- Custom commands
- Filters & notes
- User data
- Task progress

**Auto-backup:** Every 24 hours
**Max backups:** 7 per group

⚠️ **Warning:** Restore will overwrite current settings!"""
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def _toggle_setting(self, query, settings):
        """Toggle a setting"""
        chat_id = query.message.chat.id
        setting = query.data.replace("toggle_", "")
        
        if setting == "welcome_enabled":
            settings[setting] = not settings.get(setting, False)
        elif setting == "goodbye_enabled":
            settings[setting] = not settings.get(setting, False)
        elif setting == "captcha":
            settings['captcha_enabled'] = not settings.get('captcha_enabled', False)
        elif setting == "approval":
            settings['approval_mode'] = not settings.get('approval_mode', False)
        elif setting == "tasks":
            settings['task_system_active'] = not settings.get('task_system_active', False)
        elif setting == "smart_detection":
            settings['smart_detection'] = not settings.get('smart_detection', False)
        
        # Save settings
        db.update_group_settings(chat_id, settings)
        
        # Update the menu
        if "welcome" in setting:
            await self._show_welcome_settings(query, settings)
        elif "goodbye" in setting:
            await self._show_goodbye_settings(query, settings)
        elif setting in ["captcha", "approval"]:
            await self._show_antispam_settings(query, settings)
        elif setting == "tasks":
            await self._show_tasks_settings(query, settings)
        elif setting == "smart_detection":
            await self._show_ai_settings(query, settings)
    
    async def _toggle_lock(self, query, settings):
        """Toggle a lock"""
        chat_id = query.message.chat.id
        lock_type = query.data.replace("lock_", "")
        
        if lock_type == "all":
            # Lock all
            for item in LOCKABLE_ITEMS:
                settings['locks'][item] = True
        elif lock_type == "unlock_all":
            # Unlock all
            for item in LOCKABLE_ITEMS:
                settings['locks'][item] = False
        else:
            # Toggle specific lock
            settings['locks'][lock_type] = not settings['locks'].get(lock_type, False)
        
        # Save settings
        db.update_group_settings(chat_id, settings)
        
        # Update the menu
        await self._show_locks_settings(query, settings)
    
    async def setwelcome_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set welcome message"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command!")
            return
        
        chat_id = update.effective_chat.id
        
        if context.args:
            welcome_text = " ".join(context.args)
        elif update.message.reply_to_message and update.message.reply_to_message.text:
            welcome_text = update.message.reply_to_message.text
        else:
            await update.message.reply_text("❌ Welcome message kya hai? Reply kar ya text de!")
            return
        
        # Simple storage without database
        if not hasattr(self, 'welcome_messages'):
            self.welcome_messages = {}
        
        self.welcome_messages[chat_id] = welcome_text
        
        await update.message.reply_text(f"✅ Welcome message set:\n\n{welcome_text}")
        
        await update.message.reply_text(
            f"✅ **Welcome message set!** ✅\n\n"
            f"```\n{welcome_text}\n```\n\n"
            f"Welcome enabled automatically!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def setrules_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set group rules"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command!")
            return
        
        chat_id = update.effective_chat.id
        
        if context.args:
            rules_text = " ".join(context.args)
        elif update.message.reply_to_message and update.message.reply_to_message.text:
            rules_text = update.message.reply_to_message.text
        else:
            await update.message.reply_text("❌ Rules kya hai? Reply kar ya text de!")
            return
        
        # Update settings
        settings = db.get_group_settings(chat_id)
        settings['rules_text'] = rules_text
        db.update_group_settings(chat_id, settings)
        
        await update.message.reply_text(
            f"✅ **Rules updated!** ✅\n\n"
            f"```\n{rules_text}\n```\n\n"
            f"Use /rules to show them!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def rules_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group rules"""
        chat_id = update.effective_chat.id
        settings = db.get_group_settings(chat_id)
        
        rules_text = settings.get('rules_text', DEFAULT_GROUP_CONFIG['rules_text'])
        
        await update.message.reply_text(
            f"📜 **GROUP RULES** 📜\n\n{rules_text}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def lock_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lock items in group"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command!")
            return
        
        if not context.args:
            await update.message.reply_text(
                f"❌ Kya lock karna hai?\n\n"
                f"Available: {', '.join(LOCKABLE_ITEMS[:10])}\n"
                f"Example: /lock stickers links"
            )
            return
        
        chat_id = update.effective_chat.id
        items_to_lock = context.args
        
        settings = db.get_group_settings(chat_id)
        locks = settings.get('locks', {})
        
        for item in items_to_lock:
            if item in LOCKABLE_ITEMS:
                locks[item] = True
        
        settings['locks'] = locks
        db.update_group_settings(chat_id, settings)
        
        await update.message.reply_text(
            f"🔒 **LOCKED!** 🔒\n\n"
            f"Items locked: {', '.join(items_to_lock)}\n\n"
            f"Ab sirf admins use kar sakte hain!"
        )
    
    async def unlock_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unlock items in group"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Kya unlock karna hai?")
            return
        
        chat_id = update.effective_chat.id
        items_to_unlock = context.args
        
        settings = db.get_group_settings(chat_id)
        locks = settings.get('locks', {})
        
        for item in items_to_unlock:
            if item in LOCKABLE_ITEMS:
                locks[item] = False
        
        settings['locks'] = locks
        db.update_group_settings(chat_id, settings)
        
        await update.message.reply_text(
            f"🔓 **UNLOCKED!** 🔓\n\n"
            f"Items unlocked: {', '.join(items_to_unlock)}\n\n"
            f"Ab sab use kar sakte hain!"
        )
    
    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new member welcome"""
        chat_id = update.effective_chat.id
        settings = db.get_group_settings(chat_id)
        
        if not settings.get('welcome_enabled'):
            return
        
        welcome_text = settings.get('welcome_text', DEFAULT_GROUP_CONFIG['welcome_text'])
        
        for new_member in update.message.new_chat_members:
            # Get user mention
            if new_member.username:
                mention = f"@{new_member.username}"
            else:
                mention = f"[{html.escape(new_member.first_name)}](tg://user?id={new_member.id})"
            
            # Replace variables
            formatted_text = welcome_text.format(
                mention=mention,
                chat=update.effective_chat.title,
                count=await context.bot.get_chat_member_count(chat_id)
            )
            
            # Send welcome message
            await context.bot.send_message(
                chat_id,
                formatted_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Add to user database
            db.get_or_create_user(
                new_member.id,
                new_member.username,
                new_member.first_name,
                new_member.last_name,
                new_member.is_bot
            )
    
    async def goodbye_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle member goodbye"""
        chat_id = update.effective_chat.id
        settings = db.get_group_settings(chat_id)
        
        if not settings.get('goodbye_enabled'):
            return
        
        goodbye_text = settings.get('goodbye_text', DEFAULT_GROUP_CONFIG['goodbye_text'])
        
        left_member = update.message.left_chat_member
        
        # Get user mention
        if left_member.username:
            mention = f"@{left_member.username}"
        else:
            mention = f"[{html.escape(left_member.first_name)}](tg://user?id={left_member.id})]"
        
        # Replace variables
        formatted_text = goodbye_text.format(
            mention=mention,
            chat=update.effective_chat.title
        )
        
        # Send goodbye message
        await context.bot.send_message(
            chat_id,
            formatted_text,
            parse_mode=ParseMode.MARKDOWN
        )

    async def requestban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Request a ban for a user"""
        user = update.effective_user
        chat = update.effective_chat
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to the user you want to ban!")
            return
            
        target_user = update.message.reply_to_message.from_user
        reason = " ".join(context.args) if context.args else "No reason provided"
        
        # Notify Admins
        admins = await context.bot.get_chat_administrators(chat.id)
        admin_mentions = []
        for admin in admins:
            if not admin.user.is_bot:
                admin_mentions.append(self.get_user_mention(admin.user))
        
        admin_text = ", ".join(admin_mentions)
        
        await update.message.reply_text(
            f"🚨 **BAN REQUEST** 🚨\n\n"
            f"👤 **Target:** {self.get_user_mention(target_user)}\n"
            f"📝 **Reason:** {reason}\n"
            f"👮 **Admins:** {admin_text}\n\n"
            f"Admins, please review!",
            parse_mode=ParseMode.MARKDOWN
        )

# Initialize group management
group_management = GroupManagement()

if __name__ == "__main__":
    print("👥 Group management module loaded!")
    print("Features: settings, welcome, rules, locks, anti-spam")
