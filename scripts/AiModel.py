#Perfectly functioning AI model for collecting user information.
import json
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain.prompts import SystemMessagePromptTemplate
from scripts.TTS_test_11 import tts
from scripts.STT_test_dg import listen_and_recognize
import os
from dotenv import load_dotenv
import scripts.tool as t
import scripts.custom_prompt as cp

load_dotenv()
tools = [t.fetch_doc_details,t.extract_unique_doctor_names,t.collect_user_info, t.save_info,t.close_chat]

    # Load base prompt
base_prompt = hub.pull("hwchase17/structured-chat-agent")
custom_format = """
    You are Chris from MindRind who is created to help the user.First introduct yourself then if user ask about your company then tell user that
    MindRind is a product-based software house.
    Entertain user's query and after answering 2-3 queries ask the user if they want to book an appointment,
    you dont need any tool for answering random question and answer, call tool when you have to 
    ask user if they want to book an appointment if the use says Yes then collect user's name,before asking for date and time for appointment you have
    to call extract_unique_doctor_names tool to get the list of the doctors and then ask the user to select a doctor from the list when 
    user select a doctor call fetch_doc_details tool to get the details of the selected doctor and show it to the user and ask the user
    to select the time and date for the appointment from the provivded details(in the provided details you will receive two dates
    which means that he is availble from date 1 till date 2, the entire duaration between the dates and also check the date and time
    user provides match the doctors availability.) 
    and then ask the user to provide their email address.
    Make sure to handle the errors gracefully.
    And most importantly if you are not given any query then tell the user that you are unable to understand
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
    # Customize the system prompt with structured formatting instructions
base_prompt.messages[0] = SystemMessagePromptTemplate.from_template(
custom_format + "\n\n" + base_prompt.messages[0].prompt.template
)
prompt = base_prompt
llm = GoogleGenerativeAI(
model="gemini-2.0-flash",
api_key=os.getenv("gen_ai_API_key"),
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