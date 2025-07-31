import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "agent-chat-secret-key-2025")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///agent_chat.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from agent_models import User
    return User.query.get(int(user_id))

# Import the agent chat bot
from agent_chat_bot import AgentChatBot

# Initialize the bot
agent_bot = AgentChatBot()
logging.info("🤖 Agent Chat Bot initialized for webhook handling")

# Main webhook route for the agent chat
@app.route('/agent-webhook', methods=['POST'])
def agent_webhook():
    """Agent Chat webhook - unified functionality"""
    try:
        update = request.get_json()
        if not update:
            return "OK", 200
        
        logging.info(f"📥 Agent webhook received update: {update.get('update_id', 'unknown')}")
        
        # Process message or callback query
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            logging.info(f"📝 Agent message from {chat_id}: {text}")
            
            if text == '/start':
                agent_bot.send_welcome_message(chat_id)
            elif text and len(text) > 0:
                # Handle text search with intelligent response
                agent_bot.handle_text_message(chat_id, text)
        
        elif 'callback_query' in update:
            # Handle button callbacks
            callback_query = update['callback_query']
            agent_bot.handle_callback_query(callback_query)
        
        return "OK", 200
        
    except Exception as e:
        logging.error(f"❌ Agent webhook error: {e}")
        return "ERROR", 500

# Health check route
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "agent-chat"})

# Main route
@app.route('/')
def index():
    return render_template('agent_index.html')

# Create database tables
with app.app_context():
    import agent_models
    db.create_all()
    logging.info("✅ Agent Chat database tables created")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)