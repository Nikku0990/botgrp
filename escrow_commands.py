"""
🤝 ESCROW COMMANDS
Ultimate Group King Bot - Escrow Commands
Author: Nikhil Mehra (NikkuAi09)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from escrow_system import escrow_system
from database import Database

class EscrowCommands:
    """Handler for escrow related commands"""
    
    async def deal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Initiate a new deal"""
        user = update.effective_user
        
        # Usage: /deal <amount> <@user> <description>
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ Invalid usage!\n\n"
                "Usage: `/deal <amount> <@user> <description>`\n"
                "Example: `/deal 500 @seller Buying PUBG Account`"
            )
            return
            
        try:
            amount = float(context.args[0])
            target_username = context.args[1].replace('@', '')
            description = " ".join(context.args[2:])
            
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return
            
        # Find seller ID from username (simplified lookup)
        # In a real scenario, we'd need a robust way to resolve usernames to IDs
        # For now, we'll try to find in our DB
        seller = None
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, first_name FROM users WHERE username = ?', (target_username,))
            seller = cursor.fetchone()
            
        if not seller:
            await update.message.reply_text(f"❌ User @{target_username} not found in bot database! Ask them to /start the bot first.")
            return
            
        seller_id = seller[0]
        seller_name = seller[1]
        
        # Create deal
        success, result = escrow_system.create_deal(user.id, seller_id, amount, description)
        
        if success:
            deal_id = result
            
            # Notify User
            await update.message.reply_text(
                f"🤝 **DEAL CREATED!** 🤝\n\n"
                f"🆔 **Deal ID:** `{deal_id}`\n"
                f"💰 **Amount:** {amount}\n"
                f"📝 **Item:** {description}\n"
                f"👤 **Seller:** {seller_name}\n\n"
                f"⏳ Waiting for seller to accept...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify Seller (if possible, or they see it in group)
            try:
                keyboard = [[InlineKeyboardButton("✅ Accept Deal", callback_data=f"accept_deal_{deal_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=seller_id,
                    text=f"🤝 **NEW DEAL REQUEST** 🤝\n\n"
                         f"👤 **Buyer:** {user.first_name}\n"
                         f"💰 **Amount:** {amount}\n"
                         f"📝 **Item:** {description}\n\n"
                         f"👇 Click to accept:",
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                pass # Seller might have blocked bot or privacy settings
        else:
            await update.message.reply_text(f"❌ {result}")

    async def accept_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle accept deal callback"""
        query = update.callback_query
        await query.answer()
        
        data = query.data.split('_')
        deal_id = data[2]
        user_id = query.from_user.id
        
        success, message = escrow_system.accept_deal(deal_id, user_id)
        
        if success:
            await query.edit_message_text(f"✅ **DEAL ACCEPTED!**\n\n{message}", parse_mode=ParseMode.MARKDOWN)
            
            # Notify Buyer to Pay
            deal = escrow_system.get_deal(deal_id)
            if deal:
                buyer_id = deal['buyer_id']
                keyboard = [[InlineKeyboardButton("💸 Pay Now", callback_data=f"pay_deal_{deal_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=buyer_id,
                    text=f"✅ **Seller Accepted Deal {deal_id}!**\n\n"
                         f"💰 Please pay **{deal['amount']}** to Escrow now.",
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await query.edit_message_text(f"❌ {message}")

    async def pay_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pay deal callback"""
        query = update.callback_query
        await query.answer()
        
        data = query.data.split('_')
        deal_id = data[2]
        user_id = query.from_user.id
        
        success, message = escrow_system.pay_deal(deal_id, user_id)
        
        if success:
            await query.edit_message_text(f"✅ **PAYMENT SUCCESSFUL!**\n\n{message}", parse_mode=ParseMode.MARKDOWN)
            
            # Notify Seller
            deal = escrow_system.get_deal(deal_id)
            if deal:
                seller_id = deal['seller_id']
                await context.bot.send_message(
                    chat_id=seller_id,
                    text=f"💰 **Deal {deal_id} Funded!**\n\n"
                         f"Buyer has paid to Escrow. Please deliver the item/service now.\n"
                         f"Once buyer confirms receipt, funds will be released."
                )
        else:
            await query.edit_message_text(f"❌ {message}")

    async def release_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Release funds"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: `/release <deal_id>`")
            return
            
        deal_id = context.args[0]
        success, message = escrow_system.release_funds(deal_id, user.id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
            
            # Notify Seller
            deal = escrow_system.get_deal(deal_id)
            if deal:
                seller_id = deal['seller_id']
                await context.bot.send_message(
                    chat_id=seller_id,
                    text=f"🎉 **Deal {deal_id} Completed!**\n\n"
                         f"Funds have been released to your wallet."
                )
        else:
            await update.message.reply_text(f"❌ {message}")

    async def dispute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Dispute a deal"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: `/dispute <deal_id>`")
            return
            
        deal_id = context.args[0]
        success, message = escrow_system.dispute_deal(deal_id, user.id)
        
        if success:
            await update.message.reply_text(f"⚠️ {message}")
            # Here we would notify admins
        else:
            await update.message.reply_text(f"❌ {message}")

escrow_commands = EscrowCommands()
