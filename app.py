from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 Get API key from environment
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    if not user_message:
        return jsonify({'response': 'Please type a message.'})
    
    if not OPENROUTER_API_KEY:
        return jsonify({'response': '⚠️ API key missing. Please add OPENROUTER_API_KEY to environment variables.'})
    
    try:
        # ✅ USING OPENROUTER API (WORKS PERFECTLY)
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        payload = {
            "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a compassionate Wellness Guide AI. Provide helpful, empathetic, and practical wellness advice. Keep responses warm, supportive, and actionable. Never give medical advice."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://wellness-guide-ai.onrender.com",
            "X-Title": "Wellness Guide AI"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        else:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', str(error_data))
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
