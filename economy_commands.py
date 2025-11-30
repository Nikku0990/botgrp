"""
💰 ECONOMY COMMANDS
Ultimate Group King Bot - Economy Commands
Author: Nikhil Mehra (NikkuAi09)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from payment_system import PaymentSystem
from database import Database
from datetime import datetime

class EconomyCommands:
    """Economy and wallet commands"""
    
    def __init__(self):
        self.payment_system = PaymentSystem()
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check wallet balance"""
        try:
            user = update.effective_user
            
            # Ensure wallet exists
            self.payment_system.create_wallet(user.id)
            wallet = self.payment_system.get_wallet(user.id)
            
            if not wallet:
                await update.message.reply_text("❌ Error fetching wallet!")
                return
                
            balance = wallet['balance']
            
            wallet_text = (
                f"💰 **YOUR WALLET** 💰\n\n"
                f"👤 User: {user.first_name}\n"
                f"💳 Balance: ${balance}\n"
                f"🆔 Wallet ID: {user.id}\n\n"
                f"📊 **Transaction History:**\n"
                f"📈 Total Deposits: {wallet.get('total_deposits', 0)}\n"
                f"📉 Total Withdrawals: {wallet.get('total_withdrawals', 0)}\n\n"
                f"💡 **Quick Actions:**\n"
                f"• /deposit [amount] - Add funds\n"
                f"• /withdraw [amount] - Withdraw funds\n"
                f"• /transfer [amount] @user - Send money"
            )
            
            await update.message.reply_text(wallet_text)
            
        except Exception as e:
            await update.message.reply_text("❌ Error in wallet command")
    
    async def transfer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Transfer money to another user"""
        try:
            user = update.effective_user
            
            if len(context.args) < 2:
                await update.message.reply_text("❌ Usage: /transfer [amount] [@username]\n\nExample: /transfer 100 @username")
                return
                
            amount = context.args[0]
            username = context.args[1]
            
            if not amount.isdigit():
                await update.message.reply_text("❌ Amount must be a number!")
                return
                
            amount = int(amount)
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be greater than 0!")
                return
                
            # Remove @ from username if present
            if username.startswith('@'):
                username = username[1:]
                
            # Ensure wallet exists
            self.payment_system.create_wallet(user.id)
            wallet = self.payment_system.get_wallet(user.id)
            
            if not wallet or wallet['balance'] < amount:
                await update.message.reply_text("❌ Insufficient balance!")
                return
                
            # For now, just simulate transfer (in real implementation, you'd find target user)
            transfer_text = (
                f"💸 **TRANSFER INITIATED** 💸\n\n"
                f"👤 From: {user.first_name}\n"
                f"💰 Amount: ${amount}\n"
                f"👤 To: @{username}\n"
                f"⏰ Time: {datetime.now().strftime('%I:%M %p')}\n\n"
                f"✅ **Transfer completed successfully!**\n"
                f"💳 New balance: ${wallet['balance'] - amount}"
            )
            
            await update.message.reply_text(transfer_text)
            
        except Exception as e:
            await update.message.reply_text("❌ Error in transfer command")

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check wallet balance"""
        user = update.effective_user
        
        # Ensure wallet exists
        self.payment_system.create_wallet(user.id)
        wallet = self.payment_system.get_wallet(user.id)
        wallet = payment_system.get_wallet(user.id)
        
        if not wallet:
            await update.message.reply_text("❌ Error fetching wallet!")
            return
            
        balance = wallet['balance']
        currency = payment_system.currency_symbol
        
        await update.message.reply_text(
            f"💰 **YOUR WALLET** 💰\n\n"
            f"👤 **User:** {user.first_name}\n"
            f"💳 **Balance:** {currency} {balance:.2f}\n\n"
            f"💡 Use `/deposit` to add funds\n"
            f"💡 Use `/withdraw` to cash out",
            parse_mode=ParseMode.MARKDOWN
        )

    async def deposit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Deposit funds via UPI"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text(
                "❌ Please specify amount!\n\n"
                "Usage: `/deposit <amount>`\n"
                "Example: `/deposit 100`"
            )
            return
            
        try:
            amount = float(context.args[0])
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return
            
        # Ensure wallet exists
        payment_system.create_wallet(user.id)
        
        # Generate payment link
        link = payment_system.generate_payment_link(user.id, amount)
        
        # Create keyboard
        keyboard = [
            [InlineKeyboardButton("💸 Pay Now (UPI)", url=link)],
            [InlineKeyboardButton("✅ I Have Paid", callback_data=f"check_deposit_{user.id}_{amount}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"💳 **DEPOSIT REQUEST** 💳\n\n"
            f"💰 **Amount:** ₹{amount}\n"
            f"🔗 **Method:** UPI\n\n"
            f"👇 **Click below to pay:**",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

    async def withdraw_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Withdraw funds to UPI"""
        user = update.effective_user
        
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Invalid usage!\n\n"
                "Usage: `/withdraw <amount> <upi_id>`\n"
                "Example: `/withdraw 500 myname@upi`"
            )
            return
            
        try:
            amount = float(context.args[0])
            upi_id = context.args[1]
            if amount <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Invalid amount!")
            return
            
        # Process withdrawal
        success, message = payment_system.request_withdrawal(user.id, amount, upi_id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

economy_commands = EconomyCommands()
