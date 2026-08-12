from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 This reads the key from Render's Environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'response': 'Please type a message.'})
    
    try:
        # ✅ USING THE CORRECT, ACTIVE MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are a compassionate Wellness Guide AI. Provide helpful, empathetic, and practical wellness advice. User: {user_message}"
                }]
            }]
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            ai_response = data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'response': ai_response})
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown API error')
            return jsonify({'response': f'⚠️ API Error: {error_msg}'})
            
    except Exception as e:
        return jsonify({'response': f'⚠️ Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
