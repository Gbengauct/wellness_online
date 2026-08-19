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
        # ✅ USING THE NEW INTERACTIONS API (RECOMMENDED BY GOOGLE)
        url = "https://generativelanguage.googleapis.com/v1beta2/interactions"
        
        payload = {
            "model": "gemini-3.6-flash",
            "input": user_message,
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract response from the new API structure
            ai_response = None
            
            # Method 1: Check output_text (simplest)
            if data.get('output_text'):
                ai_response = data['output_text']
            
            # Method 2: Extract from steps
            if not ai_response:
                for step in data.get('steps', []):
                    if step.get('type') == 'model_output':
                        for content in step.get('content', []):
                            if content.get('type') == 'text':
                                ai_response = content.get('text')
                                break
                    if ai_response:
                        break
            
            if ai_response:
                return jsonify({'response': ai_response})
            else:
                return jsonify({'response': f'⚠️ No response. Raw data: {str(data)[:200]}'})
                
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
