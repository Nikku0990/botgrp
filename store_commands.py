"""
🏪 STORE COMMANDS
Ultimate Group King Bot - Store Commands
Author: Nikhil Mehra (NikkuAi09)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from store_system import store_system
from database import Database

class StoreCommands:
    """Handler for store related commands"""
    
    async def createstore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create a new store"""
        user = update.effective_user
        
        # Usage: /createstore <name> | <description>
        if not context.args:
            await update.message.reply_text(
                "❌ Invalid usage!\n\n"
                "Usage: `/createstore <name> | <description>`\n"
                "Example: `/createstore Nikhil's Shop | Best accounts and scripts`"
            )
            return
            
        args_text = " ".join(context.args)
        if "|" not in args_text:
            await update.message.reply_text("❌ Please separate name and description with `|`")
            return
            
        name, description = [x.strip() for x in args_text.split("|", 1)]
        
        success, message = store_system.create_store(user.id, name, description)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def additem_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add item to store"""
        user = update.effective_user
        
        # Usage: /additem <name> | <price> | <description> | <content>
        if not context.args:
            await update.message.reply_text(
                "❌ Invalid usage!\n\n"
                "Usage: `/additem <name> | <price> | <desc> | <content>`\n"
                "Example: `/additem Netflix 1 Month | 100 | 4K UHD | user:pass`\n\n"
                "Note: `content` is what the buyer receives after payment."
            )
            return
            
        args_text = " ".join(context.args)
        parts = [x.strip() for x in args_text.split("|")]
        
        if len(parts) < 4:
            await update.message.reply_text("❌ Missing arguments! Need: Name | Price | Desc | Content")
            return
            
        name = parts[0]
        try:
            price = float(parts[1])
        except ValueError:
            await update.message.reply_text("❌ Invalid price!")
            return
        description = parts[2]
        content = parts[3]
        
        success, message = store_system.add_item(user.id, name, price, description, content)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def viewstore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View a store"""
        # Can view by username or reply
        target_user_id = update.effective_user.id
        
        if context.args:
            username = context.args[0].replace('@', '')
            # Resolve username (simplified)
            with db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
                row = cursor.fetchone()
                if row:
                    target_user_id = row[0]
                else:
                    await update.message.reply_text("❌ User not found!")
                    return
        elif update.message.reply_to_message:
            target_user_id = update.message.reply_to_message.from_user.id
            
        store = store_system.get_store(target_user_id)
        if not store:
            await update.message.reply_text("❌ This user does not have a store!")
            return
            
        items = store_system.get_store_items(store['store_id'])
        
        store_text = f"🏪 **{store['name']}** 🏪\n"
        store_text += f"📝 {store['description']}\n\n"
        store_text += f"📦 **Available Items:**\n\n"
        
        if not items:
            store_text += "No items yet!"
            await update.message.reply_text(store_text, parse_mode=ParseMode.MARKDOWN)
            return
            
        for item in items:
            store_text += f"🔹 **{item['name']}** - ₹{item['price']}\n"
            store_text += f"   {item['description']}\n\n"
            
            # Add Buy Button
            keyboard = [[InlineKeyboardButton(f"🛒 Buy for ₹{item['price']}", callback_data=f"buy_item_{item['item_id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🔹 **{item['name']}**\n"
                f"💰 Price: ₹{item['price']}\n"
                f"📝 {item['description']}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
        # await update.message.reply_text(store_text, parse_mode=ParseMode.MARKDOWN)

    async def buy_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle buy button click"""
        query = update.callback_query
        user = query.from_user
        
        item_id = query.data.replace("buy_item_", "")
        
        success, message, content = store_system.buy_item(user.id, item_id)
        
        if success:
            await query.answer("✅ Purchase successful!", show_alert=True)
            
            # Send content in DM
            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=f"📦 **Your Purchase: {item_id}**\n\n"
                         f"🔐 **Content:**\n`{content}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                await query.edit_message_text(f"✅ Purchased! Check DM.")
            except Exception:
                await query.edit_message_text(f"✅ Purchased! (Enable DM for content)")
        else:
            await query.answer(f"❌ {message}", show_alert=True)

    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Buy an item"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: `/buy <item_id>`")
            return
            
        item_id = context.args[0]
        
        success, message, content = store_system.buy_item(user.id, item_id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
            
            # Send content in DM
            try:
                await context.bot.send_message(
                    chat_id=user.id,
                    text=f"📦 **Your Purchase: {item_id}**\n\n"
                         f"🔐 **Content:**\n`{content}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text("📩 Check your DM for the item!")
            except Exception:
                await update.message.reply_text("❌ Could not DM you! Please start the bot in private.")
        else:
            await update.message.reply_text(f"❌ {message}")

store_commands = StoreCommands()
