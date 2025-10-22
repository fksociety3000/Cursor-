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
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Arrow
import numpy as np
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import logging
import requests
from urllib.parse import quote

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

@app.route('/api/generate-visual', methods=['POST'])
def generate_visual():
    """Generate educational visual content based on topic and content"""
    try:
        data = request.json
        topic = data.get('topic', 'general')
        content = data.get('content', '')
        
        if not content:
            return jsonify({"error": "No content provided"}), 400
        
        # Generate visual based on topic
        image_data = create_educational_visual(topic, content)
        
        return jsonify({
            "image_data": image_data,
            "format": "png",
            "topic": topic
        })
        
    except Exception as e:
        logger.error(f"Error generating visual: {str(e)}")
        return jsonify({"error": "Visual generation failed"}), 500

def create_educational_visual(topic, content):
    """Create topic-specific educational visuals"""
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Set background color
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#ffffff')
    
    try:
        if topic == "math" or topic == "mathematics":
            create_math_visual(ax, content)
        elif topic == "science":
            create_science_visual(ax, content)
        elif topic == "physics":
            create_physics_visual(ax, content)
        elif topic == "chemistry":
            create_chemistry_visual(ax, content)
        elif topic == "biology":
            create_biology_visual(ax, content)
        elif topic == "history":
            create_history_visual(ax, content)
        elif topic == "technology":
            create_technology_visual(ax, content)
        elif topic == "art":
            create_art_visual(ax, content)
        elif topic == "language":
            create_language_visual(ax, content)
        elif topic == "philosophy":
            create_philosophy_visual(ax, content)
        else:
            create_general_visual(ax, topic, content)
            
    except Exception as e:
        logger.error(f"Error creating {topic} visual: {str(e)}")
        create_fallback_visual(ax, topic, content)
    
    # Remove axes for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Save to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150, 
                facecolor='#f8f9fa', edgecolor='none')
    buffer.seek(0)
    image_data = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)
    
    return image_data

def create_math_visual(ax, content):
    """Create mathematical visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    # Title
    ax.text(5, 7.5, 'Mathematical Concept', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    if any(word in content.lower() for word in ['function', 'graph', 'equation']):
        # Draw a function graph
        x = np.linspace(1, 9, 100)
        y1 = 3 + 2 * np.sin(x)
        y2 = 4 + 0.5 * x
        
        ax.plot(x, y1, 'b-', linewidth=3, label='f(x) = sin(x)', color='#3498db')
        ax.plot(x, y2, 'r--', linewidth=3, label='g(x) = linear', color='#e74c3c')
        ax.legend(loc='upper right', fontsize=12)
        
    elif any(word in content.lower() for word in ['geometry', 'shape', 'circle', 'triangle']):
        # Draw geometric shapes
        circle = Circle((3, 4), 1.5, fill=False, linewidth=3, color='#3498db')
        ax.add_patch(circle)
        ax.text(3, 4, 'Circle\nA = πr²', ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Triangle
        triangle = patches.Polygon([(6, 2), (8, 2), (7, 4.5)], fill=False, linewidth=3, color='#e74c3c')
        ax.add_patch(triangle)
        ax.text(7, 3, 'Triangle\nA = ½bh', ha='center', va='center', fontsize=12, fontweight='bold')
        
    else:
        # Default math visualization
        ax.text(5, 5, '🔢 Mathematics', fontsize=48, ha='center', va='center')
        ax.text(5, 3.5, 'Numbers • Patterns • Logic', fontsize=16, ha='center', va='center', 
                style='italic', color='#7f8c8d')
        
        # Add some mathematical symbols
        symbols = ['∑', '∫', '√', '∞', 'π', '∆']
        for i, symbol in enumerate(symbols):
            x_pos = 1.5 + i * 1.3
            ax.text(x_pos, 1.5, symbol, fontsize=24, ha='center', va='center', 
                   color='#9b59b6', alpha=0.7)

def create_science_visual(ax, content):
    """Create science visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Science Exploration', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    if 'atom' in content.lower() or 'molecule' in content.lower():
        # Draw atomic structure
        nucleus = Circle((5, 4), 0.3, color='#e74c3c', alpha=0.8)
        ax.add_patch(nucleus)
        
        # Electron orbits
        for radius in [1, 1.8, 2.5]:
            orbit = Circle((5, 4), radius, fill=False, linewidth=2, color='#34495e', alpha=0.6)
            ax.add_patch(orbit)
        
        # Electrons
        electrons = [(6, 4), (3.2, 4), (6.5, 5.5), (3.5, 2.5), (7, 4)]
        for pos in electrons:
            electron = Circle(pos, 0.1, color='#3498db')
            ax.add_patch(electron)
            
        ax.text(5, 1.5, 'Atomic Structure', fontsize=16, ha='center', fontweight='bold')
        
    else:
        # General science visual
        ax.text(5, 5, '🔬 Science', fontsize=48, ha='center', va='center')
        ax.text(5, 3.5, 'Observe • Hypothesize • Experiment', fontsize=14, ha='center', 
                va='center', style='italic', color='#7f8c8d')

