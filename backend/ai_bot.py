import os,json
from typing import Union, Dict, Any
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions,function_tool
from livekit.plugins import (
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
    google
)
from google.cloud import pubsub_v1
from generate_prompt import generate_system_prompt
from livekit.plugins.turn_detector.multilingual import MultilingualModel
credentials_path = "cred.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

custom_prompt=generate_system_prompt("I want a doctor's appointment assistant.")
load_dotenv()
# @function_tool
# async def create_prompt(user_request: str)-> str:
#     """This tool only updates the prompt."""
#     prompt=generate_prompt(user_request)
#     global custom_prompt
#     custom_prompt=prompt
#     return "Prompt updated."

@function_tool
async def publish_data_fn(data: Union[str, Dict[str, Any]]) -> str:
    """Publishes appointment data to Pub/Sub."""
    # Parse JSON string if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {str(e)}"

    if not data:
        return "❌ No data provided to publish."

    project_id = "gen-lang-client-0194953633"
    topic_id = "appointment-setter"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    description = "; ".join(f"{k}: {v}" for k, v in data.items() if v is not None)
    attributes = {str(k): str(v) for k, v in data.items() if v is not None}

    try:
        future = publisher.publish(topic_path, description.encode("utf-8"), **attributes)
        message_id = future.result(timeout=10)
        return f"✅ Data published. Message ID: {message_id}"
    except Exception as e:
        return f"❌ Failed to publish data: {str(e)}"



class Assistant(Agent): #Instance of the agent.
    def __init__(self) -> None:
        
        super().__init__(tools=[publish_data_fn],instructions=custom_prompt)


async def entrypoint(ctx: agents.JobContext): #Enterypoint function for our persistant AI assistant.
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-2.0-flash-001"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

#Starting the session.
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(), 
        ),
    )

    await ctx.connect()

    await session.generate_reply()
    
    

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))