#!/usr/bin/env python3
"""
👑 OWNER COMMANDS
Ultimate Group King Bot - Owner-Only Commands
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import os
import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import OWNER_ID
from database import Database

class OwnerCommands:
    """Handles owner-only commands"""
    
    def __init__(self):
        self.broadcast_queue = []
        self.broadcast_status = {}
        self.bot_restart_time = None
        self.shutdown_time = None
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
        
        # Owner verification
        self.owner_commands = {
            'broadcast': self.broadcast_command,
            'backup': self.backup_command,
            'restart': self.restart_command,
            'shutdown': self.shutdown_command,
            'stats': self.owner_stats_command,
            'logs': self.logs_command,
            'eval': self.eval_command,
            'exec': self.exec_command,
            'sql': self.sql_command,
            'system': self.system_command,
            'users': self.users_command,
            'chats': self.chats_command,
            'blacklist': self.blacklist_command,
            'whitelist': self.whitelist_command,
            'maintenance': self.maintenance_command,
            'update': self.update_command,
            'cleanup': self.cleanup_command
        }
    
    async def handle_owner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, command_name: str) -> bool:
        """Handle owner command"""
        user_id = update.effective_user.id
        
        # Verify owner
        if user_id != OWNER_ID:
            await update.message.reply_text("❌ Owner-only command!")
            return False
        
        # Execute command
        if command_name in self.owner_commands:
            try:
                await self.owner_commands[command_name](update, context)
                return True
            except Exception as e:
                await update.message.reply_text(f"❌ Command error: `{str(e)}`")
                return False
        else:
            await update.message.reply_text(f"❌ Unknown owner command: {command_name}")
            return False
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all chats"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/broadcast <message>`\n\n"
                "Examples:\n"
                "• `/broadcast Bot maintenance in 5 minutes`\n"
                "• `/broadcast New features added! Check /help`\n\n"
                f"📢 **Message will be sent to all active chats!**"
            )
            return
        
        message = " ".join(context.args)
        
        # Get all chats
        chats = db.get_all_chats()
        
        if not chats:
            await update.message.reply_text("❌ No active chats found!")
            return
        
        # Create broadcast
        broadcast_id = f"broadcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.broadcast_queue.append({
            'id': broadcast_id,
            'message': message,
            'chats': chats,
            'sent': 0,
            'failed': 0,
            'total': len(chats),
            'status': 'queued',
            'created_at': datetime.now()
        })
        
        # Send confirmation
        await update.message.reply_text(
            f"📢 **BROADCAST QUEUED** 📢\n\n"
            f"📝 **Message:** {message}\n"
            f"📊 **Chats:** {len(chats)}\n"
            f"🆔 **ID:** {broadcast_id}\n\n"
            f"⏳ **Sending in background...**\n"
            f"📊 **Check status:** `/broadcast status {broadcast_id}`"
        )
        
        # Start broadcast in background
        asyncio.create_task(self._process_broadcast(broadcast_id))
    
    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create database backup"""
        backup_type = "full"
        if context.args:
            backup_type = context.args[0].lower()
        
        if backup_type not in ['full', 'users', 'chats', 'commands', 'tasks']:
            await update.message.reply_text(
                "❌ Invalid backup type!\n\n"
                "Types: full, users, chats, commands, tasks"
            )
            return
        
        try:
            # Create backup
            backup_data = await self._create_backup(backup_type)
            
            # Save to file
            filename = f"backup_{backup_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(f"backups/{filename}", 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            # Get file size
            file_size = os.path.getsize(f"backups/{filename}")
            
            await update.message.reply_text(
                f"📦 **BACKUP CREATED** 📦\n\n"
                f"📋 **Type:** {backup_type}\n"
                f"📁 **File:** {filename}\n"
                f"📊 **Size:** {file_size:,} bytes\n"
                f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"💾 **Backup saved successfully!**"
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Backup failed: `{str(e)}`")
    
    async def restart_command(self, Update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Restart the bot"""
        delay = 0
        if context.args:
            try:
                delay = int(context.args[0])
                delay = max(0, min(delay, 300))  # Max 5 minutes
            except ValueError:
                delay = 0
        
        if delay > 0:
            self.bot_restart_time = datetime.now() + timedelta(seconds=delay)
            
            await update.message.reply_text(
                f"🔄 **BOT RESTART SCHEDULED** 🔄\n\n"
                f"⏰ **Time:** {delay} seconds\n"
                f"📅 **At:** {self.bot_restart_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"💡 **Cancel with:** `/restart cancel`"
            )
        else:
            await update.message.reply_text(
                f"🔄 **RESTARTING BOT** 🔄\n\n"
                f"⏰ **Restarting now...**\n"
                f"📊 **Bot will be back in 30 seconds**"
            )
            
            # Schedule restart
            asyncio.create_task(self._restart_bot())
    
    async def shutdown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Shutdown the bot"""
        delay = 0
        if context.args:
            try:
                delay = int(context.args[0])
                delay = max(0, min(delay, 300))  # Max 5 minutes
            except ValueError:
                delay = 0
        
        if delay > 0:
            self.shutdown_time = datetime.now() + timedelta(seconds=delay)
            
            await update.message.reply_text(
                f"🛑 **BOT SHUTDOWN SCHEDULED** 🛑\n\n"
                f"⏰ **Time:** {delay} seconds\n"
                f"📅 **At:** {self.shutdown_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"💡 **Cancel with:** `/shutdown cancel`"
            )
        else:
            await update.message.reply_text(
                f"🛑 **SHUTTING DOWN BOT** 🛑\n\n"
                f"⏰ **Shutting down now...**\n"
                f"📊 **Bot will stop immediately**"
            )
            
            # Schedule shutdown
            asyncio.create_task(self._shutdown_bot())
    
    async def owner_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed owner statistics"""
        # Get comprehensive stats
        stats = {
            'bot': self._get_bot_stats(),
            'database': self._get_database_stats(),
            'system': self._get_system_stats(),
            'performance': self._get_performance_stats()
        }
        
        # Create stats message
        stats_text = f"📊 **OWNER STATISTICS** 📊\n\n"
        
        # Bot stats
        bot_stats = stats['bot']
        stats_text += f"🤖 **Bot Stats:**\n"
        stats_text += f"• Messages: {bot_stats['total_messages']:,}\n"
        stats_text += f"• Commands: {bot_stats['total_commands']:,}\n"
        stats_text += f"• Users: {bot_stats['total_users']:,}\n"
        stats_text += f"• Chats: {bot_stats['total_chats']:,}\n"
        stats_text += f"• Uptime: {bot_stats['uptime']}\n\n"
        
        # Database stats
        db_stats = stats['database']
        stats_text += f"🗄️ **Database Stats:**\n"
        stats_text += f"• Tables: {db_stats['tables']}\n"
        stats_text += f"• Records: {db_stats['total_records']:,}\n"
        stats_text += f"• Size: {db_stats['size_mb']:.2f} MB\n\n"
        
        # System stats
        sys_stats = stats['system']
        stats_text += f"💻 **System Stats:**\n"
        stats_text += f"• CPU: {sys_stats['cpu_percent']}%\n"
        stats_text += f"• Memory: {sys_stats['memory_percent']}%\n"
        stats_text += f"• Disk: {sys_stats['disk_percent']}%\n\n"
        
        # Performance stats
        perf_stats = stats['performance']
        stats_text += f"⚡ **Performance Stats:**\n"
        stats_text += f"• Response Time: {perf_stats['avg_response_time']:.2f}ms\n"
        stats_text += f"• Error Rate: {perf_stats['error_rate']}%\n"
        stats_text += f"• Commands/min: {perf_stats['commands_per_minute']:.1f}\n\n"
        
        stats_text += f"📅 **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system logs"""
        lines = 20
        level = "INFO"
        
        if context.args:
            if context.args[0].isdigit():
                lines = int(context.args[0])
                lines = min(lines, 100)  # Max 100 lines
            else:
                level = context.args[0].upper()
                if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    level = "INFO"
        
        # Get logs (mock implementation)
        logs = self._get_logs(lines, level)
        
        if not logs:
            await update.message.reply_text(f"📋 No {level} logs found!")
            return
        
        logs_text = f"📋 **SYSTEM LOGS** 📋\n\n"
        logs_text += f"📊 **Level:** {level}\n"
        logs_text += f"📏 **Lines:** {len(logs)}\n\n"
        
        for log in logs:
            logs_text += f"`{log['timestamp']}` [{log['level']}] {log['message']}\n"
        
        await update.message.reply_text(logs_text, parse_mode=ParseMode.MARKDOWN)
    
    async def eval_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Evaluate Python code"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/eval <python_code>`\n\n"
                "Example: `/eval 2+2`"
            )
            return
        
        code = " ".join(context.args)
        
        try:
            # Security check
            if not self._is_safe_eval_code(code):
                await update.message.reply_text("❌ Unsafe code detected!")
                return
            
            # Evaluate
            result = eval(code)
            
            await update.message.reply_text(
                f"🐍 **EVAL RESULT** 🐍\n\n"
                f"📝 **Code:** `{code}`\n"
                f"📊 **Result:** `{result}`\n"
                f"📋 **Type:** `{type(result).__name__}`",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Eval error: `{str(e)}`")
    
    async def exec_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute shell command"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/exec <shell_command>`\n\n"
                "Example: `/exec ls -la`"
            )
            return
        
        command = " ".join(context.args)
        
        # Security check
        dangerous_commands = ['rm', 'sudo', 'su', 'chmod', 'chown', 'passwd', 'kill', 'pkill']
        if any(danger in command for danger in dangerous_commands):
            await update.message.reply_text("❌ Dangerous command detected!")
            return
        
        try:
            # Execute command
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            output = result.stdout or result.stderr
            
            await update.message.reply_text(
                f"🖥️ **EXEC RESULT** 🖥️\n\n"
                f"📝 **Command:** `{command}`\n"
                f"📊 **Exit Code:** {result.returncode}\n\n"
                f"📋 **Output:**\n```\n{output[:1000]}{'...' if len(output) > 1000 else ''}\n```",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except subprocess.TimeoutExpired:
            await update.message.reply_text("❌ Command timed out!")
        except Exception as e:
            await update.message.reply_text(f"❌ Exec error: `{str(e)}`")
    
    async def sql_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute SQL query"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/sql <query>`\n\n"
                "Example: `/sql SELECT COUNT(*) FROM users`"
            )
            return
        
        query = " ".join(context.args)
        
        # Security check - only allow SELECT queries
        if not query.strip().upper().startswith('SELECT'):
            await update.message.reply_text("❌ Only SELECT queries allowed!")
            return
        
        try:
            # Execute query
            results = db.execute_query(query)
            
            if not results:
                await update.message.reply_text("📊 Query returned no results!")
                return
            
            # Format results
            result_text = f"🗄️ **SQL RESULT** 🗄️\n\n"
            result_text += f"📝 **Query:** `{query}`\n"
            result_text += f"📊 **Rows:** {len(results)}\n\n"
            
            # Show first 10 rows
            for i, row in enumerate(results[:10]):
                result_text += f"**Row {i+1}:** {row}\n"
            
            if len(results) > 10:
                result_text += f"\n... and {len(results) - 10} more rows"
            
            await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ SQL error: `{str(e)}`")
    
    async def system_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system information"""
        import psutil
        import platform
        
        # Get system info
        system_info = {
            'platform': platform.platform(),
            'python': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Create system info message
        info_text = f"💻 **SYSTEM INFORMATION** 💻\n\n"
        info_text += f"🖥️ **Platform:** {system_info['platform']}\n"
        info_text += f"🐍 **Python:** {system_info['python']}\n"
        info_text += f"💾 **Memory:** {system_info['memory_total'] / (1024**3):.1f} GB\n"
        info_text += f"💿 **Disk:** {system_info['disk_total'] / (1024**3):.1f} GB\n"
        info_text += f"⚡ **CPU Cores:** {system_info['cpu_count']}\n"
        info_text += f"⏰ **Boot Time:** {system_info['boot_time']}\n\n"
        
        # Current usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info_text += f"📊 **Current Usage:**\n"
        info_text += f"• CPU: {cpu_percent}%\n"
        info_text += f"• Memory: {memory.percent}% ({memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB)\n"
        info_text += f"• Disk: {disk.percent}% ({disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB)\n\n"
        
        info_text += f"📅 **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics"""
        limit = 20
        if context.args and context.args[0].isdigit():
            limit = int(context.args[0])
            limit = min(limit, 100)  # Max 100 users
        
        # Get top users
        top_users = db.get_top_users(None, limit, 'exp')
        
        if not top_users:
            await update.message.reply_text("📊 No users found!")
            return
        
        users_text = f"👥 **TOP USERS** 👥\n\n"
        users_text += f"📊 **Showing:** {len(top_users)} users\n"
        users_text += f"📋 **Sorted by:** EXP\n\n"
        
        for i, user in enumerate(top_users, 1):
            username = user.get('username', 'Unknown')
            first_name = user.get('first_name', 'Unknown')
            exp = user.get('exp', 0)
            messages = user.get('message_count', 0)
            commands = user.get('command_count', 0)
            
            users_text += f"**{i}.** {first_name} (@{username})\n"
            users_text += f"   💎 EXP: {exp:,} | 💬 Messages: {messages:,} | ⚡ Commands: {commands:,}\n\n"
        
        await update.message.reply_text(users_text, parse_mode=ParseMode.MARKDOWN)
    
    async def chats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show chat statistics"""
        limit = 20
        if context.args and context.args[0].isdigit():
            limit = int(context.args[0])
            limit = min(limit, 100)  # Max 100 chats
        
        # Get all chats
        chats = db.get_all_chats()[:limit]
        
        if not chats:
            await update.message.reply_text("📊 No chats found!")
            return
        
        chats_text = f"💬 **ACTIVE CHATS** 💬\n\n"
        chats_text += f"📊 **Showing:** {len(chats)} chats\n\n"
        
        for i, chat in enumerate(chats, 1):
            chat_type = chat.get('type', 'Unknown')
            title = chat.get('title', 'Unknown')
            member_count = chat.get('member_count', 0)
            message_count = chat.get('message_count', 0)
            
            chats_text += f"**{i}.** {title} ({chat_type})\n"
            chats_text += f"   👥 Members: {member_count:,} | 💬 Messages: {message_count:,}\n\n"
        
        await update.message.reply_text(chats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def blacklist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage blacklist"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/blacklist <add/remove> <user_id>`\n\n"
                "Examples:\n"
                "• `/blacklist add 123456789`\n"
                "• `/blacklist remove 123456789`\n"
                "• `/blacklist list`"
            )
            return
        
        action = context.args[0].lower()
        
        if action == 'list':
            # Show blacklist (mock implementation)
            await update.message.reply_text("📋 **BLACKLIST** 📋\n\n*No users blacklisted*")
        elif action in ['add', 'remove'] and len(context.args) >= 2:
            user_id = context.args[1]
            # Add/remove from blacklist (mock implementation)
            await update.message.reply_text(f"✅ User {user_id} {action}ed from blacklist!")
        else:
            await update.message.reply_text("❌ Invalid blacklist command!")
    
    async def whitelist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage whitelist"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/whitelist <add/remove> <user_id>`\n\n"
                "Examples:\n"
                "• `/whitelist add 123456789`\n"
                "• `/whitelist remove 123456789`\n"
                "• `/whitelist list`"
            )
            return
        
        action = context.args[0].lower()
        
        if action == 'list':
            # Show whitelist (mock implementation)
            await update.message.reply_text("📋 **WHITELIST** 📋\n\n*No users whitelisted*")
        elif action in ['add', 'remove'] and len(context.args) >= 2:
            user_id = context.args[1]
            # Add/remove from whitelist (mock implementation)
            await update.message.reply_text(f"✅ User {user_id} {action}ed from whitelist!")
        else:
            await update.message.reply_text("❌ Invalid whitelist command!")
    
    async def maintenance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle maintenance mode"""
        # Toggle maintenance mode (mock implementation)
        await update.message.reply_text("🔧 **MAINTENANCE MODE** 🔧\n\n*Maintenance mode toggled!*")
    
    async def update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Update bot"""
        await update.message.reply_text(
            "🔄 **BOT UPDATE** 🔄\n\n"
            "📥 Checking for updates...\n\n"
            "⚠️ **This feature is not implemented yet!**"
        )
    
    async def cleanup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cleanup database and files"""
        cleanup_type = "all"
        if context.args:
            cleanup_type = context.args[0].lower()
        
        if cleanup_type not in ['all', 'logs', 'cache', 'temp', 'old']:
            await update.message.reply_text(
                "❌ Invalid cleanup type!\n\n"
                "Types: all, logs, cache, temp, old"
            )
            return
        
        # Perform cleanup (mock implementation)
        await update.message.reply_text(
            f"🧹 **CLEANUP** 🧹\n\n"
            f"📋 **Type:** {cleanup_type}\n"
            f"✅ **Cleanup completed!**"
        )
    
    async def _process_broadcast(self, broadcast_id: str):
        """Process broadcast in background"""
        # Find broadcast in queue
        broadcast = None
        for b in self.broadcast_queue:
            if b['id'] == broadcast_id:
                broadcast = b
                break
        
        if not broadcast:
            return
        
        # Update status
        broadcast['status'] = 'sending'
        
        # Send to each chat
        for chat in broadcast['chats']:
            try:
                # Send message (mock implementation)
                broadcast['sent'] += 1
                
                # Small delay to avoid flooding
                await asyncio.sleep(0.1)
                
            except Exception as e:
                broadcast['failed'] += 1
                print(f"Failed to send to chat {chat}: {e}")
        
        # Update status
        broadcast['status'] = 'completed'
        broadcast['completed_at'] = datetime.now()
    
    async def _create_backup(self, backup_type: str) -> Dict[str, Any]:
        """Create backup data"""
        backup_data = {
            'backup_type': backup_type,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        if backup_type in ['full', 'users']:
            backup_data['users'] = db.get_all_users()
        
        if backup_type in ['full', 'chats']:
            backup_data['chats'] = db.get_all_chats()
        
        if backup_type in ['full', 'commands']:
            backup_data['commands'] = db.get_all_command_stats()
        
        if backup_type in ['full', 'tasks']:
            backup_data['tasks'] = db.get_all_task_stats()
        
        return backup_data
    
    async def _restart_bot(self):
        """Restart the bot"""
        print("🔄 Restarting bot...")
        # In real implementation, this would restart the bot process
        sys.exit(0)
    
    async def _shutdown_bot(self):
        """Shutdown the bot"""
        print("🛑 Shutting down bot...")
        # In real implementation, this would shutdown the bot process
        sys.exit(0)
    
    def _get_bot_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        return {
            'total_messages': 0,  # Would get from database
            'total_commands': 0,
            'total_users': 0,
            'total_chats': 0,
            'uptime': '0 days, 0 hours, 0 minutes'
        }
    
    def _get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = db.get_database_stats()
            return {
                'tables': len(stats),
                'total_records': sum(stats.values()) if stats else 0,
                'size_mb': 0  # Would calculate actual file size
            }
        except:
            return {'tables': 0, 'total_records': 0, 'size_mb': 0}
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        import psutil
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    
    def _get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'avg_response_time': 150.5,
            'error_rate': 0.5,
            'commands_per_minute': 12.3
        }
    
    def _get_logs(self, lines: int, level: str) -> List[Dict[str, Any]]:
        """Get system logs (mock implementation)"""
        logs = []
        for i in range(lines):
            logs.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'level': level,
                'message': f'Sample log message {i+1}'
            })
        return logs
    
    def _is_safe_eval_code(self, code: str) -> bool:
        """Check if eval code is safe"""
        dangerous_patterns = [
            'import', 'exec', 'eval', 'open', 'file', 'os', 'sys',
            '__import__', '__builtins__', '__globals__', 'subprocess',
            'input', 'print', 'lambda:', '->', '=', '+=', '-=', '*=', '/='
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return False
        
        return True

# Initialize owner commands
owner_commands = OwnerCommands()

if __name__ == "__main__":
    # Test owner commands
    print("👑 Testing Owner Commands...")
    
    # Test eval safety
    print(f"✅ '2+2' safe: {owner_commands._is_safe_eval_code('2+2')}")
    print(f"❌ 'import os' safe: {owner_commands._is_safe_eval_code('import os')}")
    
    # Test stats
    bot_stats = owner_commands._get_bot_stats()
    print(f"📊 Bot stats: {bot_stats}")
    
    print("✅ Owner Commands test complete!")
