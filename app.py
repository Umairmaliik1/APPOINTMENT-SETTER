from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from backend.end_point_functions import chat, text_to_speech_elevenlabs, save_availability,save_through_file
from flask import request, jsonify

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
        
    data = request.get_json()
    name = data.get('name')
    desc=data.get('description')
    email = data.get('email')
    available_dates = data.get('availableDates')  # Should be a list
    time_description = data.get('timeDescription')
            # Validate all fields
    if not all([name, email, available_dates, time_description]):
        return jsonify({"error": "Missing required fields."}), 400
    try:
        save_availability(name,desc,email,available_dates,time_description)
        return jsonify({"message": "Availability saved successfully."}), 200
    except Exception as e: 
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/savethroughFile', methods=['POST'])
def save_throught_file_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and file.filename.endswith('.xlsx'):
        try:
            save_through_file(file)
            return jsonify({
                "message": "Excel converted and saved to admin_availability.json with nested details",
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Only .xlsx files are supported"}), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

