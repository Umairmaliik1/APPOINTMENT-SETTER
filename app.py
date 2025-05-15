from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from backend.end_point_functions import chat, text_to_speech_elevenlabs, save_availability
from flask import request, jsonify
import os,json
import pandas as pd
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
            # Save the uploaded Excel file temporarily
            os.makedirs("temp", exist_ok=True)
            temp_excel_path = os.path.join("temp", file.filename)
            file.save(temp_excel_path)

            # Read Excel data
            df = pd.read_excel(temp_excel_path, engine='openpyxl')

            # Convert and reshape each record
            reshaped_data = []
            for _, row in df.iterrows():
                doctor = {
                    "name": row["name"],
                    "description": row["description"],
                    "details": {
                        "email": row["email"],
                        "availableDates_start": row["availableDates_start"],
                        "availableDates_end": row["availableDates_end"],
                        "timeDescription": row["timeDescription"]
                    }
                }
                reshaped_data.append(doctor)

            # Save reshaped data to admin_availability.json
            output_json_path = "admin_availability.json"
            with open(output_json_path, 'w', encoding='utf-8') as json_file:
                json.dump(reshaped_data, json_file, indent=4, ensure_ascii=False)

            # Clean up temp file
            os.remove(temp_excel_path)

            return jsonify({
                "message": "Excel converted and saved to admin_availability.json with nested details",
                "data": reshaped_data
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Only .xlsx files are supported"}), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

