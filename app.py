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
    
    try:
        # Using the new Interactions API format
        payload = {
            "model": "gemini-3.6-flash",  # ✅ Active model
            "input": user_message,
            # Optional: store the conversation history for context
            # "previous_interaction_id": "some_id"  # For multi-turn conversations
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        response = requests.post(API_URL, json=payload, headers=headers)
        data = response.json()
        
        if response.status_code == 200:
            # The new API returns a different structure
            # The response is in the 'steps' array
            ai_response = None
            for step in data.get('steps', []):
                if step.get('type') == 'model_output':
                    # Extract text from the content array
                    for content in step.get('content', []):
                        if content.get('type') == 'text':
                            ai_response = content.get('text')
                            break
                    if ai_response:
                        break
            
            if ai_response:
                return jsonify({'response': ai_response})
            else:
                # Fallback: try to get output_text if available
                output_text = data.get('output_text')
                if output_text:
                    return jsonify({'response': output_text})
                else:
                    return jsonify({'response': '⚠️ No response from AI. Please try again.'})
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown API error')
            return jsonify({'response': f'⚠️ API Error: {error_msg}'})
            
    except Exception as e:
        return jsonify({'response': f'⚠️ Error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
