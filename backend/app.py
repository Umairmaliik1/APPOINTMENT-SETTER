from flask import Flask, request, jsonify
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain.prompts import SystemMessagePromptTemplate
import json
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask import request, Response, jsonify 
from elevenlabs.client import ElevenLabs
# from scripts.TTS_test_11 import tts
# from scripts/TT_test_dg import listen_and_recognize

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  
should_close = False

# Define tools
@tool
def collect_user_info(input: str) -> str:
    """
    Tool to process user responses when collecting name, date and time for appointment, and for example user says example at gmail.com or
    example at the rate gamil.com it means he is trying to say example@gmail.com and also if you find any spaces before @ or
    after @ then remove them.
    The agent controls the logic, not this tool. And most importantly if you are not given any query then tell the user 
    that you are unable to understand what i said.
    """
    return input

@tool
def save_info(info: str) -> str:
    """
    Save collected user info to a JSON file. Info must contain 'name', 'date_time_appointment', and 'email'.
    """
    try:
        user_data = json.loads(info)
        required_fields = ['name', 'date_time_appointment', 'email']
        if not all(field in user_data for field in required_fields):
            return "Error: Missing required fields."

        data = []
        if os.path.exists('user_info.json'):
            with open('user_info.json', 'r') as f:
                try:
                    existing_data = json.load(f)
                    if isinstance(existing_data, dict):
                        data = [existing_data]
                    elif isinstance(existing_data, list):
                        data = existing_data
                except json.JSONDecodeError:
                    data = []

        data.append(user_data)
        with open('user_info.json', 'w') as f:
            json.dump(data, f, indent=4)

        return "User info saved successfully."
    except Exception as e:
        return f"Save error: {str(e)}"

@tool
def close_chat() -> str:
    """
    Ends the chat when booking is done and confirmation email will be sent soon.
    """
    global should_close
    should_close = True
    return "Ending the call."

tools = [collect_user_info, save_info, close_chat]

# Load and customize prompt
base_prompt = hub.pull("hwchase17/structured-chat-agent")

custom_format = """"
You are Chris from MindRind who is created to help the user. First introduce yourself. 
If the user asks about your company, explain that MindRind is a product-based software house.
After answering 2-3 general queries, ask the user if they want to book an appointment.
Collect name, date/time, and email in a structured way using tools.
When done, ask if they want to end the call.
If yes, use close_chat tool and say goodbye. If no, ask what else they need.
Always follow this format:

Question: user's message
Thought: what should I do now?
Action:
```json
{{
  "action": "tool_name",
  "action_input": "input to tool"
}}
Observation: result of the tool
... (Repeat Thought/Action/Observation)

Thought: I have everything
Action:
{{
  "action": "save_info",
  "action_input": "{{\\"name\\": \\"John\\", \\"date_time_appointment\\": \\"15th May at evening\\", \\"email\\": \\"john@example.com\\"}}"
}}
To respond directly to the user, use:
{{
  "action": "Final Answer",
  "action_input": "message to user"
}}
Begin!
"""

base_prompt.messages[0] = SystemMessagePromptTemplate.from_template(
    custom_format + "\n\n" + base_prompt.messages[0].prompt.template
)

llm = GoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=os.getenv("gen_ai_API_key"),
    temperature=1,
)

agent = create_structured_chat_agent(llm, tools, base_prompt)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, handle_parsing_errors=True)

@app.route("/chat-booking", methods=["POST"])
def chat():
    global should_close
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Missing user message"}), 400

    if should_close:
        return jsonify({"response": "Goodbye!", "end": True})

    try:
        response = agent_executor.invoke({"input": user_input})
        return jsonify({"response": response["output"], "end": should_close})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/tts", methods=["POST"])
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
    
@app.route('/api/save-availability', methods=['POST'])
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

