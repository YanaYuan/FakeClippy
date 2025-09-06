from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "simple test working"})

# Vercel WSGI handler
def handler(environ, start_response):
    return app(environ, start_response)
