from flask import Flask, request, Response, jsonify
import json
import os
import requests

# API Configuration - Load from environment variables
API_CONFIG = {
    "api_key": os.getenv("CLAUDE_API_KEY", ""),
    "base_url": os.getenv("CLAUDE_BASE_URL", "https://www.dmxapi.cn/v1"),
    "model": os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
}

app = Flask(__name__)

# CORS headers for all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/api/test', methods=['GET'])
def simple_test():
    return jsonify({
        "status": "Flask is working on Vercel!",
        "api_key_configured": bool(API_CONFIG["api_key"])
    })

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def handle_chat():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        # Check if API key is configured
        if not API_CONFIG["api_key"]:
            return jsonify({'error': 'API key not configured'}), 500
        
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
                    error_data = json.dumps({'error': f'API request failed with status {response.status_code}'})
                    yield f"data: {error_data}\n\n"
                    return
                
                # Stream the response
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_content = line[6:]  # Remove 'data: ' prefix
                            if data_content.strip() == '[DONE]':
                                done_data = json.dumps({'done': True})
                                yield f"data: {done_data}\n\n"
                                break
                            try:
                                chunk_data = json.loads(data_content)
                                output = json.dumps(chunk_data)
                                yield f"data: {output}\n\n"
                            except json.JSONDecodeError:
                                continue
                
                # Ensure connection is properly closed
                response.close()
                
            except requests.exceptions.Timeout:
                error_data = json.dumps({'error': 'Request timed out'})
                yield f"data: {error_data}\n\n"
            except requests.exceptions.RequestException as e:
                error_data = json.dumps({'error': f'Request failed: {str(e)}'})
                yield f"data: {error_data}\n\n"
            except Exception as e:
                error_data = json.dumps({'error': f'Server error: {str(e)}'})
                yield f"data: {error_data}\n\n"
        
        return Response(generate(), content_type='text/plain', headers={
            'Cache-Control': 'no-cache',
            'Connection': 'close'
        })
                
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api', methods=['GET'])
@app.route('/api/', methods=['GET'])
def handle_api_info():
    return jsonify({
        'message': 'FakeClippy API is running', 
        'endpoints': ['/api/chat', '/api/test'],
        'api_key_configured': bool(API_CONFIG["api_key"])
    })

# 直接导出 app，无需自定义 handler

