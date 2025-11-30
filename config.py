#!/usr/bin/env python3
"""
🔧 CONFIGURATION & CONSTANTS
Ultimate Group King Bot - Configuration File
Author: Nikhil Mehra (NikkuAi09)
"""

import os
from typing import List, Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# === BOT CONFIGURATION ===
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
OWNER_ID = int(os.getenv('OWNER_ID', '123456789'))  # Replace with your ID

# === API KEYS ===
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')  # Users will set their own
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '5417fa8bfe2191cccd6a57a0aac827fe')

# === DATABASE ===
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ultimate_bot.db')

# === AI MODELS (OpenRouter) ===
AVAILABLE_MODELS = [
    "deepseek/deepseek-r1-0528-qwen3-8b:free",  # Primary
    "mistralai/mistral-small-3.2-24b-instruct:free",  # Fallback 1
    "meta-llama/llama-3.3-70b-instruct:free",  # Fallback 2
]

# === EXP & ADMIN SYSTEM ===
EXP_THRESHOLDS = {
    500: 2,      # 2 minutes admin
    1000: 5,     # 5 minutes admin
    5000: 30,    # 30 minutes admin
    10000: 120,  # 2 hours admin
    20000: 300,  # 5 hours admin
    50000: 600,  # 10 hours admin
}

EXP_PER_MESSAGE = 10
EXP_PER_COMMAND = 5

