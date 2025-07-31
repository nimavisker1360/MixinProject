# 🖥️ Cursor Desktop App Setup Guide
## Agent Chat Bot Project - From mixinproject Repository

### 🎯 How to Access This Project in Cursor Desktop App

This guide will help you move this agent chat project from the current environment to your **Cursor Desktop Application** so you can work on it locally.

---

## 📂 Step 1: Download Project Files

### Option A: Download Individual Files
Copy these key files to your local machine:

**Core Application Files:**
- `simple_agent_test.py` - Working agent chat bot
- `new_agent_app.py` - Full Flask application  
- `agent_chat_bot.py` - Bot functionality
- `agent_models.py` - Database models
- `agent_mixin_service.py` - Mixin API integration

**Configuration Files:**
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `deploy_agent.py` - Deployment script

**Templates:**
- `templates/agent_index.html` - Web interface

**Documentation:**
- `README_AGENT.md` - Complete setup guide
- `AGENT_CHAT_SUMMARY.md` - Project overview

### Option B: Clone/Download Repository
If this is in a Git repository, clone it:
```bash
git clone <repository-url>
cd agent-chat-project
```

---

## 🖥️ Step 2: Open in Cursor Desktop App

1. **Launch Cursor Desktop Application**
2. **Open Folder**: 
   - Click `File` → `Open Folder`
   - Select the folder containing your agent chat files
3. **Cursor will automatically detect** it's a Python project

---

## 🐍 Step 3: Python Environment Setup in Cursor

### Create Virtual Environment:
```bash
# In Cursor's integrated terminal:
python -m venv agent_venv
source agent_venv/bin/activate  # On Windows: agent_venv\Scripts\activate
```

### Install Dependencies:
```bash
pip install -r requirements.txt
```

### Set Environment Variables:
```bash
# Copy environment template
cp .env.example .env

# Edit .env file in Cursor and add your API keys:
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SERPAPI_API_KEY=your_serpapi_key
MIXIN_API_KEY=your_mixin_key
```

---

## 🚀 Step 4: Run Agent in Cursor

### Quick Start (Minimal Dependencies):
```bash
# In Cursor terminal:
python simple_agent_test.py
```
**Access at:** http://localhost:8000

### Full Application:
```bash
# In Cursor terminal:
python new_agent_app.py
```
**Access at:** http://localhost:5000

---

## ⚙️ Step 5: Cursor IDE Configuration

### Recommended Cursor Extensions:
- **Python** - Python language support
- **Pylance** - Python IntelliSense
- **Python Docstring Generator** - Auto-generate docstrings
- **SQLite Viewer** - View agent database
- **Thunder Client** - Test API endpoints

### Cursor Workspace Settings:
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./agent_venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "files.associations": {
        "*.py": "python"
    },
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

---

## 🔧 Step 6: Development Workflow in Cursor

### File Structure in Cursor:
```
agent-chat-project/
├── 📁 templates/           # Web interface templates
├── 📄 simple_agent_test.py # Quick start agent
├── 📄 new_agent_app.py     # Full Flask app
├── 📄 agent_chat_bot.py    # Core bot logic
├── 📄 agent_models.py      # Database models
├── 📄 requirements.txt     # Dependencies
├── 📄 .env                 # Your API keys
├── 📄 README_AGENT.md      # Documentation
└── 📄 simple_agent.db     # SQLite database (auto-created)
```

### Running Commands in Cursor:
1. **Open Terminal**: `Ctrl+`` (backtick)
2. **Run Agent**: `python simple_agent_test.py`
3. **Stop Agent**: `Ctrl+C` in terminal
4. **View Database**: Use SQLite Viewer extension

---

## 🌐 Step 7: Access Agent Interface

### Web Interface:
- **URL**: http://localhost:8000
- **Features**: Persian interface, product search, statistics
- **Health Check**: http://localhost:8000/health

### Telegram Integration:
1. **Create Bot**: Message @BotFather on Telegram
2. **Get Token**: Add to `.env` file
3. **Set Webhook**: 
   ```bash
   curl -F "url=https://your-domain.com/agent-webhook" \
        https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook
   ```

---

## 🛠️ Step 8: Customize and Develop

### Key Files to Edit in Cursor:

**🤖 Bot Functionality:**
- `agent_chat_bot.py` - Modify agent responses
- `agent_mixin_service.py` - Update Mixin API integration

**🌐 Web Interface:**
- `templates/agent_index.html` - Customize web UI
- `simple_agent_test.py` - Add new features

**💾 Database:**
- `agent_models.py` - Add new data models
- View data with SQLite Viewer extension

**⚙️ Configuration:**
- `.env` - API keys and settings
- `requirements.txt` - Python packages

---

## 🐛 Step 9: Debugging in Cursor

### Debug Configuration:
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Agent Chat Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/simple_agent_test.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Debug Features:
- **Breakpoints**: Click left margin in code
- **Variables**: Inspect values during debugging
- **Step Through**: F10 (step over), F11 (step into)
- **Debug Console**: Interact with running code

---

## 📊 Step 10: Monitor Agent Activity

### Database Inspection:
```sql
-- View users
SELECT * FROM users;

-- View search history  
SELECT * FROM search_history;

-- User activity stats
SELECT COUNT(*) as total_searches FROM search_history;
```

### Log Monitoring:
- **Cursor Terminal**: See real-time logs
- **Debug Console**: Inspect variables
- **HTTP Requests**: Monitor in browser dev tools

---

## 🚀 Step 11: Deploy from Cursor

### Local Development:
```bash
# Run locally
python simple_agent_test.py
```

### Production Deployment:
```bash
# Use deployment script
python deploy_agent.py

# Or manual deployment
gunicorn new_agent_app:app --bind 0.0.0.0:5000
```

---

## 🎯 Quick Commands Reference

### Essential Cursor Commands:
```bash
# Start agent
python simple_agent_test.py

# Install packages
pip install package_name

# View database
sqlite3 simple_agent.db ".tables"

# Test API
curl http://localhost:8000/health

# Check logs
tail -f agent.log
```

---

## 🔗 Integration with Original mixinproject

### Maintain Compatibility:
- **File Structure**: Follows original patterns
- **Database Models**: Compatible with original schema  
- **API Integration**: Uses same Mixin.ir approach
- **Deployment**: Similar VPS deployment strategy

### Migration from Original:
```python
# Import original data
from original_models import *
# Convert to new models
from agent_models import *
```

---

## 💡 Tips for Cursor Development

### Cursor AI Features:
- **Code Completion**: Cursor's AI suggests completions
- **Code Generation**: Ask Cursor to generate functions
- **Bug Fixes**: Let Cursor suggest fixes
- **Refactoring**: Use AI for code improvements

### Productivity Features:
- **Multiple Cursors**: `Ctrl+Alt+Down`
- **Command Palette**: `Ctrl+Shift+P`
- **File Search**: `Ctrl+P`
- **Symbol Search**: `Ctrl+Shift+O`

---

## 🎉 You're Ready!

Your agent chat bot project is now set up in **Cursor Desktop App**:

✅ **Local Development Environment**  
✅ **Full Python Project Structure**  
✅ **Integrated Terminal and Debugging**  
✅ **AI-Powered Code Assistance**  
✅ **Database and API Integration**  
✅ **Based on mixinproject Architecture**

**Start coding with**: `python simple_agent_test.py`  
**Access at**: http://localhost:8000

---

*🎯 Based on mixinproject repository structure*  
*🤖 Enhanced for Cursor Desktop App development*