"""
🗳️ POLITICS COMMANDS
Ultimate Group King Bot - Politics Commands
Author: Nikhil Mehra (NikkuAi09)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from politics_system import politics_system
from database import Database

class PoliticsCommands:
    """Handler for politics related commands"""
    
    async def election_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start an election"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Admin only
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can start elections!")
            return
            
        if not context.args:
            await update.message.reply_text("Usage: `/election <Title>`")
            return
            
        title = " ".join(context.args)
        success, message = politics_system.create_election(chat.id, title)
        
        if success:
            await update.message.reply_text(
                f"🗳️ **ELECTION STARTED!** 🗳️\n\n"
                f"📜 **Title:** {title}\n"
                f"⏳ **Duration:** 24 Hours\n\n"
                f"👉 Use `/nominate <manifesto>` to run for office!",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(f"❌ {message}")

    async def nominate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Nominate self for election"""
        user = update.effective_user
        chat = update.effective_chat
        
        if not context.args:
            await update.message.reply_text("Usage: `/nominate <Your Manifesto>`")
            return
            
        manifesto = " ".join(context.args)
        success, message = politics_system.nominate_candidate(chat.id, user.id, manifesto)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def vote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vote for a candidate"""
        # This command is usually triggered via buttons, but can be manual
        user = update.effective_user
        chat = update.effective_chat
        
        if not context.args:
            await update.message.reply_text("Usage: `/vote <candidate_id>` (Better use /polls)")
            return
            
        candidate_id = context.args[0]
        success, message = politics_system.vote(chat.id, user.id, candidate_id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def polls_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show voting polls"""
        chat = update.effective_chat
        
        success, title, results = politics_system.get_election_results(chat.id)
        
        if not success:
            await update.message.reply_text(f"❌ {title}")
            return
            
        if "COMPLETED" in title:
            await update.message.reply_text("❌ Election is over! Use /results to see winners.")
            return
            
        keyboard = []
        for candidate in results:
            keyboard.append([InlineKeyboardButton(
                f"🗳️ {candidate['name']} ({candidate['votes']})", 
                callback_data=f"vote_{candidate['candidate_id']}"
            )])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🗳️ **VOTE NOW!** 🗳️\n\n"
            f"Election: {title}\n\n"
            f"Click a candidate to cast your vote:",
            reply_markup=reply_markup
        )

    async def vote_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle vote button click"""
        query = update.callback_query
        user = query.from_user
        chat = query.message.chat
        
        candidate_id = query.data.split('_')[1]
        
        success, message = politics_system.vote(chat.id, user.id, candidate_id)
        
        if success:
            await query.answer("✅ Vote cast successfully!", show_alert=True)
            # Refresh polls
            # (In a real scenario, we might not want to refresh on every vote to avoid rate limits, 
            # but for now it provides immediate feedback)
            # await self.polls_command(update, context) 
        else:
            await query.answer(f"❌ {message}", show_alert=True)

    async def results_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show election results"""
        chat = update.effective_chat
        
        success, title, results = politics_system.get_election_results(chat.id)
        
        if not success:
            await update.message.reply_text(f"❌ {title}")
            return
            
        text = f"📊 **ELECTION RESULTS** 📊\n\n{title}\n\n"
        
        if not results:
            text += "No candidates yet!"
        else:
            for i, candidate in enumerate(results):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🔸"
                text += f"{medal} **{candidate['name']}**: {candidate['votes']} votes\n"
                text += f"   📜 \"{candidate['manifesto']}\"\n\n"
                
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    async def endelection_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """End election manually"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Admin only
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can end elections!")
            return
            
        success, message = politics_system.end_election(chat.id)
        
        if success:
            await update.message.reply_text(f"🛑 {message}")
            await self.results_command(update, context)
        else:
            await update.message.reply_text(f"❌ {message}")

politics_commands = PoliticsCommands()