# === TASK LIST (50+ TASKS) ===
TASK_LIST = {
    # Chat Tasks
    "chat_master": {
        "name": "💬 Chat Master",
        "description": "Send 100 messages",
        "target": 100,
        "exp_reward": 1000,
        "type": "messages"
    },
    "flood_king": {
        "name": "🌊 Flood King",
        "description": "Send 50 messages in 1 minute",
        "target": 50,
        "exp_reward": 500,
        "type": "flood",
        "time_limit": 60
    },
    "silent_learner": {
        "name": "🤫 Silent Learner",
        "description": "Stay silent for 1 hour then send 1 message",
        "target": 3600,  # 1 hour in seconds
        "exp_reward": 300,
        "type": "silence"
    },
    "night_owl": {
        "name": "🦉 Night Owl",
        "description": "Chat between 2 AM - 4 AM",
        "target": 5,
        "exp_reward": 250,
        "type": "time_based",
        "start_hour": 2,
        "end_hour": 4
    },
    "early_bird": {
        "name": "🐦 Early Bird",
        "description": "Chat between 5 AM - 7 AM",
        "target": 5,
        "exp_reward": 200,
        "type": "time_based",
        "start_hour": 5,
        "end_hour": 7
    },
    
    # Media Tasks
    "emoji_king": {
        "name": "😎 Emoji King",
        "description": "Use 50 emojis in messages",
        "target": 50,
        "exp_reward": 150,
        "type": "emoji"
    },
    "sticker_lover": {
        "name": "😻 Sticker Lover",
        "description": "Send 30 stickers",
        "target": 30,
        "exp_reward": 200,
        "type": "sticker"
    },
    "media_master": {
        "name": "📸 Media Master",
        "description": "Send 50 photos/videos",
        "target": 50,
        "exp_reward": 500,
        "type": "media"
    },
    "gif_master": {
        "name": "🎬 GIF Master",
        "description": "Send 25 GIFs",
        "target": 25,
        "exp_reward": 250,
        "type": "gif"
    },
    "voice_chat": {
        "name": "🎤 Voice Chat",
        "description": "Send 20 voice messages",
        "target": 20,
        "exp_reward": 350,
        "type": "voice"
    },
    
    # Interactive Tasks
    "poll_creator": {
        "name": "📊 Poll Creator",
        "description": "Create 10 polls",
        "target": 10,
        "exp_reward": 400,
        "type": "poll"
    },
    "hashtag_king": {
        "name": "#️⃣ Hashtag King",
        "description": "Use 25 hashtags",
        "target": 25,
        "exp_reward": 100,
        "type": "hashtag"
    },
    "mention_master": {
        "name": "👤 Mention Master",
        "description": "Mention 40 users",
        "target": 40,
        "exp_reward": 200,
        "type": "mention"
    },
    "link_sharer": {
        "name": "🔗 Link Sharer",
        "description": "Share 15 links",
        "target": 15,
        "exp_reward": 150,
        "type": "link"
    },
    "file_sender": {
        "name": "📁 File Sender",
        "description": "Send 20 documents",
        "target": 20,
        "exp_reward": 300,
        "type": "file"
    },
    
    # Game Tasks
    "quiz_master": {
        "name": "🧠 Quiz Master",
        "description": "Answer 20 quizzes correctly",
        "target": 20,
        "exp_reward": 600,
        "type": "quiz"
    },
    "truth_teller": {
        "name": "🗣️ Truth Teller",
        "description": "Play truth 15 times",
        "target": 15,
        "exp_reward": 200,
        "type": "truth"
    },
    "dare_devil": {
        "name": "😈 Dare Devil",
        "description": "Complete 10 dares",
        "target": 10,
        "exp_reward": 300,
        "type": "dare"
    },
    "game_champion": {
        "name": "🏆 Game Champion",
        "description": "Win 5 games",
        "target": 5,
        "exp_reward": 800,
        "type": "game"
    },
    "riddle_solver": {
        "name": "🧩 Riddle Solver",
        "description": "Solve 30 riddles",
        "target": 30,
        "exp_reward": 450,
        "type": "riddle"
    },
    
    # AI Tasks
    "roast_master": {
        "name": "🔥 Roast Master",
        "description": "Get roasted by bot 20 times",
        "target": 20,
        "exp_reward": 250,
        "type": "roast"
    },
    "ai_chat": {
        "name": "🤖 AI Chat",
        "description": "Chat with AI 100 times",
        "target": 100,
        "exp_reward": 500,
        "type": "ai_chat"
    },
    "command_king": {
        "name": "⚡ Command King",
        "description": "Use 50 different commands",
        "target": 50,
        "exp_reward": 400,
        "type": "command"
    },
    
    # Time-based Tasks
    "night_gamer": {
        "name": "🌙 Night Gamer",
        "description": "Play games between 12 AM - 3 AM",
        "target": 10,
        "exp_reward": 350,
        "type": "time_game",
        "start_hour": 0,
        "end_hour": 3
    },
    "day_achiever": {
        "name": "☀️ Day Achiever",
        "description": "Complete 5 tasks in one day",
        "target": 5,
        "exp_reward": 1000,
        "type": "daily"
    },
    "week_warrior": {
        "name": "⚔️ Week Warrior",
        "description": "Complete 20 tasks in a week",
        "target": 20,
        "exp_reward": 2500,
        "type": "weekly"
    },
    "month_master": {
        "name": "📅 Month Master",
        "description": "Complete 80 tasks in a month",
        "target": 80,
        "exp_reward": 10000,
        "type": "monthly"
    },
    
    # Help Tasks
    "helping_hand": {
        "name": "🤝 Helping Hand",
        "description": "Help others 30 times",
        "target": 30,
        "exp_reward": 400,
        "type": "help"
    },
    "problem_solver": {
        "name": "🔧 Problem Solver",
        "description": "Solve 25 member issues",
        "target": 25,
        "exp_reward": 600,
        "type": "solve"
    },
    "report_helper": {
        "name": "🚨 Report Helper",
        "description": "Report 15 spam messages",
        "target": 15,
        "exp_reward": 200,
        "type": "report"
    },
    
    # Group Tasks
    "welcome_wagon": {
        "name": "👋 Welcome Wagon",
        "description": "Welcome 20 new members",
        "target": 20,
        "exp_reward": 150,
        "type": "welcome"
    },
    "goodbye_sayer": {
        "name": "👋 Goodbye Sayer",
        "description": "Say goodbye to 10 members",
        "target": 10,
        "exp_reward": 50,
        "type": "goodbye"
    },
    "group_keeper": {
        "name": "🛡️ Group Keeper",
        "description": "Stay in group for 30 days",
        "target": 30,
        "exp_reward": 1500,
        "type": "stay"
    },
    "event_creator": {
        "name": "📅 Event Creator",
        "description": "Create 10 group events",
        "target": 10,
        "exp_reward": 700,
        "type": "event"
    },
    "announcement_maker": {
        "name": "📢 Announcement Maker",
        "description": "Make 15 announcements",
        "target": 15,
        "exp_reward": 300,
        "type": "announce"
    },
    
    # Rule Tasks
    "rule_knower": {
        "name": "📜 Rule Knower",
        "description": "Quote rules 20 times",
        "target": 20,
        "exp_reward": 100,
        "type": "rule"
    },
    "settings_master": {
        "name": "⚙️ Settings Master",
        "description": "Change settings 10 times",
        "target": 10,
        "exp_reward": 200,
        "type": "settings"
    },
    
    # Advanced Tasks
    "backup_creator": {
        "name": "💾 Backup Creator",
        "description": "Create 5 group backups",
        "target": 5,
        "exp_reward": 800,
        "type": "backup"
    },
    "custom_cmd_creator": {
        "name": "🔧 Custom Cmd Creator",
        "description": "Create 10 custom commands",
        "target": 10,
        "exp_reward": 500,
        "type": "custom_cmd"
    },
    "link_generator": {
        "name": "🔗 Link Generator",
        "description": "Generate 25 invite links",
        "target": 25,
        "exp_reward": 150,
        "type": "invite"
    },
    
    # Mod Tasks
    "ban_helper": {
        "name": "🚫 Ban Helper",
        "description": "Help ban 20 spammers",
        "target": 20,
        "exp_reward": 400,
        "type": "ban_help"
    },
    "mute_helper": {
        "name": "🔇 Mute Helper",
        "description": "Help mute 30 troublemakers",
        "target": 30,
        "exp_reward": 300,
        "type": "mute_help"
    },
    "warn_giver": {
        "name": "⚠️ Warn Giver",
        "description": "Give 40 warnings",
        "target": 40,
        "exp_reward": 200,
        "type": "warn"
    },
    "note_maker": {
        "name": "📝 Note Maker",
        "description": "Create 30 notes",
        "target": 30,
        "exp_reward": 350,
        "type": "note"
    },
    "filter_setter": {
        "name": "🔍 Filter Setter",
        "description": "Set 20 filters",
        "target": 20,
        "exp_reward": 250,
        "type": "filter"
    },
    "blacklist_manager": {
        "name": "🚫 Blacklist Manager",
        "description": "Manage blacklist 15 times",
        "target": 15,
        "exp_reward": 200,
        "type": "blacklist"
    },
    
    # EXP Milestones
    "exp_moderator": {
        "name": "💎 EXP Moderator",
        "description": "Reach 5000 EXP",
        "target": 5000,
        "exp_reward": 2000,
        "type": "exp_milestone"
    },
    "legend_member": {
        "name": "👑 Legend Member",
        "description": "Reach 10000 EXP",
        "target": 10000,
        "exp_reward": 5000,
        "type": "exp_milestone"
    },
    "ultimate_king": {
        "name": "🔥 Ultimate King",
        "description": "Reach 50000 EXP",
        "target": 50000,
        "exp_reward": 10000,
        "type": "exp_milestone"
    }
}