def create_physics_visual(ax, content):
    """Create physics visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Physics Concepts', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    if any(word in content.lower() for word in ['wave', 'frequency', 'wavelength']):
        # Draw wave
        x = np.linspace(1, 9, 200)
        y = 4 + 1.5 * np.sin(2 * np.pi * x / 2)
        ax.plot(x, y, 'b-', linewidth=4, color='#3498db')
        
        # Wave properties
        ax.annotate('Wavelength (λ)', xy=(3, 4), xytext=(3, 2.5),
                   arrowprops=dict(arrowstyle='<->', color='#e74c3c', lw=2))
        ax.annotate('Amplitude', xy=(2, 5.5), xytext=(0.5, 6.5),
                   arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2))
        
    elif 'force' in content.lower() or 'motion' in content.lower():
        # Draw force diagram
        box = Rectangle((4, 3.5), 2, 1, fill=True, color='#95a5a6', alpha=0.8)
        ax.add_patch(box)
        
        # Force arrows
        ax.arrow(6.2, 4, 1.5, 0, head_width=0.2, head_length=0.2, fc='#e74c3c', ec='#e74c3c')
        ax.text(7.5, 4.5, 'Force (F)', fontsize=12, color='#e74c3c', fontweight='bold')
        
    else:
        ax.text(5, 5, '⚡ Physics', fontsize=48, ha='center', va='center')
        ax.text(5, 3.5, 'Forces • Energy • Motion', fontsize=14, ha='center', 
                va='center', style='italic', color='#7f8c8d')

def create_chemistry_visual(ax, content):
    """Create chemistry visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Chemistry Concepts', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    if 'molecule' in content.lower() or 'bond' in content.lower():
        # Draw molecular structure (water molecule example)
        # Oxygen
        oxygen = Circle((5, 4), 0.4, color='#e74c3c', alpha=0.8)
        ax.add_patch(oxygen)
        ax.text(5, 4, 'O', fontsize=16, fontweight='bold', ha='center', va='center', color='white')
        
        # Hydrogens
        h1 = Circle((3.5, 3), 0.25, color='#ecf0f1', alpha=0.9, edgecolor='#34495e', linewidth=2)
        h2 = Circle((6.5, 3), 0.25, color='#ecf0f1', alpha=0.9, edgecolor='#34495e', linewidth=2)
        ax.add_patch(h1)
        ax.add_patch(h2)
        ax.text(3.5, 3, 'H', fontsize=12, fontweight='bold', ha='center', va='center')
        ax.text(6.5, 3, 'H', fontsize=12, fontweight='bold', ha='center', va='center')
        
        # Bonds
        ax.plot([4.3, 3.7], [3.7, 3.2], 'k-', linewidth=3)
        ax.plot([5.7, 6.3], [3.7, 3.2], 'k-', linewidth=3)
        
        ax.text(5, 1.5, 'H₂O - Water Molecule', fontsize=16, ha='center', fontweight='bold')
        
    else:
        ax.text(5, 5, '🧪 Chemistry', fontsize=48, ha='center', va='center')
        ax.text(5, 3.5, 'Elements • Compounds • Reactions', fontsize=14, ha='center', 
                va='center', style='italic', color='#7f8c8d')

