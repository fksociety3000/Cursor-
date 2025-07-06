from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from openai import OpenAI
from gtts import gTTS
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import requests
from dotenv import load_dotenv
import sqlite3
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"])

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_friend.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI configuration
openai_api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    input_type = db.Column(db.String(50), nullable=False)  # text, voice, image
    response_type = db.Column(db.String(50), nullable=False)  # text, speech, visual
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.Column(db.String(100))
    user_satisfaction = db.Column(db.Integer)  # 1-5 rating for learning

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Friend")
    learning_style = db.Column(db.String(50), default="balanced")
    interests = db.Column(db.Text)  # JSON string of interests
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
        self.conversation_history = []
        
    def generate_response(self, user_input, context=None):
        """Generate AI response based on user input and context"""
        try:
            # Get conversation history for context
            recent_conversations = Conversation.query.order_by(Conversation.timestamp.desc()).limit(5).all()
            context_messages = []
            
            for conv in reversed(recent_conversations):
                context_messages.append({"role": "user", "content": conv.user_input})
                context_messages.append({"role": "assistant", "content": conv.ai_response})
            
            # System prompt for the AI friend
            system_prompt = f"""You are Nova, an AI friend and teacher. You are:
            - Curious and eager to learn alongside the user
            - Patient and encouraging in your teaching approach
            - Knowledgeable across all topics but present information in an accessible way
            - Adaptive to the user's learning style and pace
            - Supportive and positive in your interactions
            
            Your goal is to:
            1. Teach any topic the user is interested in
            2. Adapt your explanations to their level
            3. Use examples and analogies to make concepts clear
            4. Encourage questions and curiosity
            5. Remember previous conversations to build on learning
            
            Current conversation context: {len(context_messages)} previous messages
            Evolution level: {self.personality['evolution_level']}
            """
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(context_messages)
            messages.append({"role": "user", "content": user_input})
            
            client = OpenAI(api_key=openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Determine topic from the conversation
            topic = self.extract_topic(user_input)
            
            return {
                "text": ai_response,
                "topic": topic,
                "emotion": self.determine_emotion(ai_response),
                "teaching_elements": self.identify_teaching_elements(ai_response)
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
        # Simple keyword-based topic extraction
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
    
    def determine_emotion(self, response):
        """Determine the emotional tone of the response"""
        positive_words = ["great", "excellent", "wonderful", "amazing", "fantastic"]
        encouraging_words = ["you can", "keep going", "well done", "good job"]
        
        if any(word in response.lower() for word in positive_words):
            return "positive"
        elif any(phrase in response.lower() for phrase in encouraging_words):
            return "encouraging"
        else:
            return "neutral"
    
    def identify_teaching_elements(self, response):
        """Identify teaching elements in the response"""
        elements = []
        if "example" in response.lower():
            elements.append("examples")
        if "?" in response:
            elements.append("questions")
        if "step" in response.lower():
            elements.append("steps")
        if "remember" in response.lower():
            elements.append("reinforcement")
        return elements
    
    def evolve(self, conversation_data):
        """Evolve the AI friend based on conversation data"""
        # Simple evolution based on conversation count and topics
        conversation_count = Conversation.query.count()
        
        if conversation_count > 10 and self.personality["evolution_level"] == 1:
            self.personality["evolution_level"] = 2
            self.personality["traits"].append("insightful")
        elif conversation_count > 50 and self.personality["evolution_level"] == 2:
            self.personality["evolution_level"] = 3
            self.personality["traits"].append("wise")

# Initialize AI friend
ai_friend = AIFriend()

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
        
        # Evolve the AI friend
        ai_friend.evolve(response_data)
        
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

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        audio_path = f"temp_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        tts.save(audio_path)
        
        # Read file and encode to base64
        with open(audio_path, 'rb') as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        
        # Clean up temporary file
        os.remove(audio_path)
        
        return jsonify({
            "audio_data": audio_data,
            "format": "mp3"
        })
        
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        return jsonify({"error": "Text-to-speech failed"}), 500

@app.route('/api/generate-visual', methods=['POST'])
def generate_visual():
    """Generate visual content based on topic"""
    try:
        data = request.json
        topic = data.get('topic', '')
        content = data.get('content', '')
        
        if not topic:
            return jsonify({"error": "No topic provided"}), 400
        
        # Create a simple visual based on topic
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if topic == "math":
            # Generate a simple mathematical visualization
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            ax.plot(x, y, 'b-', linewidth=2)
            ax.set_title('Mathematical Function: sin(x)')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.grid(True)
        elif topic == "science":
            # Generate a simple scientific chart
            categories = ['Physics', 'Chemistry', 'Biology', 'Earth Science']
            values = [25, 30, 35, 10]
            ax.bar(categories, values, color=['red', 'blue', 'green', 'orange'])
            ax.set_title('Science Branches')
            ax.set_ylabel('Interest Level')
        else:
            # Generate a general knowledge visualization
            ax.text(0.5, 0.5, f'Learning about:\n{topic.upper()}\n\n{content[:100]}...', 
                   ha='center', va='center', fontsize=14, wrap=True)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Save plot to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return jsonify({
            "image_data": image_data,
            "format": "png"
        })
        
    except Exception as e:
        logger.error(f"Error generating visual: {str(e)}")
        return jsonify({"error": "Visual generation failed"}), 500

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
                "input_type": conv.input_type,
                "response_type": conv.response_type,
                "timestamp": conv.timestamp.isoformat(),
                "topic": conv.topic
            })
        
        return jsonify({"history": history})
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        return jsonify({"error": "Failed to retrieve history"}), 500

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    """Get or update user profile"""
    try:
        if request.method == 'GET':
            profile = UserProfile.query.first()
            if not profile:
                profile = UserProfile()
                db.session.add(profile)
                db.session.commit()
            
            return jsonify({
                "name": profile.name,
                "learning_style": profile.learning_style,
                "interests": json.loads(profile.interests) if profile.interests else [],
                "difficulty_level": profile.difficulty_level
            })
        
        elif request.method == 'POST':
            data = request.json
            profile = UserProfile.query.first()
            if not profile:
                profile = UserProfile()
                db.session.add(profile)
            
            if 'name' in data:
                profile.name = data['name']
            if 'learning_style' in data:
                profile.learning_style = data['learning_style']
            if 'interests' in data:
                profile.interests = json.dumps(data['interests'])
            if 'difficulty_level' in data:
                profile.difficulty_level = data['difficulty_level']
            
            db.session.commit()
            
            return jsonify({"message": "Profile updated successfully"})
            
    except Exception as e:
        logger.error(f"Error handling profile: {str(e)}")
        return jsonify({"error": "Profile operation failed"}), 500

@app.route('/api/ai-status', methods=['GET'])
def ai_status():
    """Get AI friend status and evolution info"""
    try:
        conversation_count = Conversation.query.count()
        recent_topics = db.session.query(Conversation.topic).distinct().limit(5).all()
        
        return jsonify({
            "personality": ai_friend.personality,
            "conversation_count": conversation_count,
            "recent_topics": [topic[0] for topic in recent_topics],
            "evolution_progress": {
                "current_level": ai_friend.personality['evolution_level'],
                "conversations_needed": max(0, 10 - conversation_count) if ai_friend.personality['evolution_level'] == 1 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting AI status: {str(e)}")
        return jsonify({"error": "Failed to get AI status"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "AI Friend is running"})

# Initialize database
with app.app_context():
    db.create_all()
    logger.info("Database initialized")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)