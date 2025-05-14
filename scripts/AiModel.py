#Perfectly functioning AI model for collecting user information.
import json
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.tools import tool
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

def model():
    tools = [t.collect_user_info, t.save_info,t.close_chat]

    # Load base prompt
    base_prompt = hub.pull("hwchase17/structured-chat-agent")

    # Customize the system prompt with structured formatting instructions
    base_prompt.messages[0] = SystemMessagePromptTemplate.from_template(
    cp + "\n\n" + base_prompt.messages[0].prompt.template
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
    print("Assistant: Hi!")

    while True:
            if t.should_close:
                print("Assistant: Goodbye!")
                break
            user_input = listen_and_recognize()
            print(f"User: {str(user_input)}")
            
            try:
                response = agent_executor.invoke({"input": str(user_input)})
                tts(response['output'])
            except Exception as e:
                print(f"Error: {str(e)}")