from flask import Flask, render_template, request, jsonify
import requests
import os
import json

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
    
    # Check if API key exists
    if not GEMINI_API_KEY:
        return jsonify({'response': '⚠️ API key not configured. Please add GEMINI_API_KEY to environment variables.'})
    
    try:
        # ✅ USING THE SIMPLEST, MOST RELIABLE MODEL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are a compassionate Wellness Guide AI. Provide helpful, empathetic, and practical wellness advice. User: {user_message}"
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Check if response is valid JSON
        try:
            data = response.json()
        except:
            return jsonify({'response': f'⚠️ Invalid response from API. Status: {response.status_code}. Please check your API key.'})
        
        if response.status_code == 200:
            try:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({'response': ai_response})
            except (KeyError, IndexError):
                return jsonify({'response': f'⚠️ Unexpected API response structure: {data}'})
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            return jsonify({'response': f'⚠️ API Error ({response.status_code}): {error_msg}'})
            
    except requests.exceptions.Timeout:
        return jsonify({'response': '⏰ Request timed out. Please try again.'})
    except requests.exceptions.ConnectionError:
        return jsonify({'response': '🔌 Connection error. Please check your internet.'})
    except Exception as e:
        return jsonify({'response': f'⚠️ Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
