#!/usr/bin/env python3
"""
Simple run script for Nova AI Friend
This script starts just the Flask backend server.
"""

import os
import sys
from pathlib import Path

def check_env():
    """Check if environment is set up correctly."""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your-openai-api-key-here")
        return False
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            print("❌ OpenAI API key not configured!")
            print("Please add your API key to the .env file")
            return False
        
        print("✅ Environment configuration looks good")
        return True
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error checking environment: {e}")
        return False

def main():
    """Main function to run the Flask app."""
    print("🤖 Nova AI Friend - Backend Server")
    print("=" * 40)
    
    if not check_env():
        sys.exit(1)
    
    try:
        from app import app
        print("🚀 Starting Flask backend server...")
        print("🎯 Backend API: http://localhost:5000")
        print("🌐 Frontend: Open index.html in your browser")
        print("=" * 40)
        print("Press Ctrl+C to stop the server")
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()