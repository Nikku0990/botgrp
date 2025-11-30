#!/usr/bin/env python3
# 🌟 MAGICAL FEATURES - Ultimate Power Commands
# Author: Nikhil Mehra (NikkuAi09) & Cascade

import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ContextTypes
from telegram.error import BadRequest
import logging

logger = logging.getLogger(__name__)

class MagicalFeatures:
    def __init__(self):
        self.ban_requests = {}  # {user_id: {target_id, reason, votes}}
        self.tagall_messages = {}
        self.call_messages = {}
        
        # 🌟 Enhanced Magic Spells with Creative Effects 🌟
        self.magic_spells = {
            'thunder': '⚡ *THUNDER STRIKE* ⚡\n🌩️ Lightning strikes the target!\n⚡ Electric shock! ⚡',
            'fire': '🔥 *FIRE STORM* 🔥\n🌋 Volcanic eruption!\n🔥 Burning everything! 🔥',
            'ice': '❄️ *ICE FREEZE* ❄️\n🧊 Absolute zero!\n❄️ Frozen solid! ❄️',
            'shadow': '🌑 *SHADOW BIND* 🌑\n🦇 Darkness consumes!\n🌑 Trapped in shadows! 🌑',
            'heal': '💚 *HEALING LIGHT* 💚\n✨ Divine healing!\n💚 Fully restored! 💚',
            'teleport': '🌀 *TELEPORT* 🌀\n🌪️ Space-time manipulation!\n🌀 Vanished into thin air! 🌀',
            'poison': '☠️ *POISON DART* ☠️\n🐍 Toxic venom spreads!\n☠️ Life draining away! ☠️',
            'earthquake': '🌍 *EARTHQUAKE* 🌍\n🏔️ Ground shaking violently!\n🌍 Everything collapsing! 🌍',
            'tsunami': '🌊 *TSUNAMI* 🌊\n🌊 Massive waves incoming!\n🌊 Swept away by water! 🌊',
            'tornado': '🌪️ *TORNADO* 🌪️\n🌀 Wind vortex spinning!\n🌪️ Sucked into the storm! 🌪️'
        }
        
        # 🎨 Creative Emoji Collections for Call Command 🎨
        self.emoji_collections = [
            "🫳 🧑🏼‍🦲 👷🏼‍♂️ 🐎 🫁",  # Random mix
            "🤞🏿 🤾🏼 🤷‍♂️ 🤖 👵🏽",  # People & tech
            "🧑🏽‍🏫 👷🏼 🏇🏽 💕 👇🏿",  # Professions
            "👨🏽‍✈️ 🤷🏾‍♀️ 🐩 👏🏾 📭",  # Animals & objects
            "👩🏻‍💻 🏕 👨🏼‍💻 🧓 🤾🏻",  # Tech & nature
            "👩‍👩‍👦 🚣‍♀️ ⛸ 😥 👩🏿‍🔬",  # Family & sports
            "🦤 🧑🏾‍🏫 🦯 ⚽️ 🫅🏾",  # Birds & sports
            "🚜 🧑🏽‍🦳 🗃 👱‍♀️ 🧝🏾",  # Vehicles & fantasy
            "💂🏾 🖱 💁🏾‍♀️ 🐎 👨🏿‍✈️",  # Military & tech
            "🐏 🏇🏿 🛠 🚴🏼‍♀️ 🫢",  # Animals & tools
            "🤦🏼‍♀️ 🕵🏽‍♀️ 💅 🍦 🏋🏻‍♀️",  # People & food
            "🤮 🫅🏿 👻 🔮 🧟‍♂️",  # Funny & spooky
            "🌈 🦄 🍄 🌸 🦋",  # Nature & fantasy
            "🚀 🛸 👽 🌙 ⭐",  # Space theme
            "🎭 🎪 🎨 🎵 🎸",  # Arts & music
            "🏰 👑 ⚔️ 🛡️ 🐉",  # Medieval theme
            "🏖️ 🌊 🏄‍♂️ 🏐 🌴",  # Beach theme
            "🎰 🎲 🃏 🎰 🎪",  # Casino theme
            "🌺 🌻 🌷 🌹 🌸",  # Flowers
            "🍕 🍔 🍟 🍕 🌮",  # Food
            "⚡ 🔥 💧 🌍 🌪️"   # Elements
        ]
        
        # 🎭 Creative Messages for Call Command 🎭
        self.call_messages = [
            "📢 *EMERGENCY CALL* 📢\n\n{message}\n\n{emojis}\n\n🔔 *All members please respond!* 🔔",
            "⚡ *URGENT ANNOUNCEMENT* ⚡\n\n{message}\n\n{emojis}\n\n📣 *Attention required!* 📣",
            "🚨 *ALERT CALL* 🚨\n\n{message}\n\n{emojis}\n\n🔥 *Immediate action needed!* 🔥",
            "📯 *GROUP CALL* 📯\n\n{message}\n\n{emojis}\n\n🎯 *Everyone check this out!* 🎯",
            "🎺 *MAGIC CALL* 🎺\n\n{message}\n\n{emojis}\n\n✨ *Magical summoning!* ✨",
            "🌟 *SPECIAL CALL* 🌟\n\n{message}\n\n{emojis}\n\n🎪 *Circus is in town!* 🎪",
            "🎭 *DRAMA CALL* 🎭\n\n{message}\n\n{emojis}\n\n🎬 *Show time!* 🎬",
            "🎪 *FUN CALL* 🎪\n\n{message}\n\n{emojis}\n\n🎊 *Party time!* 🎊",
            "🎨 *CREATIVE CALL* 🎨\n\n{message}\n\n{emojis}\n\n🖌️ *Artistic expression!* 🖌️"
        ]
        
    async def tagall_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tag all members with custom message"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # Check if user is admin
        if not await self.is_admin(context, chat_id, user.id):
            await update.message.reply_text("❌ Admin only command!")
            return
            
        # Get custom message
        custom_msg = " ".join(context.args) if context.args else "📢 *Important Announcement*"
        
        try:
            # Get all chat members
            members = []
            async for member in context.bot.get_chat_members(chat_id):
                if not member.user.is_bot:
                    members.append(f"@{member.user.username}" if member.user.username else member.user.first_name)
            
            # Create chunks to avoid message length limit
            chunk_size = 50
            chunks = [members[i:i+chunk_size] for i in range(0, len(members), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                tag_text = f"{custom_msg}\n\n" + "\n".join(chunk)
                if i == 0:
                    await update.message.reply_text(tag_text)
                else:
                    await context.bot.send_message(chat_id, tag_text)
                    
            await update.message.reply_text(f"✅ Tagged {len(members)} members!")
            
        except Exception as e:
            logger.error(f"Tagall error: {e}")
            await update.message.reply_text("❌ Failed to tag members!")
    
    async def call_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🎨 Enhanced Call Command with Creative Emojis and Effects 🎨"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        if not await self.is_admin(context, chat_id, user.id):
            await update.message.reply_text("❌ Admin only command!")
            return
            
        custom_msg = " ".join(context.args) if context.args else "📞 *Emergency Call*"
        
        try:
            # 🎭 Get random emoji collection and message template
            random_emojis = random.choice(self.emoji_collections)
            random_message = random.choice(self.call_messages)
            
            # 🌟 Format the creative message
            call_text = random_message.format(
                message=custom_msg,
                emojis=random_emojis
            )
            
            # 🎨 Add creative footer
            call_text += f"\n\n🎭 *Called by: {user.first_name}*\n"
            call_text += f"⏰ *Time: {datetime.now().strftime('%I:%M %p')}*\n"
            call_text += f"🎪 *Magical Call System Active!* 🎪"
            
            # 🎯 Create interactive keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ I'm Here! 🎉", callback_data="call_respond"),
                    InlineKeyboardButton("❌ Busy 😴", callback_data="call_busy")
                ],
                [
                    InlineKeyboardButton("🎮 Play Game 🎮", callback_data="call_game"),
                    InlineKeyboardButton("🎯 Check Status 🎯", callback_data="call_status")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # 📢 Send the creative call message
            await update.message.reply_text(call_text, reply_markup=reply_markup, parse_mode='Markdown')
            
            # 🌟 Send multiple emoji messages for effect (like the example)
            await asyncio.sleep(1)
            await context.bot.send_message(
                chat_id,
                f"{random_emojis}\n\n{custom_msg}\n\n{random.choice(self.emoji_collections)}",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Call command error: {e}")
            await update.message.reply_text("❌ Failed to cast magical call!")
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ban with or without reason"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        if not await self.is_admin(context, chat_id, user.id):
            await update.message.reply_text("❌ Admin only command!")
            return
            
        if not context.args:
            await update.message.reply_text("Usage: /ban [username/user_id] [reason(optional)]")
            return
            
        # Parse target
        target = context.args[0]
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        try:
            # Get target user info - MULTIPLE METHODS
            target_user = None
            
            if target.startswith('@'):
                # Method 1: Try to get from reply message
                if update.message.reply_to_message and update.message.reply_to_message.from_user:
                    target_user = update.message.reply_to_message.from_user
                    target_id = target_user.id
                else:
                    # Method 2: Try username directly
                    target_username = target[1:]
                    try:
                        # Try to get user by username
                        target_user = await context.bot.get_chat(f"@{target_username}")
                        target_id = target_user.id
                    except:
                        await update.message.reply_text(
                            f"❌ Cannot find user @{target_username}!\n\n"
                            f"🔧 **Solutions:**\n"
                            f"1. Reply to user's message then use command\n"
                            f"2. Use User ID instead\n"
                            f"3. Use /whois to get user info\n\n"
                            f"💡 **Example:**\n"
                            f"Reply to user's message → /ban test reason"
                        )
                        return
            else:
                # Method 3: Try User ID
                try:
                    target_user = await context.bot.get_chat(int(target))
                    target_id = target_user.id
                except:
                    await update.message.reply_text(f"❌ User ID {target} not found!")
                    return
            
            if not target_user:
                await update.message.reply_text("❌ Target user not found!")
                return
            
            target_id = target_user.id
            
            if await self.is_admin(context, chat_id, target_id):
                await update.message.reply_text("❌ Cannot ban admin!")
                return
                
            # Ban with magical effect
            spell = random.choice(list(self.magic_spells.values()))
            ban_msg = f"{spell}\n\n"
            ban_msg += f"🚫 *BANNED* 🚫\n"
            ban_msg += f"👤 User: {target_user.first_name}\n"
            ban_msg += f"🆔 ID: {target_user.id}\n"
            ban_msg += f"📝 Reason: {reason}\n"
            ban_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await context.bot.ban_chat_member(chat_id, target_id)
            await update.message.reply_text(ban_msg)
            
            logger.info(f"User {target_id} banned by {user.id} for: {reason}")
            
        except Exception as e:
            logger.error(f"Ban error: {e}")
            await update.message.reply_text("❌ Failed to ban user!")
            
        except Exception as e:
            logger.error(f"Ban error: {e}")
            await update.message.reply_text("❌ Failed to ban user!")
    
    async def kick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kick with or without reason"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        if not await self.is_admin(context, chat_id, user.id):
            await update.message.reply_text("❌ Admin only command!")
            return
            
        if not context.args:
            await update.message.reply_text("Usage: /kick [username/user_id] [reason(optional)]")
            return
            
        target = context.args[0]
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        try:
            # Get target user info - MULTIPLE METHODS
            target_user = None
            
            if target.startswith('@'):
                # Method 1: Try to get from reply message
                if update.message.reply_to_message and update.message.reply_to_message.from_user:
                    target_user = update.message.reply_to_message.from_user
                    target_id = target_user.id
                else:
                    # Method 2: Try username directly
                    target_username = target[1:]
                    try:
                        # Try to get user by username
                        target_user = await context.bot.get_chat(f"@{target_username}")
                        target_id = target_user.id
                    except:
                        await update.message.reply_text(
                            f"❌ Cannot find user @{target_username}!\n\n"
                            f"🔧 **Solutions:**\n"
                            f"1. Reply to user's message then use command\n"
                            f"2. Use User ID instead\n"
                            f"3. Use /whois to get user info\n\n"
                            f"💡 **Example:**\n"
                            f"Reply to user's message → /kick test reason"
                        )
                        return
            else:
                # Method 3: Try User ID
                try:
                    target_user = await context.bot.get_chat(int(target))
                    target_id = target_user.id
                except:
                    await update.message.reply_text(f"❌ User ID {target} not found!")
                    return
            
            if not target_user:
                await update.message.reply_text("❌ Target user not found!")
                return
            
            target_id = target_user.id
            
            if await self.is_admin(context, chat_id, target_id):
                await update.message.reply_text("❌ Cannot kick admin!")
                return
                
            # Kick with magical effect
            spell = random.choice(list(self.magic_spells.values()))
            kick_msg = f"{spell}\n\n"
            kick_msg += f"👢 *KICKED* 👢\n"
            kick_msg += f"👤 User: {target_user.first_name}\n"
            kick_msg += f"🆔 ID: {target_user.id}\n"
            kick_msg += f"📝 Reason: {reason}\n"
            kick_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await context.bot.ban_chat_member(chat_id, target_id, until_date=datetime.now() + timedelta(seconds=30))
            await update.message.reply_text(kick_msg)
            
            logger.info(f"User {target_id} kicked by {user.id} for: {reason}")
            
        except Exception as e:
            logger.error(f"Kick error: {e}")
            await update.message.reply_text("❌ Failed to kick user!")
    
    async def ban_request_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Submit ban request for voting"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text("Usage: /banrequest [username/user_id] [reason]")
            return
            
        target = context.args[0]
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        try:
            if target.startswith('@'):
                target_user = await context.bot.get_chat(username=target)
            else:
                target_user = await context.bot.get_chat(chat_id, int(target))
            
            target_id = target_user.id
            
            # Create ban request
            request_id = f"{chat_id}_{target_id}_{datetime.now().timestamp()}"
            self.ban_requests[request_id] = {
                'target_id': target_id,
                'target_name': target_user.first_name,
                'requester_id': user.id,
                'requester_name': user.first_name,
                'reason': reason,
                'votes': {},
                'created_at': datetime.now()
            }
            
            # Create voting keyboard
            keyboard = [
                [InlineKeyboardButton("✅ Vote Ban", callback_data=f"ban_vote_{request_id}_yes")],
                [InlineKeyboardButton("❌ Vote Keep", callback_data=f"ban_vote_{request_id}_no")],
                [InlineKeyboardButton(f"📊 Votes: 0", callback_data=f"ban_votes_{request_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            request_msg = f"🗳️ *BAN REQUEST* 🗳️\n\n"
            request_msg += f"👤 Target: {target_user.first_name}\n"
            request_msg += f"🙋 Requester: {user.first_name}\n"
            request_msg += f"📝 Reason: {reason}\n"
            request_msg += f"⏰ Vote ends in 24 hours\n\n"
            request_msg += f"👇 Cast your vote below!"
            
            await update.message.reply_text(request_msg, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ban request error: {e}")
            await update.message.reply_text("❌ Failed to create ban request!")
    
    async def magic_spell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cast magical spells with effects"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        if not context.args:
            spells_text = "🌟 *Available Magic Spells* 🌟\n\n"
            for spell, effect in self.magic_spells.items():
                spells_text += f"🔮 /{spell} - {effect}\n"
            await update.message.reply_text(spells_text)
            return
            
        spell_name = context.args[0].lower()
        
        if spell_name in self.magic_spells:
            spell_effect = self.magic_spells[spell_name]
            
            # Magical effects based on spell type
            if spell_name == 'thunder':
                await self.thunder_effect(update, context)
            elif spell_name == 'fire':
                await self.fire_effect(update, context)
            elif spell_name == 'ice':
                await self.ice_effect(update, context)
            elif spell_name == 'shadow':
                await self.shadow_effect(update, context)
            elif spell_name == 'heal':
                await self.heal_effect(update, context)
            elif spell_name == 'teleport':
                await self.teleport_effect(update, context)
        else:
            await update.message.reply_text(f"❌ Unknown spell: {spell_name}")
    
    async def thunder_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Thunder strike effect"""
        effects = ["⚡", "🌩️", "⛈️", "💥"]
        for effect in effects:
            await update.message.reply_text(effect)
            await asyncio.sleep(0.5)
        await update.message.reply_text("⚡ *THUNDER STRIKE COMPLETE* ⚡")
    
    async def fire_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fire storm effect"""
        effects = ["🔥", "🌋", "💥", "🔥🔥🔥"]
        for effect in effects:
            await update.message.reply_text(effect)
            await asyncio.sleep(0.5)
        await update.message.reply_text("🔥 *FIRE STORM COMPLETE* 🔥")
    
    async def ice_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ice freeze effect"""
        effects = ["❄️", "🧊", "🥶", "❄️❄️❄️"]
        for effect in effects:
            await update.message.reply_text(effect)
            await asyncio.sleep(0.5)
        await update.message.reply_text("❄️ *ICE FREEZE COMPLETE* ❄️")
    
    async def shadow_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Shadow bind effect"""
        effects = ["🌑", "🌒", "🌓", "🌑🌑🌑"]
        for effect in effects:
            await update.message.reply_text(effect)
            await asyncio.sleep(0.5)
        await update.message.reply_text("🌑 *SHADOW BIND COMPLETE* 🌑")
    
    async def heal_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Healing light effect"""
        effects = ["💚", "💚💚", "💚💚💚", "✨"]
        for effect in effects:
            await update.message.reply_text(effect)
            await asyncio.sleep(0.5)
        await update.message.reply_text("💚 *HEALING COMPLETE* 💚")
    
    async def teleport_effect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Teleport effect"""
        effects = ["🌀", "🌪️", "✨", "👻"]
        for effect in effects:
            await update.message.reply_text(effect)
            await asyncio.sleep(0.5)
        await update.message.reply_text("🌀 *TELEPORT COMPLETE* 🌀")
    
    async def handle_magical_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle magical feature callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("ban_vote_"):
            await self.handle_ban_vote(update, context, query)
        elif data.startswith("call_"):
            await self.handle_call_response(update, context, query)
        elif data.startswith("ban_votes_"):
            await self.show_ban_votes(update, context, query)
    
    async def handle_ban_vote(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query):
        """Handle ban voting"""
        data = query.data.split("_")
        request_id = "_".join(data[2:5])
        vote = data[5]
        
        if request_id not in self.ban_requests:
            await query.edit_message_text("❌ Ban request expired!")
            return
            
        user_id = query.from_user.id
        request = self.ban_requests[request_id]
        
        # Add vote
        request['votes'][user_id] = vote
        
        # Update keyboard
        yes_votes = sum(1 for v in request['votes'].values() if v == 'yes')
        no_votes = sum(1 for v in request['votes'].values() if v == 'no')
        
        keyboard = [
            [InlineKeyboardButton(f"✅ Vote Ban ({yes_votes})", callback_data=f"ban_vote_{request_id}_yes")],
            [InlineKeyboardButton(f"❌ Vote Keep ({no_votes})", callback_data=f"ban_vote_{request_id}_no")],
            [InlineKeyboardButton(f"📊 Total Votes: {len(request['votes'])}", callback_data=f"ban_votes_{request_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Check if enough votes for ban (need 5 yes votes and more yes than no)
        if yes_votes >= 5 and yes_votes > no_votes:
            try:
                await context.bot.ban_chat_member(query.message.chat_id, request['target_id'])
                await query.edit_message_text(f"✅ Ban request approved!\n\n{request['target_name']} has been banned.")
                del self.ban_requests[request_id]
            except Exception as e:
                logger.error(f"Auto ban failed: {e}")
        else:
            await query.edit_message_reply_markup(reply_markup)
    
    async def handle_call_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query):
        """🎭 Enhanced Call Response Handler with Creative Effects 🎭"""
        response = query.data.split("_")[1]
        user_name = query.from_user.first_name
        
        # 🎨 Get random emoji for response
        response_emojis = {
            "respond": ["🎉", "✅", "🎊", "👏", "🙌", "🎯"],
            "busy": ["😴", "❌", "👋", "😔", "🚫", "⏰"],
            "game": ["🎮", "🎲", "🎯", "🎪", "🎨", "🎭"],
            "status": ["🎯", "📊", "🔍", "📈", "💯", "⭐"]
        }
        
        emoji = random.choice(response_emojis.get(response, ["🎭"]))
        
        if response == "respond":
            await query.answer(f"🎉 {user_name} is here! Thanks for responding! 🎉")
            await query.edit_message_text(
                f"✅ {user_name} responded to the call! 🎉\n\n"
                f"🎭 Status: Present 👑\n"
                f"⏰ Response time: {datetime.now().strftime('%I:%M %p')}\n"
                f"🌟 Thanks for being active! 🌟"
            )
            
        elif response == "busy":
            await query.answer(f"😴 {user_name} is busy right now! 😴")
            await query.edit_message_text(
                f"❌ {user_name} is busy! 😴\n\n"
                f"🎭 Status: Busy 😔\n"
                f"⏰ Response time: {datetime.now().strftime('%I:%M %p')}\n"
                f"🌟 We'll catch you later! 🌟"
            )
            
        elif response == "game":
            await query.answer(f"🎮 {user_name} wants to play! 🎮")
            await query.edit_message_text(
                f"🎮 {user_name} wants to play a game! 🎲\n\n"
                f"🎭 Status: Ready for fun! 🎪\n"
                f"⏰ Response time: {datetime.now().strftime('%I:%M %p')}\n"
                f"🌟 Use /games to start playing! 🌟"
            )
            
        elif response == "status":
            await query.answer(f"🎯 {user_name} checked status! 🎯")
            await query.edit_message_text(
                f"🎯 {user_name} checked status! 📊\n\n"
                f"🎭 Status: Active ✅\n"
                f"⏰ Check time: {datetime.now().strftime('%I:%M %p')}\n"
                f"🌟 User is online and ready! 🌟"
            )
    
    async def add_magical_effects(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🌟 Add magical effects to messages 🌟"""
        magical_effects = [
            "✨ *Magical sparkles everywhere!* ✨",
            "🌟 *Stars falling from the sky!* 🌟", 
            "🎆 *Fireworks exploding!* 🎆",
            "🎨 *Rainbow colors appearing!* 🎨",
            "🎪 *Circus music playing!* 🎪",
            "🎭 *Dramatic effects!* 🎭",
            "🌈 *Unicorn magic!* 🌈",
            "🦄 *Mythical creatures appearing!* 🦄",
            "🎯 *Laser beams shooting!* 🎯",
            "🎮 *Game power-ups activated!* 🎮"
        ]
        
        effect = random.choice(magical_effects)
        await update.message.reply_text(effect, parse_mode='Markdown')
    
    async def creative_announce(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🎨 Creative announcement system 🎨"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /announce [message]")
            return
            
        message = " ".join(context.args)
        
        # 🎭 Get random creative template
        templates = [
            "🎪 *CIRCUS ANNOUNCEMENT* 🎪\n\n{message}\n\n🎭 Step right up! 🎭",
            "🎨 *ARTISTIC GALLERY* 🎨\n\n{message}\n\n🖌️ Masterpiece created! 🖌️",
            "🎮 *GAME SHOW* 🎮\n\n{message}\n\n🎯 Contestant ready! 🎯",
            "🌟 *STAR PERFORMANCE* 🌟\n\n{message}\n\n✨ Standing ovation! ✨",
            "🎭 *DRAMA THEATER* 🎭\n\n{message}\n\n🎬 Show time! 🎬",
            "🎪 *MAGIC SHOW* 🎪\n\n{message}\n\n🎩 Abracadabra! 🎩"
        ]
        
        template = random.choice(templates)
        announcement = template.format(message=message)
        
        # 🌟 Add random emojis
        emojis = random.choice(self.emoji_collections)
        announcement += f"\n\n{emojis}"
        
        await update.message.reply_text(announcement, parse_mode='Markdown')
    
    async def show_ban_votes(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query):
        """Show detailed ban votes"""
        request_id = query.data.split("_")[2]
        
        if request_id not in self.ban_requests:
            await query.answer("Ban request expired!")
            return
            
        request = self.ban_requests[request_id]
        
        votes_text = f"📊 *Ban Request Votes* 📊\n\n"
        votes_text += f"👤 Target: {request['target_name']}\n"
        votes_text += f"📝 Reason: {request['reason']}\n\n"
        votes_text += f"✅ Yes Votes: {sum(1 for v in request['votes'].values() if v == 'yes')}\n"
        votes_text += f"❌ No Votes: {sum(1 for v in request['votes'].values() if v == 'no')}\n\n"
        votes_text += f"📋 *Voters:*\n"
        
        for user_id, vote in request['votes'].items():
            vote_emoji = "✅" if vote == 'yes' else "❌"
            try:
                user = await context.bot.get_chat(user_id)
                votes_text += f"{vote_emoji} {user.first_name}\n"
            except:
                votes_text += f"{vote_emoji} Unknown User\n"
        
        await query.answer(votes_text, show_alert=True)
    
    async def is_admin(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
        """Check if user is admin"""
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['creator', 'administrator']
        except:
            return False

# Initialize magical features
magical = MagicalFeatures()

