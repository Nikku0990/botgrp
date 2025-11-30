#!/usr/bin/env python3
"""
🚀 ULTIMATE BOT LAUNCHER
Ultimate Group King Bot - All Features Integrated
Author: Nikhil Mehra (NikkuAi09)
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import all modules
from database import Database
from working_commands import WorkingCommands
from magical_features import MagicalFeatures

# Advanced Commands
from ai_handler import AIHandler
from admin_commands import AdminCommands
from owner_commands import OwnerCommands
from custom_commands import CustomCommands

# Games & Fun
from fun_commands import FunCommands
from payment_system import PaymentSystem
from escrow_system import EscrowSystem
from store_system import StoreSystem
from task_system import TaskSystem
from social_system import SocialSystem
from identity_system import IdentitySystem
from politics_system import PoliticsSystem

# Management
from group_management import GroupManagement

# Utilities
from error_handler import ErrorHandler
from smart_detection import SmartDetection
from utility_commands import UtilityCommands
from economy_commands import EconomyCommands
from real_games import real_games

# Big Data Analytics
from admin_data import super_admin_system
from data_filters import advanced_filter_system
from data_commands import big_data_commands

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# Initialize Database and Commands
db = Database()
commands = WorkingCommands()
magical = MagicalFeatures()

# Connect to database AFTER all modules are imported
try:
    db.connect()
    print("✅ Database connected successfully!")
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")
    print("🚀 Bot will continue without database...")

# Initialize all modules (without database connection for now)
ai_handler = AIHandler()
admin = AdminCommands()
owner = OwnerCommands()
custom = CustomCommands()
fun = FunCommands()
payment = PaymentSystem()
escrow = EscrowSystem()
store = StoreSystem()
tasks = TaskSystem()
social = SocialSystem()
identity = IdentitySystem()
politics = PoliticsSystem()
group = GroupManagement()
error = ErrorHandler()
detection = SmartDetection()
utility = UtilityCommands()
economy = EconomyCommands()

# Initialize Big Data Analytics (without database for now)
big_data = big_data_commands

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Working /start command with Astra DB integration."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot.")

    try:
        # Get or create user in Astra DB
        user_data = db.get_user(user.id)
        
        if not user_data:
            # Create new user
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'join_date': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'message_count': 0,
                'games_played': 0,
                'wins': 0,
                'losses': 0,
                'points': 0,
                'level': 1,
                'exp': 0
            }
            db.update_user(user.id, user_data)
            welcome_msg = f"🎉 **Welcome to ULTIMATE KING BOT!** 🎉\n\n"
            welcome_msg += f"👋 Hello {user.first_name}!\n"
            welcome_msg += f"🆕 New account created!\n"
            welcome_msg += f"🎮 **600+ Commands Available!**\n"
            welcome_msg += f"🔥 **24/7 Online Service**\n"
            welcome_msg += f"⚡ **Lightning Fast Response**\n\n"
            welcome_msg += f"📋 **Quick Start:**\n"
            welcome_msg += f"• /help - View all commands\n"
            welcome_msg += f"• /ai - Chat with AI\n"
            welcome_msg += f"• /games - Play games\n"
            welcome_msg += f"• /magic - Cast magical spells\n"
            welcome_msg += f"• /poll - Create polls\n"
            welcome_msg += f"• /contest - Start contests\n\n"
            welcome_msg += f"🌟 **Special Features:**\n"
            welcome_msg += f"• /tagall - Tag all members\n"
            welcome_msg += f"• /call - Emergency call\n"
            welcome_msg += f"• /banrequest - Democratic ban\n"
            welcome_msg += f"• /superadmin - Admin panel\n\n"
            welcome_msg += f"👑 **Created by: @nikhilmehra099**"
        else:
            # Update last active
            user_data['last_active'] = datetime.now().isoformat()
            db.update_user(user.id, user_data)
            
            welcome_msg = f"🚀 **Welcome Back!** 🚀\n\n"
            welcome_msg += f"👋 Hello {user.first_name}!\n"
            welcome_msg += f"📊 **Your Stats:**\n"
            welcome_msg += f"• Level: {user_data.get('level', 1)}\n"
            welcome_msg += f"• Points: {user_data.get('points', 0)}\n"
            welcome_msg += f"• Games: {user_data.get('games_played', 0)}\n"
            welcome_msg += f"• Wins: {user_data.get('wins', 0)}\n\n"
            welcome_msg += f"🎮 **Ready to play?**\n"
            welcome_msg += f"• /games - Browse 162 games\n"
            welcome_msg += f"• /ai - Chat with AI\n"
            welcome_msg += f"• /help - All commands\n\n"
            welcome_msg += f"👑 **Created by: @nikhilmehra099**"

        # Create welcome keyboard
        keyboard = [
            [
                InlineKeyboardButton("🎮 Games", callback_data="menu_games"),
                InlineKeyboardButton("🤖 AI Chat", callback_data="menu_ai")
            ],
            [
                InlineKeyboardButton("🌟 Magical", callback_data="menu_magical"),
                InlineKeyboardButton("👑 Admin", callback_data="menu_admin")
            ],
            [
                InlineKeyboardButton("🏪 Store", callback_data="menu_store"),
                InlineKeyboardButton("📊 Stats", callback_data="menu_stats")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Start command error: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Error starting bot: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comprehensive help menu with all features."""
    help_text = (
        "🚀 **ULTIMATE KING BOT - HELP** 🚀\n\n"
        "🌟 **Complete Feature List!** 🌟\n\n"
        "📋 **MAIN CATEGORIES:**\n\n"
        "🎮 **Games & Entertainment:**\n"
        "• /games - Browse 20 real games\n"
        "• /play - Play random game\n"
        "• /roulette - Casino roulette\n"
        "• /slots - Slot machine\n"
        "• /coin - Flip coin\n"
        "• /dice - Roll dice\n"
        "• /joke - Random jokes\n"
        "• /truth - Truth or dare\n"
        "• /dare - Get a dare\n"
        "• /fact - Random facts\n\n"
        "🌟 **Magical Features:**\n"
        "• /tagall [msg] - Tag all members\n"
        "• /call [msg] - Emergency call\n"
        "• /magic [spell] - Cast spells\n"
        "• /thunder - Lightning strike\n"
        "• /fire - Fire storm\n"
        "• /ice - Ice freeze\n"
        "• /shadow - Shadow bind\n"
        "• /heal - Healing light\n"
        "• /teleport - Teleport\n"
        "• /poison - Poison dart\n"
        "• /earthquake - Earthquake\n"
        "• /tsunami - Tsunami waves\n"
        "• /tornado - Tornado vortex\n"
        "• /effects - Random effects\n"
        "• /announce [msg] - Announcement\n\n"
        "🤖 **AI Commands:**\n"
        "• /ai [message] - Chat with AI\n"
        "• /ask [question] - Ask AI\n"
        "• /chat - AI conversation\n"
        "• /image [prompt] - Generate images\n\n"
        "🏪 **Store & Economy:**\n"
        "• /createstore - Open your store\n"
        "• /viewstore [@user] - View stores\n"
        "• /additem [name] [price] - Add products\n"
        "• /wallet - Check balance\n"
        "• /deposit [amount] - Add funds\n"
        "• /withdraw [amount] - Withdraw\n"
        "• /transfer [amount] @user - Send money\n"
        "• /balance - Check balance\n\n"
        "🗳️ **Politics System:**\n"
        "• /election [title] - Start election\n"
        "• /nominate [manifesto] - Run for office\n"
        "• /vote [candidate_id] - Cast vote\n"
        "• /results - Election results\n"
        "• /endelection - End election\n\n"
        "👤 **Identity & Business:**\n"
        "• /setid [@handle] - Set custom ID\n"
        "• /setbio [text] - Set your bio\n"
        "• /setbusiness [name] - Set business\n"
        "• /identity - View identity card\n\n"
        "👑 **Admin Tools:**\n"
        "• /ban [@user] [reason] - Ban user\n"
        "• /kick [@user] [reason] - Kick user\n"
        "• /mute [@user] [time] - Mute user\n"
        "• /unmute [@user] - Unmute user\n"
        "• /promote [@user] - Promote admin\n"
        "• /demote [@user] - Demote admin\n"
        "• /pin - Pin message (reply)\n"
        "• /unpin - Unpin message\n"
        "• /delete - Delete message (reply)\n"
        "• /purge - Delete multiple messages\n\n"
        "� **Utilities:**\n"
        "• /calc [expression] - Calculator\n"
        "• /time - Current time\n"
        "• /ping - Bot speed\n"
        "• /stats - Your statistics\n"
        "• /about - About bot\n\n"
        "⚙️ **Custom Commands:**\n"
        "• /createcmd - Create custom command\n"
        "• /deletecmd - Delete command\n"
        "• /listcmds - List commands\n"
        "• /runcmd - Execute command\n\n"
        "📊 **Big Data Analytics:**\n"
        "• /analytics - View dashboard\n"
        "• /filter - Filter data\n"
        "• /advanced_filter - Advanced filters\n"
        "• /export - Export data\n\n"
        "👑 **Created by: @nikhilmehra099**\n"
        "🚀 **Status: ALL SYSTEMS ACTIVE!**"
    )
    
    # Create help menu keyboard
    keyboard = [
        [
            InlineKeyboardButton("🎮 Games", callback_data="help_games"),
            InlineKeyboardButton("🌟 Magical", callback_data="help_magical")
        ],
        [
            InlineKeyboardButton("👑 Admin", callback_data="help_admin"),
            InlineKeyboardButton("📊 Analytics", callback_data="help_data")
        ],
        [
            InlineKeyboardButton("🤖 AI", callback_data="help_ai"),
            InlineKeyboardButton("🏪 Store", callback_data="help_store")
        ],
        [
            InlineKeyboardButton("🗳️ Politics", callback_data="help_politics"),
            InlineKeyboardButton("👤 Identity", callback_data="help_identity")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu callbacks."""
    query = update.callback_query
    await query.answer()
    
    menu_type = query.data.replace("menu_", "")
    
    if menu_type == "games":
        await commands.games_command(update, context)
    elif menu_type == "ai":
        await ai_handler.ask_command(update, context)
    elif menu_type == "magical":
        await magical.magic_spell_command(update, context, [])
    elif menu_type == "admin":
        await big_data.analytics_command(update, context)
    elif menu_type == "store":
        await store.store_command(update, context)
    elif menu_type == "stats":
        await commands.stats_command(update, context)

async def help_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help menu callbacks."""
    query = update.callback_query
    await query.answer()
    
    help_type = query.data.replace("help_", "")
    
    help_texts = {
        "games": "🎮 **GAMES COMMANDS** 🎮\n\n• /games - Browse 20 real games\n• /play - Play random game\n• /roulette - Casino\n• /slots - Slots\n• /coin - Coin flip\n• /dice - Roll dice\n• /joke - Jokes\n• /truth - Truth or dare\n• /dare - Get a dare\n• /fact - Random facts",
        
        "magical": "🌟 **MAGICAL COMMANDS** 🌟\n\n• /tagall [msg] - Tag all\n• /call [msg] - Emergency call\n• /ban [@user] - Ban with effects\n• /kick [@user] - Kick with effects\n• /banrequest [@user] - Democratic ban\n• /magic [spell] - Cast spells\n• /thunder - Lightning\n• /fire - Fire storm\n• /ice - Ice freeze\n• /shadow - Shadow bind\n• /heal - Healing\n• /teleport - Teleport\n• /effects - Random effects",
        
        "admin": "👑 **ADMIN COMMANDS** 👑\n\n• /ban [@user] - Ban user\n• /kick [@user] - Kick user\n• /mute [@user] - Mute user\n• /unmute [@user] - Unmute user\n• /promote [@user] - Promote\n• /demote [@user] - Demote\n• /pin - Pin message\n• /unpin - Unpin\n• /delete - Delete message\n• /purge - Delete multiple",
        
        "data": "📊 **BIG DATA ANALYTICS** 📊\n\n• /analytics - Dashboard\n• /filter - Filter data\n• /advanced_filter - Advanced filters\n• /export - Export data\n• /filter_stats - Statistics",
        
        "ai": "🤖 **AI COMMANDS** 🤖\n\n• /ai [message] - Chat with AI\n• /ask [question] - Ask AI\n• /chat - AI conversation\n• /image [prompt] - Generate images",
        
        "store": "🏪 **STORE COMMANDS** 🏪\n\n• /createstore - Create store\n• /viewstore [@user] - View stores\n• /additem [name] [price] - Add item\n• /buyitem [id] - Buy item\n• /wallet - Check balance\n• /deposit [amount] - Add funds\n• /withdraw [amount] - Withdraw\n• /transfer [amount] @user - Send money",
        
        "politics": "🗳️ **POLITICS COMMANDS** 🗳️\n\n• /election [title] - Start election\n• /nominate [manifesto] - Run for office\n• /vote [candidate_id] - Cast vote\n• /results - View results\n• /endelection - End election\n\n**Democratic system for group governance!**",
        
        "identity": "👤 **IDENTITY COMMANDS** 👤\n\n• /setid [@handle] - Set custom ID\n• /setbio [text] - Set your bio\n• /setbusiness [name] - Set business name\n• /identity - View identity card\n\n**Create your unique identity!**"
    }
    
    text = help_texts.get(help_type, "❌ Category not found")
    
    # Back button
    keyboard = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query handler."""
    query = update.callback_query
    data = query.data
    
    if data.startswith("menu_"):
        await menu_callback_handler(update, context)
    elif data.startswith("help_"):
        await help_callback_handler(update, context)
    elif data.startswith("game_"):
        # Real games callbacks
        if data == "game_number_guess":
            await real_games.number_guess_start(update, context)
        elif data == "game_word_scramble":
            await real_games.word_scramble_start(update, context)
        elif data == "game_math_quiz":
            await real_games.math_quiz_start(update, context)
        elif data == "game_trivia":
            await real_games.trivia_start(update, context)
        elif data == "game_riddle":
            await real_games.riddle_start(update, context)
        elif data == "game_rps":
            await real_games.rps_start(update, context)
        elif data == "game_coin":
            await real_games.coin_start(update, context)
        elif data == "game_dice":
            await real_games.dice_start(update, context)
        elif data == "game_truth_dare":
            await real_games.truth_dare_start(update, context)
        elif data == "game_would_rather":
            await real_games.would_rather_start(update, context)
        elif data == "game_stats":
            await real_games.show_stats(update, context)
        else:
            await commands.handle_callback_query(update, context)
    elif data.startswith("magical_"):
        await magical.handle_magical_callback(update, context)
    elif data.startswith("super_"):
        await big_data.filter_command(update, context)
    elif data.startswith("data_"):
        await big_data.filter_command(update, context)
    elif data.startswith("detection_"):
        await detection.handle_detection_callback(update, context)
    else:
        await query.answer("Unknown callback")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with smart detection."""
    if not update.message or not update.message.text:
        return
    
    message_text = update.message.text.lower()
    
    # Check for active game responses first
    if await real_games.handle_game_response(update, context):
        return
    
    # Smart detection for commands without /
    if await detection.detect_command(update, context):
        return
    
    # Simple AI responses
    greetings = ["hello", "hi", "hey", "namaste"]
    if any(greet in message_text for greet in greetings):
        await update.message.reply_text(f"👋 Hello {update.effective_user.first_name}! Use /help to see all commands!")
    
    elif "help" in message_text:
        await update.message.reply_text("📝 Use /help to see all available commands!")
    
    elif "game" in message_text:
        await update.message.reply_text("🎮 Use /games to browse all available games!")
    
    elif "ai" in message_text:
        await update.message.reply_text("🤖 Use /ai to chat with AI or /ask to ask questions!")

def main():
    """Main function to run the bot."""
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create the Application
    application = Application.builder().token(bot_token).build()
    
    # 🎯 SET BOT COMMANDS MENU
    async def post_init(app: Application) -> None:
        """Set bot commands menu"""
        from telegram import BotCommand
        commands_list = [
            # Games & Fun
            BotCommand("games", "🎮 Browse all games"),
            BotCommand("play", "🎯 Play a random game"),
            BotCommand("roulette", "🎰 Casino roulette"),
            BotCommand("slots", "🎰 Slot machine"),
            BotCommand("coin", "🪙 Flip a coin"),
            BotCommand("dice", "🎲 Roll dice"),
            BotCommand("joke", "😂 Random joke"),
            BotCommand("truth", "🤔 Truth or Dare"),
            BotCommand("dare", "😈 Get a dare"),
            BotCommand("fact", "📚 Random fact"),
            
            # AI & Chat
            BotCommand("ai", "🤖 Chat with AI"),
            BotCommand("ask", "❓ Ask AI anything"),
            BotCommand("chat", "💬 AI conversation"),
            BotCommand("setapi", "🔑 Set API Key"),
            
            # Utility
            BotCommand("ping", "⚡ Check bot speed"),
            BotCommand("time", "🕐 Current time"),
            BotCommand("calc", "🔢 Calculator"),
            BotCommand("stats", "📊 Your statistics"),
            BotCommand("about", "ℹ️ About bot"),
            
            # Economy
            BotCommand("wallet", "💰 Check wallet"),
            BotCommand("balance", "💵 Check balance"),
            BotCommand("deposit", "💳 Deposit money"),
            BotCommand("withdraw", "🏦 Withdraw money"),
            BotCommand("transfer", "💸 Transfer money"),
            
            # Store & Business
            BotCommand("createstore", "🏪 Create your store"),
            BotCommand("viewstore", "🛍️ View stores"),
            BotCommand("additem", "➕ Add store item"),
            
            # Politics
            BotCommand("election", "🗳️ Start election"),
            BotCommand("nominate", "📝 Nominate yourself"),
            BotCommand("vote", "✅ Cast your vote"),
            BotCommand("results", "📊 Election results"),
            
            # Identity
            BotCommand("setid", "🆔 Set custom ID"),
            BotCommand("setbio", "📄 Set your bio"),
            BotCommand("setbusiness", "💼 Set business"),
            BotCommand("identity", "👤 View identity card"),
            
            # Magical Features
            BotCommand("tagall", "📢 Tag all members"),
            BotCommand("call", "🚨 Emergency call"),
            BotCommand("magic", "✨ Cast magic spell"),
            BotCommand("thunder", "⚡ Thunder strike"),
            BotCommand("fire", "🔥 Fire storm"),
            
            # Admin
            BotCommand("ban", "🚫 Ban user"),
            BotCommand("kick", "🦵 Kick user"),
            BotCommand("mute", "🔇 Mute user"),
            BotCommand("unmute", "🔊 Unmute user"),
            
            # Custom
            BotCommand("createcmd", "⚙️ Create custom command"),
            BotCommand("listcmds", "📋 List custom commands"),
            
            # Analytics
            BotCommand("analytics", "📊 View analytics"),
            BotCommand("filter", "🔍 Filter data"),
            
            # Help
            BotCommand("help", "❓ Show all commands"),
        ]
        await app.bot.set_my_commands(commands_list)
        logger.info("✅ Bot commands menu set successfully!")
    
    application.post_init = post_init

    
    # --- Basic Command Handlers ---
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # --- Real Games (20 Interactive Games) ---
    application.add_handler(CommandHandler("games", real_games.games_menu))
    application.add_handler(CommandHandler("play", commands.play_command))
    application.add_handler(CommandHandler("roulette", commands.roulette_command))
    application.add_handler(CommandHandler("slots", commands.slots_command))
    application.add_handler(CommandHandler("coin", commands.coin_command))
    application.add_handler(CommandHandler("dice", commands.dice_command))
    application.add_handler(CommandHandler("joke", commands.joke_command))
    application.add_handler(CommandHandler("truth", commands.truth_command))
    application.add_handler(CommandHandler("dare", commands.dare_command))
    application.add_handler(CommandHandler("fact", commands.fact_command))
    application.add_handler(CommandHandler("ai", commands.ai_command))
    application.add_handler(CommandHandler("ping", commands.ping_command))
    application.add_handler(CommandHandler("time", commands.time_command))
    application.add_handler(CommandHandler("calc", commands.calc_command))
    application.add_handler(CommandHandler("about", commands.about_command))
    application.add_handler(CommandHandler("stats", commands.stats_command))
    
    # --- AI Commands ---
    application.add_handler(CommandHandler("ask", ai_handler.ask_command))
    application.add_handler(CommandHandler("chat", ai_handler.chat_command))
    application.add_handler(CommandHandler("setapi", ai_handler.setapi_command))
    
    # --- Smart Detection Commands ---
    application.add_handler(CommandHandler("detect", detection.detect_command))
    application.add_handler(CommandHandler("scan", detection.scan_command))
    
    # --- Economy Commands ---
    application.add_handler(CommandHandler("wallet", economy.wallet_command))
    application.add_handler(CommandHandler("transfer", economy.transfer_command))
    application.add_handler(CommandHandler("balance", economy.balance_command))
    application.add_handler(CommandHandler("deposit", economy.deposit_command))
    application.add_handler(CommandHandler("withdraw", economy.withdraw_command))
    
    # --- Custom Commands ---
    # application.add_handler(CommandHandler("custom", custom.custom_command))
    # application.add_handler(CommandHandler("addcmd", custom.add_command))
    application.add_handler(CommandHandler("createcmd", custom.create_command))
    application.add_handler(CommandHandler("deletecmd", custom.delete_command))
    application.add_handler(CommandHandler("listcmds", custom.list_commands))
    application.add_handler(CommandHandler("runcmd", custom.execute_command))
    
    # 🌟 MAGICAL FEATURES - DHAMAKA COMMANDS 🌟
    application.add_handler(CommandHandler("tagall", magical.tagall_command))
    application.add_handler(CommandHandler("call", magical.call_command))
    application.add_handler(CommandHandler("banrequest", magical.ban_request_command))
    application.add_handler(CommandHandler("magic", magical.magic_spell_command))
    application.add_handler(CommandHandler("thunder", lambda u,c: magical.magic_spell_command(u,c, ["thunder"])))
    application.add_handler(CommandHandler("fire", lambda u,c: magical.magic_spell_command(u,c, ["fire"])))
    application.add_handler(CommandHandler("ice", lambda u,c: magical.magic_spell_command(u,c, ["ice"])))
    application.add_handler(CommandHandler("shadow", lambda u,c: magical.magic_spell_command(u,c, ["shadow"])))
    application.add_handler(CommandHandler("heal", lambda u,c: magical.magic_spell_command(u,c, ["heal"])))
    application.add_handler(CommandHandler("teleport", lambda u,c: magical.magic_spell_command(u,c, ["teleport"])))
    application.add_handler(CommandHandler("poison", lambda u,c: magical.magic_spell_command(u,c, ["poison"])))
    application.add_handler(CommandHandler("earthquake", lambda u,c: magical.magic_spell_command(u,c, ["earthquake"])))
    application.add_handler(CommandHandler("tsunami", lambda u,c: magical.magic_spell_command(u,c, ["tsunami"])))
    application.add_handler(CommandHandler("tornado", lambda u,c: magical.magic_spell_command(u,c, ["tornado"])))
    application.add_handler(CommandHandler("effects", magical.add_magical_effects))
    application.add_handler(CommandHandler("announce", magical.creative_announce))
    
    # 👑 ADMIN COMMANDS
    application.add_handler(CommandHandler("ban", admin.ban_command))
    application.add_handler(CommandHandler("kick", admin.kick_command))
    application.add_handler(CommandHandler("mute", admin.mute_command))
    application.add_handler(CommandHandler("unmute", admin.unmute_command))
    
    # --- Big Data Analytics Features ---
    application.add_handler(CommandHandler("analytics", big_data.analytics_command))
    application.add_handler(CommandHandler("filter", big_data.filter_command))
    application.add_handler(CommandHandler("advanced_filter", big_data.advanced_filter_command))
    application.add_handler(CommandHandler("preset_filters", big_data.preset_filters_command))
    application.add_handler(CommandHandler("big_data_monitor", big_data.big_data_monitor_command))
    application.add_handler(CommandHandler("export", big_data.export_data_command))
    application.add_handler(CommandHandler("filter_stats", big_data.filter_stats_command))
    
    # --- Error Handler ---
    application.add_error_handler(error.error_handler)
    
    # --- Callback Query Handler (including all feature callbacks) ---
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    
    # --- Message Handler ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # --- New Chat Members Handler ---
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, start_command))
    
    logger.info("🚀 BIG DATA KING BOT is up and running with advanced analytics! 📊")
    
    # Run the bot
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
