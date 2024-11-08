from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import process_query, llm  # Import your RAG function
from langchain.memory import ConversationSummaryMemory
import uuid


app = Flask(__name__)

# Configure CORS for specific routes and options
CORS(app, resources={r"/chat": {"origins": "http://localhost:3000"}}, 
     supports_credentials=True,
     methods=["POST", "OPTIONS"],
     allow_headers=["Content-Type"])


# In-memory storage for sessions (use a persistent storage like Redis or a database for production)
conversations = {}

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    # Extract data from the request
    data = request.json
    user_query = data.get('message')
    session_id = data.get('session_id')  # Get session ID from the request

    if not session_id:
        session_id = str(uuid.uuid4())  # Generate a new session ID if not provided

    # Initialize memory for new sessions
    if session_id not in conversations:
        conversations[session_id] = ConversationSummaryMemory(
            llm=llm,  # Ensure 'llm' is accessible within process_query or pass appropriately
            return_messages=True
        )

    # Retrieve the memory associated with the session
    memory = conversations[session_id]

    # Process the user's query with the current session's memory
    response_text = process_query(user_query, memory)

    # Return the response along with the session ID
    return jsonify({'response': response_text, 'session_id': session_id})

# Debug output for request and response headers
@app.after_request
def after_request(response):
    print(f"Request from origin: {request.headers.get('Origin')}")
    print(f"Response headers: {response.headers}")
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
    