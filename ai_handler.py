#!/usr/bin/env python3
"""
🤖 AI HANDLER
Ultimate Group King Bot - AI Chat & OpenRouter Integration
Author: Nikhil Mehra (NikkuAi09)
"""

import json
import time
import requests
import random
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIHandler:
    """Handles all AI chat operations with OpenRouter API"""
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.request_count = 0
        self.error_count = 0

    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask AI a question (requires API key)."""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Check for API key
        settings = self.get_user_settings(user_id, chat_id)
        if not settings.get('has_api_key'):
            await update.message.reply_text("❌ Please set your OpenRouter API key first using /setapi <your_key>.")
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: /ask [your question]")
            return
            
        question = " ".join(context.args)
        await update.message.reply_text(f"🤖 *AI Response*\n\nYou asked: {question}\n\nAI is processing your question...")
        
        # Get response
        response = self.get_ai_response(user_id, chat_id, question)
        await update.message.reply_text(response)
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Chat with AI (requires API key)."""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Check for API key
        settings = self.get_user_settings(user_id, chat_id)
        if not settings.get('has_api_key'):
            await update.message.reply_text("❌ Please set your OpenRouter API key first using /setapi <your_key>.")
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: /chat [your message]")
            return
            
        message = " ".join(context.args)
        await update.message.reply_text(f"🤖 *AI Chat*\n\nYou: {message}\n\nAI: Hello! How can I help you today?")
        
        # Get response
        response = self.get_ai_response(user_id, chat_id, message)
        await update.message.reply_text(response)

    async def setapi_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set user's OpenRouter API key."""
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text("❌ Usage: /setapi <your_openrouter_api_key>")
            return
            
        api_key = context.args[0]
        
        if not self.validate_api_key(api_key):
            await update.message.reply_text("❌ Invalid API key format. It should start with 'sk-or-v1-'.")
            return
            
        # Test the key quickly
        await update.message.reply_text("⏳ Verifying API key...")
        if not self.test_api_key(api_key):
            await update.message.reply_text("❌ API key test failed. Please ensure it is valid and has enough quota.")
            return
            
        if self.set_user_api_key(user_id, chat_id, api_key):
            await update.message.reply_text("✅ API key set successfully! You can now use /ask and /chat.")
        else:
            await update.message.reply_text("❌ Failed to store API key. Please try again.")

    def get_ai_response(self, user_id: int, chat_id: int, user_message: str) -> str:
        """
        Get AI response with LLD Fallback system
        """
        try:
            # Get user memory and settings
            user_memory = db.get_user_memory(user_id, chat_id)
            api_key = user_memory.get('api_key')
            
            # Check if user has set API key
            if not api_key:
                gaali = random.choice(SAVAGE_GAALIYAN)
                return FALLBACK_MESSAGES["API_KEY_MISSING"].format(gaali=gaali)
            
            # Check cache first
            cache_key = f"{user_id}:{hash(user_message)}"
            if cache_key in self.cache:
                cached_time, cached_response = self.cache[cache_key]
                if time.time() - cached_time < CACHE_CONFIG["ai_responses"]:
                    return cached_response
            
            # Prepare for API request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Get user's preferred model or default
            current_model = user_memory.get('model', AVAILABLE_MODELS[0])
            current_model_index = AVAILABLE_MODELS.index(current_model) if current_model in AVAILABLE_MODELS else 0
            
            # Prepare system prompt
            system_prompt = user_memory.get('ai_system_prompt') or AI_SYSTEM_PROMPT
            
            # Get conversation history
            history = user_memory.get('history', [])
            
            # Prepare messages for API
            messages = [
                {"role": "system", "content": system_prompt},
                *history[-10:],  # Last 10 messages
                {"role": "user", "content": user_message}
            ]
            
            # Try each model (LLD Fallback)
            for attempt in range(len(AVAILABLE_MODELS)):
                try:
                    current_model = AVAILABLE_MODELS[current_model_index]
                    
                    payload = {
                        "model": current_model,
                        "messages": messages,
                        "max_tokens": user_memory.get('ai_max_tokens', 150),
                        "temperature": user_memory.get('ai_temp', 0.9)
                    }
                    
                    logger.info(f"🤖 Trying model: {current_model} for user {user_id}")
                    
                    # Make API request
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(payload),
                        timeout=60
                    )
                    
                    # Handle different response codes
                    if response.status_code == 200:
                        response_json = response.json()
                        
                        if "choices" in response_json and len(response_json["choices"]) > 0:
                            ai_message = response_json["choices"][0]["message"].get("content", "")
                            
                            if ai_message:
                                # Update user memory
                                self._update_user_memory(user_id, chat_id, user_message, ai_message)
                                
                                # Cache the response
                                self.cache[cache_key] = (time.time(), ai_message)
                                
                                # Update user's preferred model if successful
                                if current_model != user_memory.get('model'):
                                    user_memory['model'] = current_model
                                    db.save_user_memory(user_id, chat_id, user_memory)
                                
                                self.request_count += 1
                                logger.info(f"✅ AI response successful for user {user_id}")
                                return ai_message
                    
                    elif response.status_code == 429:
                        logger.warning(f"⚠️ Rate limit exceeded for model {current_model}")
                        time.sleep(1)  # Wait before trying next model
                    
                    elif response.status_code == 403:
                        logger.warning(f"⚠️ Access forbidden for model {current_model}")
                    
                    else:
                        logger.error(f"❌ API error {response.status_code}: {response.text}")
                    
                    # Try next model
                    current_model_index = (current_model_index + 1) % len(AVAILABLE_MODELS)
                    time.sleep(0.5)
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"⚠️ Timeout for model {current_model}")
                    current_model_index = (current_model_index + 1) % len(AVAILABLE_MODELS)
                    time.sleep(1)
                
                except Exception as e:
                    logger.error(f"❌ Exception with model {current_model}: {e}")
                    current_model_index = (current_model_index + 1) % len(AVAILABLE_MODELS)
                    time.sleep(0.5)
            
            # All models failed
            self.error_count += 1
            gaali = random.choice(SAVAGE_GAALIYAN)
            return FALLBACK_MESSAGES["API_FAILED"].format(gaali=gaali)
        
        except Exception as e:
            logger.error(f"❌ Critical error in AI handler: {e}")
            self.error_count += 1
            gaali = random.choice(SAVAGE_GAALIYAN)
            return FALLBACK_MESSAGES["GENERAL_ERROR"].format(gaali=gaali)
    
    def _update_user_memory(self, user_id: int, chat_id: int, user_message: str, ai_response: str):
        """Update user conversation memory"""
        try:
            user_memory = db.get_user_memory(user_id, chat_id)
            
            # Add messages to history
            history = user_memory.get('history', [])
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": ai_response})
            
            # Keep only last 50 messages
            if len(history) > 50:
                history = history[-50:]
            
            user_memory['history'] = history
            
            # Update summary (simple approach)
            if len(history) >= 4:
                # Take last 2 exchanges for summary
                recent_messages = history[-4:]
                user_memory['summary'] = f"Recent chat about: {recent_messages[-2]['content'][:100]}..."
            
            # Save to database
            db.save_user_memory(user_id, chat_id, user_memory, user_memory.get('summary'))
            
            # Update user stats
            db.update_user_stats(user_id, commands=1)
            
        except Exception as e:
            logger.error(f"❌ Failed to update user memory: {e}")
    
    def set_user_api_key(self, user_id: int, chat_id: int, api_key: str) -> bool:
        """Set user's OpenRouter API key"""
        try:
            # Validate API key format (basic check)
            if not api_key.startswith('sk-or-v1-'):
                return False
            
            user_memory = db.get_user_memory(user_id, chat_id)
            user_memory['api_key'] = api_key
            db.save_user_memory(user_id, chat_id, user_memory)
            
            logger.info(f"✅ API key set for user {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to set API key: {e}")
            return False
    
    def set_user_model(self, user_id: int, chat_id: int, model: str) -> bool:
        """Set user's preferred AI model"""
        try:
            if model not in AVAILABLE_MODELS:
                return False
            
            user_memory = db.get_user_memory(user_id, chat_id)
            user_memory['model'] = model
            db.save_user_memory(user_id, chat_id, user_memory)
            
            logger.info(f"✅ Model set to {model} for user {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to set model: {e}")
            return False
    
    def set_ai_settings(self, user_id: int, chat_id: int, **settings) -> bool:
        """Set AI settings for user"""
        try:
            user_memory = db.get_user_memory(user_id, chat_id)
            
            # Update allowed settings
            allowed_settings = ['ai_system_prompt', 'ai_temp', 'ai_max_tokens']
            for key, value in settings.items():
                if key in allowed_settings:
                    user_memory[key] = value
            
            db.save_user_memory(user_id, chat_id, user_memory)
            
            logger.info(f"✅ AI settings updated for user {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to set AI settings: {e}")
            return False
    
    def get_user_settings(self, user_id: int, chat_id: int) -> Dict[str, Any]:
        """Get user's AI settings"""
        try:
            user_memory = db.get_user_memory(user_id, chat_id)
            
            return {
                'api_key': bool(user_memory.get('api_key')),
                'model': user_memory.get('model', AVAILABLE_MODELS[0]),
                'ai_system_prompt': user_memory.get('ai_system_prompt', AI_SYSTEM_PROMPT),
                'ai_temp': user_memory.get('ai_temp', 0.9),
                'ai_max_tokens': user_memory.get('ai_max_tokens', 150),
                'has_api_key': bool(user_memory.get('api_key'))
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to get user settings: {e}")
            return {}
    
    def clear_user_memory(self, user_id: int, chat_id: int) -> bool:
        """Clear user's conversation memory"""
        try:
            user_memory = db.get_user_memory(user_id, chat_id)
            user_memory['history'] = []
            user_memory['summary'] = "New conversation"
            db.save_user_memory(user_id, chat_id, user_memory)
            
            logger.info(f"✅ Memory cleared for user {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to clear user memory: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        return AVAILABLE_MODELS.copy()
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_info = {
            "deepseek/deepseek-r1-0528-qwen3-8b:free": {
                "name": "DeepSeek R1",
                "description": "Fast, intelligent responses",
                "context_length": 8192,
                "free": True
            },
            "mistralai/mistral-small-3.2-24b-instruct:free": {
                "name": "Mistral Small",
                "description": "Balanced performance",
                "context_length": 32768,
                "free": True
            },
            "meta-llama/llama-3.3-70b-instruct:free": {
                "name": "Llama 3.3 70B",
                "description": "High quality responses",
                "context_length": 131072,
                "free": True
            }
        }
        
        return model_info.get(model, {
            "name": model,
            "description": "AI Model",
            "context_length": "Unknown",
            "free": True
        })
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate if API key is correct format"""
        try:
            # Basic format validation
            if not api_key or not isinstance(api_key, str):
                return False
            
            if not api_key.startswith('sk-or-v1-'):
                return False
            
            if len(api_key) < 20:
                return False
            
            return True
        
        except Exception:
            return False
    
    def test_api_key(self, api_key: str) -> bool:
        """Test if API key works by making a small request"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": AVAILABLE_MODELS[0],
                "messages": [
                    {"role": "user", "content": "test"}
                ],
                "max_tokens": 5
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get AI handler statistics"""
        return {
            "requests": self.request_count,
            "errors": self.error_count,
            "cache_size": len(self.cache),
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1) * 100
        }
    
    def clear_cache(self):
        """Clear AI response cache"""
        self.cache.clear()
        logger.info("✅ AI cache cleared")
    
    def roast_user(self, user_id: int, chat_id: int, target_message: str = None) -> str:
        """Generate a savage roast"""
        try:
            user_memory = db.get_user_memory(user_id, chat_id)
            api_key = user_memory.get('api_key')
            
            if not api_key:
                gaali = random.choice(SAVAGE_GAALIYAN)
                return FALLBACK_MESSAGES["API_KEY_MISSING"].format(gaali=gaali)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Special roast prompt
            roast_prompt = (
                "Tu Nikhil Papa hai, ek professional roaster. "
                "User ko roast kar in Hinglish with savage gaaliyan. "
                f"Use these gaaliyan: {', '.join(SAVAGE_GAALIYAN[:5])}. "
                "Keep it short, punchy, and brutally funny. "
                "Maximum 2-3 lines. Make it hurt but funny!"
            )
            
            user_input = target_message or "Roast me brutally"
            
            payload = {
                "model": user_memory.get('model', AVAILABLE_MODELS[0]),
                "messages": [
                    {"role": "system", "content": roast_prompt},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 100,
                "temperature": 1.0  # Higher temperature for more creativity
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                response_json = response.json()
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    roast = response_json["choices"][0]["message"].get("content", "")
                    if roast:
                        return roast
            
            # Fallback roast
            fallback_roasts = [
                f"Arre {random.choice(SAVAGE_GAALIYAN)}, teri aukat kya hai? ",
                f"Madarchod {random.choice(SAVAGE_GAALIYAN)}, dimag hai ya bhoka?",
                f"Bhenchod {random.choice(SAVAGE_GAALIYAN)}, tu kuch bhi nahi hai!",
                f"Chutiye {random.choice(SAVAGE_GAALIYAN)}, apni shakal dekhi hai kabhi?",
                f"Gandu {random.choice(SAVAGE_GAALIYAN)}, tu khud hi joke hai!"
            ]
            
            return random.choice(fallback_roasts)
        
        except Exception as e:
            logger.error(f"❌ Failed to generate roast: {e}")
            return f"Arre {random.choice(SAVAGE_GAALIYAN)}, roast nahi kar pa raha hun. System mein lafda hai!"
    
    def translate_text(self, user_id: int, chat_id: int, text: str, target_lang: str = "Hinglish") -> str:
        """Translate text to target language"""
        try:
            user_memory = db.get_user_memory(user_id, chat_id)
            api_key = user_memory.get('api_key')
            
            if not api_key:
                gaali = random.choice(SAVAGE_GAALIYAN)
                return FALLBACK_MESSAGES["API_KEY_MISSING"].format(gaali=gaali)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            translate_prompt = f"Translate this text to {target_lang}. Keep it natural and conversational: {text}"
            
            payload = {
                "model": user_memory.get('model', AVAILABLE_MODELS[0]),
                "messages": [
                    {"role": "user", "content": translate_prompt}
                ],
                "max_tokens": 200,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                response_json = response.json()
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    translation = response_json["choices"][0]["message"].get("content", "")
                    if translation:
                        return translation
            
            return f"Arre {random.choice(SAVAGE_GAALIYAN)}, translation nahi ho paaya. Try again later!"
        
        except Exception as e:
            logger.error(f"❌ Failed to translate: {e}")
            return f"Arre {random.choice(SAVAGE_GAALIYAN),} translation mein error aa gaya!"
    
    def summarize_text(self, user_id: int, chat_id: int, text: str) -> str:
        """Summarize long text"""
        try:
            user_memory = db.get_user_memory(user_id, chat_id)
            api_key = user_memory.get('api_key')
            
            if not api_key:
                gaali = random.choice(SAVAGE_GAALIYAN)
                return FALLBACK_MESSAGES["API_KEY_MISSING"].format(gaali=gaali)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            summarize_prompt = f"Summarize this text in 2-3 sentences in Hinglish: {text}"
            
            payload = {
                "model": user_memory.get('model', AVAILABLE_MODELS[0]),
                "messages": [
                    {"role": "user", "content": summarize_prompt}
                ],
                "max_tokens": 150,
                "temperature": 0.5
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                response_json = response.json()
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    summary = response_json["choices"][0]["message"].get("content", "")
                    if summary:
                        return summary
            
            return f"Arre {random.choice(SAVAGE_GAALIYAN)}, summarize nahi kar paaya. Text bahut bada hai kya!"
        
        except Exception as e:
            logger.error(f"❌ Failed to summarize: {e}")
            return f"Arre {random.choice(SAVAGE_GAALIYAN)}, summary mein error aa gaya!"

# Initialize AI handler
ai_handler = AIHandler()

if __name__ == "__main__":
    # Test AI handler
    print("🤖 Testing AI handler...")
    stats = ai_handler.get_stats()
    print(f"📊 AI stats: {stats}")
    print("✅ AI handler test complete!")
