// Auto-resize textarea
const messageInput = document.getElementById('messageInput');
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});

// Handle Enter key
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Send suggestion
function sendSuggestion(text) {
    messageInput.value = text;
    sendMessage();
}

// Send message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear input and reset height
    input.value = '';
    input.style.height = 'auto';
    
    // Disable send button
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    
    // Remove welcome message if it exists
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Add user message
    addMessage('user', message);
    
    // Add typing indicator
    addTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add AI response
        addMessage('ai', data.response);
        
        // Update document count if changed
        if (data.doc_count !== undefined) {
            updateDocCount(data.doc_count);
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('ai', '❌ Sorry, there was an error processing your request. Please try again.');
    } finally {
        sendButton.disabled = false;
        input.focus();
    }
}

// Add message to chat
function addMessage(type, text) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = type === 'user' ? '👤' : '🤖';
    const author = type === 'user' ? 'You' : 'FinBot Pioneer';
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">${author}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-text">${formatMessage(text)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message text (basic markdown-like formatting)
function formatMessage(text) {
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Bold text
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic text
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Code blocks
    text = text.replace(/`(.*?)`/g, '<code>$1</code>');
    
    return text;
}

// Add typing indicator
function addTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai-message typing-message';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">FinBot Pioneer</span>
            </div>
            <div class="message-text typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Clear conversation
async function clearConversation() {
    if (!confirm('Are you sure you want to clear the conversation?')) {
        return;
    }
    
    try {
        const response = await fetch('/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">👋</div>
                    <h2>Welcome to FinBot Pioneer!</h2>
                    <p>Your intelligent investment assistant. I analyze financial data, provide market insights, and help you make informed investment decisions.</p>
                    <div class="suggestions">
                        <div class="suggestion-title">Try asking:</div>
                        <button class="suggestion-chip" onclick="sendSuggestion('Should I invest in Reliance?')">
                            Should I invest in Reliance?
                        </button>
                        <button class="suggestion-chip" onclick="sendSuggestion('Analyze TCS stock for me')">
                            Analyze TCS stock for me
                        </button>
                        <button class="suggestion-chip" onclick="sendSuggestion('What documents do you have?')">
                            What documents do you have?
                        </button>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error clearing conversation:', error);
        alert('Failed to clear conversation. Please try again.');
    }
}

// Reload documents
async function reloadDocuments() {
    try {
        const response = await fetch('/reload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateDocCount(data.doc_count);
            
            // Update document list
            const docList = document.getElementById('docList');
            if (data.doc_names && data.doc_names.length > 0) {
                docList.innerHTML = data.doc_names.map(name => `<li>${name}</li>`).join('');
            } else {
                docList.innerHTML = '<li>No documents found</li>';
            }
            
            // Show success message in chat
            addMessage('ai', `✅ Successfully reloaded ${data.doc_count} document(s) from the data folder.`);
        }
    } catch (error) {
        console.error('Error reloading documents:', error);
        addMessage('ai', '❌ Failed to reload documents. Please try again.');
    }
}

// Update document count
function updateDocCount(count) {
    const docCountElement = document.getElementById('docCount');
    if (docCountElement) {
        docCountElement.textContent = count;
    }
}

// Focus input on load
window.addEventListener('load', () => {
    messageInput.focus();
});
