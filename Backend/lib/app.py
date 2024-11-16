from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import process_query, llm  # Import your RAG function
from langchain.memory import ConversationBufferMemory
import uuid
import whisper
import os 


app = Flask(__name__)

# Configure CORS for specific routes and options
CORS(app, resources={
    r"/chat": {"origins": "http://localhost:3000"},
    r"/transcribe": {"origins": "http://localhost:3000"}
}, 
supports_credentials=True,
methods=["POST", "OPTIONS"],
allow_headers=["Content-Type"])

model = whisper.load_model("base")

# In-memory storage for sessions (use a persistent storage like Redis or a database for production)
conversations = {}

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    # Save the uploaded audio file temporarily
    audio_path = os.path.join('/tmp', audio_file.filename)
    audio_file.save(audio_path)
    
    try:
        # Transcribe the audio file using Whisper
        result = model.transcribe(audio_path)
        transcription = result['text']
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
    
    return jsonify({'transcription': transcription})

@app.route('/chat', methods=['POST'])
def chat():

    data = request.json
    user_query = data.get('message')
    session_id = data.get('session_id') 

    if not session_id:
        session_id = str(uuid.uuid4())

    if session_id not in conversations:
        conversations[session_id] = ConversationBufferMemory(
        memory_key="history",
        return_messages=True
    )
        
    response_text = process_query(user_query)

    return jsonify({'response': response_text, 'session_id': session_id})

@app.after_request
def after_request(response):
    print(f"Request from origin: {request.headers.get('Origin')}")
    print(f"Response headers: {response.headers}")
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)