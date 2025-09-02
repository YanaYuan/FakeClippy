from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            messages = data.get('messages', [])
            
            # API Configuration - Load from environment variables
            api_key = os.getenv("CLAUDE_API_KEY", "")
            base_url = os.getenv("CLAUDE_BASE_URL", "https://www.dmxapi.cn/v1")
            model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
            
            # Check if API key is configured
            if not api_key:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'error': 'API key not configured. Please set CLAUDE_API_KEY environment variable.'}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
            # Prepare the request to Claude API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            payload = {
                'model': model,
                'messages': messages,
                'stream': True,
                'max_tokens': 10000
            }
            
            # Set up streaming response
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            try:
                # Make streaming request to Claude API
                response = requests.post(
                    f'{base_url}/chat/completions',
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=30
                )
                
                if response.status_code != 200:
                    error_data = f"data: {json.dumps({'error': f'API request failed with status {response.status_code}'})}\n\n"
                    self.wfile.write(error_data.encode('utf-8'))
                    return
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_content = line[6:]  # Remove 'data: ' prefix
                            if data_content.strip() == '[DONE]':
                                done_data = f"data: {json.dumps({'done': True})}\n\n"
                                self.wfile.write(done_data.encode('utf-8'))
                                break
                            try:
                                chunk_data = json.loads(data_content)
                                response_line = f"data: {json.dumps(chunk_data)}\n\n"
                                self.wfile.write(response_line.encode('utf-8'))
                            except json.JSONDecodeError:
                                continue
                                
            except requests.exceptions.Timeout:
                error_data = f"data: {json.dumps({'error': 'Request timed out'})}\n\n"
                self.wfile.write(error_data.encode('utf-8'))
            except requests.exceptions.RequestException as e:
                error_data = f"data: {json.dumps({'error': f'Request failed: {str(e)}'})}\n\n"
                self.wfile.write(error_data.encode('utf-8'))
            except Exception as e:
                error_data = f"data: {json.dumps({'error': f'Server error: {str(e)}'})}\n\n"
                self.wfile.write(error_data.encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'error': f'Server error: {str(e)}'}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def do_GET(self):
        # Handle GET requests
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = {'message': 'FakeClippy API is running', 'endpoints': ['/api/chat']}
        self.wfile.write(json.dumps(response).encode('utf-8'))
