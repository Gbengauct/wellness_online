from flask import Flask, render_template, request, jsonify
import requests
import socket
import os

app = Flask(__name__)

# Try to get the local IP of your computer where Ollama is running
def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "127.0.0.1"  # Fallback to localhost

OLLAMA_HOST = os.environ.get('OLLAMA_HOST', get_local_ip())
OLLAMA_PORT = os.environ.get('OLLAMA_PORT', '11434')
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'response': 'Please type a message.'})
    
    try:
        # Send request to Ollama running on your PC
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "tinyllama",
                "prompt": f"You are a compassionate Wellness Guide AI. Provide helpful, empathetic, and practical wellness advice. User: {user_message}",
                "stream": False,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            ai_response = response.json().get('response', 'I am here to help. Please try again.')
            return jsonify({'response': ai_response})
        else:
            return jsonify({'response': f'⚠️ Ollama error: {response.status_code}. Make sure your PC is on and Ollama is running.'})
            
    except requests.exceptions.Timeout:
        return jsonify({'response': '⏰ Request timed out. Please try again.'})
    except requests.exceptions.ConnectionError:
        return jsonify({'response': '🔌 Cannot connect to Ollama on your PC. Please make sure it is running and your PC is on.'})
    except Exception as e:
        return jsonify({'response': f'⚠️ Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