def create_biology_visual(ax, content):
    """Create biology visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Biology Concepts', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    if 'cell' in content.lower():
        # Draw cell structure
        cell_membrane = Circle((5, 4), 2.5, fill=False, linewidth=3, color='#27ae60')
        ax.add_patch(cell_membrane)
        
        # Nucleus
        nucleus = Circle((5, 4), 0.8, color='#8e44ad', alpha=0.7)
        ax.add_patch(nucleus)
        ax.text(5, 4, 'Nucleus', fontsize=10, ha='center', va='center', color='white', fontweight='bold')
        
        # Organelles
        mitochondria = [Circle((3.5, 5), 0.3, color='#e67e22', alpha=0.8),
                       Circle((6.5, 3), 0.3, color='#e67e22', alpha=0.8)]
        for organelle in mitochondria:
            ax.add_patch(organelle)
            
        ax.text(5, 1, 'Cell Structure', fontsize=16, ha='center', fontweight='bold')
        
    else:
        ax.text(5, 5, '🧬 Biology', fontsize=48, ha='center', va='center')
        ax.text(5, 3.5, 'Life • Evolution • Genetics', fontsize=14, ha='center', 
                va='center', style='italic', color='#7f8c8d')

def create_history_visual(ax, content):
    """Create history visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Historical Timeline', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    # Create timeline
    ax.plot([1, 9], [4, 4], 'k-', linewidth=3)
    
    # Timeline markers
    events = ['Ancient', 'Classical', 'Medieval', 'Modern', 'Present']
    positions = [1.5, 3, 5, 7, 8.5]
    
    for event, pos in zip(events, positions):
        ax.plot([pos, pos], [3.8, 4.2], 'k-', linewidth=2)
        ax.text(pos, 3.3, event, fontsize=10, ha='center', rotation=45)
        
    ax.text(5, 5.5, '📜 History', fontsize=32, ha='center', va='center')
    ax.text(5, 2, 'Understanding the Past to Shape the Future', fontsize=12, ha='center', 
            va='center', style='italic', color='#7f8c8d')

def create_technology_visual(ax, content):
    """Create technology visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Technology & Innovation', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    if any(word in content.lower() for word in ['computer', 'ai', 'algorithm', 'programming']):
        # Draw flowchart
        boxes = [
            {'pos': (2, 6), 'text': 'Input'},
            {'pos': (5, 6), 'text': 'Process'},
            {'pos': (8, 6), 'text': 'Output'}
        ]
        
        for box in boxes:
            rect = FancyBboxPatch((box['pos'][0]-0.8, box['pos'][1]-0.4), 1.6, 0.8,
                                 boxstyle="round,pad=0.1", facecolor='#3498db', 
                                 edgecolor='#2980b9', alpha=0.8)
            ax.add_patch(rect)
            ax.text(box['pos'][0], box['pos'][1], box['text'], fontsize=12, 
                   ha='center', va='center', color='white', fontweight='bold')
        
        # Arrows
        ax.arrow(2.8, 6, 1.4, 0, head_width=0.15, head_length=0.2, fc='#34495e', ec='#34495e')
        ax.arrow(5.8, 6, 1.4, 0, head_width=0.15, head_length=0.2, fc='#34495e', ec='#34495e')
        
    ax.text(5, 3.5, '💻 Technology', fontsize=32, ha='center', va='center')
    ax.text(5, 2.5, 'Innovation • Automation • Digital Future', fontsize=12, ha='center', 
            va='center', style='italic', color='#7f8c8d')

def create_art_visual(ax, content):
    """Create art visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Art & Creativity', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    # Color wheel
    theta = np.linspace(0, 2*np.pi, 12, endpoint=False)
    colors = ['#ff0000', '#ff8000', '#ffff00', '#80ff00', '#00ff00', '#00ff80',
              '#00ffff', '#0080ff', '#0000ff', '#8000ff', '#ff00ff', '#ff0080']
    
    for i, (angle, color) in enumerate(zip(theta, colors)):
        x = 5 + 1.5 * np.cos(angle)
        y = 4 + 1.5 * np.sin(angle)
        circle = Circle((x, y), 0.3, color=color, alpha=0.8)
        ax.add_patch(circle)
    
    ax.text(5, 4, 'Color\nWheel', fontsize=14, ha='center', va='center', fontweight='bold')
    ax.text(5, 1.5, '🎨 Art & Design', fontsize=16, ha='center', fontweight='bold')

