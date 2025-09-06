from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# API Configuration - Load from environment variables or use defaults
API_CONFIG = {
    "api_key": os.getenv("CLAUDE_API_KEY", ""),
    "base_url": os.getenv("CLAUDE_BASE_URL", "https://www.dmxapi.cn/v1"),
    "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
}

# If no API key in environment, try to load from .env file manually
if not API_CONFIG["api_key"]:
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('CLAUDE_API_KEY='):
                    API_CONFIG["api_key"] = line.split('=', 1)[1].strip()
                elif line.startswith('CLAUDE_BASE_URL='):
                    API_CONFIG["base_url"] = line.split('=', 1)[1].strip()
                elif line.startswith('CLAUDE_MODEL='):
                    API_CONFIG["model"] = line.split('=', 1)[1].strip()
    except FileNotFoundError:
        print("Warning: .env file not found. Please create one with your API configuration.")
    except Exception as e:
        print(f"Warning: Could not read .env file: {e}")

if not API_CONFIG["api_key"]:
    print("Warning: No API key configured. Please set CLAUDE_API_KEY environment variable or create .env file.")

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('public', filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # Prepare the request to Claude API
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_CONFIG["api_key"]}'
        }
        
        payload = {
            'model': API_CONFIG['model'],
            'messages': messages,
            'stream': True,
            'max_tokens': 10000
        }
        
        def generate():
            try:
                # Make streaming request to Claude API
                response = requests.post(
                    f'{API_CONFIG["base_url"]}/chat/completions',
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=30
                )
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'API request failed with status {response.status_code}'})}\n\n"
                    return
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_content = line[6:]  # Remove 'data: ' prefix
                            if data_content.strip() == '[DONE]':
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                break
                            try:
                                chunk_data = json.loads(data_content)
                                yield f"data: {json.dumps(chunk_data)}\n\n"
                            except json.JSONDecodeError:
                                continue
                                
            except requests.exceptions.Timeout:
                yield f"data: {json.dumps({'error': 'Request timed out'})}\n\n"
            except requests.exceptions.RequestException as e:
                yield f"data: {json.dumps({'error': f'Request failed: {str(e)}'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': f'Server error: {str(e)}'})}\n\n"
        
        return Response(generate(), mimetype='text/plain', headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
