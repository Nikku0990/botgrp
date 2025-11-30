#!/usr/bin/env python3
"""
👑 ADMIN COMMANDS
Ultimate Group King Bot - Admin & Moderation Commands
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import html
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from telegram import Update, Bot, ChatPermissions
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest
from telegram.constants import ParseMode

from config import (
    OWNER_ID, TIME_FORMATS, DEFAULT_GROUP_CONFIG, 
    EMOJIS, MAX_LIMITS
)
from database import Database

db = Database()
db.connect()

class AdminCommands:
    """Handles all admin and moderation commands"""
    
    def __init__(self):
        self.pending_bans = {}  # For confirmation dialogs
        # Connect to database
        if not db.connect():
            print("⚠️ AdminCommands: Database connection failed")
    
    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is admin or owner"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Owner is always admin
        if user_id == OWNER_ID:
            return True
        
        # Check temporary admin
        user = db.get_or_create_user(user_id)
        if user.get('is_temp_admin', False):
            return True
        
        # Check Telegram admin status
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except TelegramError:
            return False
    
    async def is_owner(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is bot owner"""
        return update.effective_user.id == OWNER_ID
    
    def parse_time(self, time_str: str) -> int:
        """Parse time string like '1h', '30m', '2d' to seconds"""
        time_str = time_str.lower().strip()
        
        for suffix, multiplier in TIME_FORMATS.items():
            if time_str.endswith(suffix):
                try:
                    number = int(time_str[:-suffix])
                    return number * multiplier
                except ValueError:
                    continue
        
        return 3600  # Default 1 hour
    
    def get_user_mention(self, user) -> str:
        """Get formatted user mention"""
        if user.username:
            return f"@{user.username}"
        else:
            return f"[{html.escape(user.first_name)}](tg://user?id={user.id})"
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ban a user from the group"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai, chutiye!")
            return
        
        # Get target user
        target_user = None
        reason = "No reason provided"
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
            if context.args:
                reason = " ".join(context.args)
        elif context.args:
            # Try to find user by username or ID
            user_input = context.args[0]
            if user_input.startswith('@'):
                username = user_input[1:]
                try:
                    # Try to get user via @username
                    chat_member = await context.bot.get_chat_member(update.effective_chat.id, username)
                    target_user = chat_member.user
                    # Use the rest of the args as reason
                    if len(context.args) > 1:
                        reason = ' '.join(context.args[1:])
                except:
                    await update.message.reply_text(f"❌ Cannot find user @{username}!\n\n"
                                                  f"Make sure user is in the group.")
                    return
            else:
                try:
                    user_id = int(user_input)
                    # Get user info
                    target_user = await context.bot.get_chat(user_id)
                except (ValueError, BadRequest):
                    await update.message.reply_text("❌ Invalid user ID! Reply to message kar!")
                    return
        else:
            await update.message.reply_text("❌ Kisko ban karna hai? Reply kar ya username de!")
            return
        
        try:
            # Perform ban
            await context.bot.ban_chat_member(update.effective_chat.id, target_user.id)
            
            # Log the action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, target_user.id, "ban", reason)
            
            # Update warnings
            db.add_mod_log(update.effective_chat.id, admin_id, target_user.id, "ban", reason)
            
            # Send confirmation
            mention = self.get_user_mention(target_user)
            await update.message.reply_text(
                f"🚫 **BANNED!** 🚫\n\n"
                f"User: {mention}\n"
                f"Reason: `{reason}`\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
                f"**Ab shanti rahegi!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Ban nahi ho paya! Error: `{e}`")
    
    async def kick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kick a user from the group"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        target_user = None
        reason = "No reason provided"
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
            if context.args:
                reason = " ".join(context.args)
        elif context.args:
            await update.message.reply_text("❌ Reply to message kar!")
            return
        else:
            await update.message.reply_text("❌ Kisko kick karna hai? Reply kar!")
            return
        
        try:
            # Kick = simple unban (removes from group)
            await context.bot.unban_chat_member(update.effective_chat.id, target_user.id)
            
            # Log action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, target_user.id, "kick", reason)
            
            # Send confirmation
            mention = self.get_user_mention(target_user)
            await update.message.reply_text(
                f"🦵 **KICKED!** 🦵\n\n"
                f"User: {mention}\n"
                f"Reason: `{reason}`\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
                f"**Dobara join kar sakta hai!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Kick nahi ho paya! Error: `{e}`")
    
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mute a user for specified duration"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        target_user = None
        duration = 3600  # Default 1 hour
        reason = "No reason provided"
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
            if context.args:
                # First arg might be time
                if context.args[0].endswith(('m', 'h', 'd', 'w')):
                    duration = self.parse_time(context.args[0])
                    reason = " ".join(context.args[1:]) if len(context.args) > 1 else reason
                else:
                    reason = " ".join(context.args)
        elif context.args and len(context.args) >= 2:
            await update.message.reply_text("❌ Reply to message kar!")
            return
        else:
            await update.message.reply_text("❌ Kisko mute karna hai? Reply kar aur time de!")
            return
        
        try:
            # Calculate mute permissions
            mute_permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
            
            # Restrict user
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                target_user.id,
                mute_permissions,
                until_date=update.message.date + timedelta(seconds=duration)
            )
            
            # Log action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, target_user.id, "mute", reason)
            
            # Format duration
            if duration < 3600:
                duration_str = f"{duration // 60} minutes"
            elif duration < 86400:
                duration_str = f"{duration // 3600} hours"
            else:
                duration_str = f"{duration // 86400} days"
            
            # Send confirmation
            mention = self.get_user_mention(target_user)
            await update.message.reply_text(
                f"🔇 **MUTED!** 🔇\n\n"
                f"User: {mention}\n"
                f"Duration: {duration_str}\n"
                f"Reason: `{reason}`\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
                f"**Ab chup baithega!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Mute nahi ho paya! Error: `{e}`")
    
    async def unmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unmute a user"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        target_user = None
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Reply to message kar!")
            return
        else:
            await update.message.reply_text("❌ Kisko unmute karna hai? Reply kar!")
            return
        
        try:
            # Grant full permissions
            full_permissions = ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
            
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                target_user.id,
                full_permissions
            )
            
            # Log action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, target_user.id, "unmute", "Unmuted")
            
            # Send confirmation
            mention = self.get_user_mention(target_user)
            await update.message.reply_text(
                f"🔊 **UNMUTED!** 🔊\n\n"
                f"User: {mention}\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
                f"**Ab bol sakta hai!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Unmute nahi ho paya! Error: `{e}`")
    
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Warn a user"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        target_user = None
        reason = "No reason provided"
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
            if context.args:
                reason = " ".join(context.args)
        elif context.args:
            await update.message.reply_text("❌ Reply to message kar!")
            return
        else:
            await update.message.reply_text("❌ Kisko warn karna hai? Reply kar!")
            return
        
        try:
            chat_id = update.effective_chat.id
            
            # Get group settings
            settings = db.get_group_settings(chat_id)
            max_warnings = settings.get('max_warnings', 3)
            
            # Add warning to database
            db.add_mod_log(chat_id, update.effective_user.id, target_user.id, "warn", reason)
            
            # Count user's warnings
            warnings = db.get_mod_logs(chat_id)
            user_warnings = [w for w in warnings if w['target_id'] == target_user.id and w['action'] == 'warn']
            warning_count = len(user_warnings)
            
            # Check if auto-action needed
            if warning_count >= max_warnings:
                auto_action = settings.get('auto_action', 'mute')
                
                if auto_action == 'mute':
                    # Auto mute for 1 hour
                    mute_permissions = ChatPermissions(can_send_messages=False)
                    await context.bot.restrict_chat_member(
                        chat_id, target_user.id, mute_permissions,
                        until_date=update.message.date + timedelta(hours=1)
                    )
                    action_text = "🔇 **AUTO MUTED!** (1 hour)"
                elif auto_action == 'kick':
                    await context.bot.unban_chat_member(chat_id, target_user.id)
                    action_text = "🦵 **AUTO KICKED!**"
                elif auto_action == 'ban':
                    await context.bot.ban_chat_member(chat_id, target_user.id)
                    action_text = "🚫 **AUTO BANNED!**"
                else:
                    action_text = ""
                
                # Log auto action
                await self._log_action(context, chat_id, update.effective_user.id, target_user.id, auto_action, f"Auto action after {warning_count} warnings")
            else:
                action_text = ""
            
            # Send warning message
            mention = self.get_user_mention(target_user)
            warning_text = (
                f"⚠️ **WARNING!** ⚠️\n\n"
                f"User: {mention}\n"
                f"Warning: {warning_count}/{max_warnings}\n"
                f"Reason: `{reason}`\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
            )
            
            if action_text:
                warning_text += f"{action_text}\n\n"
            
            warning_text += f"**Agar {max_warnings - warning_count} aur warn mile to {auto_action} ho jaega!**"
            
            await update.message.reply_text(warning_text, parse_mode=ParseMode.MARKDOWN)
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Warning nahi ho paya! Error: `{e}`")
    
    async def promote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Promote a user to admin"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        target_user = None
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Reply to message kar!")
            return
        else:
            await update.message.reply_text("❌ Kisko promote karna hai? Reply kar!")
            return
        
        try:
            await context.bot.promote_chat_member(
                update.effective_chat.id,
                target_user.id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_manage_chat=True,
                can_manage_video_chats=True
            )
            
            # Log action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, target_user.id, "promote", "Promoted to admin")
            
            # Send confirmation
            mention = self.get_user_mention(target_user)
            await update.message.reply_text(
                f"👑 **PROMOTED!** 👑\n\n"
                f"User: {mention}\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
                f"**Ab admin ban gaya!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Promote nahi ho paya! Error: `{e}`")
    
    async def demote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Demote an admin"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        target_user = None
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args:
            await update.message.reply_text("❌ Reply to message kar!")
            return
        else:
            await update.message.reply_text("❌ Kisko demote karna hai? Reply kar!")
            return
        
        try:
            await context.bot.promote_chat_member(
                update.effective_chat.id,
                target_user.id,
                can_change_info=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_manage_chat=False,
                can_manage_video_chats=False
            )
            
            # Log action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, target_user.id, "demote", "Demoted from admin")
            
            # Send confirmation
            mention = self.get_user_mention(target_user)
            await update.message.reply_text(
                f"👤 **DEMOTED!** 👤\n\n"
                f"User: {mention}\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
                f"**Ab admin nahi raha!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Demote nahi ho paya! Error: `{e}`")
    
    async def pin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pin a message"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        if update.message.reply_to_message:
            try:
                await context.bot.pin_chat_message(
                    update.effective_chat.id,
                    update.message.reply_to_message.message_id,
                    disable_notification=True
                )
                
                # Log action
                admin_id = update.effective_user.id
                await self._log_action(context, update.effective_chat.id, admin_id, 0, "pin", f"Pinned message {update.message.reply_to_message.message_id}")
                
                await update.message.reply_text("📌 **PINNED!** 📌\n\nMessage pinned successfully!")
            
            except TelegramError as e:
                await update.message.reply_text(f"❌ Pin nahi ho paya! Error: `{e}`")
        else:
            await update.message.reply_text("❌ Kya pin karna hai? Reply kar!")
    
    async def unpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unpin current pinned message"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        try:
            await context.bot.unpin_chat_message(update.effective_chat.id)
            
            # Log action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, 0, "unpin", "Unpinned message")
            
            await update.message.reply_text("📌 **UNPINNED!** 📌\n\nMessage unpinned successfully!")
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Unpin nahi ho paya! Error: `{e}`")
    
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete a message"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        if update.message.reply_to_message:
            try:
                await context.bot.delete_message(
                    update.effective_chat.id,
                    update.message.reply_to_message.message_id
                )
                
                # Log action
                admin_id = update.effective_user.id
                await self._log_action(context, update.effective_chat.id, admin_id, 0, "delete", f"Deleted message {update.message.reply_to_message.message_id}")
                
                # Also delete the command message
                await update.message.delete()
            
            except TelegramError as e:
                await update.message.reply_text(f"❌ Delete nahi ho paya! Error: `{e}`")
        else:
            await update.message.reply_text("❌ Kya delete karna hai? Reply kar!")
    
    async def purge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Purge multiple messages"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Kaha se purg karna hai? Reply kar!")
            return
        
        try:
            # Get messages to delete (from replied message to current)
            start_id = update.message.reply_to_message.message_id
            end_id = update.message.message_id
            
            messages_deleted = 0
            for msg_id in range(start_id, end_id + 1):
                try:
                    await context.bot.delete_message(update.effective_chat.id, msg_id)
                    messages_deleted += 1
                except:
                    pass
            
            # Log action
            admin_id = update.effective_user.id
            await self._log_action(context, update.effective_chat.id, admin_id, 0, "purge", f"Purged {messages_deleted} messages")
            
            await update.message.reply_text(
                f"🧹 **PURGED!** 🧹\n\n"
                f"Messages deleted: {messages_deleted}\n"
                f"Admin: {self.get_user_mention(update.effective_user)}\n\n"
                f"**Safai ho gayi!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Purge nahi ho paya! Error: `{e}`")
    
    async def adminlist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all admins in the group"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return
        
        try:
            administrators = await context.bot.get_chat_administrators(update.effective_chat.id)
            
            admin_text = "👑 **GROUP ADMINS** 👑\n\n"
            
            for admin in administrators:
                if admin.user.is_bot:
                    admin_text += f"🤖 {self.get_user_mention(admin.user)} - Bot\n"
                elif admin.status == 'creator':
                    admin_text += f"👑 {self.get_user_mention(admin.user)} - Owner\n"
                else:
                    admin_text += f"🛡️ {self.get_user_mention(admin.user)} - Admin\n"
            
            await update.message.reply_text(admin_text, parse_mode=ParseMode.MARKDOWN)
        
        except TelegramError as e:
            await update.message.reply_text(f"❌ Admin list nahi mil paya! Error: `{e}`")
    
    async def _log_action(self, context, chat_id: int, admin_id: int, target_id: int, action: str, reason: str):
        """Log moderation action"""
        try:
            details = {
                "action": action,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            db.add_mod_log(chat_id, admin_id, target_id, action, reason, details)
            
            # Send to log channel if set
            settings = db.get_group_settings(chat_id)
            log_channel = settings.get('log_channel')
            
            if log_channel:
                try:
                    admin_user = await context.bot.get_chat(admin_id)
                    admin_mention = self.get_user_mention(admin_user)
                    
                    log_text = f"🔹 **{action.upper()}** 🔹\n\n"
                    log_text += f"Admin: {admin_mention}\n"
                    log_text += f"Target: `{target_id}`\n"
                    log_text += f"Reason: `{reason}`\n"
                    log_text += f"Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
                    
                    await context.bot.send_message(log_channel, log_text, parse_mode=ParseMode.MARKDOWN)
                except:
                    pass  # Ignore log channel errors
        
        except Exception as e:
            print(f"Failed to log action: {e}")

# Initialize admin commands
admin_commands = AdminCommands()

if __name__ == "__main__":
    print("👑 Admin commands module loaded!")
    print("Available commands: ban, kick, mute, unmute, warn, promote, demote, pin, unpin, delete, purge, adminlist")
