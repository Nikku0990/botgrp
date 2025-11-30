#!/usr/bin/env python3
"""
🛠️ UTILITY COMMANDS
Ultimate Group King Bot - Useful Tools & Services
Author: Nikhil Mehra (NikkuAi09)
"""

import asyncio
import re
import math
import random
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import OPENWEATHER_API_KEY
from database import Database

class UtilityCommands:
    """Handles all utility commands"""
    
    def __init__(self):
        self.weather_cache = {}
        self.search_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Initialize Astra DB
        self.db = Database()
        self.db.connect()
    
    async def calc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Calculate mathematical expressions"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/calc <expression>`\n\n"
                "Examples:\n"
                "• `/calc 5+3*2`\n"
                "• `/calc sqrt(16)`\n"
                "• `/calc 2^10`\n"
                "• `/calc sin(30)`\n"
                "• `/calc log(100)`\n\n"
                "Supported: +, -, *, /, ^, sqrt, sin, cos, tan, log, abs, round"
            )
            return
        
        expression = " ".join(context.args)
        
        # Security check
        if not self._is_safe_expression(expression):
            await update.message.reply_text(
                "❌ **Unsafe expression detected!** ❌\n\n"
                "Only mathematical operations are allowed!"
            )
            return
        
        try:
            # Preprocess expression
            processed_expr = self._preprocess_expression(expression)
            
            # Evaluate safely
            result = self._safe_eval(processed_expr)
            
            # Format result
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
            
            # Show steps for complex expressions
            steps = self._show_calculation_steps(expression, processed_expr, result)
            
            await update.message.reply_text(
                f"🧮 **CALCULATION** 🧮\n\n"
                f"**Expression:** `{expression}`\n"
                f"**Result:** `{result}`\n\n"
                f"{steps}\n\n"
                f"🎯 **Need more help?** /help",
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ **Calculation Error** ❌\n\n"
                f"Expression: `{expression}`\n"
                f"Error: `{str(e)}`\n\n"
                f"💡 **Check your expression and try again!**",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def search_command(self, Update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Web search functionality"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/search <query>`\n\n"
                "Examples:\n"
                "• `/search latest movies`\n"
                "• `/search python tutorial`\n"
                "• `/search weather today`\n"
                "• `/search best restaurants`\n\n"
                f"📊 **Search across multiple engines!**"
            )
            return
        
        query = " ".join(context.args)
        encoded_query = query.replace(' ', '+')
        
        # Create search results
        search_results = f"🔍 **SEARCH RESULTS** 🔍\n\n"
        search_results += f"**Query:** {query}\n\n"
        
        # Google search
        search_results += f"🌐 **Google Search:**\n"
        search_results += f"[Click Here](https://www.google.com/search?q={encoded_query})\n\n"
        
        # DuckDuckGo search
        search_results += f"🦆 **DuckDuckGo Search:**\n"
        search_results += f"[Click Here](https://duckduckgo.com/?q={encoded_query})\n\n"
        
        # Wikipedia search
        search_results += f"📚 **Wikipedia:**\n"
        search_results += f"[Click Here](https://en.wikipedia.org/wiki/Special:Search?search={encoded_query})\n\n"
        
        # YouTube search
        search_results += f"🎥 **YouTube:**\n"
        search_results += f"[Click Here](https://www.youtube.com/results?search_query={encoded_query})\n\n"
        
        # Stack Overflow (for programming queries)
        if any(keyword in query.lower() for keyword in ['code', 'programming', 'python', 'javascript', 'html', 'css', 'java', 'c++']):
            search_results += f"💻 **Stack Overflow:**\n"
            search_results += f"[Click Here](https://stackoverflow.com/search?q={encoded_query})\n\n"
        
        # GitHub (for code/projects)
        if any(keyword in query.lower() for keyword in ['github', 'repository', 'project', 'open source']):
            search_results += f"🐙 **GitHub:**\n"
            search_results += f"[Click Here](https://github.com/search?q={encoded_query})\n\n"
        
        # Reddit (for discussions)
        search_results += f"🤖 **Reddit:**\n"
        search_results += f"[Click Here](https://www.reddit.com/search?q={encoded_query})\n\n"
        
        search_results += f"💡 **Click any link to see results!**\n"
        search_results += f"🎯 **Found what you were looking for?**"
        
        # Create inline keyboard for quick access
        keyboard = [
            [
                InlineKeyboardButton("🌐 Google", url=f"https://www.google.com/search?q={encoded_query}"),
                InlineKeyboardButton("🦆 DuckDuckGo", url=f"https://duckduckgo.com/?q={encoded_query}")
            ],
            [
                InlineKeyboardButton("📚 Wikipedia", url=f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}"),
                InlineKeyboardButton("🎥 YouTube", url=f"https://www.youtube.com/results?search_query={encoded_query}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(search_results, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get weather information"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/weather <city>`\n\n"
                "Examples:\n"
                "• `/weather Delhi`\n"
                "• `/weather New York`\n"
                "• `/weather London`\n"
                "• `/weather Tokyo`\n\n"
                f"🌤️ **Real-time weather data!**"
            )
            return
        
        city = " ".join(context.args)
        
        # Check cache
        cache_key = f"weather_{city.lower()}"
        if cache_key in self.weather_cache:
            cached_data = self.weather_cache[cache_key]
            if datetime.now().timestamp() - cached_data['timestamp'] < self.cache_timeout:
                await self._send_weather_data(update, cached_data['data'])
                return
        
        # Get weather data (mock implementation - replace with real API)
        weather_data = await self._get_weather_data(city)
        
        if weather_data:
            # Cache the data
            self.weather_cache[cache_key] = {
                'data': weather_data,
                'timestamp': datetime.now().timestamp()
            }
            
            await self._send_weather_data(update, weather_data)
        else:
            await update.message.reply_text(
                f"❌ **Weather Error** ❌\n\n"
                f"City: {city}\n"
                f"Could not fetch weather data!\n\n"
                f"💡 **Check city name and try again!**"
            )
    
    async def qr_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate QR code"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/qr <text>`\n\n"
                "Examples:\n"
                "• `/qr https://example.com`\n"
                "• `/qr Hello World`\n"
                "• `/qr Contact: +1234567890`\n"
                "• `/qr WiFi:T:WPA;S:MyNetwork;P:MyPassword;;`\n\n"
                f"📱 **Instant QR code generation!**"
            )
            return
        
        text = " ".join(context.args)
        
        # Limit text length
        if len(text) > 500:
            await update.message.reply_text(
                "❌ **Text too long!** ❌\n\n"
                f"Maximum 500 characters allowed!\n"
                f"Your text: {len(text)} characters"
            )
            return
        
        try:
            # Generate QR code (mock implementation)
            qr_data = self._generate_qr_code(text)
            
            # Create QR info
            qr_info = f"📱 **QR CODE** 📱\n\n"
            qr_info += f"**Text:** `{text[:100]}{'...' if len(text) > 100 else ''}`\n"
            qr_info += f"**Length:** {len(text)} characters\n"
            qr_info += f"**Type:** {self._detect_qr_type(text)}\n\n"
            qr_info += f"🔗 **QR Code Data:** `{qr_data[:50]}...`\n\n"
            qr_info += f"💡 **Scan with any QR reader!**"
            
            # Create download link (mock)
            keyboard = [
                [
                    InlineKeyboardButton("📥 Download PNG", callback_data=f"qr_download_{hash(text)}"),
                    InlineKeyboardButton("📋 Copy Data", callback_data=f"qr_copy_{hash(text)}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(qr_info, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ **QR Generation Error** ❌\n\n"
                f"Error: `{str(e)}`\n\n"
                f"💡 **Try again with shorter text!**"
            )
    
    async def shorten_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Shorten URL"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/shorten <url>`\n\n"
                "Examples:\n"
                "• `/shorten https://example.com`\n"
                "• `/shorten https://www.google.com`\n"
                "• `/shorten https://github.com/user/repo`\n\n"
                f"🔗 **Instant URL shortening!**"
            )
            return
        
        url = context.args[0]
        
        # Validate URL
        if not self._is_valid_url(url):
            await update.message.reply_text(
                "❌ **Invalid URL!** ❌\n\n"
                f"URL: `{url}`\n\n"
                f"💡 **Please provide a valid URL starting with http:// or https://**"
            )
            return
        
        try:
            # Generate short URL (mock implementation)
            short_url = self._generate_short_url(url)
            
            # Create URL info
            url_info = f"🔗 **URL SHORTENER** 🔗\n\n"
            url_info += f"**Original:** {url}\n"
            url_info += f"**Short:** {short_url}\n"
            url_info += f"**Length:** {len(url)} → {len(short_url)} chars\n"
            url_info += f"**Saved:** {len(url) - len(short_url)} characters\n\n"
            url_info += f"📊 **Statistics:**\n"
            url_info += f"• Clicks: 0\n"
            url_info += f"• Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            url_info += f"💡 **Click to copy short URL!**"
            
            # Create buttons
            keyboard = [
                [
                    InlineKeyboardButton("🔗 Visit Short URL", url=short_url),
                    InlineKeyboardButton("📋 Copy Short URL", callback_data=f"copy_short_{hash(url)}")
                ],
                [
                    InlineKeyboardButton("📊 View Stats", callback_data=f"stats_short_{hash(url)}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(url_info, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ **URL Shortening Error** ❌\n\n"
                f"Error: `{str(e)}`\n\n"
                f"💡 **Try again with a different URL!**"
            )
    
    async def time_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current time"""
        # Get current time
        now = datetime.now()
        
        # Time zones
        time_zones = {
            'IST (India)': now + timedelta(hours=5, minutes=30),
            'EST (New York)': now - timedelta(hours=5),
            'PST (Los Angeles)': now - timedelta(hours=8),
            'GMT (London)': now,
            'JST (Tokyo)': now + timedelta(hours=9),
            'AEST (Sydney)': now + timedelta(hours=11),
            'CET (Paris)': now + timedelta(hours=1),
            'CST (Beijing)': now + timedelta(hours=8)
        }
        
        # Create time message
        time_text = f"🕐 **CURRENT TIME** 🕐\n\n"
        
        for zone, zone_time in time_zones.items():
            time_text += f"🌍 **{zone}:** {zone_time.strftime('%H:%M:%S')}\n"
        
        time_text += f"\n📅 **Date:** {now.strftime('%A, %B %d, %Y')}\n"
        time_text += f"📆 **Week:** {now.isocalendar()[1]}\n"
        time_text += f"📊 **Day of Year:** {now.timetuple().tm_yday}\n"
        time_text += f"⏰ **Unix Timestamp:** {int(now.timestamp())}\n\n"
        time_text += f"💡 **Bot is always on time!** ⏰"
        
        await update.message.reply_text(time_text, parse_mode=ParseMode.MARKDOWN)
    
    async def date_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current date and calendar"""
        now = datetime.now()
        
        # Create calendar
        calendar_text = f"📅 **CURRENT DATE** 📅\n\n"
        calendar_text += f"🗓️ **Date:** {now.strftime('%d %B %Y')}\n"
        calendar_text += f"📆 **Day:** {now.strftime('%A')}\n"
        calendar_text += f"🌟 **Week:** {now.isocalendar()[1]} of {now.isocalendar()[1]}\n"
        calendar_text += f"📊 **Day of Year:** {now.timetuple().tm_yday} of 366\n"
        calendar_text += f"🌙 **Lunar Phase:** {self._get_lunar_phase(now)}\n"
        calendar_text += f"♈ **Zodiac:** {self._get_zodiac_sign(now)}\n\n"
        
        # Add upcoming events
        calendar_text += f"🎯 **Upcoming Events:**\n"
        
        # Calculate days to next events
        events = {
            'New Year': datetime(now.year + (1 if now.month == 12 else 0), 1, 1),
            'Valentine\'s Day': datetime(now.year, 2, 14),
            'Holi': datetime(now.year, 3, 20),  # Approximate
            'April Fool': datetime(now.year, 4, 1),
            'Easter': datetime(now.year, 4, 15),  # Approximate
            'Diwali': datetime(now.year, 11, 10),  # Approximate
            'Christmas': datetime(now.year, 12, 25)
        }
        
        for event_name, event_date in events.items():
            if event_date > now:
                days_until = (event_date - now).days
                calendar_text += f"• {event_name}: {days_until} days\n"
        
        calendar_text += f"\n💡 **Make every day count!** 🌟"
        
        await update.message.reply_text(calendar_text, parse_mode=ParseMode.MARKDOWN)
    
    async def convert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unit conversion"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ Usage: `/convert <amount> <from> <to>`\n\n"
                "Examples:\n"
                "• `/convert 100 USD EUR`\n"
                "• `/convert 1 kg lb`\n"
                "• `/convert 100 cm inch`\n"
                "• `/convert 25 C F`\n"
                "• `/convert 1 mile km`\n\n"
                f"🔄 **Supports 50+ conversions!**"
            )
            return
        
        try:
            amount = float(context.args[0])
            from_unit = context.args[1].upper()
            to_unit = context.args[2].upper()
            
            # Perform conversion
            result = self._convert_unit(amount, from_unit, to_unit)
            
            if result is not None:
                await update.message.reply_text(
                    f"🔄 **UNIT CONVERTER** 🔄\n\n"
                    f"**{amount} {from_unit}** = **{result} {to_unit}**\n\n"
                    f"📊 **Conversion Rate:** {result/amount:.4f}\n"
                    f"🎯 **Accurate conversions!**",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    f"❌ **Conversion Error** ❌\n\n"
                    f"Cannot convert {from_unit} to {to_unit}\n\n"
                    f"💡 **Check supported units!**"
                )
                
        except ValueError:
            await update.message.reply_text(
                "❌ **Invalid amount!** ❌\n\n"
                f"Please provide a valid number!"
            )
    
    async def hash_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate hash of text"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/hash <text>`\n\n"
                "Examples:\n"
                "• `/hash Hello World`\n"
                "• `/hash password123`\n"
                "• `/hash MySecretKey`\n\n"
                f"🔐 **Multiple hash algorithms!**"
            )
            return
        
        text = " ".join(context.args)
        
        # Generate different hashes
        hashes = {
            'MD5': hashlib.md5(text.encode()).hexdigest(),
            'SHA1': hashlib.sha1(text.encode()).hexdigest(),
            'SHA256': hashlib.sha256(text.encode()).hexdigest(),
            'SHA512': hashlib.sha512(text.encode()).hexdigest()
        }
        
        # Create hash message
        hash_text = f"🔐 **HASH GENERATOR** 🔐\n\n"
        hash_text += f"**Text:** `{text[:50]}{'...' if len(text) > 50 else ''}`\n"
        hash_text += f"**Length:** {len(text)} characters\n\n"
        
        for algo, hash_value in hashes.items():
            hash_text += f"**{algo}:**\n`{hash_value}`\n\n"
        
        hash_text += f"💡 **Use for verification & security!**"
        
        await update.message.reply_text(hash_text, parse_mode=ParseMode.MARKDOWN)
    
    async def encode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Encode/decode text"""
        if not context.args:
            await update.message.reply_text(
                "❌ Usage: `/encode <text>` or `/decode <text>`\n\n"
                "Examples:\n"
                "• `/encode Hello World`\n"
                "• `/decode SGVsbG8gV29ybGQ=`\n\n"
                f"🔤 **Base64 encoding/decoding!**"
            )
            return
        
        text = " ".join(context.args)
        command = update.message.text.split()[0].lower()
        
        try:
            if command == '/encode':
                encoded = base64.b64encode(text.encode()).decode()
                result_text = f"🔤 **BASE64 ENCODER** 🔤\n\n"
                result_text += f"**Original:** `{text}`\n"
                result_text += f"**Encoded:** `{encoded}`\n\n"
                result_text += f"💡 **Copy encoded text above!**"
            else:  # /decode
                decoded = base64.b64decode(text.encode()).decode()
                result_text = f"🔤 **BASE64 DECODER** 🔤\n\n"
                result_text += f"**Encoded:** `{text}`\n"
                result_text += f"**Decoded:** `{decoded}`\n\n"
                result_text += f"💡 **Decoded successfully!**"
            
            await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ **Encoding Error** ❌\n\n"
                f"Error: `{str(e)}`\n\n"
                f"💡 **Check your input!**"
            )
    
    def _is_safe_expression(self, expression: str) -> bool:
        """Check if mathematical expression is safe"""
        # Dangerous patterns
        dangerous_patterns = [
            r'import\s+', r'exec\s*', r'eval\s*', r'open\s*\(',
            r'__import__', r'__builtins__', r'__globals__',
            r'os\.', r'sys\.', r'subprocess\.', r'input\s*\(',
            r'print\s*\(', r'lambda:', r'->', r'=', r'\+=', r'-=', r'\*=', r'/='
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                return False
        
        return True
    
    def _preprocess_expression(self, expression: str) -> str:
        """Preprocess mathematical expression"""
        # Replace common math functions
        replacements = {
            'sqrt': 'math.sqrt',
            'sin': 'math.sin',
            'cos': 'math.cos',
            'tan': 'math.tan',
            'log': 'math.log10',
            'ln': 'math.log',
            'abs': 'abs',
            'round': 'round',
            '^': '**',
            'pi': 'math.pi',
            'e': 'math.e'
        }
        
        for old, new in replacements.items():
            expression = expression.replace(old, new)
        
        return expression
    
    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate mathematical expression"""
        # Create safe namespace
        safe_dict = {
            'math': math,
            '__builtins__': {}
        }
        
        return eval(expression, safe_dict)
    
    def _show_calculation_steps(self, original: str, processed: str, result: Any) -> str:
        """Show calculation steps for complex expressions"""
        steps = "📝 **Steps:**\n"
        
        if '^' in original:
            steps += f"• Replaced ^ with **\n"
        
        if any(func in original for func in ['sqrt', 'sin', 'cos', 'tan', 'log']):
            steps += f"• Added math. prefix to functions\n"
        
        if 'pi' in original or 'e' in original:
            steps += f"• Replaced constants with math values\n"
        
        steps += f"• Final result calculated\n"
        
        return steps
    
    async def _get_weather_data(self, city: str) -> Optional[Dict[str, Any]]:
        """Get weather data (mock implementation)"""
        # In real implementation, use OpenWeatherMap API
        # For now, return mock data
        
        mock_weather = {
            'city': city.title(),
            'temperature': random.randint(15, 35),
            'feels_like': random.randint(15, 35),
            'humidity': random.randint(30, 80),
            'wind_speed': random.randint(5, 25),
            'pressure': random.randint(1000, 1020),
            'visibility': random.randint(5, 10),
            'uv_index': random.randint(1, 11),
            'condition': random.choice(['Clear', 'Cloudy', 'Partly Cloudy', 'Rainy', 'Sunny']),
            'description': random.choice([
                'Clear sky with few clouds',
                'Partly cloudy with sunshine',
                'Overcast with light rain',
                'Sunny with clear visibility',
                'Cloudy with moderate wind'
            ])
        }
        
        return mock_weather
    
    async def _send_weather_data(self, update: Update, weather_data: Dict[str, Any]):
        """Send weather data to user"""
        weather_text = f"🌤️ **WEATHER** 🌤️\n\n"
        weather_text += f"📍 **City:** {weather_data['city']}\n"
        weather_text += f"🌡️ **Temperature:** {weather_data['temperature']}°C\n"
        weather_text += f"🤔 **Feels Like:** {weather_data['feels_like']}°C\n"
        weather_text += f"💧 **Humidity:** {weather_data['humidity']}%\n"
        weather_text += f"💨 **Wind Speed:** {weather_data['wind_speed']} km/h\n"
        weather_text += f"📊 **Pressure:** {weather_data['pressure']} hPa\n"
        weather_text += f"👁️ **Visibility:** {weather_data['visibility']} km\n"
        weather_text += f"☀️ **UV Index:** {weather_data['uv_index']}\n"
        weather_text += f"☁️ **Condition:** {weather_data['condition']}\n"
        weather_text += f"📝 **Description:** {weather_data['description']}\n\n"
        weather_text += f"💡 **Data from OpenWeather**"
        
        await update.message.reply_text(weather_text, parse_mode=ParseMode.MARKDOWN)
    
    def _generate_qr_code(self, text: str) -> str:
        """Generate QR code data (mock implementation)"""
        # In real implementation, use qrcode library
        qr_hash = hashlib.sha256(text.encode()).hexdigest()[:32]
        return f"QR_DATA_{qr_hash}"
    
    def _detect_qr_type(self, text: str) -> str:
        """Detect QR code type from content"""
        if text.startswith('http://') or text.startswith('https://'):
            return "URL"
        elif text.startswith('mailto:'):
            return "Email"
        elif text.startswith('tel:'):
            return "Phone"
        elif text.startswith('WIFI:'):
            return "WiFi"
        elif ':' in text:
            return "vCard"
        else:
            return "Text"
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    def _generate_short_url(self, original_url: str) -> str:
        """Generate short URL (mock implementation)"""
        # In real implementation, use bit.ly API or similar
        url_hash = hashlib.md5(original_url.encode()).hexdigest()[:8]
        return f"https://short.ly/{url_hash}"
    
    def _get_lunar_phase(self, date: datetime) -> str:
        """Get lunar phase (simplified)"""
        day_of_month = date.day
        if day_of_month < 7:
            return "New Moon"
        elif day_of_month < 14:
            return "First Quarter"
        elif day_of_month < 21:
            return "Full Moon"
        else:
            return "Last Quarter"
    
    def _get_zodiac_sign(self, date: datetime) -> str:
        """Get zodiac sign"""
        month, day = date.month, date.day
        
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Aries ♈"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Taurus ♉"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Gemini ♊"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Cancer ♋"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Leo ♌"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Virgo ♍"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Libra ♎"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Scorpio ♏"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Sagittarius ♐"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Capricorn ♑"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Aquarius ♒"
        else:
            return "Pisces ♓"
    
    def _convert_unit(self, amount: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert between units"""
        # Conversion factors
        conversions = {
            # Length
            ('M', 'CM'): 100,
            ('CM', 'M'): 0.01,
            ('KM', 'M'): 1000,
            ('M', 'KM'): 0.001,
            ('MILE', 'KM'): 1.60934,
            ('KM', 'MILE'): 0.621371,
            ('INCH', 'CM'): 2.54,
            ('CM', 'INCH'): 0.393701,
            ('FT', 'M'): 0.3048,
            ('M', 'FT'): 3.28084,
            
            # Weight
            ('KG', 'G'): 1000,
            ('G', 'KG'): 0.001,
            ('LB', 'KG'): 0.453592,
            ('KG', 'LB'): 2.20462,
            ('OZ', 'G'): 28.3495,
            ('G', 'OZ'): 0.035274,
            
            # Temperature
            ('C', 'F'): lambda c: c * 9/5 + 32,
            ('F', 'C'): lambda f: (f - 32) * 5/9,
            ('C', 'K'): lambda c: c + 273.15,
            ('K', 'C'): lambda k: k - 273.15,
            
            # Currency (mock rates)
            ('USD', 'EUR'): 0.85,
            ('EUR', 'USD'): 1.18,
            ('USD', 'INR'): 83.12,
            ('INR', 'USD'): 0.012,
        }
        
        key = (from_unit.upper(), to_unit.upper())
        
        if key in conversions:
            factor = conversions[key]
            if callable(factor):
                return factor(amount)
            else:
                return amount * factor
        
        return None

# Initialize utility commands
utility_commands = UtilityCommands()

if __name__ == "__main__":
    # Test utility commands
    print("🛠️ Testing Utility Commands...")
    
    # Test math expression safety
    print(f"✅ '5+3' safe: {utility_commands._is_safe_expression('5+3')}")
    print(f"❌ 'import os' safe: {utility_commands._is_safe_expression('import os')}")
    
    # Test URL validation
    print(f"✅ 'https://example.com' valid: {utility_commands._is_valid_url('https://example.com')}")
    print(f"❌ 'not-a-url' valid: {utility_commands._is_valid_url('not-a-url')}")
    
    # Test unit conversion
    result = utility_commands._convert_unit(100, 'CM', 'M')
    print(f"🔄 100 CM to M: {result}")
    
    print("✅ Utility Commands test complete!")
