#!/usr/bin/env python3
"""
Desktop Agent Launcher
Simple launcher for the desktop agent chat application
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_requirements():
    """Check if requirements are met"""
    try:
        import tkinter
        import sqlite3
        import json
        import threading
        import datetime
        import webbrowser
        return True
    except ImportError as e:
        messagebox.showerror("Missing Requirements", f"Missing required module: {e}")
        return False

def check_agent_files():
    """Check if agent files exist"""
    required_files = [
        "simple_agent_test.py",
        "desktop_agent_app.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        messagebox.showerror(
            "Missing Files", 
            f"Missing required files:\n" + "\n".join(missing_files)
        )
        return False
    
    return True

def show_startup_dialog():
    """Show startup options dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    result = messagebox.askyesnocancel(
        "🤖 Agent Chat Desktop Launcher",
        "How would you like to start the Agent Chat?\n\n" +
        "YES: Full Desktop Application (Recommended)\n" +
        "NO: Simple Agent Server Only\n" +
        "CANCEL: Exit"
    )
    
    root.destroy()
    return result

def launch_desktop_app():
    """Launch the full desktop application"""
    try:
        print("🚀 Launching Desktop Agent Chat Application...")
        subprocess.run([sys.executable, "desktop_agent_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch desktop app: {e}")
        return False
    except FileNotFoundError:
        print("❌ Desktop app file not found")
        return False
    
    return True

def launch_agent_server():
    """Launch just the agent server"""
    try:
        print("🚀 Launching Agent Server...")
        subprocess.run([sys.executable, "simple_agent_test.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch agent server: {e}")
        return False
    except FileNotFoundError:
        print("❌ Agent server file not found")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🤖 Desktop Agent Chat Launcher")
    print("=" * 40)
    print("🎯 Based on mixinproject repository")
    print()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        return 1
    
    # Check agent files
    if not check_agent_files():
        print("❌ Agent files check failed")
        return 1
    
    print("✅ All requirements met")
    print()
    
    # Show startup options if GUI available
    try:
        choice = show_startup_dialog()
        
        if choice is True:
            # Launch desktop app
            print("🖥️ Starting Desktop Application...")
            launch_desktop_app()
        elif choice is False:
            # Launch server only
            print("🌐 Starting Agent Server Only...")
            launch_agent_server()
        else:
            # User cancelled
            print("❌ Cancelled by user")
            return 0
            
    except Exception as e:
        # Fallback to console mode
        print(f"⚠️ GUI not available: {e}")
        print()
        print("Available options:")
        print("1. Desktop Application (full GUI)")
        print("2. Agent Server Only (web interface)")
        print("3. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == "1":
                    launch_desktop_app()
                    break
                elif choice == "2":
                    launch_agent_server()
                    break
                elif choice == "3":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)