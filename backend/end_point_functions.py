from flask import request, Response, jsonify 
from elevenlabs.client import ElevenLabs
import json,os
from scripts.AiModel import agent_executor
from scripts.tool import should_close
import pyttsx3
from langchain.agents import AgentExecutor
# Initialize client here or use a global one if appropriate for Flask context
client = ElevenLabs(api_key=os.getenv("elevenlabs_Api_key"))
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

    