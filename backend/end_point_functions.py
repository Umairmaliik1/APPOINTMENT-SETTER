from flask import request, Response, jsonify 
from elevenlabs.client import ElevenLabs
import json,os
from scripts.AiModel import model

def chat():
    global should_close
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Missing user message"}), 400

    if should_close:
        return jsonify({"response": "Goodbye!", "end": True})

    try:
        response = model.agent_executor.invoke({"input": user_input})
        return jsonify({"response": response["output"], "end": should_close})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def text_to_speech_elevenlabs():
    text_to_speak = request.json.get("text")
    if not text_to_speak:
        return jsonify({"error": "Missing text"}), 400

    try:
        # Initialize client here or use a global one if appropriate for Flask context
        client = ElevenLabs(api_key=os.getenv("elevenlabs_Api_key"))
        
        audio_stream_generator = client.text_to_speech.convert_as_stream(
            text=text_to_speak,
            voice_id="JBFqnCBsd6RMkjVDRZzb", # Your chosen voice_id
            model_id="eleven_multilingual_v2"
        )
        
        # Collect all audio byte chunks
        audio_bytes_list = []
        for chunk in audio_stream_generator:
            if isinstance(chunk, bytes):
                audio_bytes_list.append(chunk)
        
        full_audio_bytes = b"".join(audio_bytes_list)

        if not full_audio_bytes:
            return jsonify({"error": "No audio data generated"}), 500

        return Response(full_audio_bytes, mimetype="audio/mpeg")

    except Exception as e:
        print(f"ElevenLabs TTS Error: {e}") # Log the error on the server
        return jsonify({"error": "TTS generation failed", "details": str(e)}), 500


def save_availability():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        available_dates = data.get('availableDates')  # Should be a list
        time_description = data.get('timeDescription')

        # Validate all fields
        if not all([name, email, available_dates, time_description]):
            return jsonify({"error": "Missing required fields."}), 400

        # Prepare data to be saved
        availability_entry = {
            "name": name,
            "details" :{
            "email": email,
            "availableDates": available_dates,
            "timeDescription": time_description
            }
        }

        # Read existing data
        file_path = 'admin_availability.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = []
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Append and save
        existing_data.append(availability_entry)
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=4)

        return jsonify({"message": "Admin availability saved successfully."}), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500