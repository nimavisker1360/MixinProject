#!/usr/bin/env python3
"""
Agent Chat Bot Deployment Script
Based on mixinproject repository deployment approach
"""

import os
import subprocess
import sys
import json
import time
from datetime import datetime

def log_info(message):
    """Log information message"""
    print(f"🔍 {datetime.now().strftime('%H:%M:%S')} - {message}")

def log_success(message):
    """Log success message"""
    print(f"✅ {datetime.now().strftime('%H:%M:%S')} - {message}")

def log_error(message):
    """Log error message"""
    print(f"❌ {datetime.now().strftime('%H:%M:%S')} - {message}")

def run_command(command, description=""):
    """Run a command and return success status"""
    try:
        if description:
            log_info(f"{description}")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            if description:
                log_success(f"{description} - Completed")
            return True
        else:
            log_error(f"Command failed: {command}")
            log_error(f"Error: {result.stderr}")
            return False
    except Exception as e:
        log_error(f"Exception running command: {e}")
        return False

def check_requirements():
    """Check if all requirements are met"""
    log_info("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        log_error("Python 3.8+ is required")
        return False
    
    log_success(f"Python {python_version.major}.{python_version.minor} found")
    
    # Check if pip is available
    if not run_command("pip --version", "Checking pip"):
        log_error("pip is required but not found")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    log_info("Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        return False
    
    log_success("Dependencies installed successfully")
    return True

def setup_environment():
    """Setup environment variables"""
    log_info("Setting up environment...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            # Copy example to .env
            if run_command("cp .env.example .env", "Creating .env from example"):
                log_info("Please edit .env file with your actual API keys")
            else:
                return False
        else:
            log_error(".env.example not found. Please create .env file manually")
            return False
    else:
        log_success(".env file already exists")
    
    return True

def setup_database():
    """Initialize database"""
    log_info("Setting up database...")
    
    try:
        # Import and initialize database
        from new_agent_app import app, db
        
        with app.app_context():
            db.create_all()
            log_success("Database tables created successfully")
        
        return True
    except Exception as e:
        log_error(f"Database setup failed: {e}")
        return False

def test_agent_bot():
    """Test agent bot initialization"""
    log_info("Testing agent bot initialization...")
    
    try:
        from agent_chat_bot import AgentChatBot
        
        # Create bot instance (without actual API calls)
        bot = AgentChatBot()
        log_success("Agent bot initialized successfully")
        return True
    except Exception as e:
        log_error(f"Agent bot test failed: {e}")
        return False

def create_systemd_service():
    """Create systemd service for production deployment"""
    log_info("Creating systemd service...")
    
    service_content = f"""[Unit]
Description=Agent Chat Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={os.getcwd()}
Environment=PATH={os.getcwd()}/venv/bin
ExecStart={sys.executable} new_agent_app.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    try:
        with open('agent-chat-bot.service', 'w') as f:
            f.write(service_content)
        
        log_success("Systemd service file created: agent-chat-bot.service")
        log_info("To install: sudo cp agent-chat-bot.service /etc/systemd/system/")
        log_info("Then run: sudo systemctl enable agent-chat-bot && sudo systemctl start agent-chat-bot")
        return True
    except Exception as e:
        log_error(f"Failed to create systemd service: {e}")
        return False

def create_nginx_config():
    """Create nginx configuration"""
    log_info("Creating nginx configuration...")
    
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /agent-webhook {
        proxy_pass http://127.0.0.1:5000/agent-webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    
    try:
        with open('agent-chat-bot.nginx', 'w') as f:
            f.write(nginx_config)
        
        log_success("Nginx config created: agent-chat-bot.nginx")
        log_info("To install: sudo cp agent-chat-bot.nginx /etc/nginx/sites-available/")
        log_info("Then run: sudo ln -s /etc/nginx/sites-available/agent-chat-bot.nginx /etc/nginx/sites-enabled/")
        return True
    except Exception as e:
        log_error(f"Failed to create nginx config: {e}")
        return False

def create_startup_script():
    """Create startup script for development"""
    log_info("Creating startup script...")
    
    startup_script = f"""#!/bin/bash
# Agent Chat Bot Startup Script

echo "🚀 Starting Agent Chat Bot..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
    echo "✅ Environment variables loaded"
fi

# Start the application
echo "🔥 Starting Flask application..."
python new_agent_app.py
"""
    
    try:
        with open('start_agent.sh', 'w') as f:
            f.write(startup_script)
        
        # Make executable
        os.chmod('start_agent.sh', 0o755)
        
        log_success("Startup script created: start_agent.sh")
        return True
    except Exception as e:
        log_error(f"Failed to create startup script: {e}")
        return False

def main():
    """Main deployment function"""
    print("🤖 Agent Chat Bot Deployment Script")
    print("=" * 50)
    
    # Step 1: Check requirements
    if not check_requirements():
        log_error("Requirements check failed")
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies():
        log_error("Dependencies installation failed")
        sys.exit(1)
    
    # Step 3: Setup environment
    if not setup_environment():
        log_error("Environment setup failed")
        sys.exit(1)
    
    # Step 4: Setup database
    if not setup_database():
        log_error("Database setup failed")
        sys.exit(1)
    
    # Step 5: Test agent bot
    if not test_agent_bot():
        log_error("Agent bot test failed")
        sys.exit(1)
    
    # Step 6: Create deployment files
    create_systemd_service()
    create_nginx_config()
    create_startup_script()
    
    print("\n" + "=" * 50)
    log_success("Agent Chat Bot deployment completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your actual API keys")
    print("2. For development: ./start_agent.sh")
    print("3. For production: Setup systemd service and nginx")
    print("4. Set your Telegram webhook URL to: https://your-domain.com/agent-webhook")
    print("\n🎯 Based on mixinproject repository structure")

if __name__ == "__main__":
    main()