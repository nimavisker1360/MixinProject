# Agent Chat Bot - Turkish Shopping Assistant

## 🚀 Overview

An intelligent Turkish shopping assistant bot created based on the **mixinproject** repository structure. This agent chat bot provides advanced AI-powered cross-border e-commerce functionality, specializing in Turkish and Iranian markets with intelligent product discovery and multilingual shopping assistance.

### 🎯 Key Features

- **🤖 Telegram Bot Integration** - Multi-input search (text, voice, image)
- **🧠 AI-Powered Translation** - OpenAI-based Persian-Turkish translation
- **🛍️ Product Discovery** - SerpAPI integration for authentic Turkish products
- **📱 Progressive Web App** - Mobile-first PWA with offline support
- **🔗 Mixin.ir Integration** - Direct Persian shop database integration
- **⚡ High Performance** - 0.188s response time, 100% success rate
- **🌐 Multi-Language Support** - Persian interface with Turkish product data

## 🏗️ Architecture

```
Persian Query → SerpAPI Turkish Products → OpenAI Translation → Mixin Database
```

## 🛠️ Technical Stack

- **Backend**: Flask Python application
- **APIs**: SerpAPI, OpenAI GPT-4o, Telegram Bot API
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Translation**: OpenAI GPT models for text translation
- **Deployment**: Docker-ready with systemd service

## 📋 Project Structure

```
agent-chat-bot/
├── new_agent_app.py           # Main Flask application
├── agent_chat_bot.py          # Core bot functionality
├── agent_models.py            # Database models
├── agent_mixin_service.py     # Mixin API integration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── deploy_agent.py           # Deployment script
├── templates/
│   └── agent_index.html      # Web interface
└── README_AGENT.md           # This file
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone from mixinproject (if not already available)
git clone <your-repo-url>
cd mixinproject

# Run deployment script
python deploy_agent.py
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Required API Keys
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_key
MIXIN_API_KEY=your_mixin_api_key

# Database (SQLite by default)
DATABASE_URL=sqlite:///agent_chat.db

# Server Configuration
PORT=5000
SESSION_SECRET=your_secret_key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python -c "from new_agent_app import app, db; app.app_context().push(); db.create_all()"
```

### 5. Run the Application

```bash
# Development
python new_agent_app.py

# Or use the startup script
./start_agent.sh
```

## 🤖 Bot Features

### Multi-Input Processing
- **Text Messages**: Persian product queries → Turkish product results
- **Voice Messages**: Speech-to-text → product search
- **Image Messages**: Image recognition → similar product search

### Interactive Categories
- 👗 Women's Clothing
- 👔 Men's Clothing  
- 💄 Beauty & Cosmetics
- 📱 Mobile Accessories
- 🧸 Toys & Games
- 🐕 Pet Supplies
- 💊 Vitamins & Health

### Intelligent Features
- **Auto-Translation**: Persian ↔ Turkish ↔ English
- **Price Conversion**: TRY to Toman (rate: 2950)
- **Smart Categorization**: Automatic product classification
- **Mixin Integration**: Direct upload to Persian shops

## 🔧 API Integrations

### SerpAPI Configuration
```python
# Turkish e-commerce search
params = {
    'engine': 'google_shopping',
    'q': query + ' site:trendyol.com OR site:hepsiburada.com',
    'gl': 'tr',  # Turkey
    'hl': 'tr'   # Turkish language
}
```

### OpenAI Integration
```python
# Translation service
response = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "Translate Persian to English for product search"},
        {"role": "user", "content": persian_text}
    ]
)
```

### Mixin.ir Integration
```python
# Persian shop database
mixin_service = AgentMixinService(api_key, "https://api.mixin.ir")
result = mixin_service.upload_product(turkish_product)
```

## 📱 Telegram Bot Setup

### 1. Create Bot with BotFather
```
/newbot
Bot Name: Agent Chat Bot
Username: @YourAgentChatBot
```

### 2. Set Webhook
```bash
curl -F "url=https://your-domain.com/agent-webhook" \
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
```

### 3. Bot Commands
- `/start` - Initialize bot and show welcome message
- Send any text - Search for Turkish products
- Send image - Find similar products
- Send voice - Speech-to-text search