# === DEFAULT GROUP SETTINGS ===
DEFAULT_GROUP_CONFIG = {
    "welcome_enabled": True,
    "welcome_text": "👋 Welcome {mention} to {chat}! 🎉\nEarn EXP and become admin! 🚀",
    "goodbye_enabled": False,
    "goodbye_text": "👋 {mention} left {chat}",
    "rules_text": "📜 **GROUP RULES** 📜\n\n1. No spam\n2. No abuse\n3. Be respectful\n4. Enjoy! 😊",
    "max_warnings": 3,
    "auto_action": "mute",
    "flood_limit": 5,
    "captcha_enabled": False,
    "approval_mode": False,
    "task_system_active": False,
    "smart_detection": True,
    "antispam_level": "medium",
    
    # Locks
    "locks": {
        "photo": False,
        "video": False,
        "sticker": False,
        "gif": False,
        "voice": False,
        "link": False,
        "forward": False,
        "command": False,
        "english": False,
        "arabic": False,
        "rtl": False,
        "button": False,
        "game": False,
        "inline": False,
        "url": False
    },
    
    # Filters
    "filters": {},
    "blacklist": [],
    
    # Custom Commands
    "custom_commands": {},
    
    # Log Channel
    "log_channel": None,
    
    # Admin Task System
    "admin_task_system": False,
    "exp_to_admin": 500,
    "admin_duration": 2,  # minutes
}

