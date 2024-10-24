from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import process_query  # Import your RAG function

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        # Handling preflight request
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    #this extracts the user's message from the JSON payload of the request  
    data = request.json
    user_query = data.get('message')
    
    # Process the query using your RAG pipeline
    response = process_query(user_query)
    
    return jsonify({'response': response})

@app.after_request
def after_request(response):
    print(f"Request from origin: {request.headers.get('Origin')}")
    print(f"Response headers: {response.headers}")
    return response

if __name__ == '__main__':
    # Run Flask server on localhost
    app.run(debug=True, host='127.0.0.1', port=5000)