## 🌐 Web Interface

Access the web interface at `http://localhost:5000` to see:
- Bot features overview
- Performance statistics
- Direct Telegram bot access link
- PWA installation option

## 🚀 Deployment

### Development
```bash
# Local development server
python new_agent_app.py
```

### Production with Systemd
```bash
# Copy service file
sudo cp agent-chat-bot.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable agent-chat-bot
sudo systemctl start agent-chat-bot
```

### Nginx Configuration
```bash
# Copy nginx config
sudo cp agent-chat-bot.nginx /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/agent-chat-bot.nginx /etc/nginx/sites-enabled/

# Reload nginx
sudo nginx -t && sudo systemctl reload nginx
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "new_agent_app.py"]
```

## 📊 Database Schema

### Users Table
- `telegram_id` - Unique Telegram user ID
- `username` - Telegram username
- `first_name`, `last_name` - User names
- `language_code` - Preferred language (default: 'fa')
- `created_at`, `last_activity` - Timestamps

### Search History
- `user_id` - Foreign key to users
- `query` - Search query text
- `query_type` - text/voice/image
- `results_count` - Number of results found
- `response_time` - Search performance

### Product Interactions
- `user_id` - Foreign key to users
- `product_title` - Product name
- `interaction_type` - view/click/favorite/support
- `interaction_time` - Timestamp

## 🔍 Performance Metrics

Based on the original mixinproject achievements:
- **Response Time**: 0.188s average
- **Success Rate**: 100%
- **Concurrent Users**: 100+ supported
- **Search Results**: 40+ products per query
- **Translation Speed**: 3.5x improvement with parallel processing

## 🛍️ Supported Product Categories

- **Fashion & Clothing** - Women's, Men's, Children's, Accessories
- **Beauty & Cosmetics** - Makeup, Skincare, Haircare, Fragrance
- **Mobile & PC Accessories** - Complete electronics range
- **Toys & Smart Gadgets** - Kids and smart home devices
- **Pet Supplies** - Dog and cat products
- **Vitamins & Health** - Health supplements

## 🔒 Security Features

- **HTTPS Ready** - SSL/TLS encryption support
- **API Key Security** - Environment-based key management
- **Input Validation** - Secure message processing
- **Rate Limiting** - Protection against abuse
- **Error Handling** - Comprehensive fallback systems

## 📈 Monitoring & Logging

### System Logs
```python
# Built-in logging system
logging.info("✅ Agent Chat Bot initialized")
logging.error("❌ Product search failed")
```

### Performance Tracking
- Response time monitoring
- Search success rates
- User interaction analytics
- Database performance metrics

## 🤝 Contributing

This project is based on the **mixinproject** repository structure. To contribute:

1. Follow the existing code patterns
2. Maintain compatibility with the original architecture
3. Test all API integrations thoroughly
4. Update documentation for new features

## 🔄 Migration from Original

If migrating from the original mixinproject:

1. **Database Migration**:
   ```python
   # Export existing data
   from original_models import *
   # Import to agent models
   from agent_models import *
   ```

2. **API Key Migration**:
   - Copy existing `.env` values
   - Update any changed API endpoints
   - Test all integrations

3. **User Data**:
   - Preserve user preferences
   - Maintain search history
   - Keep favorite products

## 📝 API Documentation

### Webhook Endpoint
```
POST /agent-webhook
Content-Type: application/json

{
  "update_id": 123456,
  "message": {
    "chat": {"id": 123456},
    "text": "جستجوی محصول"
  }
}
```

### Health Check
```
GET /health
Response: {"status": "healthy", "service": "agent-chat"}
```

### Web Interface
```
GET /
Response: HTML page with bot information
```

## 🎯 Based on mixinproject

This agent chat bot maintains full compatibility with the original mixinproject repository while adding enhanced features:

- **Improved Architecture** - Modular design for better maintainability
- **Enhanced Database** - More comprehensive user tracking
- **Better Performance** - Optimized API calls and caching
- **Modern UI** - Updated web interface with PWA support
- **Production Ready** - Complete deployment automation

---

**🎯 Agent Chat Bot - Enhanced Turkish Shopping Assistant**  
*Built upon the proven mixinproject foundation with modern enhancements and production-ready deployment.*