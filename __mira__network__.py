from flask import Flask, request, jsonify, render_template_string
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import json
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Conversations directory
CONVERSATIONS_DIR = 'conversations'
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# Load GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained(r"M:\")
tokenizer = GPT2Tokenizer.from_pretrained(r"M:\")

def save_conversation(conversation_id, messages):
    """Save a conversation to a JSON file"""
    filename = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    with open(filename, 'w') as f:
        json.dump(messages, f, indent=2)

def load_conversation(conversation_id):
    """Load a conversation from a JSON file"""
    filename = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def get_conversation_list():
    """Retrieve list of saved conversations"""
    return [f.replace('.json', '') for f in os.listdir(CONVERSATIONS_DIR) if f.endswith('.json')]

@app.route('/delete_conversation/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    try:
        filename = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
        if os.path.exists(filename):
            os.remove(filename)
            return jsonify({"status": "success", "message": "Conversation deleted"}), 200
        else:
            return jsonify({"status": "error", "message": "Conversation not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def navi_os():
    conversations = get_conversation_list()
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Mrror</title>
        <style>
            body {
                margin: 0;
                display: flex;
                height: 100vh;
                font-family: 'Courier New', Courier, monospace;
                background: #008080;
            }
            #conversations {
                width: 250px;
                background: #006666;
                padding: 20px;
                overflow-y: auto;
                color: white;
            }
            #navi-terminal {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                height: 100vh;
                padding: 20px;
                box-sizing: border-box;
                color: white;
            }
            .conversation-container {
                display: flex;
                align-items: center;
                margin-bottom: 5px;
            }
            .conversation-item {
                cursor: pointer;
                padding: 10px;
                flex-grow: 1;
                background: #005555;
            }
            .conversation-item:hover {
                background: #004444;
            }
            .delete-conversation {
                background: red;
                color: white;
                border: none;
                margin-left: 10px;
                padding: 5px 10px;
                cursor: pointer;
                font-size: 12px;
            }
            #new-conversation {
                background: #00ffcc;
                color: black;
                padding: 10px;
                text-align: center;
                cursor: pointer;
                margin-bottom: 10px;
            }
            .output {
                flex-grow: 1;
                overflow-y: auto;
                white-space: pre-wrap;
                padding-bottom: 20px;
            }
            .input-area {
                display: flex;
                align-items: center;
            }
            #input-field {
                flex-grow: 1;
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
                outline: none;
            }
            .user { color: #00ffcc; }
            .ai { color: #ffffff; }
        </style>
    </head>
    <body>
        <div id="conversations">
            <div id="new-conversation">New Conversation</div>
            <div id="conversation-list">
                {% for conv in conversations %}
                <div class="conversation-container">
                    <div class="conversation-item" data-id="{{ conv }}">{{ conv }}</div>
                    <button class="delete-conversation" data-id="{{ conv }}">✖</button>
                </div>
                {% endfor %}
            </div>
        </div>
        <div id="navi-terminal">
            <div class="output" id="output"></div>
            <div class="input-area">
                <span>></span>
                <input id="input-field" type="text" placeholder="Enter your message...">
            </div>
        </div>

        <script>
            let currentConversationId = null;

            function refreshConversationList() {
                fetch('/conversations')
                    .then(response => response.json())
                    .then(conversations => {
                        const conversationList = document.getElementById('conversation-list');
                        conversationList.innerHTML = ''; // Clear existing list
                        conversations.forEach(conv => {
                            const convContainer = document.createElement('div');
                            convContainer.classList.add('conversation-container');

                            const convElement = document.createElement('div');
                            convElement.classList.add('conversation-item');
                            convElement.setAttribute('data-id', conv);
                            convElement.textContent = conv;

                            const deleteButton = document.createElement('button');
                            deleteButton.textContent = '✖';
                            deleteButton.classList.add('delete-conversation');
                            deleteButton.setAttribute('data-id', conv);

                            convContainer.appendChild(convElement);
                            convContainer.appendChild(deleteButton);
                            conversationList.appendChild(convContainer);
                        });
                    });
            }

            document.getElementById('conversation-list').addEventListener('click', (e) => {
                if (e.target.classList.contains('delete-conversation')) {
                    const conversationId = e.target.getAttribute('data-id');
                    
                    if (confirm(`Are you sure you want to delete conversation ${conversationId}?`)) {
                        fetch(`/delete_conversation/${conversationId}`, {
                            method: 'DELETE'
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                if (currentConversationId === conversationId) {
                                    document.getElementById('output').innerHTML = '';
                                    currentConversationId = null;
                                }
                                refreshConversationList();
                            } else {
                                alert('Failed to delete conversation');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('Failed to delete conversation');
                        });
                    }
                } else if (e.target.classList.contains('conversation-item')) {
                    currentConversationId = e.target.getAttribute('data-id');
                    loadConversation(currentConversationId);
                }
            });

            document.getElementById('new-conversation').addEventListener('click', () => {
                currentConversationId = null;
                document.getElementById('output').innerHTML = '';
                
                fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        prompt: "", 
                        conversation_id: undefined 
                    })
                })
                .then(response => response.json())
                .then(data => {
                    currentConversationId = data.conversation_id;
                    refreshConversationList();
                });
            });

            function loadConversation(convId) {
                fetch(`/conversation/${convId}`)
                    .then(response => response.json())
                    .then(messages => {
                        const outputDiv = document.getElementById('output');
                        outputDiv.innerHTML = '';
                        messages.forEach(msg => {
                            outputDiv.innerHTML += `<div class="${msg.role}">${msg.content}</div>`;
                        });
                    });
            }

            document.getElementById('input-field').addEventListener('keydown', async (e) => {
                if (e.key === 'Enter') {
                    const prompt = e.target.value.trim();
                    if (prompt) {
                        const outputDiv = document.getElementById('output');
                        
                        outputDiv.innerHTML += `<div class="user">> ${prompt}</div>`;
                        
                        try {
                            const response = await fetch('/generate', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ 
                                    prompt: prompt, 
                                    conversation_id: currentConversationId || undefined 
                                })
                            });
                            const data = await response.json();
                            
                            currentConversationId = data.conversation_id;
                            
                            outputDiv.innerHTML += `<div class="ai">${data.generated_text}</div>`;
                            outputDiv.scrollTop = outputDiv.scrollHeight;

                            refreshConversationList();
                        } catch (error) {
                            outputDiv.innerHTML += `<div class="error">Error: ${error.message}</div>`;
                        }
                        
                        e.target.value = '';
                    }
                }
            });
        </script>
    </body>
    </html>
    ''', conversations=conversations)

@app.route('/conversations')
def list_conversations():
    conversations = get_conversation_list()
    return jsonify(conversations)

@app.route('/conversation/<conversation_id>')
def get_conversation(conversation_id):
    messages = load_conversation(conversation_id)
    return jsonify(messages)

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.get_json()
    prompt = data.get("prompt", "")
    conversation_id = data.get("conversation_id", str(uuid.uuid4()))
    max_length = data.get("max_length", 150)

    # Load existing conversation or start new
    conversation_history = load_conversation(conversation_id)

    # Add current message to conversation
    conversation_history.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    })

    # Generate response using context
    context = " ".join([msg['content'] for msg in conversation_history[-5:]])  # Use last 5 messages as context
    inputs = tokenizer.encode(context, return_tensors="pt")
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Add AI response to conversation
    conversation_history.append({
        "role": "ai",
        "content": generated_text,
        "timestamp": datetime.now().isoformat()
    })

    # Save updated conversation
    save_conversation(conversation_id, conversation_history)

    return jsonify({
        "generated_text": generated_text,
        "conversation_id": conversation_id
    })

if __name__ == "__main__":
    app.run(debug=True)
