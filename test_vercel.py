#!/usr/bin/env python3
"""
Local test script to simulate Vercel serverless environment
"""
import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Import the Vercel handler
from index import handler as vercel_handler

class TestHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/api/'):
            # Create a mock request object for the Vercel handler
            mock_handler = vercel_handler()
            mock_handler.path = self.path
            mock_handler.headers = self.headers
            mock_handler.rfile = self.rfile
            mock_handler.wfile = self.wfile
            mock_handler.send_response = self.send_response
            mock_handler.send_header = self.send_header
            mock_handler.end_headers = self.end_headers
            
            # Call the Vercel handler
            mock_handler.do_POST()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path.startswith('/api/'):
            # Create a mock request object for the Vercel handler
            mock_handler = vercel_handler()
            mock_handler.path = self.path
            mock_handler.headers = self.headers
            mock_handler.rfile = self.rfile
            mock_handler.wfile = self.wfile
            mock_handler.send_response = self.send_response
            mock_handler.send_header = self.send_header
            mock_handler.end_headers = self.end_headers
            
            # Call the Vercel handler
            mock_handler.do_GET()
        else:
            # Parse URL to remove query parameters
            parsed_url = urlparse(self.path)
            clean_path = parsed_url.path
            
            # Serve static files from the static directory
            if clean_path == '/':
                file_path = 'static/index.html'
            else:
                file_path = 'static' + clean_path
            
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html')
                elif file_path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>404 Not Found</h1><p>File not found: ' + file_path.encode() + b'</p>')

if __name__ == '__main__':
    # Set environment variables for testing
    os.environ['CLAUDE_API_KEY'] = os.getenv('CLAUDE_API_KEY', '')
    if not os.environ['CLAUDE_API_KEY']:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('CLAUDE_API_KEY='):
                        os.environ['CLAUDE_API_KEY'] = line.split('=', 1)[1].strip()
        except FileNotFoundError:
            pass
    
    server = HTTPServer(('localhost', 8080), TestHTTPRequestHandler)
    print("🧪 Vercel simulation server running at http://localhost:8080")
    print("   This simulates how your app will work on Vercel")
    print("   Test it, then compare with the local dev server at http://localhost:5000")
    server.serve_forever()
