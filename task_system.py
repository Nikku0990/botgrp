#!/usr/bin/env python3
"""
📋 TASK SYSTEM
Ultimate Group King Bot - Task Management & EXP System
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import TASK_LIST, EXP_THRESHOLDS, EXP_PER_MESSAGE, EXP_PER_COMMAND
from database import Database

class TaskSystem:
    """Manages the task system and EXP rewards"""
    
    def __init__(self):
        self.active_tasks = {}
        self.task_progress = {}
        self.exp_multipliers = {
            'weekend': 1.5,  # Weekend bonus
            'night': 1.2,    # Night owl bonus
            'streak': 2.0    # Streak bonus
        }
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    async def process_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process message for task updates"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        message = update.message
        
        # Update basic tasks
        await self._update_chat_master_task(user_id, chat_id)
        await self._update_emoji_task(user_id, chat_id, message.text or "")
        await self._update_mention_task(user_id, chat_id, message)
        await self._update_hashtag_task(user_id, chat_id, message.text or "")
        await self._update_link_task(user_id, chat_id, message)
        await self._update_time_based_tasks(user_id, chat_id)
        await self._update_streak_task(user_id, chat_id)
        
        # Check for task completion
        await self._check_task_completion(user_id, chat_id)
    
    async def process_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE, media_type: str):
        """Process media message for task updates"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Update media-specific tasks
        if media_type == 'photo':
            await self._update_media_master_task(user_id, chat_id)
        elif media_type == 'sticker':
            await self._update_sticker_lover_task(user_id, chat_id)
        elif media_type == 'gif':
            await self._update_gif_master_task(user_id, chat_id)
        elif media_type == 'voice':
            await self._update_voice_chat_task(user_id, chat_id)
        elif media_type == 'document':
            await self._update_file_sender_task(user_id, chat_id)
    
    async def process_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, command_name: str):
        """Process command for task updates"""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Update command tasks
        await self._update_command_king_task(user_id, chat_id)
        
        # Special command tasks
        if command_name in ['ai', 'chat']:
            await self._update_ai_chat_task(user_id, chat_id)
        elif command_name == 'roast':
            await self._update_roast_master_task(user_id, chat_id)
        elif command_name == 'truth':
            await self._update_truth_teller_task(user_id, chat_id)
        elif command_name == 'dare':
            await self._update_dare_devil_task(user_id, chat_id)
        elif command_name in ['game', 'roll', 'coin']:
            await self._update_game_champion_task(user_id, chat_id)
    
    async def _update_chat_master_task(self, user_id: int, chat_id: int):
        """Update chat master task progress"""
        task_name = "chat_master"
        task = TASK_LIST[task_name]
        
        # Get current progress
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        # Update progress
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        # Check if completed
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_media_master_task(self, user_id: int, chat_id: int):
        """Update media master task progress"""
        task_name = "media_master"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_sticker_lover_task(self, user_id: int, chat_id: int):
        """Update sticker lover task progress"""
        task_name = "sticker_lover"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_gif_master_task(self, user_id: int, chat_id: int):
        """Update GIF master task progress"""
        task_name = "gif_master"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_voice_chat_task(self, user_id: int, chat_id: int):
        """Update voice chat task progress"""
        task_name = "voice_chat"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_file_sender_task(self, user_id: int, chat_id: int):
        """Update file sender task progress"""
        task_name = "file_sender"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_emoji_task(self, user_id: int, chat_id: int, text: str):
        """Update emoji king task progress"""
        import re
        
        # Count emojis in text
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        emojis = re.findall(emoji_pattern, text)
        
        if not emojis:
            return
        
        task_name = "emoji_king"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + len(emojis)
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_mention_task(self, user_id: int, chat_id: int, message):
        """Update mention master task progress"""
        if not message.entities:
            return
        
        # Count mentions
        mention_count = len([e for e in message.entities if e.type == 'mention'])
        
        if mention_count == 0:
            return
        
        task_name = "mention_master"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + mention_count
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_hashtag_task(self, user_id: int, chat_id: int, text: str):
        """Update hashtag king task progress"""
        import re
        
        # Count hashtags
        hashtags = re.findall(r'#\w+', text)
        
        if not hashtags:
            return
        
        task_name = "hashtag_king"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + len(hashtags)
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_link_task(self, user_id: int, chat_id: int, message):
        """Update link sharer task progress"""
        if not message.entities:
            return
        
        # Count URLs
        url_count = len([e for e in message.entities if e.type == 'url'])
        
        if url_count == 0:
            return
        
        task_name = "link_sharer"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + url_count
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_time_based_tasks(self, user_id: int, chat_id: int):
        """Update time-based tasks"""
        current_hour = datetime.now().hour
        
        # Night Owl Task (2 AM - 4 AM)
        if 2 <= current_hour <= 4:
            task_name = "night_owl"
            task = TASK_LIST[task_name]
            
            user_tasks = db.get_user_tasks(user_id, chat_id)
            current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
            current_progress = current_task['progress'] if current_task else 0
            
            new_progress = current_progress + 1
            db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
            
            if new_progress >= task['target']:
                await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
        
        # Early Bird Task (5 AM - 7 AM)
        elif 5 <= current_hour <= 7:
            task_name = "early_bird"
            task = TASK_LIST[task_name]
            
            user_tasks = db.get_user_tasks(user_id, chat_id)
            current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
            current_progress = current_task['progress'] if current_task else 0
            
            new_progress = current_progress + 1
            db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
            
            if new_progress >= task['target']:
                await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_streak_task(self, user_id: int, chat_id: int):
        """Update daily streak task"""
        today = datetime.now().date()
        
        # Get last activity date
        user = db.get_or_create_user(user_id)
        last_active_str = user.get('last_active', '')
        
        if last_active_str:
            last_active = datetime.fromisoformat(last_active_str).date()
            days_diff = (today - last_active).days
            
            # Update streak
            if days_diff == 1:
                # Continued streak
                current_streak = user.get('daily_streak', 0) + 1
            elif days_diff == 0:
                # Same day, no change
                current_streak = user.get('daily_streak', 0)
            else:
                # Streak broken
                current_streak = 1
        else:
            current_streak = 1
        
        # Update user streak (this would need a separate database field)
        # For now, just track in memory
        
        # Award streak bonuses
        if current_streak >= 7:
            await self._award_exp(user_id, chat_id, 100, "weekly_streak")
        elif current_streak >= 30:
            await self._award_exp(user_id, chat_id, 500, "monthly_streak")
    
    async def _update_command_king_task(self, user_id: int, chat_id: int):
        """Update command king task progress"""
        task_name = "command_king"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_ai_chat_task(self, user_id: int, chat_id: int):
        """Update AI chat task progress"""
        task_name = "ai_chat"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_roast_master_task(self, user_id: int, chat_id: int):
        """Update roast master task progress"""
        task_name = "roast_master"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_truth_teller_task(self, user_id: int, chat_id: int):
        """Update truth teller task progress"""
        task_name = "truth_teller"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_dare_devil_task(self, user_id: int, chat_id: int):
        """Update dare devil task progress"""
        task_name = "dare_devil"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _update_game_champion_task(self, user_id: int, chat_id: int):
        """Update game champion task progress"""
        task_name = "game_champion"
        task = TASK_LIST[task_name]
        
        user_tasks = db.get_user_tasks(user_id, chat_id)
        current_task = next((t for t in user_tasks if t['task_name'] == task_name), None)
        current_progress = current_task['progress'] if current_task else 0
        
        new_progress = current_progress + 1
        db.create_or_update_task(user_id, chat_id, task_name, new_progress, task['target'])
        
        if new_progress >= task['target']:
            await self._award_exp(user_id, chat_id, task['exp_reward'], task_name)
    
    async def _check_task_completion(self, user_id: int, chat_id: int):
        """Check for completed tasks and award EXP"""
        user_tasks = db.get_user_tasks(user_id, chat_id)
        
        for task in user_tasks:
            if not task['completed'] and task['progress'] >= task['target']:
                task_name = task['task_name']
                if task_name in TASK_LIST:
                    exp_reward = TASK_LIST[task_name]['exp_reward']
                    await self._award_exp(user_id, chat_id, exp_reward, task_name)
    
    async def _award_exp(self, user_id: int, chat_id: int, exp_amount: int, reason: str):
        """Award EXP to user"""
        # Apply multipliers
        final_exp = await self._apply_exp_multipliers(user_id, chat_id, exp_amount)
        
        # Update user EXP
        db.update_user_exp(user_id, final_exp)
        
        # Check for admin promotion
        await self._check_admin_promotion(user_id, chat_id)
        
        # Log the EXP award
        print(f"💎 Awarded {final_exp} EXP to user {user_id} for {reason}")
    
    async def _apply_exp_multipliers(self, user_id: int, chat_id: int, base_exp: int) -> int:
        """Apply EXP multipliers"""
        multiplier = 1.0
        
        # Weekend multiplier
        now = datetime.now()
        if now.weekday() >= 5:  # Saturday or Sunday
            multiplier *= self.exp_multipliers['weekend']
        
        # Night multiplier
        if 22 <= now.hour or now.hour <= 6:
            multiplier *= self.exp_multipliers['night']
        
        # Streak multiplier (would need streak tracking)
        # multiplier *= self.exp_multipliers['streak']
        
        return int(base_exp * multiplier)
    
    async def _check_admin_promotion(self, user_id: int, chat_id: int):
        """Check if user should be promoted to admin"""
        user = db.get_or_create_user(user_id)
        current_exp = user.get('exp', 0)
        
        # Get group settings
        settings = db.get_group_settings(chat_id)
        
        if not settings.get('task_system_active', False):
            return
        
        if user.get('is_temp_admin', False):
            return
        
        # Find highest threshold user qualifies for
        eligible_thresholds = [
            (threshold, minutes) for threshold, minutes in EXP_THRESHOLDS.items()
            if current_exp >= threshold
        ]
        
        if eligible_thresholds:
            # Get the highest threshold
            threshold, admin_minutes = max(eligible_thresholds, key=lambda x: x[0])
            
            # Promote user (this would need actual Telegram API calls)
            await self._promote_to_temp_admin(user_id, chat_id, admin_minutes, threshold)
    
    async def _promote_to_temp_admin(self, user_id: int, chat_id: int, duration_minutes: int, threshold: int):
        """Promote user to temporary admin"""
        # Update user record
        user = db.get_or_create_user(user_id)
        user['is_temp_admin'] = True
        user['admin_start_time'] = datetime.now().isoformat()
        user['admin_duration_minutes'] = duration_minutes
        
        # Log promotion
        print(f"👑 User {user_id} promoted to temp admin for {duration_minutes} minutes (EXP: {threshold})")
        
        # In real implementation, you'd:
        # 1. Send notification to user
        # 2. Promote in Telegram group
        # 3. Schedule demotion
    
    async def get_user_task_summary(self, user_id: int, chat_id: int) -> Dict[str, Any]:
        """Get user's task summary"""
        user_tasks = db.get_user_tasks(user_id, chat_id)
        completed_tasks = [t for t in user_tasks if t['completed']]
        in_progress_tasks = [t for t in user_tasks if not t['completed']]
        
        return {
            'total_tasks': len(TASK_LIST),
            'completed_tasks': len(completed_tasks),
            'in_progress_tasks': len(in_progress_tasks),
            'completion_rate': (len(completed_tasks) / len(TASK_LIST)) * 100,
            'recent_completions': completed_tasks[-5:] if completed_tasks else []
        }
    
    async def get_leaderboard(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get EXP leaderboard"""
        top_users = db.get_top_users(chat_id, limit, 'exp')
        
        leaderboard = []
        for i, user in enumerate(top_users, 1):
            leaderboard.append({
                'rank': i,
                'user_id': user['user_id'],
                'username': user.get('username', 'Unknown'),
                'first_name': user.get('first_name', 'Unknown'),
                'exp': user.get('exp', 0),
                'level': self._calculate_level(user.get('exp', 0))
            })
        
        return leaderboard
    
    def _calculate_level(self, exp: int) -> int:
        """Calculate user level based on EXP"""
        level = 1
        while exp >= level * 1000:
            level += 1
        return level
    
    async def schedule_demotion(self, user_id: int, chat_id: int, duration_minutes: int):
        """Schedule user demotion after admin duration"""
        # In real implementation, you'd use a scheduler like APScheduler
        demotion_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        # This would be handled by a background task
        print(f"⏰ Scheduled demotion for user {user_id} at {demotion_time}")
    
    def get_task_categories(self) -> Dict[str, List[str]]:
        """Get tasks grouped by category"""
        categories = {
            '💬 Chat': [],
            '📸 Media': [],
            '🎮 Games': [],
            '🤖 AI': [],
            '⏰ Time': [],
            '🛡️ Help': [],
            '👑 Admin': [],
            '💎 EXP': []
        }
        
        for task_name, task in TASK_LIST.items():
            task_type = task.get('type', '')
            
            if 'message' in task_type or 'chat' in task_type:
                categories['💬 Chat'].append(task_name)
            elif any(x in task_type for x in ['sticker', 'media', 'photo', 'video', 'gif', 'voice']):
                categories['📸 Media'].append(task_name)
            elif any(x in task_type for x in ['game', 'quiz', 'truth', 'dare', 'riddle']):
                categories['🎮 Games'].append(task_name)
            elif 'ai' in task_type or 'roast' in task_type:
                categories['🤖 AI'].append(task_name)
            elif 'time' in task_type:
                categories['⏰ Time'].append(task_name)
            elif any(x in task_type for x in ['help', 'report', 'solve', 'welcome']):
                categories['🛡️ Help'].append(task_name)
            elif any(x in task_type for x in ['ban', 'mute', 'warn', 'admin']):
                categories['👑 Admin'].append(task_name)
            elif 'exp' in task_type or 'milestone' in task_type:
                categories['💎 EXP'].append(task_name)
        
        return categories
    
    def get_exp_thresholds(self) -> Dict[int, int]:
        """Get EXP thresholds for admin promotion"""
        return EXP_THRESHOLDS.copy()

# Initialize task system
task_system = TaskSystem()

if __name__ == "__main__":
    # Test task system
    print("📋 Testing Task System...")
    
    # Test task categories
    categories = task_system.get_task_categories()
    print(f"📊 Task categories: {list(categories.keys())}")
    
    # Test EXP thresholds
    thresholds = task_system.get_exp_thresholds()
    print(f"💎 EXP thresholds: {thresholds}")
    
    print("✅ Task System test complete!")
