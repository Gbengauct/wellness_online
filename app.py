from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 Get API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'response': 'Please type a message.'})
    
    if not GEMINI_API_KEY:
        return jsonify({'response': '⚠️ API key missing. Please add GEMINI_API_KEY to environment variables.'})
    
    try:
        # ✅ USING THE CORRECT, WORKING MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are a compassionate Wellness Guide AI. Provide helpful, empathetic, and practical wellness advice. Keep responses short, warm, and actionable. User: {user_message}"
                }]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        # Check if we got a valid response
        if response.status_code == 200:
            data = response.json()
            try:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({'response': ai_response})
            except (KeyError, IndexError):
                return jsonify({'response': f'⚠️ Unexpected response format: {data}'})
        else:
            # Try to get error message
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            except:
                error_msg = response.text
            
            return jsonify({'response': f'⚠️ API Error ({response.status_code}): {error_msg}'})
            
    except requests.exceptions.Timeout:
        return jsonify({'response': '⏰ Timeout. Please try again.'})
    except requests.exceptions.ConnectionError:
        return jsonify({'response': '🔌 Connection error. Check internet.'})
    except Exception as e:
        return jsonify({'response': f'⚠️ Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
