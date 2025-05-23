#Perfectly functioning AI model for collecting user information.
from langchain_google_genai.llms import GoogleGenerativeAI
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain.prompts import SystemMessagePromptTemplate
import os
from dotenv import load_dotenv
from tool import *
from custom_prompt import *
from generate_prompt import generate_prompt

load_dotenv()
user_request = input("Enter the type of assistant you want:")
custom_format=generate_prompt(user_request)
#Defining tools for the agent.
tools = [collect_user_info,publish_data]

# Load base prompt
base_prompt = hub.pull("hwchase17/structured-chat-agent")


# Customize the system prompt with structured formatting instructions
base_prompt.messages[0] = SystemMessagePromptTemplate.from_template(
custom_format + "\n\n" + base_prompt.messages[0].prompt.template
)
prompt = base_prompt

#Initializing the LLM.
llm = GoogleGenerativeAI(
model="gemini-2.0-flash",
api_key=os.getenv("gen_ai_API_key"),
temperature=1,
)
#Initializing the agent and adding memory.
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

#For testing purposes.
while True:
    user_input = input("You: ")
    result = agent_executor.invoke({"input": user_input})
    print("AI:", result["output"])