# === SAVAGE PERSONA (For AI) ===
SAVAGE_GAALIYAN = [
    "behen ke lode", "madarchod", "bhenchod", "gandu", "chutiya", 
    "bhosdike", "randi ke bacche", "harami", "saale kutte", "lawde", 
    "randwe", "bhosda", "lauda", "maa-chod"
]

# === AI SYSTEM PROMPT ===
AI_SYSTEM_PROMPT = (
    "Tu Nikhil Papa hai, ek savage Hinglish roaster. "
    "RULES: 1. SHORT responses de - maximum 2-3 lines. "
    "2. Smartly 2-3 gaaliyan use kar from these options: " + ", ".join(SAVAGE_GAALIYAN) + ". "
    "3. Maa-chod style quick replies de with creative roasting. "
    "4. User ko roast kar but keep it crisp and impactful. "
    "5. Boring long messages mat bhej. "
    "EXAMPLE: 'Arre behen ke lode, tera dimag kahan gaya? Madarchod agli baar soch kar bol!' "
    "KEEP IT SHORT AND SAVAGE!"
)

# === WEB DASHBOARD CONFIG ===
WEB_DASHBOARD = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False,
    "secret_key": os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
}

# === FALLBACK MESSAGES ===
FALLBACK_MESSAGES = {
    "API_KEY_MISSING": "Arre {gaali}, pehle apna **OpenRouter API Key** set kar! `/api` use kar, {gaali}. Bina key ke main hawa mein baat karun kya?",
    "API_FAILED": "Madarchod, API request fail ho gaya! Server mein kuch lafda hai, {gaali}. Thodi der baad try karna.",
    "RATE_LIMIT": "Bhenchod, server pe load hai! Rate limit lag gayi, {gaali}. Thoda ruk ja.",
    "TIMEOUT": "Lawde, request time out ho gaya! Server so raha hai kya, {gaali}? Dobara try kar.",
    "EMPTY_RESPONSE": "Chutiye, AI ne kuch nahi bola! Khali haath wapas aa gaya, {gaali}.",
    "GENERAL_ERROR": "Arre {gaali}, kuch to gadbad hai! System mein kuch lafda ho gaya hai, {gaali}."
}

# === LOCKABLE ITEMS ===
LOCKABLE_ITEMS = [
    "all", "messages", "media", "stickers", "gifs", "photos", "videos",
    "audio", "voice", "documents", "links", "urls", "forwards",
    "commands", "bots", "inline", "games", "polls", "invites",
    "contacts", "location", "venue", "english", "arabic", "rtl",
    "buttons", "games", "inline"
]

# === COMMAND CATEGORIES ===
COMMAND_CATEGORIES = {
    "👑 Admin": ["ban", "kick", "mute", "unmute", "promote", "demote", "warn", "pin", "unpin"],
    "🧠 AI": ["ai", "chat", "roast", "ask", "api", "models", "translate"],
    "🛠️ Utility": ["weather", "calc", "search", "qr", "shorten", "time", "date"],
    "🎮 Fun": ["game", "truth", "dare", "roll", "coin", "meme", "gif"],
    "⚙️ Settings": ["settings", "config", "rules", "welcome", "lock", "unlock"],
    "📊 Stats": ["stats", "info", "profile", "leaderboard", "top"],
    "🔧 Tools": ["filter", "blacklist", "note", "backup", "export"]
}

# === SMART DETECTION PATTERNS ===
SMART_PATTERNS = {
    "ban": r"(?:ban|kick|nikal|bahar kar) (.+)",
    "mute": r"(?:mute|chup|silent) (.+)",
    "roast": r"(?:roast|ukhaad|jala) (.+)",
    "weather": r"(?:weather|mausam|climate) (.+)",
    "help": r"(?:help|madad|kaise kare)",
    "rules": r"(?:rules|niyam|guidelines)",
    "info": r"(?:info|jankari|details)",
    "ping": r"(?:ping|pong|speed|latency)",
    "calc": r"(?:calc|calculate|math) (.+)",
    "search": r"(?:search|google|find) (.+)"
}

