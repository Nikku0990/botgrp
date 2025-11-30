#!/usr/bin/env python3
"""
💕 SOCIAL SYSTEM
Ultimate Group King Bot - Relationships & Social Interactions
Author: Nikhil Mehra (NikkuAi09)
"""

import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database import Database

class SocialSystem:
    """Handles social interactions like marriage, friendship, and fun actions"""
    
    def __init__(self):
        self.pending_proposals = {}  # Store pending marriage proposals
        self.marriages = {}  # Store active marriages (In real app, use DB)
        self.friends = {}    # Store friendships
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
        
    async def marry_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Propose to someone"""
        user = update.effective_user
        chat = update.effective_chat
        
        if not context.args:
            await update.message.reply_text("💍 Usage: `/marry @username` - Propose to someone!")
            return
            
        # Get target user (simplified for demo, normally would resolve username)
        target_name = context.args[0]
        
        # Store proposal
        proposal_id = f"{user.id}_{datetime.now().timestamp()}"
        self.pending_proposals[proposal_id] = {
            'proposer': user.first_name,
            'proposer_id': user.id,
            'target': target_name,
            'chat_id': chat.id
        }
        
        # Create buttons
        keyboard = [
            [
                InlineKeyboardButton("💍 Yes, I do!", callback_data=f"marry_yes_{proposal_id}"),
                InlineKeyboardButton("💔 No, sorry", callback_data=f"marry_no_{proposal_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"💍 **MARRIAGE PROPOSAL** 💍\n\n"
            f"{user.first_name} has proposed to {target_name}!\n\n"
            f"Will you marry them?\n"
            f"💕 **Love is in the air!**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def friend_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a friend"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("🤝 Usage: `/friend @username` - Make a new friend!")
            return
            
        target = context.args[0]
        
        await update.message.reply_text(
            f"🤝 **FRIENDSHIP REQUEST** 🤝\n\n"
            f"{user.first_name} wants to be friends with {target}!\n"
            f"🌟 **Friendship is magic!**",
            parse_mode=ParseMode.MARKDOWN
        )

    async def divorce_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Divorce your partner"""
        await update.message.reply_text("💔 **Divorce initiated...** Things didn't work out.")

    async def dance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send dancing emojis"""
        dancers = ["💃", "🕺", "👯", "👯‍♂️", "👯‍♀️"]
        party = ["✨", "🎉", "🎊", "🎵", "🎶"]
        
        dance_party = ""
        for _ in range(5):
            dance_party += f"{random.choice(dancers)} {random.choice(party)} "
            
        await update.message.reply_text(
            f"🎵 **DANCE PARTY!** 🎵\n\n"
            f"{dance_party}\n\n"
            f"🕺 **Let's groove!** 💃",
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_social_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle social callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("marry_yes_"):
            proposal_id = data.replace("marry_yes_", "")
            proposal = self.pending_proposals.get(proposal_id)
            
            if proposal:
                # Generate Certificate (Text based for now)
                certificate = (
                    "📜 **MARRIAGE CERTIFICATE** 📜\n\n"
                    "This certifies that\n"
                    f"**{proposal['proposer']}** & **{proposal['target']}**\n"
                    "Are now happily married!\n\n"
                    f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n"
                    "✍️ Witness: Ultimate Group King Bot\n\n"
                    "💕 **May your love last forever!** 💕"
                )
                
                await query.edit_message_text(certificate, parse_mode=ParseMode.MARKDOWN)
                
        elif data.startswith("marry_no_"):
            await query.edit_message_text("💔 **Proposal Rejected.** Maybe next time!", parse_mode=ParseMode.MARKDOWN)

