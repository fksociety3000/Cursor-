class AIFriend {
    constructor() {
        this.currentMode = 'text';
        this.isListening = false;
        this.isSpeaking = false;
        this.cameraStream = null;
        this.apiBaseUrl = '/api';
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.activeResponseTypes = ['text'];
        
        this.initializeElements();
        this.initializeEventListeners();
        this.initializeSpeechRecognition();
        this.loadUserProfile();
        this.loadAIStatus();
        this.loadConversationHistory();
        
        // Auto-resize textarea
        this.autoResizeTextarea();
    }
    
    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        
        // Mode elements
        this.modeButtons = document.querySelectorAll('.mode-btn');
        this.inputField = document.querySelector('.input-field');
        this.voiceControls = document.getElementById('voiceControls');
        this.cameraControls = document.getElementById('cameraControls');
        
        // Voice elements
        this.voiceToggle = document.getElementById('voiceToggle');
        this.voiceStatus = document.getElementById('voiceStatus');
        
        // Camera elements
        this.cameraVideo = document.getElementById('cameraVideo');
        this.captureBtn = document.getElementById('captureBtn');
        this.closeCameraBtn = document.getElementById('closeCameraBtn');
        
        // Response elements
        this.responseButtons = document.querySelectorAll('.response-btn');
        this.visualDisplay = document.getElementById('visualDisplay');
        this.visualImage = document.getElementById('visualImage');
        this.closeVisual = document.getElementById('closeVisual');
        
        // Sidebar elements
        this.sidebar = document.getElementById('sidebar');
        this.profileBtn = document.getElementById('profileBtn');
        this.historyBtn = document.getElementById('historyBtn');
        this.settingsBtn = document.getElementById('settingsBtn');
        
        // Panel elements
        this.profilePanel = document.getElementById('profilePanel');
        this.historyPanel = document.getElementById('historyPanel');
        this.settingsPanel = document.getElementById('settingsPanel');
        
        // Profile elements
        this.userName = document.getElementById('userName');
        this.learningStyle = document.getElementById('learningStyle');
        this.difficultyLevel = document.getElementById('difficultyLevel');
        this.interestsTags = document.getElementById('interestsTags');
        this.saveProfile = document.getElementById('saveProfile');
        
        // History elements
        this.historyList = document.getElementById('historyList');
        
        // Settings elements
        this.evolutionLevel = document.getElementById('evolutionLevel');
        this.evolutionProgress = document.getElementById('evolutionProgress');
        this.currentLevel = document.getElementById('currentLevel');
        this.progressText = document.getElementById('progressText');
        this.speechRate = document.getElementById('speechRate');
        this.voicePitch = document.getElementById('voicePitch');
        this.autoVisuals = document.getElementById('autoVisuals');
        
        // Loading and toast elements
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.toastContainer = document.getElementById('toastContainer');
    }
    
    initializeEventListeners() {
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Mode switching
        this.modeButtons.forEach(btn => {
            btn.addEventListener('click', () => this.switchMode(btn.dataset.mode));
        });
        
        // Voice controls
        this.voiceToggle.addEventListener('click', () => this.toggleVoiceRecognition());
        
        // Camera controls
        this.captureBtn.addEventListener('click', () => this.captureImage());
        this.closeCameraBtn.addEventListener('click', () => this.closeCamera());
        
        // Response type selection
        this.responseButtons.forEach(btn => {
            btn.addEventListener('click', () => this.toggleResponseType(btn));
        });
        
        // Visual controls
        this.closeVisual.addEventListener('click', () => this.closeVisualDisplay());
        
        // Sidebar controls
        this.profileBtn.addEventListener('click', () => this.openPanel('profile'));
        this.historyBtn.addEventListener('click', () => this.openPanel('history'));
        this.settingsBtn.addEventListener('click', () => this.openPanel('settings'));
        
        // Panel close buttons
        document.querySelectorAll('.btn-close').forEach(btn => {
            btn.addEventListener('click', () => {
                if (btn.dataset.panel) {
                    this.closePanel(btn.dataset.panel);
                } else {
                    this.closeVisualDisplay();
                }
            });
        });
        
        // Profile management
        this.saveProfile.addEventListener('click', () => this.saveUserProfile());
        this.interestsTags.addEventListener('click', (e) => {
            if (e.target.classList.contains('interest-tag')) {
                e.target.classList.toggle('selected');
            }
        });
        
        // Settings
        this.speechRate.addEventListener('input', () => this.updateSpeechSettings());
        this.voicePitch.addEventListener('input', () => this.updateSpeechSettings());
        
        // Click outside to close sidebar
        document.addEventListener('click', (e) => {
            if (!this.sidebar.contains(e.target) && 
                !this.profileBtn.contains(e.target) && 
                !this.historyBtn.contains(e.target) && 
                !this.settingsBtn.contains(e.target)) {
                this.closeSidebar();
            }
        });
    }
    
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isListening = true;
                this.voiceToggle.classList.add('listening');
                this.voiceStatus.textContent = 'Listening...';
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
                this.sendMessage();
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                this.voiceToggle.classList.remove('listening');
                this.voiceStatus.textContent = 'Click to start listening...';
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showToast('Speech recognition error', 'error');
                this.isListening = false;
                this.voiceToggle.classList.remove('listening');
                this.voiceStatus.textContent = 'Click to start listening...';
            };
        } else {
            this.showToast('Speech recognition not supported in this browser', 'error');
        }
    }
    
    switchMode(mode) {
        this.currentMode = mode;
        
        // Update button states
        this.modeButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        // Show/hide appropriate controls
        this.inputField.style.display = mode === 'text' ? 'flex' : 'none';
        this.voiceControls.style.display = mode === 'voice' ? 'flex' : 'none';
        this.cameraControls.style.display = mode === 'camera' ? 'flex' : 'none';
        
        // Initialize camera if needed
        if (mode === 'camera') {
            this.initializeCamera();
        } else if (this.cameraStream) {
            this.closeCamera();
        }
    }
    
    async initializeCamera() {
        try {
            this.cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
            this.cameraVideo.srcObject = this.cameraStream;
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.showToast('Camera access denied', 'error');
            this.switchMode('text');
        }
    }
    
    closeCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
        this.switchMode('text');
    }
    
    captureImage() {
        if (!this.cameraStream) return;
        
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = this.cameraVideo.videoWidth;
        canvas.height = this.cameraVideo.videoHeight;
        
        context.drawImage(this.cameraVideo, 0, 0);
        
        const imageData = canvas.toDataURL('image/png');
        
        // For now, just add a message about the image
        this.messageInput.value = 'I captured an image. Can you help me understand what you see?';
        this.sendMessage();
        
        // In a real implementation, you'd send the image to the backend
        // this.sendImageMessage(imageData);
    }
    
    toggleVoiceRecognition() {
        if (!this.recognition) {
            this.showToast('Speech recognition not available', 'error');
            return;
        }
        
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }
    
    toggleResponseType(button) {
        const type = button.id.replace('ResponseBtn', '').toLowerCase();
        
        if (type === 'text') {
            // Text is always active
            return;
        }
        
        button.classList.toggle('active');
        
        if (button.classList.contains('active')) {
            this.activeResponseTypes.push(type);
        } else {
            this.activeResponseTypes = this.activeResponseTypes.filter(t => t !== type);
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Clear input
        this.messageInput.value = '';
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show loading
        this.showLoading();
        
        try {
            // Send to backend
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    type: this.currentMode
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Add AI response to chat
            this.addMessage(data.response, 'ai', data.topic, data.emotion);
            
            // Handle different response types
            if (this.activeResponseTypes.includes('speech')) {
                this.speakText(data.response);
            }
            
            if (this.activeResponseTypes.includes('visual') && this.autoVisuals.checked) {
                this.generateVisual(data.topic, data.response);
            }
            
            // Update evolution level
            if (data.evolution_level) {
                this.updateEvolutionLevel(data.evolution_level);
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai', 'error');
            this.showToast('Failed to send message', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    addMessage(text, sender, topic = 'general', emotion = 'neutral') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-meta">
                    <span class="topic-tag">${topic}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    async speakText(text) {
        if (this.isSpeaking) {
            this.synthesis.cancel();
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = parseFloat(this.speechRate.value);
        utterance.pitch = parseFloat(this.voicePitch.value);
        
        utterance.onstart = () => {
            this.isSpeaking = true;
        };
        
        utterance.onend = () => {
            this.isSpeaking = false;
        };
        
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            this.isSpeaking = false;
        };
        
        this.synthesis.speak(utterance);
    }
    
    async generateVisual(topic, content) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/generate-visual`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: topic,
                    content: content
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate visual');
            }
            
            const data = await response.json();
            this.showVisualContent(data.image_data);
            
        } catch (error) {
            console.error('Error generating visual:', error);
            this.showToast('Failed to generate visual', 'error');
        }
    }
    
    showVisualContent(imageData) {
        this.visualImage.src = `data:image/png;base64,${imageData}`;
        this.visualDisplay.style.display = 'block';
    }
    
    closeVisualDisplay() {
        this.visualDisplay.style.display = 'none';
    }
    
    openPanel(panelName) {
        this.closeSidebar();
        
        // Hide all panels
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Show selected panel
        document.getElementById(`${panelName}Panel`).classList.add('active');
        
        // Show sidebar
        this.sidebar.classList.add('open');
        
        // Load panel-specific data
        if (panelName === 'history') {
            this.loadConversationHistory();
        } else if (panelName === 'settings') {
            this.loadAIStatus();
        }
    }
    
    closePanel(panelName) {
        document.getElementById(`${panelName}Panel`).classList.remove('active');
        this.closeSidebar();
    }
    
    closeSidebar() {
        this.sidebar.classList.remove('open');
    }
    
    async loadUserProfile() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/profile`);
            if (!response.ok) throw new Error('Failed to load profile');
            
            const data = await response.json();
            
            this.userName.value = data.name || '';
            this.learningStyle.value = data.learning_style || 'balanced';
            this.difficultyLevel.value = data.difficulty_level || 'intermediate';
            
            // Update interest tags
            const interests = data.interests || [];
            this.interestsTags.querySelectorAll('.interest-tag').forEach(tag => {
                if (interests.includes(tag.textContent)) {
                    tag.classList.add('selected');
                }
            });
            
        } catch (error) {
            console.error('Error loading profile:', error);
        }
    }
    
    async saveUserProfile() {
        const selectedInterests = Array.from(this.interestsTags.querySelectorAll('.interest-tag.selected'))
            .map(tag => tag.textContent);
        
        const profileData = {
            name: this.userName.value,
            learning_style: this.learningStyle.value,
            difficulty_level: this.difficultyLevel.value,
            interests: selectedInterests
        };
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(profileData)
            });
            
            if (!response.ok) throw new Error('Failed to save profile');
            
            this.showToast('Profile saved successfully!', 'success');
            
        } catch (error) {
            console.error('Error saving profile:', error);
            this.showToast('Failed to save profile', 'error');
        }
    }
    
    async loadConversationHistory() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/conversation-history`);
            if (!response.ok) throw new Error('Failed to load history');
            
            const data = await response.json();
            
            this.historyList.innerHTML = '';
            
            data.history.forEach(conv => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                
                const date = new Date(conv.timestamp).toLocaleDateString();
                const time = new Date(conv.timestamp).toLocaleTimeString();
                
                historyItem.innerHTML = `
                    <div class="history-item-header">
                        <span class="history-item-topic">${conv.topic}</span>
                        <span class="history-item-time">${date} ${time}</span>
                    </div>
                    <div class="history-item-content">
                        <strong>You:</strong> ${conv.user_input.substring(0, 100)}...
                        <br>
                        <strong>Nova:</strong> ${conv.ai_response.substring(0, 100)}...
                    </div>
                `;
                
                this.historyList.appendChild(historyItem);
            });
            
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    
    async loadAIStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/ai-status`);
            if (!response.ok) throw new Error('Failed to load AI status');
            
            const data = await response.json();
            
            this.updateEvolutionLevel(data.personality.evolution_level);
            
            // Update progress
            const progress = data.evolution_progress;
            if (progress.current_level === 1) {
                const progressPercent = ((10 - progress.conversations_needed) / 10) * 100;
                this.evolutionProgress.style.width = `${progressPercent}%`;
                this.progressText.textContent = `${10 - progress.conversations_needed}/10 conversations`;
            } else if (progress.current_level === 2) {
                const progressPercent = ((50 - progress.conversations_needed) / 50) * 100;
                this.evolutionProgress.style.width = `${progressPercent}%`;
                this.progressText.textContent = `${50 - progress.conversations_needed}/50 conversations`;
            } else {
                this.evolutionProgress.style.width = '100%';
                this.progressText.textContent = 'Max level reached!';
            }
            
        } catch (error) {
            console.error('Error loading AI status:', error);
        }
    }
    
    updateEvolutionLevel(level) {
        this.evolutionLevel.textContent = level;
        this.currentLevel.textContent = level;
        
        // Update header status
        document.getElementById('evolutionLevel').textContent = level;
    }
    
    updateSpeechSettings() {
        // Settings are applied in speakText method
    }
    
    autoResizeTextarea() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });
    }
    
    showLoading() {
        this.loadingOverlay.classList.add('show');
        this.sendBtn.disabled = true;
    }
    
    hideLoading() {
        this.loadingOverlay.classList.remove('show');
        this.sendBtn.disabled = false;
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.toastContainer.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize the AI Friend when the page loads
let aiApp;
document.addEventListener('DOMContentLoaded', () => {
    aiApp = new AIFriend();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Additional utility functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
        return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
        return Math.floor(diff / 60000) + ' minutes ago';
    } else if (diff < 86400000) { // Less than 1 day
        return Math.floor(diff / 3600000) + ' hours ago';
    } else {
        return date.toLocaleDateString();
    }
}

// Error handling for uncaught promises
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    // You could show a toast notification here
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('Back online');
    // You could show a toast notification here
});

window.addEventListener('offline', () => {
    console.log('Gone offline');
    // You could show a toast notification here
});