# === TIME FORMATS ===
TIME_FORMATS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800
}

# === COLORS FOR WEB DASHBOARD ===
WEB_COLORS = {
    "primary": "#007bff",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#17a2b8",
    "dark": "#343a40",
    "light": "#f8f9fa"
}

# === EMOJIS ===
EMOJIS = {
    "admin": "👑",
    "mod": "🛡️",
    "user": "👤",
    "bot": "🤖",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "welcome": "👋",
    "goodbye": "👋",
    "ban": "🚫",
    "kick": "🦵",
    "mute": "🔇",
    "warn": "⚠️",
    "pin": "📌",
    "lock": "🔒",
    "unlock": "🔓",
    "exp": "💎",
    "task": "📋",
    "ai": "🤖",
    "game": "🎮",
    "music": "🎵",
    "photo": "📸",
    "video": "🎬",
    "file": "📁",
    "link": "🔗",
    "star": "⭐",
    "fire": "🔥",
    "heart": "❤️",
    "brain": "🧠",
    "rocket": "🚀",
    "trophy": "🏆",
    "crown": "👑",
    "lightning": "⚡",
    "sparkles": "✨"
}

# === WEB DASHBOARD ===
WEB_DASHBOARD_ENABLED = os.getenv('WEB_DASHBOARD_ENABLED', 'True').lower() == 'true'
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', 8080))
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'ultimate-group-king-secret-key-2024')

# === LOGGING ===
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')

# === LOG LEVELS ===
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# === MAX LIMITS ===
MAX_LIMITS = {
    "message_length": 4096,
    "caption_length": 1024,
    "username_length": 32,
    "group_title_length": 255,
    "bio_length": 70,
    "commands_per_user": 100,
    "filters_per_group": 100,
    "notes_per_group": 100,
    "warnings_per_user": 10,
    "exp_per_user": 1000000
}

# === RATE LIMITING ===
RATE_LIMITS = {
    "messages_per_minute": 30,
    "commands_per_minute": 10,
    "ai_requests_per_hour": 100,
    "search_requests_per_hour": 50
}

# === WEBHOOK CONFIG ===
WEBHOOK_CONFIG = {
    "enabled": False,
    "url": None,
    "port": 8443,
    "cert": None,
    "key": None
}

# === CACHE CONFIG ===
CACHE_CONFIG = {
    "ai_responses": 3600,  # 1 hour
    "user_info": 300,      # 5 minutes
    "group_info": 600,     # 10 minutes
    "weather": 1800,       # 30 minutes
    "search": 300          # 5 minutes
}

# === BACKUP CONFIG ===
BACKUP_CONFIG = {
    "auto_backup": True,
    "backup_interval": 86400,  # 24 hours
    "max_backups": 7,
    "backup_path": "backups/"
}

# === SECURITY CONFIG ===
SECURITY_CONFIG = {
    "max_login_attempts": 5,
    "lockout_time": 900,  # 15 minutes
    "session_timeout": 3600,  # 1 hour
    "require_https": False,
    "allowed_origins": ["*"]
}

# === DEVELOPMENT CONFIG ===
DEV_CONFIG = {
    "debug": False,
    "testing": False,
    "mock_api": False,
    "log_all": True,
    "save_state": True
}

# === FEATURE FLAGS ===
FEATURE_FLAGS = {
    "web_dashboard": True,
    "ai_chat": True,
    "task_system": True,
    "custom_commands": True,
    "smart_detection": True,
    "captcha": True,
    "federation": False,
    "voice_commands": False,
    "multi_language": False,
    "advanced_analytics": True
}

# === MIGRATION CONFIG ===
MIGRATION_CONFIG = {
    "version": "1.0.0",
    "auto_migrate": True,
    "backup_before_migrate": True
}

print("✅ Configuration loaded successfully!")
print(f"📊 Total tasks defined: {len(TASK_LIST)}")
print(f"🤖 AI models available: {len(AVAILABLE_MODELS)}")
print(f"🔧 Lockable items: {len(LOCKABLE_ITEMS)}")
print(f"📝 Command categories: {len(COMMAND_CATEGORIES)}")
