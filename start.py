#!/usr/bin/env python3
"""
Nova AI Friend - Startup Script
This script starts the Flask backend and serves the frontend files.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import threading
import time
from flask import Flask, send_from_directory, render_template_string
from werkzeug.serving import make_server
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import openai
        import matplotlib
        import numpy
        logger.info("✅ All dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path('.env')
    if not env_path.exists():
        logger.warning("⚠️  .env file not found")
        logger.info("Creating .env file with template...")
        create_env_template()
        return False
    
    # Check for OpenAI API key
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            logger.warning("⚠️  OpenAI API key not configured")
            logger.info("Please add your OpenAI API key to the .env file")
            return False
        logger.info("✅ Environment configuration looks good")
        return True
    except Exception as e:
        logger.error(f"❌ Error checking environment: {e}")
        return False

def create_env_template():
    """Create a template .env file."""
    template = """# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=nova-ai-friend-secret-key-change-this

# Database Configuration
DATABASE_URL=sqlite:///ai_friend.db

# Application Configuration
APP_NAME=Nova AI Friend
APP_VERSION=1.0.0
APP_HOST=localhost
APP_PORT=5000
"""
    
    with open('.env', 'w') as f:
        f.write(template)
    logger.info("📝 Created .env template file")

def create_simple_server():
    """Create a simple Flask server to serve the frontend files."""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        try:
            with open('index.html', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Frontend files not found. Please ensure index.html exists."
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        return send_from_directory('.', filename)
    
    return app

def start_backend():
    """Start the Flask backend server."""
    try:
        logger.info("🚀 Starting Nova AI Friend backend...")
        # Import the main app after environment is set up
        from app import app
        
        # Create a server that can be shut down
        server = make_server('localhost', 5000, app, threaded=True)
        logger.info("🎯 Backend server started on http://localhost:5000")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        sys.exit(1)

def start_frontend():
    """Start the frontend server."""
    try:
        logger.info("🌐 Starting Nova AI Friend frontend...")
        frontend_app = create_simple_server()
        
        # Start frontend on a different port
        server = make_server('localhost', 3000, frontend_app, threaded=True)
        logger.info("🎨 Frontend server started on http://localhost:3000")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Failed to start frontend: {e}")
        sys.exit(1)

def open_browser():
    """Open the browser after a delay."""
    time.sleep(2)  # Wait for servers to start
    try:
        webbrowser.open('http://localhost:3000')
        logger.info("🌐 Opened browser to http://localhost:3000")
    except Exception as e:
        logger.warning(f"⚠️  Could not open browser automatically: {e}")
        logger.info("Please open your browser and navigate to http://localhost:3000")

def main():
    """Main function to start the application."""
    print("🤖 Nova AI Friend - Starting up...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_file():
        print("\n" + "=" * 50)
        print("⚠️  Setup Required:")
        print("1. Get your OpenAI API key from: https://platform.openai.com/")
        print("2. Add it to the .env file: OPENAI_API_KEY=your-actual-key-here")
        print("3. Run this script again")
        print("=" * 50)
        sys.exit(1)
    
    print("\n🚀 Starting Nova AI Friend...")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("\n✅ Nova AI Friend is running!")
    print("🎯 Backend API: http://localhost:5000")
    print("🌐 Frontend: http://localhost:3000")
    print("=" * 50)
    print("💡 Tips:")
    print("   - Use voice input for natural conversation")
    print("   - Enable speech output for audio responses")
    print("   - Check the profile settings to customize your experience")
    print("   - Nova evolves as you interact with it!")
    print("=" * 50)
    print("Press Ctrl+C to stop the servers")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Nova AI Friend...")
        print("Thank you for using Nova! 🤖✨")
        sys.exit(0)

if __name__ == '__main__':
    main()