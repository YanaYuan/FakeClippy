from flask import Flask, request, Response, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/test', methods=['GET'])
def simple_test():
    return jsonify({"status": "Flask is working on Vercel!"})

@app.route('/', methods=['POST', 'OPTIONS'])
@app.route('/chat', methods=['POST', 'OPTIONS'])
def handle_chat():
    if request.method == 'OPTIONS':
        response = Response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        return jsonify({"error": "Temporarily disabled for debugging"}), 200
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

# 直接导出 app，移除自定义 handler

