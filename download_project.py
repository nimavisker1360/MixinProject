#!/usr/bin/env python3
"""
Project Download Helper
Creates a downloadable package of the agent chat project files
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_project_package():
    """Create a downloadable package of the project"""
    
    # Project files to include
    project_files = [
        # Core application files
        'simple_agent_test.py',
        'new_agent_app.py', 
        'agent_chat_bot.py',
        'agent_models.py',
        'agent_mixin_service.py',
        
        # Configuration files
        'requirements.txt',
        '.env.example',
        'deploy_agent.py',
        
        # Documentation
        'README_AGENT.md',
        'AGENT_CHAT_SUMMARY.md',
        'CURSOR_SETUP_GUIDE.md',
        
        # Templates
        'templates/agent_index.html',
        
        # Additional files
        'desktop_agent_app.py',
        'launch_desktop_agent.py'
    ]
    
    # Create project directory
    project_name = f"agent-chat-bot-{datetime.now().strftime('%Y%m%d')}"
    project_dir = f"/tmp/{project_name}"
    
    # Clean up existing directory
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
    
    os.makedirs(project_dir)
    os.makedirs(f"{project_dir}/templates", exist_ok=True)
    
    print(f"📦 Creating project package: {project_name}")
    print("=" * 50)
    
    # Copy files
    copied_files = []
    missing_files = []
    
    for file_path in project_files:
        source_path = file_path
        dest_path = os.path.join(project_dir, file_path)
        
        # Create destination directory if needed
        dest_dir = os.path.dirname(dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            copied_files.append(file_path)
            print(f"✅ Copied: {file_path}")
        else:
            missing_files.append(file_path)
            print(f"⚠️ Missing: {file_path}")
    
    # Create additional helpful files
    
    # Create .vscode/settings.json
    vscode_dir = os.path.join(project_dir, '.vscode')
    os.makedirs(vscode_dir, exist_ok=True)
    
    settings_json = '''{
    "python.defaultInterpreterPath": "./agent_venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "files.associations": {
        "*.py": "python"
    },
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}'''
    
    with open(os.path.join(vscode_dir, 'settings.json'), 'w') as f:
        f.write(settings_json)
    print("✅ Created: .vscode/settings.json")
    
    # Create .vscode/launch.json
    launch_json = '''{
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
}'''
    
    with open(os.path.join(vscode_dir, 'launch.json'), 'w') as f:
        f.write(launch_json)
    print("✅ Created: .vscode/launch.json")
    
    # Create startup script
    startup_script = '''#!/bin/bash
# Agent Chat Bot Startup Script for Cursor

echo "🚀 Starting Agent Chat Bot..."
echo "🎯 Based on mixinproject repository"

# Check if virtual environment exists
if [ ! -d "agent_venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv agent_venv
fi

# Activate virtual environment
source agent_venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env from template..."
    cp .env.example .env
    echo "❗ Please edit .env file with your API keys"
fi

# Start the agent
echo "🤖 Starting agent chat bot..."
python simple_agent_test.py
'''
    
    with open(os.path.join(project_dir, 'start.sh'), 'w') as f:
        f.write(startup_script)
    os.chmod(os.path.join(project_dir, 'start.sh'), 0o755)
    print("✅ Created: start.sh")
    
    # Create README for Cursor
    cursor_readme = '''# 🤖 Agent Chat Bot - Cursor Desktop Setup

## Quick Start

1. **Open this folder in Cursor Desktop App**
2. **Run setup**: `./start.sh` or follow steps below
3. **Manual setup**:
   ```bash
   python3 -m venv agent_venv
   source agent_venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   python simple_agent_test.py
   ```
4. **Access agent**: http://localhost:8000

## Files Overview

- `simple_agent_test.py` - Quick start agent (minimal dependencies)
- `new_agent_app.py` - Full Flask application
- `agent_chat_bot.py` - Core bot functionality
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `CURSOR_SETUP_GUIDE.md` - Detailed setup guide

## Based on mixinproject Repository

This agent chat maintains full compatibility with the original mixinproject structure while adding modern enhancements.

Happy coding! 🎯
'''
    
    with open(os.path.join(project_dir, 'README_CURSOR.md'), 'w') as f:
        f.write(cursor_readme)
    print("✅ Created: README_CURSOR.md")
    
    # Create zip file
    zip_path = f"/tmp/{project_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)
                zipf.write(file_path, arcname)
    
    print("\n" + "=" * 50)
    print(f"📦 Package created successfully!")
    print(f"📁 Directory: {project_dir}")
    print(f"📦 Zip file: {zip_path}")
    print(f"✅ Copied files: {len(copied_files)}")
    
    if missing_files:
        print(f"⚠️ Missing files: {len(missing_files)}")
        for file in missing_files:
            print(f"   - {file}")
    
    print("\n🎯 Next steps:")
    print("1. Download the zip file to your local machine")
    print("2. Extract it to a folder")
    print("3. Open the folder in Cursor Desktop App")
    print("4. Follow CURSOR_SETUP_GUIDE.md")
    
    return project_dir, zip_path

def list_project_files():
    """List all available project files"""
    print("📋 Available Project Files:")
    print("=" * 30)
    
    all_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.html', '.json', '.sh')):
                file_path = os.path.join(root, file)
                if not file_path.startswith('./.git') and not file_path.startswith('./agent_venv'):
                    all_files.append(file_path)
    
    for file_path in sorted(all_files):
        file_size = os.path.getsize(file_path)
        print(f"📄 {file_path:<30} ({file_size:,} bytes)")
    
    print(f"\n📊 Total: {len(all_files)} files")

if __name__ == "__main__":
    print("🤖 Agent Chat Bot - Project Package Creator")
    print("🎯 Based on mixinproject repository")
    print()
    
    try:
        list_project_files()
        print()
        create_project_package()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()