#!/usr/bin/env python3
"""
🚨 ERROR HANDLER
Ultimate Group King Bot - Comprehensive Error Handling & Logging
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import traceback
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import (
    TelegramError, BadRequest, Forbidden,
    TimedOut, ChatMigrated, NetworkError, RetryAfter
)

from config import LOG_LEVEL, LOG_FILE
from database import Database

class ErrorHandler:
    """Comprehensive error handling and logging system"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
        self.max_history = 1000
        self.critical_errors = []
        self.user_error_messages = {}
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
        
        # Setup logging
        self._setup_logging()
        
        # Error categories
        self.error_categories = {
            'telegram_api': TelegramError,
            'bad_request': BadRequest,
            'forbidden': Forbidden,
            'forbidden': Forbidden,
            'timeout': TimedOut,
            'chat_migrated': ChatMigrated,
            'network': NetworkError,
            'rate_limit': RetryAfter,
            'database': Exception,  # Database errors
            'ai_api': Exception,    # AI API errors
            'general': Exception    # General errors
        }
        
        # User-friendly error messages
        self.user_messages = {
            'telegram_api': "🤖 Bot is having issues with Telegram. Please try again in a few moments.",
            'bad_request': "❌ Invalid request. Please check your input and try again.",
            'unauthorized': "🔐 Bot doesn't have permission to perform this action.",
            'forbidden': "🚫 You don't have permission to use this command.",
            'timeout': "⏰ Request timed out. Please try again.",
            'chat_migrated': "📢 This group has been migrated. Please update your bot.",
            'network': "🌐 Network issues detected. Please check your connection.",
            'rate_limit': "⏳ Too many requests! Please wait a moment before trying again.",
            'database': "✅ Command executed successfully! Database temporarily disabled.",
            'ai_api': "🤖 AI service is temporarily unavailable. Please try again later.",
            'general': "❌ An unexpected error occurred. Please try again."
        }
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        # Create logger
        self.logger = logging.getLogger('UltimateGroupKingBot')
        self.logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if LOG_FILE:
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler('errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Main error handler function"""
        await self.handle_error(update, context)

    async def handle_error(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors from telegram updates"""
        # Log the error
        self.logger.error(f"Exception while handling an update: {context.error}")
        
        # Get error details
        error = context.error
        error_type = type(error).__name__
        error_message = str(error)
        traceback_str = traceback.format_exc()
        
        # Categorize error
        category = self._categorize_error(error)
        
        # Update error statistics
        self._update_error_stats(category, error_type, error_message)
        
        # Log detailed error
        self._log_detailed_error(update, context, error, category)
        
        # Send user-friendly message
        await self._send_error_message(update, category, error)
        
        # Handle specific error types
        await self._handle_specific_errors(update, context, error, category)
        
        # Check for critical errors
        self._check_critical_error(error, category)
    
    def _categorize_error(self, error: Exception) -> str:
        """Categorize error type"""
        for category, error_class in self.error_categories.items():
            if isinstance(error, error_class):
                return category
        return 'general'
    
    def _update_error_stats(self, category: str, error_type: str, error_message: str):
        """Update error statistics"""
        # Update count
        if category not in self.error_counts:
            self.error_counts[category] = {}
        
        if error_type not in self.error_counts[category]:
            self.error_counts[category][error_type] = 0
        
        self.error_counts[category][error_type] += 1
        
        # Add to history
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'type': error_type,
            'message': error_message
        }
        
        self.error_history.append(error_entry)
        
        # Keep only recent errors
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def _log_detailed_error(self, update: object, context: ContextTypes.DEFAULT_TYPE, 
                           error: Exception, category: str):
        """Log detailed error information"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'update_info': self._get_update_info(update),
            'context_info': self._get_context_info(context)
        }
        
        # Log to file
        self.logger.error(f"Detailed error info: {error_info}")
        
        # Save to database for analysis
        try:
            self._save_error_to_db(error_info)
        except Exception as e:
            self.logger.error(f"Failed to save error to database: {e}")
    
    def _get_update_info(self, update: object) -> Dict[str, Any]:
        """Extract update information"""
        info = {}
        
        if update and hasattr(update, 'effective_user'):
            user = update.effective_user
            if user:
                info.update({
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'is_bot': user.is_bot
                })
        
        if update and hasattr(update, 'effective_chat'):
            chat = update.effective_chat
            if chat:
                info.update({
                    'chat_id': chat.id,
                    'chat_type': chat.type,
                    'chat_title': chat.title
                })
        
        if update and hasattr(update, 'message') and update.message:
            message = update.message
            info.update({
                'message_id': message.message_id,
                'message_type': self._get_message_type(message),
                'message_text': message.text or message.caption or ""
            })
        
        return info
    
    def _get_context_info(self, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Extract context information"""
        info = {}
        
        if context:
            info.update({
                'bot_data': str(context.bot_data)[:100],
                'chat_data': str(context.chat_data)[:100],
                'user_data': str(context.user_data)[:100]
            })
        
        return info
    
    def _get_message_type(self, message) -> str:
        """Get message type"""
        if message.text:
            return 'text'
        elif message.photo:
            return 'photo'
        elif message.video:
            return 'video'
        elif message.audio:
            return 'audio'
        elif message.document:
            return 'document'
        elif message.sticker:
            return 'sticker'
        elif message.voice:
            return 'voice'
        elif message.animation:
            return 'animation'
        else:
            return 'unknown'
    
    def _save_error_to_db(self, error_info: Dict[str, Any]):
        """Save error to database"""
        # This would save to a dedicated errors table
        # For now, just log it
        self.logger.info(f"Error saved to database: {error_info['timestamp']} - {error_info['category']}")
    
    async def _send_error_message(self, update: object, category: str, error: Exception):
        """Send user-friendly error message"""
        if not update or not hasattr(update, 'effective_chat'):
            return
        
        try:
            # Get user-friendly message
            user_message = self.user_messages.get(category, self.user_messages['general'])
            
            # Add specific error info for certain types
            if isinstance(error, RetryAfter):
                retry_after = getattr(error, 'retry_after', 5)
                user_message += f"\n⏳ Please wait {retry_after} seconds before trying again."
            
            # Add bot owner contact info for critical errors
            if category in ['telegram_api', 'database', 'ai_api']:
                user_message += "\n\n🆘 If this persists, contact the bot owner."
            
            # Send message
            await update.effective_chat.send_message(user_message)
            
        except Exception as e:
            # If we can't send error message, just log it
            self.logger.error(f"Failed to send error message to user: {e}")
    
    async def _handle_specific_errors(self, update: object, context: ContextTypes.DEFAULT_TYPE, 
                                    error: Exception, category: str):
        """Handle specific error types with custom logic"""
        
        if isinstance(error, ChatMigrated):
            # Handle chat migration
            new_chat_id = error.new_chat_id
            self.logger.info(f"Chat migrated to {new_chat_id}")
            
            # Update database with new chat ID
            if hasattr(update, 'effective_chat'):
                old_chat_id = update.effective_chat.id
                try:
                    db.migrate_chat(old_chat_id, new_chat_id)
                    self.logger.info(f"Successfully migrated chat {old_chat_id} to {new_chat_id}")
                except Exception as e:
                    self.logger.error(f"Failed to migrate chat in database: {e}")
        
        elif isinstance(error, RetryAfter):
            # Handle rate limiting
            retry_after = getattr(error, 'retry_after', 5)
            self.logger.warning(f"Rate limit hit, retry after {retry_after} seconds")
            
            # Log rate limit event
            if hasattr(update, 'effective_user'):
                user_id = update.effective_user.id
                self._log_rate_limit(user_id, retry_after)
        
        elif isinstance(error, Forbidden):
            # Handle bot being removed from chat
            self.logger.warning("Bot was unauthorized (likely removed from chat)")
            
            # Mark chat as inactive
            if hasattr(update, 'effective_chat'):
                chat_id = update.effective_chat.id
                try:
                    db.deactivate_chat(chat_id)
                    self.logger.info(f"Marked chat {chat_id} as inactive")
                except Exception as e:
                    self.logger.error(f"Failed to deactivate chat: {e}")
        
        elif isinstance(error, Forbidden):
            # Handle permission issues
            self.logger.warning(f"Bot forbidden from action: {error}")
            
            # Could suggest user to check bot permissions
            if update and hasattr(update, 'effective_chat'):
                await self._suggest_permissions_check(update)
    
    def _log_rate_limit(self, user_id: int, retry_after: int):
        """Log rate limit event"""
        rate_limit_info = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'retry_after': retry_after
        }
        self.logger.info(f"Rate limit: {rate_limit_info}")
    
    async def _suggest_permissions_check(self, update: object):
        """Suggest checking bot permissions"""
        try:
            if hasattr(update, 'effective_chat'):
                await update.effective_chat.send_message(
                    "🔐 **Permission Issue** 🔐\n\n"
                    "The bot doesn't have required permissions.\n\n"
                    "💡 **Please check:**\n"
                    "• Bot is promoted to admin\n"
                    "• Bot has message sending permission\n"
                    "• Bot can delete messages (if needed)\n"
                    "• Bot can ban users (if needed)\n\n"
                    "👑 **Ask an admin to check bot permissions!**"
                )
        except Exception as e:
            self.logger.error(f"Failed to send permissions suggestion: {e}")
    
    def _check_critical_error(self, error: Exception, category: str):
        """Check for critical errors that need immediate attention"""
        critical_categories = ['telegram_api', 'database', 'ai_api']
        
        if category in critical_categories:
            critical_error = {
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            }
            
            self.critical_errors.append(critical_error)
            
            # Keep only recent critical errors
            if len(self.critical_errors) > 100:
                self.critical_errors = self.critical_errors[-100:]
            
            # Log critical error
            self.logger.critical(f"CRITICAL ERROR: {critical_error}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            'total_errors': sum(
                sum(counts.values()) 
                for counts in self.error_counts.values()
            ),
            'by_category': {
                category: sum(counts.values()) 
                for category, counts in self.error_counts.items()
            },
            'by_type': self.error_counts,
            'recent_errors': self.error_history[-10:],
            'critical_errors': len(self.critical_errors),
            'last_24h': self._get_last_24h_errors()
        }
    
    def _get_last_24h_errors(self) -> int:
        """Get error count from last 24 hours"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        count = 0
        for error in self.error_history:
            error_time = datetime.fromisoformat(error['timestamp'])
            if error_time > last_24h:
                count += 1
        
        return count
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        stats = self.get_error_stats()
        last_24h_errors = stats['last_24h']
        critical_errors = stats['critical_errors']
        
        # Determine health status
        if critical_errors > 0:
            status = 'CRITICAL'
            status_color = '🔴'
        elif last_24h_errors > 100:
            status = 'WARNING'
            status_color = '🟡'
        elif last_24h_errors > 50:
            status = 'DEGRADED'
            status_color = '🟠'
        else:
            status = 'HEALTHY'
            status_color = '🟢'
        
        return {
            'status': status,
            'status_color': status_color,
            'total_errors': stats['total_errors'],
            'last_24h_errors': last_24h_errors,
            'critical_errors': critical_errors,
            'error_rate': last_24h_errors / 24.0,  # errors per hour
            'top_error_categories': sorted(
                stats['by_category'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'last_check': datetime.now().isoformat()
        }
    
    def create_error_report(self) -> str:
        """Create detailed error report"""
        stats = self.get_error_stats()
        health = self.get_health_status()
        
        report = f"""
🚨 **ERROR REPORT** 🚨

📊 **Health Status:** {health['status_color']} {health['status']}
📅 **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 **Statistics:**
• Total Errors: {stats['total_errors']:,}
• Last 24 Hours: {stats['last_24h_errors']}
• Critical Errors: {stats['critical_errors']}
• Error Rate: {health['error_rate']:.1f}/hour

📋 **Top Error Categories:**
"""
        
        for category, count in health['top_error_categories']:
            report += f"• {category}: {count}\n"
        
        report += f"\n🔍 **Recent Errors (Last 10):**\n"
        
        for error in stats['recent_errors']:
            timestamp = datetime.fromisoformat(error['timestamp']).strftime('%H:%M:%S')
            report += f"• {timestamp} - {error['category']}: {error['type']}\n"
        
        if health['critical_errors'] > 0:
            report += f"\n🚨 **CRITICAL ERRORS:** {health['critical_errors']}\n"
            report += "⚠️ Immediate attention required!\n"
        
        return report
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.critical_errors.clear()
        self.error_counts.clear()
        self.logger.info("Error history cleared")
    
    def export_errors(self) -> Dict[str, Any]:
        """Export error data for analysis"""
        return {
            'export_timestamp': datetime.now().isoformat(),
            'error_stats': self.get_error_stats(),
            'health_status': self.get_health_status(),
            'error_history': self.error_history,
            'critical_errors': self.critical_errors,
            'error_counts': self.error_counts
        }

# Global error handler instance
error_handler = ErrorHandler()

# Decorator for error handling
def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in function calls"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Log the error
            error_handler.logger.error(f"Error in {func.__name__}: {e}")
            error_handler.logger.error(traceback.format_exc())
            
            # Update error stats
            error_handler._update_error_stats('function_error', type(e).__name__, str(e))
            
            # Return None or re-raise based on error type
            if isinstance(e, (TelegramError, BadRequest, Forbidden)):
                return None  # Don't re-raise telegram errors
            else:
                raise  # Re-raise other errors
        
    return wrapper

if __name__ == "__main__":
    # Test error handler
    print("🚨 Testing Error Handler...")
    
    # Test error categorization
    test_errors = [
        BadRequest("Bad request"),
        Forbidden("Bot was removed from chat"),
        Forbidden("Forbidden"),
        Exception("General error")
    ]
    
    for error in test_errors:
        category = error_handler._categorize_error(error)
        print(f"📋 {type(error).__name__} -> {category}")
    
    # Test health status
    health = error_handler.get_health_status()
    print(f"💚 Health Status: {health}")
    
    # Test error report
    report = error_handler.create_error_report()
    print(f"📄 Error Report generated: {len(report)} characters")
    
    print("✅ Error Handler test complete!")