def create_language_visual(ax, content):
    """Create language visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Language & Communication', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    # Word tree or grammar structure
    ax.text(5, 5.5, '📚 Language', fontsize=32, ha='center', va='center')
    
    # Different writing systems examples
    examples = ['Hello', 'Hola', '你好', 'مرحبا', 'Bonjour']
    y_positions = [4.5, 4, 3.5, 3, 2.5]
    
    for example, y_pos in zip(examples, y_positions):
        ax.text(5, y_pos, example, fontsize=14, ha='center', va='center', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#ecf0f1', alpha=0.8))

def create_philosophy_visual(ax, content):
    """Create philosophy visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7.5, 'Philosophical Thinking', fontsize=20, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    ax.text(5, 5, '🤔 Philosophy', fontsize=32, ha='center', va='center')
    
    # Thought bubbles
    questions = ['What is truth?', 'Why do we exist?', 'What is good?']
    positions = [(2.5, 3.5), (5, 3), (7.5, 3.5)]
    
    for question, pos in zip(questions, positions):
        bubble = Circle(pos, 1, fill=True, color='#ecf0f1', alpha=0.9, 
                       edgecolor='#bdc3c7', linewidth=2)
        ax.add_patch(bubble)
        ax.text(pos[0], pos[1], question, fontsize=9, ha='center', va='center', 
               wrap=True, style='italic')

def create_general_visual(ax, topic, content):
    """Create general topic visualizations"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 7, f'Learning About: {topic.title()}', fontsize=18, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    # Create a mind map style visual
    ax.text(5, 4.5, '🧠', fontsize=48, ha='center', va='center')
    ax.text(5, 3.5, 'Knowledge', fontsize=20, ha='center', va='center', fontweight='bold')
    
    # Add concept branches
    concepts = ['Learn', 'Understand', 'Apply', 'Teach']
    angles = [0, np.pi/2, np.pi, 3*np.pi/2]
    
    for concept, angle in zip(concepts, angles):
        x = 5 + 2 * np.cos(angle)
        y = 4 + 2 * np.sin(angle)
        ax.plot([5, x], [4, y], 'k-', linewidth=2, alpha=0.6)
        ax.text(x, y, concept, fontsize=12, ha='center', va='center', 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='#3498db', alpha=0.8),
               color='white', fontweight='bold')

def create_fallback_visual(ax, topic, content):
    """Create fallback visual when other methods fail"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    
    ax.text(5, 6, f'📖 {topic.title()}', fontsize=24, fontweight='bold', 
            ha='center', color='#2c3e50')
    
    # Simple content summary
    wrapped_content = content[:150] + '...' if len(content) > 150 else content
    ax.text(5, 4, wrapped_content, fontsize=12, ha='center', va='center', 
           wrap=True, bbox=dict(boxstyle="round,pad=0.5", facecolor='#ecf0f1', alpha=0.9))
    
    ax.text(5, 2, '🎓 Educational Content', fontsize=16, ha='center', va='center', 
           style='italic', color='#7f8c8d')

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