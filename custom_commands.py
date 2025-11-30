#!/usr/bin/env python3
"""
🔧 CUSTOM COMMANDS
Ultimate Group King Bot - Custom Command Management
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from telegram.constants import ParseMode

from config import MAX_LIMITS
from database import Database

class CustomCommands:
    """Manages custom commands created by admins"""
    
    def __init__(self):
        self.command_cache = {}
        self.media_cache = {}
        self.supported_types = ['text', 'photo', 'video', 'sticker', 'audio', 'document', 'voice', 'animation']
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    async def create_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Create a new custom command"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Check if user is admin
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return False
        
        # Parse command arguments
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Usage: `/setcmd <command_name> <type>`\n\n"
                "Types: text, photo, video, sticker, audio, document, voice, animation\n\n"
                "Example: `/setcmd rules text`\n"
                "Then reply with the content!"
            )
            return False
        
        command_name = context.args[0].lower().strip()
        command_type = context.args[1].lower().strip()
        
        # Validate command name
        if not self._validate_command_name(command_name):
            await update.message.reply_text(
                "❌ Invalid command name!\n\n"
                "Rules:\n"
                "• Only letters, numbers, and underscores\n"
                "• Must start with a letter\n"
                "• Max 20 characters\n"
                "• Cannot conflict with built-in commands"
            )
            return False
        
        # Validate command type
        if command_type not in self.supported_types:
            await update.message.reply_text(
                f"❌ Invalid type! Supported types: {', '.join(self.supported_types)}\n\n"
                "Example: `/setcmd rules text`"
            )
            return False
        
        # Check if command already exists
        existing_cmd = db.get_custom_command(chat_id, command_name)
        if existing_cmd:
            await update.message.reply_text(
                f"❌ Command `/{command_name}` already exists!\n\n"
                f"Type: {existing_cmd['command_type']}\n"
                f"Use `/delcmd {command_name}` to delete it first."
            )
            return False
        
        # Check if user replied to a message
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ Please reply to a message with the content for the command!\n\n"
                f"1. Send the content (text/photo/video/etc.)\n"
                f"2. Reply to it with: `/setcmd {command_name} {command_type}`"
            )
            return False
        
        # Extract content based on type
        reply_msg = update.message.reply_to_message
        content = await self._extract_content(reply_msg, command_type)
        
        if not content:
            await update.message.reply_text(
                f"❌ Could not extract {command_type} content!\n\n"
                f"Make sure the replied message contains the right type of content."
            )
            return False
        
        # Create the command
        command_data = {
            'command_name': command_name,
            'command_type': command_type,
            'content': content,
            'creator_id': user_id,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        # Save to database
        if db.create_custom_command(chat_id, command_name, command_type, content, user_id):
            # Update cache
            self.command_cache[f"{chat_id}_{command_name}"] = command_data
            
            await update.message.reply_text(
                f"✅ **Custom Command Created!** ✅\n\n"
                f"📝 **Command:** `/{command_name}`\n"
                f"📋 **Type:** {command_type}\n"
                f"👤 **Creator:** {update.effective_user.first_name}\n\n"
                f"🎯 **Usage:** Just type /{command_name}\n"
                f"💡 **Manage:** /delcmd {command_name}"
            )
            return True
        else:
            await update.message.reply_text("❌ Failed to create command! Please try again.")
            return False
    
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Check if user is admin
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ Admin command! Tere paas power nahi hai!")
            return False
        
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/delcmd <command_name>`\n\n"
                "Example: `/delcmd rules`"
            )
            return False
        
        command_name = context.args[0].lower().strip()
        
        # Check if command exists
        existing_cmd = db.get_custom_command(chat_id, command_name)
        if not existing_cmd:
            await update.message.reply_text(
                f"❌ Command `/{command_name}` not found!\n\n"
                f"View all commands: `/cmds`"
            )
            return False
        
        # Delete from database
        if db.delete_custom_command(chat_id, command_name):
            # Remove from cache
            cache_key = f"{chat_id}_{command_name}"
            if cache_key in self.command_cache:
                del self.command_cache[cache_key]
            
            await update.message.reply_text(
                f"✅ **Command Deleted!** ✅\n\n"
                f"🗑️ **Command:** `/{command_name}`\n"
                f"👤 **Deleted by:** {update.effective_user.first_name}",
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        else:
            await update.message.reply_text("❌ Failed to delete command! Please try again.")
            return False
    
    async def list_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all custom commands"""
        chat_id = update.effective_chat.id
        commands = db.get_custom_commands(chat_id)
        
        if not commands:
            await update.message.reply_text(
                "❌ No custom commands found!\n\n"
                f"💡 **Create one:** `/setcmd <name> <type>`"
            )
            return
        
        # Group commands by type
        commands_by_type = {}
        for cmd in commands:
            cmd_type = cmd['command_type']
            if cmd_type not in commands_by_type:
                commands_by_type[cmd_type] = []
            commands_by_type[cmd_type].append(cmd)
        
        # Create message
        message_text = f"🔧 **CUSTOM COMMANDS** 🔧\n\n"
        message_text += f"📊 **Total:** {len(commands)} commands\n\n"
        
        type_emojis = {
            'text': '📝',
            'photo': '📸',
            'video': '🎥',
            'sticker': '😄',
            'audio': '🎵',
            'document': '📄',
            'voice': '🎤',
            'animation': '🎬'
        }
        
        for cmd_type, cmd_list in commands_by_type.items():
            emoji = type_emojis.get(cmd_type, '📋')
            message_text += f"{emoji} **{cmd_type.title()} Commands:**\n"
            
            for cmd in cmd_list:
                usage_count = cmd.get('usage_count', 0)
                creator = cmd.get('creator_name', 'Unknown')
                message_text += f"  • `/{cmd['command_name']}` ({usage_count} uses)\n"
            
            message_text += "\n"
        
        message_text += f"💡 **Usage:** Just type the command name!\n"
        message_text += f"🔧 **Manage:** `/setcmd` | `/delcmd`"
        
        await update.message.reply_text(message_text, parse_mode=ParseMode.MARKDOWN)
    
    async def execute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, command_name: str) -> bool:
        """Execute a custom command"""
        chat_id = update.effective_chat.id
        
        # Get command from cache or database
        cache_key = f"{chat_id}_{command_name}"
        
        if cache_key in self.command_cache:
            command_data = self.command_cache[cache_key]
        else:
            command_data = db.get_custom_command(chat_id, command_name)
            if command_data:
                self.command_cache[cache_key] = command_data
            else:
                return False
        
        # Execute based on type
        command_type = command_data['command_type']
        content = command_data['content']
        
        try:
            if command_type == 'text':
                await self._execute_text_command(update, context, content)
            elif command_type == 'photo':
                await self._execute_media_command(update, context, content, 'photo')
            elif command_type == 'video':
                await self._execute_media_command(update, context, content, 'video')
            elif command_type == 'sticker':
                await self._execute_media_command(update, context, content, 'sticker')
            elif command_type == 'audio':
                await self._execute_media_command(update, context, content, 'audio')
            elif command_type == 'document':
                await self._execute_media_command(update, context, content, 'document')
            elif command_type == 'voice':
                await self._execute_media_command(update, context, content, 'voice')
            elif command_type == 'animation':
                await self._execute_media_command(update, context, content, 'animation')
            
            # Update usage count
            db.update_command_usage(chat_id, command_name)
            command_data['usage_count'] = command_data.get('usage_count', 0) + 1
            
            return True
            
        except Exception as e:
            print(f"Error executing custom command {command_name}: {e}")
            await update.message.reply_text(
                f"❌ Error executing command `/{command_name}`!\n"
                f"Please try again or contact an admin."
            )
            return False
    
    async def _execute_text_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, content: str):
        """Execute text command"""
        # Support formatting
        if content.startswith('markdown:'):
            text_content = content[9:]  # Remove 'markdown:' prefix
            await update.message.reply_text(text_content, parse_mode=ParseMode.MARKDOWN)
        elif content.startswith('html:'):
            text_content = content[5:]  # Remove 'html:' prefix
            await update.message.reply_text(text_content, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(content)
    
    async def _execute_media_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   file_id: str, media_type: str):
        """Execute media command"""
        try:
            if media_type == 'photo':
                await context.bot.send_photo(
                    update.effective_chat.id,
                    photo=file_id
                )
            elif media_type == 'video':
                await context.bot.send_video(
                    update.effective_chat.id,
                    video=file_id
                )
            elif media_type == 'sticker':
                await context.bot.send_sticker(
                    update.effective_chat.id,
                    sticker=file_id
                )
            elif media_type == 'audio':
                await context.bot.send_audio(
                    update.effective_chat.id,
                    audio=file_id
                )
            elif media_type == 'document':
                await context.bot.send_document(
                    update.effective_chat.id,
                    document=file_id
                )
            elif media_type == 'voice':
                await context.bot.send_voice(
                    update.effective_chat.id,
                    voice=file_id
                )
            elif media_type == 'animation':
                await context.bot.send_animation(
                    update.effective_chat.id,
                    animation=file_id
                )
        except TelegramError as e:
            print(f"Telegram API error: {e}")
            await update.message.reply_text(
                "❌ Media not available! It might have been deleted."
            )
    
    async def _extract_content(self, message, command_type: str) -> Optional[str]:
        """Extract content from message based on type"""
        try:
            if command_type == 'text':
                return message.text or message.caption or ""
            elif command_type == 'photo':
                if message.photo:
                    return message.photo[-1].file_id  # Get highest resolution
            elif command_type == 'video':
                if message.video:
                    return message.video.file_id
            elif command_type == 'sticker':
                if message.sticker:
                    return message.sticker.file_id
            elif command_type == 'audio':
                if message.audio:
                    return message.audio.file_id
            elif command_type == 'document':
                if message.document:
                    return message.document.file_id
            elif command_type == 'voice':
                if message.voice:
                    return message.voice.file_id
            elif command_type == 'animation':
                if message.animation:
                    return message.animation.file_id
            
            return None
            
        except Exception as e:
            print(f"Error extracting content: {e}")
            return None
    
    def _validate_command_name(self, name: str) -> bool:
        """Validate custom command name"""
        import re
        
        # Check length
        if len(name) > 20 or len(name) < 2:
            return False
        
        # Check pattern (letters, numbers, underscores, start with letter)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            return False
        
        # Check if it conflicts with built-in commands
        built_in_commands = [
            'start', 'help', 'explain', 'ping', 'uptime', 'stats', 'about',
            'ban', 'kick', 'mute', 'unmute', 'warn', 'promote', 'demote',
            'pin', 'unpin', 'delete', 'purge', 'adminlist',
            'settings', 'setwelcome', 'setrules', 'rules', 'lock', 'unlock',
            'ai', 'chat', 'roast', 'api', 'models', 'translate', 'summarize',
            'task', 'tasks', 'profile', 'leaderboard', 'exp',
            'setcmd', 'delcmd', 'cmds',
            'calc', 'search', 'weather', 'qr', 'shorten', 'time', 'date',
            'game', 'truth', 'dare', 'roll', 'coin', 'meme', 'joke',
            'filter', 'filters', 'note', 'notes', 'savenote',
            'broadcast', 'backup', 'restart', 'shutdown'
        ]
        
        if name in built_in_commands:
            return False
        
        return True
    
    async def _is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is admin"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except:
            return False
    
    async def get_command_info(self, chat_id: int, command_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a command"""
        command_data = db.get_custom_command(chat_id, command_name)
        
        if not command_data:
            return None
        
        # Add additional info
        command_data['age_days'] = self._calculate_command_age(command_data.get('created_at'))
        command_data['popularity_score'] = self._calculate_popularity_score(command_data)
        
        return command_data
    
    def _calculate_command_age(self, created_at: str) -> int:
        """Calculate command age in days"""
        if not created_at:
            return 0
        
        try:
            created_date = datetime.fromisoformat(created_at)
            age = datetime.now() - created_date
            return age.days
        except:
            return 0
    
    def _calculate_popularity_score(self, command_data: Dict[str, Any]) -> float:
        """Calculate popularity score based on usage and age"""
        usage_count = command_data.get('usage_count', 0)
        age_days = self._calculate_command_age(command_data.get('created_at'))
        
        if age_days == 0:
            age_days = 1  # Avoid division by zero
        
        # Score = usage per day
        return usage_count / age_days
    
    async def get_popular_commands(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular custom commands"""
        commands = db.get_custom_commands(chat_id)
        
        # Sort by usage count
        sorted_commands = sorted(commands, key=lambda x: x.get('usage_count', 0), reverse=True)
        
        return sorted_commands[:limit]
    
    async def export_commands(self, chat_id: int) -> Dict[str, Any]:
        """Export all custom commands for backup"""
        commands = db.get_custom_commands(chat_id)
        
        export_data = {
            'chat_id': chat_id,
            'export_date': datetime.now().isoformat(),
            'total_commands': len(commands),
            'commands': []
        }
        
        for cmd in commands:
            export_data['commands'].append({
                'command_name': cmd['command_name'],
                'command_type': cmd['command_type'],
                'content': cmd['content'],
                'creator_id': cmd['creator_id'],
                'created_at': cmd['created_at'],
                'usage_count': cmd.get('usage_count', 0)
            })
        
        return export_data
    
    async def import_commands(self, chat_id: int, import_data: Dict[str, Any]) -> bool:
        """Import custom commands from backup"""
        try:
            commands = import_data.get('commands', [])
            imported_count = 0
            
            for cmd_data in commands:
                command_name = cmd_data['command_name']
                command_type = cmd_data['command_type']
                content = cmd_data['content']
                creator_id = cmd_data['creator_id']
                
                # Check if command already exists
                existing = db.get_custom_command(chat_id, command_name)
                if existing:
                    continue  # Skip existing commands
                
                # Import command
                if db.create_custom_command(chat_id, command_name, command_type, content, creator_id):
                    imported_count += 1
            
            return imported_count > 0
            
        except Exception as e:
            print(f"Error importing commands: {e}")
            return False
    
    def clear_cache(self, chat_id: Optional[int] = None):
        """Clear command cache"""
        if chat_id:
            # Clear cache for specific chat
            keys_to_remove = [k for k in self.command_cache.keys() if k.startswith(f"{chat_id}_")]
            for key in keys_to_remove:
                del self.command_cache[key]
        else:
            # Clear all cache
            self.command_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cached_commands': len(self.command_cache),
            'cache_size_bytes': len(json.dumps(self.command_cache)),
            'supported_types': self.supported_types
        }

# Initialize custom commands
custom_commands = CustomCommands()

if __name__ == "__main__":
    # Test custom commands
    print("🔧 Testing Custom Commands...")
    
    # Test validation
    print(f"✅ 'rules' valid: {custom_commands._validate_command_name('rules')}")
    print(f"❌ '123invalid' valid: {custom_commands._validate_command_name('123invalid')}")
    print(f"❌ 'ban' valid (built-in): {custom_commands._validate_command_name('ban')}")
    
    # Test cache stats
    stats = custom_commands.get_cache_stats()
    print(f"📊 Cache stats: {stats}")
    
    print("✅ Custom Commands test complete!")
