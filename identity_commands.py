"""
🆔 IDENTITY COMMANDS
Ultimate Group King Bot - Identity Commands
Author: Nikhil Mehra (NikkuAi09)
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from identity_system import identity_system
from database import Database

class IdentityCommands:
    """Handler for identity related commands"""
    
    async def setid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set custom ID"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: `/setid @YourHandle`")
            return
            
        custom_id = context.args[0]
        success, message = identity_system.set_custom_id(user.id, custom_id)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def setbio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set bio"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: `/setbio Your bio text...`")
            return
            
        bio = " ".join(context.args)
        success, message = identity_system.set_bio(user.id, bio)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def setbusiness_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set business name"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: `/setbusiness My Cool Shop`")
            return
            
        name = " ".join(context.args)
        success, message = identity_system.set_business_name(user.id, name)
        
        if success:
            await update.message.reply_text(f"✅ {message}")
        else:
            await update.message.reply_text(f"❌ {message}")

    async def identity_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show identity card"""
        target_user = update.effective_user
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
            
        identity = identity_system.get_identity(target_user.id)
        
        custom_id = identity.get('custom_id', 'Not set')
        bio = identity.get('bio', 'No bio set')
        business = identity.get('business_name', 'No business')
        
        text = f"🆔 **IDENTITY CARD** 🆔\n\n"
        text += f"👤 **Name:** {target_user.first_name}\n"
        text += f"🏷️ **Handle:** {custom_id}\n"
        text += f"🏢 **Business:** {business}\n"
        text += f"📝 **Bio:**\n_{bio}_"
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

identity_commands = IdentityCommands()
