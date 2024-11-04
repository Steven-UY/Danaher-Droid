from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import process_query  # Import your RAG function
from typing import List
import uuid

app = Flask(__name__)

# Configure CORS for specific routes and options
CORS(app, resources={r"/chat": {"origins": "http://localhost:3000"}}, 
     supports_credentials=True,
     methods=["POST", "OPTIONS"],
     allow_headers=["Content-Type"])


# Store conversations in memory (replace with database for production)
conversations = {}

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        # Handling preflight request
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Process the user's message
    data = request.json
    user_query = data.get('message')
    history = data.get('history', [])

    # **Remove the tuple conversion**
    # formatted_history = [(msg['content'], msg['sender']) for msg in history]
    formatted_history = history  # Pass history as a list of dicts

    response = process_query(user_query, formatted_history)

    # Add CORS headers for the main response
    response = jsonify({'response': response})
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Debug output for request and response headers
@app.after_request
def after_request(response):
    print(f"Request from origin: {request.headers.get('Origin')}")
    print(f"Response headers: {response.headers}")
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
