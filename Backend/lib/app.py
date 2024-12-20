from flask import Flask, request, jsonify
from flask_cors import CORS
from rag import process_query, llm  # Import your RAG function
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import uuid
import openai
from openai import OpenAI
import whisper
import os


app = Flask(__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

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


@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        print("Debug: Received request")
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        print(f"Debug: Audio filename: {audio_file.filename}")
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Convert FileStorage to a file-like object
        audio_file_object = audio_file.stream

        # Use OpenAI Whisper API to transcribe the audio
        transcript = client.audio.transcriptions.create(
            file=audio_file_object,
            model="whisper-1"
        )
        
        transcribed_text = transcript.text
        response_text = process_query(transcribed_text)

        return jsonify({
            'success': True,
            'text': transcribed_text,
            'response': response_text
        }), 200
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.after_request
def after_request(response):
    print(f"Request from origin: {request.headers.get('Origin')}")
    print(f"Response headers: {response.headers}")
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
    

