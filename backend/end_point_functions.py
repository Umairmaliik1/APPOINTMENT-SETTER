from flask import request,jsonify 
from elevenlabs.client import ElevenLabs
import json,os
from scripts.AiModel import agent_executor
from scripts.tool import should_close
import pyttsx3
import os,json
import pandas as pd
import uuid
from livekit.api import LiveKitAPI,ListRoomsRequest
from livekit import api
# Initialize client here or use a global one if appropriate for Flask context
client = ElevenLabs(api_key=os.getenv("elevenlabs_Api_key"))
async def generate_room_name():
    name="room-"+str(uuid.uuid4())[:8]
    rooms=await get_rooms()
    while name in rooms:
        name="room-"+str(uuid.uuid4())[:8]

    return name 
async def get_rooms():
    api=LiveKitAPI()
    rooms=await api.room.list_rooms(ListRoomsRequest())
    await api.aclose()
    return [room.name for room in rooms.rooms]
def save_through_file(file):
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
            return True
def get_agent_response(input:str)-> str:
    return agent_executor.invoke({"input": input})
def chat():
    should_close
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Missing user message"}), 400

    if should_close:
        return jsonify({"response": "Goodbye!", "end": True})

    try:
        response = get_agent_response(user_input)
        return jsonify({"response": response["output"], "end": should_close})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def text_to_speech_elevenlabs():
    text= request.json.get("text")
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
def save_availability(name,desc, email, available_dates, time_description):
    # Prepare data to be saved
    availability_entry = {
        "name": name,
        "description": desc,
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

    return True

    