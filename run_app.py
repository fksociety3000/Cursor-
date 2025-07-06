#!/usr/bin/env python3
"""
Nova AI Friend - Combined Frontend & Backend Server
Single Flask app that serves both the frontend HTML and the API endpoints.
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import google.generativeai as genai
from gtts import gTTS
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_friend.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API configuration
gemini_api_key = os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here')
if gemini_api_key != 'your-gemini-api-key-here':
    genai.configure(api_key=gemini_api_key)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    input_type = db.Column(db.String(50), nullable=False)
    response_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.Column(db.String(100))

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Friend")
    learning_style = db.Column(db.String(50), default="balanced")
    interests = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20), default="intermediate")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIFriend:
    def __init__(self):
        self.personality = {
            "name": "Nova",
            "traits": ["curious", "patient", "encouraging", "knowledgeable"],
            "teaching_style": "adaptive",
            "evolution_level": 1
        }
        
    def generate_response(self, user_input, context=None):
        """Generate AI response using Gemini"""
        try:
            recent_conversations = Conversation.query.order_by(Conversation.timestamp.desc()).limit(5).all()
            context_messages = []
            
            for conv in reversed(recent_conversations):
                context_messages.append(f"User: {conv.user_input}")
                context_messages.append(f"Nova: {conv.ai_response}")
            
            system_prompt = f"""You are Nova, an AI friend and teacher. You are curious, patient, encouraging, and knowledgeable. Your goal is to teach any topic the user is interested in, adapt your explanations to their level, use examples and analogies to make concepts clear, and encourage questions and curiosity.

Previous conversations:
{chr(10).join(context_messages[-10:]) if context_messages else "No previous conversations"}

User's current message: {user_input}

Please respond as Nova, keeping your response helpful, encouraging, and educational. Keep responses concise but informative.
"""
            
            if gemini_api_key == 'your-gemini-api-key-here':
                ai_response = "I'm sorry, I need a valid Gemini API key to function. Please add your Gemini API key to the .env file."
            else:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(system_prompt)
                ai_response = response.text
            
            topic = self.extract_topic(user_input)
            
            return {
                "text": ai_response,
                "topic": topic,
                "emotion": "positive",
                "teaching_elements": []
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "text": "I'm sorry, I'm having trouble processing that right now. Could you try again?",
                "topic": "error",
                "emotion": "apologetic",
                "teaching_elements": []
            }
    
    def extract_topic(self, text):
        """Extract the main topic from user input"""
        topics = {
            "math": ["math", "mathematics", "calculate", "equation", "algebra", "geometry"],
            "science": ["science", "physics", "chemistry", "biology", "experiment"],
            "history": ["history", "historical", "past", "ancient", "war", "civilization"],
            "technology": ["technology", "computer", "programming", "AI", "software", "code"],
            "language": ["language", "grammar", "vocabulary", "writing", "literature"],
            "art": ["art", "painting", "drawing", "music", "creative", "design"],
            "philosophy": ["philosophy", "ethics", "meaning", "existence", "thought"],
            "general": ["help", "explain", "what", "how", "why", "tell me"]
        }
        
        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        return "general"

# Initialize AI friend
ai_friend = AIFriend()

# Read the HTML template
def get_html_template():
    try:
        with open('index.html', 'r') as f:
            html_content = f.read()
        # Update API endpoint to current server
        html_content = html_content.replace('http://localhost:8080/api', '/api')
        html_content = html_content.replace('http://localhost:5000/api', '/api')
        return html_content
    except:
        return """
        <!DOCTYPE html>
        <html><head><title>Nova AI Friend</title></head>
        <body>
        <h1>Nova AI Friend</h1>
        <div id="chat-container">
            <div id="messages"></div>
            <input type="text" id="user-input" placeholder="Chat with Nova...">
            <button onclick="sendMessage()">Send</button>
        </div>
        <script>
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;
            
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML += '<div><strong>You:</strong> ' + message + '</div>';
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                messagesDiv.innerHTML += '<div><strong>Nova:</strong> ' + data.response + '</div>';
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            } catch (error) {
                messagesDiv.innerHTML += '<div>Error: Could not get response</div>';
            }
        }
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
        </script>
        </body></html>
        """

# Routes
@app.route('/')
def index():
    """Serve the main application"""
    return get_html_template()

@app.route('/styles.css')
def serve_css():
    """Serve CSS file"""
    try:
        with open('styles.css', 'r') as f:
            css_content = f.read()
        return css_content, 200, {'Content-Type': 'text/css'}
    except:
        return "", 200, {'Content-Type': 'text/css'}

@app.route('/script.js')
def serve_js():
    """Serve JavaScript file"""
    try:
        with open('script.js', 'r') as f:
            js_content = f.read()
        # Update API endpoint
        js_content = js_content.replace('http://localhost:8080/api', '/api')
        js_content = js_content.replace('http://localhost:5000/api', '/api')
        return js_content, 200, {'Content-Type': 'application/javascript'}
    except:
        return "", 200, {'Content-Type': 'application/javascript'}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle text-based chat"""
    try:
        data = request.json
        user_input = data.get('message', '')
        input_type = data.get('type', 'text')
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        # Generate AI response
        response_data = ai_friend.generate_response(user_input)
        
        # Save conversation to database
        conversation = Conversation(
            user_input=user_input,
            ai_response=response_data['text'],
            input_type=input_type,
            response_type='text',
            topic=response_data['topic']
        )
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            "response": response_data['text'],
            "topic": response_data['topic'],
            "emotion": response_data['emotion'],
            "teaching_elements": response_data['teaching_elements'],
            "evolution_level": ai_friend.personality['evolution_level']
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Nova AI Friend is running!"})

@app.route('/api/conversation-history', methods=['GET'])
def get_conversation_history():
    """Get conversation history"""
    try:
        conversations = Conversation.query.order_by(Conversation.timestamp.desc()).limit(20).all()
        
        history = []
        for conv in conversations:
            history.append({
                "id": conv.id,
                "user_input": conv.user_input,
                "ai_response": conv.ai_response,
                "timestamp": conv.timestamp.isoformat(),
                "topic": conv.topic
            })
        
        return jsonify({"history": history})
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        return jsonify({"error": "Failed to retrieve history"}), 500

# Initialize database
with app.app_context():
    db.create_all()
    logger.info("Database initialized")

if __name__ == '__main__':
    print("🤖 Starting Nova AI Friend...")
    print("✅ Backend and Frontend combined")
    print("✅ Database initialized")
    print("✅ Gemini AI configured")
    print("")
    print("🌐 Server will run on:")
    print("   - http://localhost:5000")
    print("   - http://127.0.0.1:5000")
    print("   - http://0.0.0.0:5000")
    print("")
    print("💡 Open your browser and visit the URL above!")
    print("🚀 Starting server...")
    
    app.run(host='0.0.0.0', port=5000, debug=False)