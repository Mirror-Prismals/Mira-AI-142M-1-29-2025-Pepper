from flask import Flask, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__)

# Load GPT-2 model and tokenizer
model = GPT2LMHeadModel.from_pretrained(r"checkpoint-2400")
tokenizer = GPT2Tokenizer.from_pretrained(r"checkpoint-2400")

@app.route("/")
def navi_os():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Mrror</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #F59E0B;
                color: #FFFFFF;
                font-family: 'Courier New', Courier, monospace;
                overflow: hidden;
            }
            #navi-terminal {
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                height: 100vh;
                padding: 20px;
                box-sizing: border-box;
            }
            .output {
                flex-grow: 1;
                overflow-y: auto;
                white-space: pre-wrap;
                padding-bottom: 20px;
            }
            .output span {
                display: block;
                margin-bottom: 5px;
                color: #FFFFFF;
                animation: rainbow 2s linear infinite;
            }
            @keyframes rainbow {
        
                85% { color: #008080; }
              
            }
            .input-area {
                display: flex;
                align-items: center;
            }
            .prompt {
                color: #FFFFFF;
            }
            #input-field {
                flex-grow: 1;
                background: transparent;
                border: none;
                color: #FFFFFF;
                font-family: 'Courier New', Courier, monospace;
                font-size: 16px;
                outline: none;
                caret-color: #00ffcc;
            }
            #input-field::placeholder {
                color: #FFFFFF;
                opacity: 0.7;
            }
            #cursor {
                animation: none;
                color: #FFFFFF;
                font-weight: bold;
            }
            @keyframes blink {
                50% {
                    opacity: 1;
                }
            }
            .button-container {
                margin-top: 10px;
            }
            button {
                background-color: #FFFFFF;
                border: none;
                padding: 10px;
                color: black;
                font-size: 14px;
                cursor: pointer;
                margin-right: 5px;
            }
            button:hover {
                background-color: #333333;
            }
        </style>
    </head>
    <body>
        <div id="navi-terminal">
            <div class="output" id="output"></div>
            <div class="input-area">
                <span class="prompt">></span>
                <input id="input-field" type="text" placeholder="Enter your command..." autofocus>
                <span id="cursor">_</span>
            </div>
            <div class="button-container">
                <button id="char-mode-btn">Character Mode</button>
                <button id="word-mode-btn">Word Mode</button>
                <button id="normal-mode-btn">Normal Mode</button>
            </div>
        </div>

        <script>
            const inputField = document.getElementById("input-field");
            const outputDiv = document.getElementById("output");

            // Variables to control the mode
            let mode = "normal";  // default mode is normal

            // Switch modes
            document.getElementById("char-mode-btn").addEventListener("click", () => {
                mode = "character";
            });
            document.getElementById("word-mode-btn").addEventListener("click", () => {
                mode = "word";
            });
            document.getElementById("normal-mode-btn").addEventListener("click", () => {
                mode = "normal";
            });

            inputField.addEventListener("keydown", async (e) => {
                if (e.key === "Enter") {
                    const prompt = inputField.value.trim();
                    if (prompt) {
                        // Display user input in terminal
                        outputDiv.innerHTML += `<span>> ${prompt}</span>`;
                        outputDiv.scrollTop = outputDiv.scrollHeight;

                        // Send to backend
                        try {
                            const response = await fetch('/generate', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ prompt: prompt, max_length: 150 })
                            });
                            const data = await response.json();
                            const generatedText = data.generated_text;

                            // Handle different modes
                            if (mode === "character") {
                                let charIndex = 0;
                                const animateTextCharacter = () => {
                                    if (charIndex < generatedText.length) {
                                        outputDiv.innerHTML += `<span>${generatedText[charIndex]}</span>`;
                                        charIndex++;
                                        outputDiv.scrollTop = outputDiv.scrollHeight;
                                        setTimeout(animateTextCharacter, 50); // Adjust delay to control animation speed
                                    }
                                };
                                animateTextCharacter();
                            } else if (mode === "word") {
                                const words = generatedText.split(' '); 
                                let wordIndex = 0;
                                const animateTextWord = () => {
                                    if (wordIndex < words.length) {
                                        outputDiv.innerHTML += `<span>${words[wordIndex]}</span>`;
                                        wordIndex++;
                                        outputDiv.scrollTop = outputDiv.scrollHeight;
                                        setTimeout(animateTextWord, 300); // Adjust delay to control animation speed
                                    }
                                };
                                animateTextWord();
                            } else {
                                // Normal mode (no animation)
                                outputDiv.innerHTML += `<span>${generatedText}</span>`;
                                outputDiv.scrollTop = outputDiv.scrollHeight;
                            }
                        } catch (error) {
                            outputDiv.innerHTML += `<span class="error">[Error: Unable to connect]</span>`;
                        }

                        inputField.value = ""; // Clear input field
                        outputDiv.scrollTop = outputDiv.scrollHeight; // Auto-scroll
                    }
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/generate', methods=['POST'])
def generate_text():
    data = request.get_json()
    prompt = data.get("prompt", "")
    max_length = data.get("max_length", 150)

    # Generate text using GPT-2
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return jsonify({ "generated_text": generated_text })

if __name__ == "__main__":
    app.run(debug=True)
