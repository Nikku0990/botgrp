#!/usr/bin/env python3
"""
🧠 SMART DETECTION
Ultimate Group King Bot - Natural Language Command Detection
Author: Nikhil Mehra (NikkuAi09)
"""

import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from telegram import Update
from telegram.ext import ContextTypes
from admin_commands import admin_commands
from utility_commands import utility_commands
from fun_commands import fun_commands as entertainment_commands
from group_management import group_management
from magical_features import magical
from working_commands import commands

class SmartDetection:
    def __init__(self):
        self.detection_patterns = {
            'admin': ['ban', 'kick', 'mute', 'promote', 'demote'],
            'utility': ['info', 'id', 'whois', 'help'],
            'entertainment': ['game', 'play', 'fun', 'joke'],
            'emergency': ['emergency', 'urgent', 'important']
        }
        
    async def detect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Smart command detection with execution"""
        if not update.message or not update.message.text:
            return

        message_text = update.message.text.lower()
        
        # 🔥 FIX: Only process if message starts with UNKNOWN / command
        if not message_text.startswith('/'):
            return  # Ignore normal messages
        
        # Check if it's a known command - if yes, ignore
        known_commands = [
            '/start', '/help', '/games', '/play', '/roulette', '/slots', '/coin', '/dice',
            '/joke', '/truth', '/dare', '/fact', '/ai', '/ping', '/time', '/calc', '/about', '/stats',
            '/ask', '/chat', '/image', '/detect', '/scan', '/wallet', '/transfer', '/balance', '/deposit', '/withdraw',
            '/createcmd', '/deletecmd', '/listcmds', '/runcmd', '/tagall', '/call', '/ban', '/kick', '/banrequest',
            '/magic', '/thunder', '/fire', '/ice', '/shadow', '/heal', '/teleport', '/poison', '/earthquake', '/tsunami', '/tornado',
            '/effects', '/announce', '/superadmin', '/broadcast', '/maintenance', '/emergency', '/userstats', '/settings',
            '/poll', '/quiz', '/contest', '/giveaway', '/voting', '/leaderboard', '/event'
        ]
        
        # Extract command name (first word after /)
        words = message_text.split()
        if words:
            cmd_name = words[0]
            if cmd_name in known_commands:
                return  # Ignore known commands
        
        # Now check for patterns in unknown commands
        detected_commands = []
        for category, keywords in self.detection_patterns.items():
            for keyword in keywords:
                if keyword in message_text:
                    detected_commands.append(f"/{keyword}")
        
        if detected_commands:
            # 🎯 EXECUTE THE DETECTED COMMANDS
            command_to_execute = detected_commands[0]  # Execute first detected command
            
            # Execute the detected command
            if command_to_execute == "/ban":
                await magical.ban_command(update, context)
            elif command_to_execute == "/kick":
                await magical.kick_command(update, context)
            elif command_to_execute == "/mute":
                await admin_commands.mute_command(update, context)
            elif command_to_execute == "/promote":
                await admin_commands.promote_command(update, context)
            elif command_to_execute == "/demote":
                await admin_commands.demote_command(update, context)
            elif command_to_execute == "/info":
                await commands.info_command(update, context)
            elif command_to_execute == "/whois":
                await commands.whois_command(update, context)
            elif command_to_execute == "/help":
                await commands.help_command(update, context)
            elif command_to_execute == "/game" or command_to_execute == "/play":
                await commands.play_command(update, context)
            elif command_to_execute == "/fun" or command_to_execute == "/joke":
                await commands.joke_command(update, context)
            elif command_to_execute == "/emergency" or command_to_execute == "/urgent":
                await update.message.reply_text("🚨 *EMERGENCY DETECTED!* 🚨\n\nAdmins have been notified!")
            else:
                await update.message.reply_text(f"🧠 *Smart Detection Active*\n\nDetected: {', '.join(detected_commands)}\n\n🎯 Executing: {command_to_execute}")
        else:
            await update.message.reply_text("🧠 No specific commands detected")
    
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Scan group for patterns"""
        await update.message.reply_text("🔍 *Group Scan Started*\n\nAnalyzing messages...")
    
    async def handle_detection_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle detection callbacks"""
        query = update.callback_query
        await query.answer("Smart detection callback handled!")
        
        # Currently no interactive callbacks for smart detection
        # This is a placeholder for future features
        return False
    
    async def _detect_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  text: str) -> bool:
        """Detect admin commands"""
        # Check if user is admin
        is_admin = await admin_commands.is_admin(update, context)
        if not is_admin:
            return False
        
        # Ban detection
        ban_patterns = [
            r'ban\s+(@\w+|\d+)',
            r'nikal\s+(@\w+|\d+)',
            r'bahar\s+kar\s+(@\w+|\d+)',
            r'kick\s+(@\w+|\d+)'
        ]
        
        for pattern in ban_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1)
                context.args = [target]
                await admin_commands.ban_command(update, context)
                return True
        
        # Mute detection
        mute_patterns = [
            r'mute\s+(@\w+|\d+)\s*(\d+[mhdw])?',
            r'chup\s+(@\w+|\d+)\s*(\d+[mhdw])?',
            r'silent\s+(@\w+|\d+)\s*(\d+[mhdw])?'
        ]
        
        for pattern in mute_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1)
                duration = match.group(2) if match.group(2) else "1h"
                context.args = [target, duration]
                await admin_commands.mute_command(update, context)
                return True
        
        # Unmute detection
        unmute_patterns = [
            r'unmute\s+(@\w+|\d+)',
            r'bol\s+(@\w+|\d+)',
            r'awaz\s+(@\w+|\d+)'
        ]
        
        for pattern in unmute_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1)
                context.args = [target]
                await admin_commands.unmute_command(update, context)
                return True
        
        # Warn detection
        warn_patterns = [
            r'warn\s+(@\w+|\d+)\s*(.+)?',
            r'warning\s+(@\w+|\d+)\s*(.+)?',
            r'dekh\s+(@\w+|\d+)\s*(.+)?'
        ]
        
        for pattern in warn_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1)
                reason = match.group(2) if match.group(2) else "No reason"
                context.args = [target, reason]
                await admin_commands.warn_command(update, context)
                return True
        
        # Promote detection
        promote_patterns = [
            r'promote\s+(@\w+|\d+)',
            r'admin\s+(@\w+|\d+)',
            r'banade\s+(@\w+|\d+)'
        ]
        
        for pattern in promote_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1)
                context.args = [target]
                await admin_commands.promote_command(update, context)
                return True
        
        # Demote detection
        demote_patterns = [
            r'demote\s+(@\w+|\d+)',
            r'admin\s+hatade\s+(@\w+|\d+)',
            r'promote\s+hatade\s+(@\w+|\d+)'
        ]
        
        for pattern in demote_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1)
                context.args = [target]
                await admin_commands.demote_command(update, context)
                return True
        
        # Pin detection (requires reply)
        pin_patterns = [
            r'pin\s+(this|is|ko)',
            r'thek\s+kar',
            r'pin\s+kar'
        ]
        
        for pattern in pin_patterns:
            if re.search(pattern, text) and update.message.reply_to_message:
                await admin_commands.pin_command(update, context)
                return True
        
        # Delete detection (requires reply)
        delete_patterns = [
            r'delete\s+(this|is|ko)',
            r'hatade\s+(this|is|ko)',
            r'ye\s+hatade'
        ]
        
        for pattern in delete_patterns:
            if re.search(pattern, text) and update.message.reply_to_message:
                await admin_commands.delete_command(update, context)
                return True
        
        return False
    
    async def _detect_utility_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    text: str, bot=None) -> bool:
        """Detect utility commands"""
        
        # Weather detection
        weather_patterns = [
            r'weather\s+(.+)',
            r'mausam\s+(.+)',
            r'climate\s+(.+)',
            r'temperature\s+(.+)'
        ]
        
        for pattern in weather_patterns:
            match = re.search(pattern, text)
            if match:
                city = match.group(1)
                context.args = [city]
                await utility_commands.weather_command(update, context)
                return True
        
        # Calc detection
        calc_patterns = [
            r'calc\s+(.+)',
            r'calculate\s+(.+)',
            r'math\s+(.+)',
            r'solve\s+(.+)'
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, text)
            if match:
                expression = match.group(1)
                context.args = expression.split()
                await utility_commands.calc_command(update, context)
                return True
        
        # Search detection
        search_patterns = [
            r'search\s+(.+)',
            r'google\s+(.+)',
            r'find\s+(.+)',
            r'dhoond\s+(.+)'
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, text)
            if match:
                query = match.group(1)
                context.args = query.split()
                await utility_commands.search_command(update, context)
                return True
        
        # Time detection
        time_patterns = [
            r'time\s+(now|abhi|hi)',
            r'what\s+time',
            r'kitna\s+time',
            r'current\s+time'
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text):
                await utility_commands.time_command(update, context)
                return True
        
        # Date detection
        date_patterns = [
            r'date\s+(today|aj)',
            r'what\s+date',
            r'kitni\s+date',
            r'current\s+date'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text):
                await utility_commands.date_command(update, context)
                return True
        
        return False
    
    async def _detect_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                 text: str, bot=None) -> bool:
        """Detect information commands"""
        
        # Help detection
        help_patterns = [
            r'help',
            r'madad',
            r'kaise\s+kare',
            r'support',
            r'commands'
        ]
        
        for pattern in help_patterns:
            if re.search(pattern, text):
                if bot and hasattr(bot, 'help_command'):
                    await bot.help_command(update, context)
                    return True
        
        # Rules detection
        rules_patterns = [
            r'rules',
            r'niyam',
            r'guidelines',
            r'kya\s+karna\s+hai',
            r'kya\s+nahi\s+karna\s+hai'
        ]
        
        for pattern in rules_patterns:
            if re.search(pattern, text):
                await group_management.rules_command(update, context)
                return True
        
        # Stats detection
        stats_patterns = [
            r'stats',
            r'statistics',
            r'info',
            r'jankari',
            r'details'
        ]
        
        for pattern in stats_patterns:
            if re.search(pattern, text):
                if bot and hasattr(bot, 'stats_command'):
                    await bot.stats_command(update, context)
                    return True
        
        # Ping detection
        ping_patterns = [
            r'ping',
            r'pong',
            r'speed',
            r'latency',
            r'kitni\s+tez'
        ]
        
        for pattern in ping_patterns:
            if re.search(pattern, text):
                if bot and hasattr(bot, 'ping_command'):
                    await bot.ping_command(update, context)
                    return True
        
        return False
    
    async def _detect_fun_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                 text: str) -> bool:
        """Detect fun commands"""
        
        # Game detection
        game_patterns = [
            r'game',
            r'khel',
            r'play',
            r'maza'
        ]
        
        for pattern in game_patterns:
            if re.search(pattern, text):
                await entertainment_commands.casino_command(update, context)
                return True
        
        # Truth detection
        truth_patterns = [
            r'truth',
            r'sach',
            r'truth\s+bata'
        ]
        
        for pattern in truth_patterns:
            if re.search(pattern, text):
                await entertainment_commands.truth_command(update, context)
                return True
        
        # Dare detection
        dare_patterns = [
            r'dare',
            r'himat',
            r'dare\s+kar'
        ]
        
        for pattern in dare_patterns:
            if re.search(pattern, text):
                await entertainment_commands.dare_command(update, context)
                return True
        
        # Roll detection
        roll_patterns = [
            r'roll',
            r'dice',
            r'baazi',
            r'roll\s+karo'
        ]
        
        for pattern in roll_patterns:
            if re.search(pattern, text):
                await entertainment_commands.dice_command(update, context)
                return True
        
        # Coin detection
        coin_patterns = [
            r'coin',
            r'flip',
            r'paisa',
            r'sikka',
            r'head\s+tail'
        ]
        
        for pattern in coin_patterns:
            if re.search(pattern, text):
                await entertainment_commands.coin_command(update, context)
                return True
        
        # Joke detection
        joke_patterns = [
            r'joke',
            r'hasi',
            r'joke\s+bata',
            r'hansao'
        ]
        
        for pattern in joke_patterns:
            if re.search(pattern, text):
                await entertainment_commands.joke_command(update, context)
                return True
        
        return False
    
    async def _detect_pattern_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    text: str, bot=None) -> bool:
        """Detect commands using predefined patterns"""
        
        for command_name, pattern in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract arguments from match
                args = list(match.groups()) if match.groups() else []
                context.args = args
                
                # Execute the corresponding command
                if bot and hasattr(bot, f"{command_name}_command"):
                    method = getattr(bot, f"{command_name}_command")
                    await method(update, context)
                    return True
                
                # Try admin commands
                if hasattr(admin_commands, f"{command_name}_command"):
                    method = getattr(admin_commands, f"{command_name}_command")
                    await method(update, context)
                    return True
                
                # Try utility commands
                if hasattr(utility_commands, f"{command_name}_command"):
                    method = getattr(utility_commands, f"{command_name}_command")
                    await method(update, context)
                    return True
                
                # Try entertainment commands
                if hasattr(entertainment_commands, f"{command_name}_command"):
                    method = getattr(entertainment_commands, f"{command_name}_command")
                    await method(update, context)
                    return True
        
        return False
    
    def add_pattern(self, command_name: str, pattern: str):
        """Add new smart detection pattern"""
        self.patterns[command_name] = pattern
    
    def remove_pattern(self, command_name: str):
        """Remove smart detection pattern"""
        if command_name in self.patterns:
            del self.patterns[command_name]
    
    def get_patterns(self) -> Dict[str, str]:
        """Get all smart detection patterns"""
        return self.patterns.copy()
    
    def is_command_like(self, text: str) -> bool:
        """Check if text looks like a command"""
        text = text.lower().strip()
        
        # Check if it starts with command-like words
        command_starters = [
            'ban', 'kick', 'mute', 'unmute', 'warn', 'promote', 'demote',
            'weather', 'calc', 'search', 'time', 'date', 'help', 'rules',
            'game', 'truth', 'dare', 'roll', 'coin', 'joke', 'ping'
        ]
        
        for starter in command_starters:
            if text.startswith(starter):
                return True
        
        # Check patterns
        for pattern in self.patterns.values():
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_command_probability(self, text: str) -> Dict[str, float]:
        """Get probability scores for different commands"""
        text = text.lower().strip()
        scores = {}
        
        # Check admin commands
        admin_keywords = ['ban', 'kick', 'mute', 'warn', 'promote', 'delete']
        for keyword in admin_keywords:
            if keyword in text:
                scores[f"admin_{keyword}"] = 0.8
        
        # Check utility commands
        utility_keywords = ['weather', 'calc', 'search', 'time', 'date']
        for keyword in utility_keywords:
            if keyword in text:
                scores[f"utility_{keyword}"] = 0.7
        
        # Check fun commands
        fun_keywords = ['game', 'truth', 'dare', 'roll', 'coin', 'joke']
        for keyword in fun_keywords:
            if keyword in text:
                scores[f"fun_{keyword}"] = 0.6
        
        return scores

# Initialize smart detection
smart_detection = SmartDetection()

if __name__ == "__main__":
    # Test smart detection
    print("🧠 Testing Smart Detection...")
    
    test_messages = [
        "ban @user123",
        "weather delhi",
        "calc 5+3",
        "time now",
        "help me",
        "game khelein",
        "truth batao",
        "roll dice"
    ]
    
    for message in test_messages:
        is_command = smart_detection.is_command_like(message)
        probability = smart_detection.get_command_probability(message)
        print(f"Message: '{message}' -> Command: {is_command} -> {probability}")
    
    print("✅ Smart Detection test complete!")
