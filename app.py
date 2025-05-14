from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from backend.end_point_functions import chat, text_to_speech_elevenlabs, save_availability

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  

@app.route("/chat-booking", methods=["POST"])
def chat_booking():
    return chat()

@app.route("/api/tts", methods=["POST"])
def tts():
    return text_to_speech_elevenlabs()

@app.route('/api/save-availability', methods=['POST'])
def save_availability_route():
    return save_availability()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

