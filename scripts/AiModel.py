#Perfectly functioning AI model for collecting user information.
import json
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain.prompts import SystemMessagePromptTemplate
from TTS_test_11 import tts
from STT_test_dg import listen_and_recognize
import os
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
            return "Error: Missing required fields. Need name, date and time for appointment, and email."

        data = []
        if os.path.exists('user_info.json'):
            with open('user_info.json', 'r') as f:
                try:
                    existing_data = json.load(f)
                    # If the existing data is a dict, convert it into a list
                    if isinstance(existing_data, dict):
                        data = [existing_data]
                    elif isinstance(existing_data, list):
                        data = existing_data
                except json.JSONDecodeError:
                    data = []

        # Append the new record
        data.append(user_data)

        # Write the updated data back to the file
        with open('user_info.json', 'w') as f:
            json.dump(data, f, indent=4)

        return "Successfully saved user information to user_info.json"

    except json.JSONDecodeError:
        return "Error: Invalid JSON format"
    except Exception as e:
        return f"Error saving information: {str(e)}"

@tool
def close_chat() -> str:
    """
    Ends the chat when booking is done and confirmation email will be sent soon.
    """
    global should_close
    should_close = True
    return "Endin the call."

tools = [collect_user_info, save_info,close_chat]

# Load base prompt
base_prompt = hub.pull("hwchase17/structured-chat-agent")

# Customize the system prompt with structured formatting instructions
custom_format = """
You are Chris from MindRind who is created to help the user.First introduct yourself then if user ask about your company then tell user that
MindRind is a product-based software house.
Entertain user's query and after answering 2-3 queries ask the user if they want to book an appointment,
you dont need any tool for answering random question and answer, call tool when you have to 
ask user if they want to book an appointment if the use says Yes then collect user's name, date and time for appointment,
and email in a structured conversation. And most importantly if you are not given any query then tell the user that you are unable to understand
what i said. After completing the appointment booking, ask the user if they want to end the call.
If the user says yes, call close_chat tool and say goodbye. If the user says no, ask if they need anything else.

ALWAYS follow this format step-by-step:
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
prompt = base_prompt
llm = GoogleGenerativeAI(
model="gemini-2.0-flash",
api_key="AIzaSyCVqq8C_DvifL7iFy1qAOZ31OyrUVhcPxQ",
temperature=1,
)
agent = create_structured_chat_agent(llm, tools, prompt)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
memory.clear()
agent_executor = AgentExecutor(
agent=agent,
tools=tools,
memory=memory,
verbose=True,
handle_parsing_errors=True,
)
print("Assistant: Hi!")

while True:
        if should_close:
            print("Assistant: Goodbye!")
            break
        user_input = listen_and_recognize()
        print(f"User: {str(user_input)}")
        
        try:
            response = agent_executor.invoke({"input": str(user_input)})
            tts(response['output'])
        except Exception as e:
            print(f"Error: {str(e)}")