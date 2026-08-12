from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 This reads the key from Render's Environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ✅ The new, correct API endpoint for Interactions API
API_URL = "https://generativelanguage.googleapis.com/v1beta2/interactions"

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
        # Using the new Interactions API format as shown in the documentation
        payload = {
            "model": "gemini-3.6-flash",  # ✅ Active model from the docs
            "input": user_message,
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        # Check if response is valid JSON
        try:
            data = response.json()
        except:
            return jsonify({'response': f'⚠️ Invalid response from API. Status: {response.status_code}. Please check your API key.'})
        
        if response.status_code == 200:
            # Extract response from the new API structure (as shown in docs)
            ai_response = None
            
            # The response is in the 'steps' array
            for step in data.get('steps', []):
                if step.get('type') == 'model_output':
                    # Extract text from the content array
                    for content in step.get('content', []):
                        if content.get('type') == 'text':
                            ai_response = content.get('text')
                            break
                    if ai_response:
                        break
            
            # Fallback: try to get output_text if available (as shown in docs)
            if not ai_response:
                ai_response = data.get('output_text')
            
            if ai_response:
                return jsonify({'response': ai_response})
            else:
                return jsonify({'response': '⚠️ No response from AI. Please try again.'})
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
