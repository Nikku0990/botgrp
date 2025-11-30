#!/usr/bin/env python3
"""
🎮 FUN COMMANDS
Ultimate Group King Bot - Entertainment & Games
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import random
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import Database

class FunCommands:
    """Handles all fun and entertainment commands"""
    
    def __init__(self):
        self.active_games = {}
        self.game_scores = {}
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
        
        # Truth questions database
        self.truth_questions = [
            "What's your biggest fear?",
            "What's your most embarrassing moment?",
            "What's your secret talent?",
            "What's the craziest thing you've ever done?",
            "What's your biggest regret?",
            "What's something you've never told anyone?",
            "What's your dream job?",
            "What's your guilty pleasure?",
            "What's the most adventurous thing you've done?",
            "What's your biggest achievement?",
            "What's your weirdest habit?",
            "What's your favorite childhood memory?",
            "What's your biggest insecurity?",
            "What's your proudest moment?",
            "What's your most embarrassing nickname?",
            "What's your biggest pet peeve?",
            "What's your favorite conspiracy theory?",
            "What's your weirdest dream?",
            "What's your most prized possession?",
            "What's your biggest secret crush?"
        ]
        
        # Dare challenges database
        self.dare_challenges = [
            "Sing a song out loud for 30 seconds",
            "Do 10 push-ups right now",
            "Tell your worst joke",
            "Dance like no one's watching for 15 seconds",
            "Speak in an accent for the next 5 minutes",
            "Post a silly selfie",
            "Do your best animal impression",
            "Tell a funny story from your childhood",
            "Compliment 3 people in the group",
            "Share your most embarrassing moment",
            "Do a cartwheel or forward roll",
            "Eat something weird",
            "Wear your clothes backward for 5 minutes",
            "Talk to a wall for 1 minute",
            "Do the chicken dance",
            "Make a prank call to a friend",
            "Draw a face on your chin and talk upside down",
            "Act like a robot for 2 minutes",
            "Do 20 jumping jacks",
            "Write a poem about the person above you"
        ]
        
        # Jokes database
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why can't a bicycle stand up by itself? It's two tired!",
            "What do you call cheese that isn't yours? Nacho cheese!",
            "Why did the cookie go to the doctor? Because it felt crumbly!",
            "What do you call a dinosaur that crashes his car? Tyrannosaurus Wrecks!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What do you call a fish with no eyes? A fsh!",
            "Why did the coffee file a police report? It got mugged!",
            "What do you call a bear in the rain? A drizzly bear!",
            "Why did the tomato turn red? Because it saw the salad dressing!",
            "What do you call a dog that can do magic tricks? A labracadabrador!",
            "Why don't oysters donate to charity? Because they're shellfish!",
            "What do you call a sleeping bull? A bulldozer!",
            "Why did the banana go to the doctor? It wasn't peeling well!",
            "What do you call a dinosaur with a great vocabulary? A thesaurus!"
        ]
        
        # Riddles database
        self.riddles = [
            {"question": "What has keys but no locks, space but no room?", "answer": "A piano"},
            {"question": "What can travel around the world while staying in a corner?", "answer": "A stamp"},
            {"question": "What gets wet while drying?", "answer": "A towel"},
            {"question": "What has an eye but cannot see?", "answer": "A needle"},
            {"question": "What has to be broken before you can use it?", "answer": "An egg"},
            {"question": "I'm tall when I'm young and short when I'm old. What am I?", "answer": "A candle"},
            {"question": "What month of the year has 28 days?", "answer": "All of them"},
            {"question": "What is full of holes but still holds water?", "answer": "A sponge"},
            {"question": "What question can you never answer yes to?", "answer": "Are you asleep yet?"},
            {"question": "What is always in front of you but can't be seen?", "answer": "The future"},
            {"question": "What goes up but never comes down?", "answer": "Your age"},
            {"question": "A man who was outside in the rain without an umbrella or hat didn't get a single hair on his head wet. Why?", "answer": "He was bald"},
            {"question": "What has many keys but can't open a single lock?", "answer": "A piano"},
            {"question": "What has a neck without a head and a body without legs?", "answer": "A bottle"},
            {"question": "What can you keep after giving to someone?", "answer": "Your word"},
            {"question": "I have cities, but no houses live there. I have mountains, but no trees. I have water, but no fish. What am I?", "answer": "A map"}
        ]
        
        # Games database
        self.games = [
            "🎮 **Rock Paper Scissors** - Choose rock, paper, or scissors!",
            "🎯 **Guess the Number** - I'm thinking of a number 1-100!",
            "🧩 **Riddle Time** - Can you solve this riddle?",
            "🎲 **Dice Battle** - Roll the dice and see who wins!",
            "🎪 **Circus Game** - Balance the ball!",
            "🏃 **Race Challenge** - Ready, set, go!",
            "🧠 **Memory Game** - Remember the sequence!",
            "🎯 **Target Practice** - Hit the bullseye!",
            "🎭 **Acting Challenge** - Act out the word!",
            "🎨 **Drawing Game** - Draw and guess!",
            "🎵 **Music Quiz** - Guess the song!",
            "🎬 **Movie Quiz** - Guess the movie!",
            "📚 **Word Chain** - Connect the words!",
            "🔤 **Word Scramble** - Unscramble the letters!",
            "🎪 **Tic Tac Toe** - Classic game!",
            "🎯 **Dart Throwing** - Aim carefully!",
            "🎲 **Yahtzee** - Roll for points!",
            "🎮 **Trivia** - Test your knowledge!",
            "🎪 **Magic 8-Ball** - Ask the magic ball!",
            "🎯 **Archery** - Shoot the target!"
        ]
    
    async def casino_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Alias for game_command (Casino games included)"""
        await self.game_command(update, context)

    async def dice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Alias for roll_command"""
        await self.roll_command(update, context)

    async def play_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Alias for game_command"""
        await self.game_command(update, context)

    async def game_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Play random game"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Select random game
        game = random.choice(self.games)
        
        # Create interactive buttons for some games
        if "Rock Paper Scissors" in game:
            await self._start_rock_paper_scissors(update, context)
        elif "Guess the Number" in game:
            await self._start_guess_number(update, context)
        elif "Riddle Time" in game:
            await self._start_riddle(update, context)
        elif "Dice Battle" in game:
            await self._start_dice_battle(update, context)
        elif "Tic Tac Toe" in game:
            await self._start_tic_tac_toe(update, context)
        else:
            # Generic game message
            await update.message.reply_text(
                f"🎮 **RANDOM GAME** 🎮\n\n{game}\n\n"
                f"💡 **Reply with your choice or action!**\n"
                f"🎯 **Good luck!**",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # Update game stats
        await self._update_game_stats(user_id, chat_id, 'game_played')
    
    async def truth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get truth question"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Select random truth question
        truth = random.choice(self.truth_questions)
        
        # Create interactive buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Completed", callback_data=f"truth_completed_{user_id}"),
                InlineKeyboardButton("⏭️ Skip", callback_data=f"truth_skip_{user_id}")
            ],
            [
                InlineKeyboardButton("🔄 Another Truth", callback_data=f"truth_another_{user_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🗣️ **TRUTH** 🗣️\n\n"
            f"**Question:** {truth}\n\n"
            f"💡 **Answer honestly!**\n"
            f"🎯 **Complete the challenge!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update stats
        await self._update_game_stats(user_id, chat_id, 'truth_asked')
    
    async def dare_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get dare challenge"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Select random dare
        dare = random.choice(self.dare_challenges)
        
        # Create interactive buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Completed", callback_data=f"dare_completed_{user_id}"),
                InlineKeyboardButton("⏭️ Skip", callback_data=f"dare_skip_{user_id}")
            ],
            [
                InlineKeyboardButton("🔄 Another Dare", callback_data=f"dare_another_{user_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"😈 **DARE** 😈\n\n"
            f"**Challenge:** {dare}\n\n"
            f"💡 **You must do it!**\n"
            f"🎯 **Complete the challenge!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update stats
        await self._update_game_stats(user_id, chat_id, 'dare_asked')
    
    async def roll_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Roll dice"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Parse sides
        sides = 6
        if context.args:
            try:
                sides = int(context.args[0])
                if sides < 2 or sides > 100:
                    sides = 6
            except ValueError:
                sides = 6
        
        # Roll dice with animation
        await update.message.reply_text("🎲 Rolling...")
        
        await asyncio.sleep(1)  # Simulate rolling
        
        result = random.randint(1, sides)
        
        # Create dice emoji based on result
        dice_emojis = {
            1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"
        }
        dice_emoji = dice_emojis.get(result, "🎲")
        
        await update.message.reply_text(
            f"🎲 **DICE ROLL** 🎲\n\n"
            f"{dice_emoji} **Result:** {result}\n"
            f"🔢 **Sides:** {sides}\n\n"
            f"🍀 **Good luck!**",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update stats
        await self._update_game_stats(user_id, chat_id, 'dice_rolled')
    
    async def coin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Flip coin"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Flip coin with animation
        await update.message.reply_text("🪙 Flipping coin...")
        
        await asyncio.sleep(1)
        
        result = random.choice(['Heads', 'Tails'])
        emoji = "🦅" if result == "Heads" else "👑"
        
        await update.message.reply_text(
            f"🪙 **COIN FLIP** 🪙\n\n"
            f"{emoji} **Result:** {result}\n\n"
            f"🍀 **It's fate!**",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update stats
        await self._update_game_stats(user_id, chat_id, 'coin_flipped')
    
    async def meme_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random meme"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Mock meme database (in real implementation, you'd fetch from API)
        meme_templates = [
            "When you finally understand the joke",
            "That moment when...",
            "Me pretending to understand advanced math",
            "My brain during exams",
            "When someone says 'just one more game'",
            "Trying to be productive on Monday",
            "My face when the WiFi disconnects",
            "Expectation vs Reality",
            "When you see your crush",
            "That awkward moment when...",
            "Me when someone asks for help at 3 AM",
            "When the food arrives",
            "My reaction to memes",
            "When the teacher calls on you",
            "Me trying to be normal",
            "When someone steals my food",
            "My face in group photos",
            "When someone says 'are you awake?'",
            "Me trying to explain something",
            "When the weekend finally arrives"
        ]
        
        meme = random.choice(meme_templates)
        
        # Create meme image (mock)
        await update.message.reply_text(
            f"😂 **RANDOM MEME** 😂\n\n"
            f"**Meme:** {meme}\n\n"
            f"💡 **Imagine the meme here!**\n"
            f"🎭 **Rate this meme 1-10!**",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update stats
        await self._update_game_stats(user_id, chat_id, 'meme_viewed')
    
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get random joke"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Select random joke
        joke = random.choice(self.jokes)
        
        # Create interactive buttons
        keyboard = [
            [
                InlineKeyboardButton("😂 Funny!", callback_data=f"joke_funny_{user_id}"),
                InlineKeyboardButton("😐 Meh", callback_data=f"joke_meh_{user_id}")
            ],
            [
                InlineKeyboardButton("🔄 Another Joke", callback_data=f"joke_another_{user_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"😄 **RANDOM JOKE** 😄\n\n"
            f"**Joke:** {joke}\n\n"
            f"😂 **Hope you laughed!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update stats
        await self._update_game_stats(user_id, chat_id, 'joke_told')
    
    async def riddle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get riddle"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Select random riddle
        riddle_data = random.choice(self.riddles)
        
        # Store answer for checking
        self.active_games[f"{chat_id}_{user_id}_riddle"] = riddle_data['answer']
        
        # Create interactive buttons
        keyboard = [
            [
                InlineKeyboardButton("💡 Give Hint", callback_data=f"riddle_hint_{user_id}"),
                InlineKeyboardButton("🎯 Reveal Answer", callback_data=f"riddle_answer_{user_id}")
            ],
            [
                InlineKeyboardButton("🔄 Another Riddle", callback_data=f"riddle_another_{user_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🧩 **RIDDLE TIME** 🧩\n\n"
            f"**Riddle:** {riddle_data['question']}\n\n"
            f"💡 **Think carefully!**\n"
            f"🎯 **Type your answer or use buttons!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Update stats
        await self._update_game_stats(user_id, chat_id, 'riddle_asked')
    
    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start quiz game"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Quiz categories
        categories = [
            "🌍 Geography",
            "🎬 Movies",
            "🎵 Music",
            "📚 History",
            "🔬 Science",
            "⚽ Sports",
            "🎮 Gaming",
            "🍔 Food"
        ]
        
        # Create category selection
        keyboard = []
        for i, category in enumerate(categories):
            keyboard.append([InlineKeyboardButton(category, callback_data=f"quiz_category_{i}_{user_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎯 **QUIZ GAME** 🎯\n\n"
            f"📚 **Choose a category:**\n\n"
            f"🎮 **Test your knowledge!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def ship_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ship two users"""
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/ship @user1 @user2`\n\n"
                "Example: `/ship @user1 @user2`"
            )
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ Please mention two users to ship!")
            return
        
        user1 = context.args[0]
        user2 = context.args[1]
        
        # Calculate ship percentage
        ship_percentage = random.randint(1, 100)
        
        # Generate ship name
        def generate_ship_name(name1, name2):
            # Remove @ if present
            name1 = name1.lstrip('@')
            name2 = name2.lstrip('@')
            
            # Take first half of first name and second half of second name
            half1 = name1[:len(name1)//2] if len(name1) > 1 else name1
            half2 = name2[len(name2)//2:] if len(name2) > 1 else name2
            
            return f"{half1}{half2}".title()
        
        ship_name = generate_ship_name(user1, user2)
        
        # Generate ship message based on percentage
        if ship_percentage >= 80:
            ship_message = f"💕 **PERFECT MATCH!** 💕"
            emoji = "💕"
        elif ship_percentage >= 60:
            ship_message = f"❤️ **Great Couple!** ❤️"
            emoji = "❤️"
        elif ship_percentage >= 40:
            ship_message = f"💛 **Good Friends!** 💛"
            emoji = "💛"
        elif ship_percentage >= 20:
            ship_message = f"💚 **Just Friends!** 💚"
            emoji = "💚"
        else:
            ship_message = f"💔 **Not Meant to Be!** 💔"
            emoji = "💔"
        
        await update.message.reply_text(
            f"💕 **SHIP CALCULATOR** 💕\n\n"
            f"{user1} + {user2} = {ship_name}\n\n"
            f"{emoji} **Compatibility:** {ship_percentage}%\n"
            f"{ship_message}\n\n"
            f"🎯 **What do you think about this ship?**",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def rate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rate something"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/rate <something>`\n\n"
                "Example: `/rate pizza`"
            )
            return
        
        something = " ".join(context.args)
        rating = random.randint(1, 10)
        
        # Generate stars
        stars = "⭐" * rating + "☆" * (10 - rating)
        
        await update.message.reply_text(
            f"⭐ **RATE-O-METER** ⭐\n\n"
            f"📊 **Rating:** {something}\n"
            f"⭐ **Score:** {rating}/10\n"
            f"{stars}\n\n"
            f"🎯 **What do you think?**",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _start_rock_paper_scissors(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start Rock Paper Scissors game"""
        user_id = update.effective_user.id
        
        keyboard = [
            [
                InlineKeyboardButton("🗿 Rock", callback_data=f"rps_rock_{user_id}"),
                InlineKeyboardButton("📄 Paper", callback_data=f"rps_paper_{user_id}"),
                InlineKeyboardButton("✂️ Scissors", callback_data=f"rps_scissors_{user_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Store bot's choice
        bot_choice = random.choice(['rock', 'paper', 'scissors'])
        self.active_games[f"{update.effective_chat.id}_{user_id}_rps"] = bot_choice
        
        await update.message.reply_text(
            f"🎮 **ROCK PAPER SCISSORS** 🎮\n\n"
            f"🤖 **I've made my choice!**\n"
            f"🎯 **Choose your move:**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _start_guess_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start Guess the Number game"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Generate random number
        number = random.randint(1, 100)
        self.active_games[f"{chat_id}_{user_id}_guess"] = number
        
        await update.message.reply_text(
            f"🎯 **GUESS THE NUMBER** 🎯\n\n"
            f"🤖 **I'm thinking of a number 1-100!**\n"
            f"🎯 **Type your guess:**\n\n"
            f"💡 **I'll tell you if it's higher or lower!**",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _start_riddle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start riddle game"""
        await self.riddle_command(update, context)
    
    async def _start_dice_battle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start dice battle"""
        user_id = update.effective_user.id
        
        keyboard = [
            [
                InlineKeyboardButton("🎲 Roll Dice", callback_data=f"dice_battle_{user_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎲 **DICE BATTLE** 🎲\n\n"
            f"🤖 **Let's roll the dice!**\n"
            f"🎯 **Higher roll wins!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _start_tic_tac_toe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start Tic Tac Toe game"""
        user_id = update.effective_user.id
        
        # Create empty board
        board = [['⬜️', '⬜️', '⬜️'], ['⬜️', '⬜️', '⬜️'], ['⬜️', '⬜️', '⬜️']]
        self.active_games[f"{update.effective_chat.id}_{user_id}_tictactoe"] = {
            'board': board,
            'player': '❌',
            'bot': '⭕'
        }
        
        # Create board buttons
        keyboard = []
        for row in board:
            button_row = []
            for i, cell in enumerate(row):
                button_row.append(InlineKeyboardButton(cell, callback_data=f"ttt_{user_id}_{keyboard.count(button_row)}_{i}"))
            keyboard.append(button_row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⭕ **TIC TAC TOE** ⭕\n\n"
            f"❌ **You** vs ⭕ **Bot**\n"
            f"🎯 **Your move first!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _update_game_stats(self, user_id: int, chat_id: int, action: str):
        """Update game statistics"""
        # This would update in database
        # For now, just print
        print(f"📊 Game stat: {action} by user {user_id} in chat {chat_id}")
    
    async def handle_game_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle game-related callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        callback_data = query.data
        
        # Handle different game callbacks
        if callback_data.startswith("rps_"):
            await self._handle_rps_callback(update, context, callback_data)
        elif callback_data.startswith("dice_battle_"):
            await self._handle_dice_battle_callback(update, context, callback_data)
        elif callback_data.startswith("ttt_"):
            await self._handle_tictactoe_callback(update, context, callback_data)
        elif callback_data.startswith("truth_"):
            await self._handle_truth_callback(update, context, callback_data)
        elif callback_data.startswith("dare_"):
            await self._handle_dare_callback(update, context, callback_data)
        elif callback_data.startswith("joke_"):
            await self._handle_joke_callback(update, context, callback_data)
        elif callback_data.startswith("riddle_"):
            await self._handle_riddle_callback(update, context, callback_data)
    
    async def _handle_rps_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle Rock Paper Scissors callback"""
        query = update.callback_query
        user_id = int(callback_data.split('_')[2])
        
        if update.effective_user.id != user_id:
            await query.answer("This isn't your game!", show_alert=True)
            return
        
        player_choice = callback_data.split('_')[1]
        chat_id = update.effective_chat.id
        
        # Get bot's choice
        bot_choice = self.active_games.get(f"{chat_id}_{user_id}_rps")
        if not bot_choice:
            await query.answer("Game expired!", show_alert=True)
            return
        
        # Determine winner
        choices = {'rock': '🗿', 'paper': '📄', 'scissors': '✂️'}
        
        if player_choice == bot_choice:
            result = "🤝 **It's a TIE!**"
        elif (player_choice == 'rock' and bot_choice == 'scissors') or \
             (player_choice == 'paper' and bot_choice == 'rock') or \
             (player_choice == 'scissors' and bot_choice == 'paper'):
            result = "🎉 **YOU WIN!**"
        else:
            result = "🤖 **BOT WINS!**"
        
        await query.edit_message_text(
            f"🎮 **ROCK PAPER SCISSORS** 🎮\n\n"
            f"❌ **You chose:** {choices[player_choice]} {player_choice.title()}\n"
            f"🤖 **Bot chose:** {choices[bot_choice]} {bot_choice.title()}\n\n"
            f"{result}\n\n"
            f"🎯 **Play again?** /game",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Clean up
        del self.active_games[f"{chat_id}_{user_id}_rps"]
    
    async def _handle_dice_battle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle Dice Battle callback"""
        query = update.callback_query
        user_id = int(callback_data.split('_')[2])
        
        if update.effective_user.id != user_id:
            await query.answer("This isn't your game!", show_alert=True)
            return
        
        # Roll dice
        player_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)
        
        # Create dice emojis
        dice_emojis = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        
        if player_roll > bot_roll:
            result = "🎉 **YOU WIN!**"
        elif player_roll < bot_roll:
            result = "🤖 **BOT WINS!**"
        else:
            result = "🤝 **It's a TIE!**"
        
        await query.edit_message_text(
            f"🎲 **DICE BATTLE** 🎲\n\n"
            f"❌ **You rolled:** {dice_emojis[player_roll]} {player_roll}\n"
            f"🤖 **Bot rolled:** {dice_emojis[bot_roll]} {bot_roll}\n\n"
            f"{result}\n\n"
            f"🎯 **Play again?** /game",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _handle_truth_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle truth callback"""
        query = update.callback_query
        user_id = int(callback_data.split('_')[-1])
        
        if update.effective_user.id != user_id:
            await query.answer("This isn't your truth!", show_alert=True)
            return
        
        action = callback_data.split('_')[1]
        
        if action == "completed":
            await query.edit_message_text(
                f"✅ **TRUTH COMPLETED!** ✅\n\n"
                f"🎉 **Good job!**\n"
                f"💎 **+10 EXP earned!**",
                parse_mode=ParseMode.MARKDOWN
            )
        elif action == "skip":
            await query.edit_message_text(
                f"⏭️ **TRUTH SKIPPED** ⏭️\n\n"
                f"😅 **No EXP earned!**\n"
                f"🎯 **Try another one!**",
                parse_mode=ParseMode.MARKDOWN
            )
        elif action == "another":
            await self.truth_command(update, context)
    
    async def _handle_dare_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle dare callback"""
        query = update.callback_query
        user_id = int(callback_data.split('_')[-1])
        
        if update.effective_user.id != user_id:
            await query.answer("This isn't your dare!", show_alert=True)
            return
        
        action = callback_data.split('_')[1]
        
        if action == "completed":
            await query.edit_message_text(
                f"✅ **DARE COMPLETED!** ✅\n\n"
                f"🎉 **Brave move!**\n"
                f"💎 **+15 EXP earned!**",
                parse_mode=ParseMode.MARKDOWN
            )
        elif action == "skip":
            await query.edit_message_text(
                f"⏭️ **DARE SKIPPED** ⏭️\n\n"
                f"😅 **No EXP earned!**\n"
                f"🎯 **Try another one!**",
                parse_mode=ParseMode.MARKDOWN
            )
        elif action == "another":
            await self.dare_command(update, context)
    
    async def _handle_joke_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle joke callback"""
        query = update.callback_query
        user_id = int(callback_data.split('_')[-1])
        
        if update.effective_user.id != user_id:
            await query.answer("This isn't your joke!", show_alert=True)
            return
        
        action = callback_data.split('_')[1]
        
        if action == "funny":
            await query.edit_message_text(
                f"😂 **Thanks for the feedback!** 😂\n\n"
                f"🎉 **Glad you liked it!**\n"
                f"💎 **+5 EXP earned!**",
                parse_mode=ParseMode.MARKDOWN
            )
        elif action == "meh":
            await query.edit_message_text(
                f"😐 **Thanks for the feedback!** 😐\n\n"
                f"🎯 **I'll try better next time!**\n"
                f"🎲 **Try another joke!**",
                parse_mode=ParseMode.MARKDOWN
            )
        elif action == "another":
            await self.joke_command(update, context)
    
    async def _handle_riddle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle riddle callback"""
        query = update.callback_query
        user_id = int(callback_data.split('_')[-1])
        
        if update.effective_user.id != user_id:
            await query.answer("This isn't your riddle!", show_alert=True)
            return
        
        action = callback_data.split('_')[1]
        chat_id = update.effective_chat.id
        
        if action == "hint":
            await query.answer("💡 Think about everyday objects!", show_alert=True)
        elif action == "answer":
            answer = self.active_games.get(f"{chat_id}_{user_id}_riddle")
            if answer:
                await query.edit_message_text(
                    f"🧩 **RIDDLE ANSWER** 🧩\n\n"
                    f"💡 **Answer:** {answer}\n\n"
                    f"🎯 **Did you get it right?**",
                    parse_mode=ParseMode.MARKDOWN
                )
                del self.active_games[f"{chat_id}_{user_id}_riddle"]
        elif action == "another":
            await self.riddle_command(update, context)

# Initialize fun commands
fun_commands = FunCommands()

if __name__ == "__main__":
    # Test fun commands
    print("🎮 Testing Fun Commands...")
    
    # Test data
    print(f"📊 Truth questions: {len(fun_commands.truth_questions)}")
    print(f"📊 Dare challenges: {len(fun_commands.dare_challenges)}")
    print(f"📊 Jokes: {len(fun_commands.jokes)}")
    print(f"📊 Riddles: {len(fun_commands.riddles)}")
    print(f"📊 Games: {len(fun_commands.games)}")
    
    print("✅ Fun Commands test complete!")
