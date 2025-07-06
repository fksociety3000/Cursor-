# Nova - AI Friend & Teacher 🤖✨

Nova is an intelligent AI companion designed to be your personal friend and teacher. It can help you learn about any topic through multiple interaction modes including text, voice, and visual responses. Nova evolves as you interact with it, becoming more insightful and personalized over time.

## 🌟 Features

### Multi-Modal Input
- **Text Input**: Type your questions and thoughts
- **Voice Input**: Speak naturally using voice recognition
- **Camera Input**: Capture images for visual learning (future feature)

### Multi-Modal Output
- **Text responses**: Clear, educational explanations
- **Speech synthesis**: Hear Nova's responses spoken aloud
- **Visual generation**: Charts, diagrams, and educational visuals

### AI Evolution
- **Learning System**: Nova evolves based on your interactions
- **Personality Growth**: Develops from curious to insightful to wise
- **Adaptive Teaching**: Adjusts to your learning style and preferences

### Personalization
- **User Profiles**: Customize your learning preferences
- **Interest Tracking**: Focus on topics that matter to you
- **Learning Styles**: Visual, auditory, kinesthetic, or balanced approaches
- **Difficulty Levels**: Beginner, intermediate, or advanced explanations

### Advanced Features
- **Conversation History**: Track your learning journey
- **Topic Classification**: Automatic categorization of discussions
- **Memory System**: Remembers past conversations for context
- **Modern Interface**: Clean, minimalist design with smooth animations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js (for any future extensions)
- OpenAI API key
- Modern web browser with microphone/camera support

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nova-ai-friend.git
   cd nova-ai-friend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

4. **Configure your API key**
   - Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
   - Add it to your `.env` file:
     ```
     OPENAI_API_KEY=your-actual-api-key-here
     ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Start chatting with Nova!

## 🎯 Usage Guide

### Getting Started
1. **First Interaction**: Nova will greet you and ask what you'd like to learn
2. **Set Up Profile**: Click the profile icon to customize your learning preferences
3. **Choose Input Mode**: Select text, voice, or camera input
4. **Select Response Types**: Choose how Nova should respond (text, speech, visuals)

### Input Modes

#### Text Mode
- Type your questions in the input field
- Press Enter or click Send
- Support for multi-line input with Shift+Enter

#### Voice Mode
- Click the microphone button to start listening
- Speak your question clearly
- Nova will automatically process and respond

#### Camera Mode (Future Feature)
- Click the camera button to access your camera
- Capture images for visual learning
- Ask Nova to explain what it sees

### Response Types

#### Text Responses
- Always available
- Clear, educational explanations
- Contextual and adaptive

#### Speech Responses
- Toggle speech output on/off
- Adjustable speech rate and pitch
- Natural-sounding voice synthesis

#### Visual Responses
- Auto-generated charts and diagrams
- Topic-specific visualizations
- Educational graphics and illustrations

### Features Deep Dive

#### AI Evolution System
Nova grows through three levels:
- **Level 1**: Curious and basic responses
- **Level 2**: Insightful and detailed explanations
- **Level 3**: Wise and comprehensive teaching

Evolution happens automatically based on:
- Number of conversations
- Topic diversity
- User engagement

#### Profile Management
Customize your experience:
- **Name**: What Nova should call you
- **Learning Style**: How you prefer to learn
- **Difficulty Level**: Complexity of explanations
- **Interests**: Focus areas for learning

#### Conversation History
- View past conversations
- Track learning progress
- Revisit important topics
- Export conversations (future feature)

## 🛠️ Technical Details

### Architecture
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: Python Flask with SQLAlchemy
- **Database**: SQLite (easily upgradeable)
- **AI**: OpenAI GPT integration
- **Speech**: Web Speech API
- **Visuals**: Matplotlib for chart generation

### API Endpoints
- `POST /api/chat` - Send messages to Nova
- `POST /api/text-to-speech` - Convert text to audio
- `POST /api/generate-visual` - Create educational visuals
- `GET /api/conversation-history` - Retrieve chat history
- `GET/POST /api/profile` - Manage user profiles
- `GET /api/ai-status` - Check Nova's evolution status

### Database Schema
- **Conversations**: Store all chat interactions
- **UserProfile**: User preferences and settings
- **AIFriend**: Evolution and personality data

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///ai_friend.db
```

### Customization Options
- **Personality**: Modify Nova's character traits
- **Topics**: Add custom topic categories
- **Visuals**: Customize chart styles and colors
- **Voice**: Adjust speech synthesis parameters

## 🔒 Privacy & Security

### Data Protection
- All conversations stored locally in SQLite
- No data sent to third parties except OpenAI
- User profiles remain private
- Easy data export/deletion

### Security Features
- API key encryption
- Secure cookie handling
- CORS protection
- Input validation and sanitization

## 🚧 Troubleshooting

### Common Issues

**Can't connect to OpenAI API**
- Check your API key is valid
- Ensure you have sufficient credits
- Verify network connectivity

**Speech recognition not working**
- Check microphone permissions
- Ensure you're using HTTPS or localhost
- Try refreshing the page

**Visual generation failing**
- Check matplotlib installation
- Verify sufficient disk space
- Review backend logs for errors

**Database errors**
- Delete `ai_friend.db` to reset
- Check file permissions
- Verify SQLite installation

### Debug Mode
Enable debug mode for detailed error messages:
```bash
export FLASK_DEBUG=True
python app.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (if applicable)
5. Submit a pull request

### Areas for Contribution
- New visual generation algorithms
- Additional language support
- Mobile app development
- Advanced AI features
- Performance optimizations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- Web Speech API for voice features
- Matplotlib for visualizations
- Flask community for the web framework
- Inter font family for typography

## 🔮 Future Roadmap

### Short Term (v1.1)
- [ ] Image recognition and analysis
- [ ] Export conversations to PDF
- [ ] Multiple language support
- [ ] Advanced visual generation

### Medium Term (v1.2)
- [ ] Mobile app (React Native)
- [ ] Plugin system for extensions
- [ ] Advanced memory system
- [ ] Collaborative learning features

### Long Term (v2.0)
- [ ] Video call integration
- [ ] Augmented reality features
- [ ] Advanced AI reasoning
- [ ] Educational curriculum tracking

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/nova-ai-friend/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/nova-ai-friend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nova-ai-friend/discussions)
- **Email**: support@nova-ai-friend.com

---

**Made with ❤️ by the Nova Team**

Transform your learning experience with Nova - your AI friend who grows with you! 
