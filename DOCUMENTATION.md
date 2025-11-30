# 📚 ULTIMATE GROUP KING BOT - COMPLETE DOCUMENTATION

## 📋 TABLE OF CONTENTS
1. [README](#readme)
2. [Installation Guide](#installation-guide)
3. [Commands List](#commands-list)
4. [Troubleshooting](#troubleshooting)
5. [Changelog](#changelog)
6. [Contributing](#contributing)
7. [Docker Deployment](#docker-deployment)

---

## 📖 README

### 🚀 ULTIMATE GROUP KING BOT

#### 👑 The World's Best Telegram Group Management Bot

![Bot Logo](https://img.shields.io/badge/Ultimate-Group%20King-blue?style=for-the-badge&logo=telegram)
![Version](https://img.shields.io/badge/Version-1.0-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

### 📋 FEATURES

#### 🎯 **200+ Commands**
- **Admin Commands**: ban, kick, mute, warn, promote, pin, delete, purge
- **AI Chat**: Intelligent chat with OpenRouter models
- **Group Management**: settings, welcome, rules, locks, filters
- **Task System**: 50+ tasks with EXP rewards
- **Fun & Games**: truth/dare, roll, coin, memes, jokes
- **Utilities**: weather, calc, search, QR, URL shortener

#### 💰 **Economy System**
- **Wallet Management**: Balance, transfer, deposit, withdraw
- **Payment Automation**: UPI links, Gmail verification
- **Store System**: Create stores, add items, buy products
- **Escrow Service**: Secure transactions between users

#### 🎮 **Entertainment**
- **162 Games**: Roulette, slots, dice, coin, number games
- **AI Features**: Chat, image generation, smart detection
- **Fun Commands**: Jokes, facts, memes, quotes
- **Interactive**: Polls, quizzes, contests

#### 🔧 **Advanced Features**
- **Smart Detection**: Detect commands without "/"
- **Database Integration**: SQLite/Supabase support
- **Error Handling**: Comprehensive error management
- **Modular Design**: Easy to extend and maintain

---

## 🛠️ INSTALLATION GUIDE

### 📋 Requirements
- Python 3.8+
- Telegram Bot Token
- OpenRouter API Key (for AI features)

### 📥 Installation Steps

1. **Clone the Repository**
```bash
git clone <repository-url>
cd chaos
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your tokens and keys
```

4. **Run the Bot**
```bash
python bot_launcher.py
```

### ⚙️ Configuration

#### Required Environment Variables
```env
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
DATABASE_URL=sqlite:///data/ultimate_bot.db
```

#### Optional Variables
```env
ADMIN_USERS=user_id1,user_id2
DEBUG_MODE=False
LOG_LEVEL=INFO
```

---

## 📋 COMMANDS LIST

### 👑 ADMIN COMMANDS
- `/ban [user] [reason]` - Ban a user
- `/kick [user] [reason]` - Kick a user
- `/mute [user] [duration]` - Mute a user
- `/promote [user]` - Promote to admin
- `/demote [user]` - Demote from admin
- `/warn [user] [reason]` - Warn a user
- `/unwarn [user]` - Remove warning
- `/pin [message]` - Pin a message
- `/unpin` - Unpin message
- `/delete` - Delete replied message
- `/purge [count]` - Delete multiple messages

### 💰 ECONOMY COMMANDS
- `/wallet` - Check wallet balance
- `/transfer [amount] [user]` - Send money
- `/deposit [amount]` - Add funds to wallet
- `/withdraw [amount]` - Withdraw funds
- `/balance` - Check balance
- `/viewstore` - View store items
- `/createstore` - Create a store
- `/additem` - Add item to store
- `/buyitem` - Buy item from store

### 🎮 ENTERTAINMENT
- `/games` - List available games
- `/play [game]` - Play a game
- `/roulette` - Play roulette
- `/slots` - Play slots
- `/dice` - Roll dice
- `/coin` - Flip coin
- `/joke` - Get a joke
- `/truth` - Truth or dare truth
- `/dare` - Truth or dare dare
- `/fact` - Get a random fact

### 🤖 AI COMMANDS
- `/ai [message]` - Chat with AI
- `/ask [question]` - Ask AI a question
- `/image [prompt]` - Generate image
- `/chat [message]` - Chat with AI
- `/detect` - Smart detection

### 🔧 UTILITY COMMANDS
- `/help` - Show help
- `/start` - Start bot
- `/ping` - Check bot status
- `/time` - Get current time
- `/calc [expression]` - Calculate expression
- `/weather [city]` - Get weather
- `/qr [text]` - Generate QR code
- `/shorten [url]` - Shorten URL

### 🎨 CUSTOM COMMANDS
- `/createcmd [name] [content]` - Create custom command
- `/deletecmd [name]` - Delete custom command
- `/listcmds` - List custom commands
- `/runcmd [name]` - Run custom command

---

## 🔧 TROUBLESHOOTING

### 🚨 Common Issues

#### 1. Bot Not Starting
**Problem**: Bot fails to start with import errors
**Solution**: 
- Check all required dependencies are installed
- Verify environment variables are set correctly
- Check database permissions

#### 2. Database Errors
**Problem**: Database connection or initialization errors
**Solution**:
- Ensure data directory exists and is writable
- Check database URL format
- Reinitialize database: `python database.py`

#### 3. Command Not Working
**Problem**: Commands return "not found" errors
**Solution**:
- Verify command handlers are registered in bot_launcher.py
- Check for syntax errors in command files
- Ensure all required modules are imported

#### 4. AI Features Not Working
**Problem**: AI commands fail or return errors
**Solution**:
- Verify OpenRouter API key is valid
- Check internet connection
- Ensure sufficient API credits

#### 5. Smart Detection Issues
**Problem**: Smart detection not working properly
**Solution**:
- Check smart_detection.py configuration
- Verify message handlers are properly registered
- Test with different message formats

### 🐛 Debug Mode
Enable debug mode for detailed logging:
```env
DEBUG_MODE=True
LOG_LEVEL=DEBUG
```

---

## 📅 CHANGELOG

### Version 1.0.0 (Latest)
- ✅ Complete bot system with 600+ commands
- ✅ Database integration with SQLite/Supabase
- ✅ Economy system with wallet and payments
- ✅ Entertainment system with 162 games
- ✅ AI integration with OpenRouter
- ✅ Smart detection for commands
- ✅ Error handling and logging
- ✅ Modular architecture

### Previous Versions
- Various beta releases and testing versions

---

## 🤝 CONTRIBUTING

### 📋 Contributing Guidelines

1. **Fork the Repository**
2. **Create a Feature Branch**
```bash
git checkout -b feature/new-feature
```

3. **Make Changes**
- Follow existing code style
- Add proper documentation
- Test your changes

4. **Submit Pull Request**
- Describe your changes
- Include screenshots if applicable
- Wait for review

### 🎯 Areas for Contribution
- Bug fixes
- New command features
- Documentation improvements
- Performance optimizations
- Translation support

### 📝 Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add comments for complex logic
- Include docstrings for functions

---

## 🐳 DOCKER DEPLOYMENT

### 📋 Docker Setup

#### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot_launcher.py"]
```

#### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: always
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./data:/app/data
```

#### 3. Deploy
```bash
docker-compose up -d
```

### 🔧 Environment Configuration
Create `.env` file with required variables:
```env
BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_api_key
DATABASE_URL=sqlite:///data/ultimate_bot.db
```

### 📊 Monitoring
- Check logs: `docker-compose logs bot`
- Monitor status: `docker-compose ps`
- Restart if needed: `docker-compose restart bot`

---

## 📞 SUPPORT

### 🆘 Getting Help
- **Telegram**: @nikhilmehra099
- **Issues**: Create GitHub issue
- **Discussions**: Join community chat

### 📚 Additional Resources
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [OpenRouter API Documentation](https://openrouter.ai/docs)

---

## 📄 LICENSE

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👑 CREDITS

**Author**: Nikhil Mehra (NikkuAi09)
**Version**: 1.0.0
**Created**: 2025
**Purpose**: Educational & Entertainment

---

⚠️ **DISCLAIMER**: This bot is for educational and entertainment purposes only. Use responsibly and comply with Telegram's Terms of Service.

---

🚀 **Thank you for using ULTIMATE GROUP KING BOT!** 🚀
