import os
from dotenv import load_dotenv
from livekit import agents
credentials_path = "C:/Users/HP/Desktop/APPOINTMENT-SETTER/pub_sub/cred.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
from livekit.agents import AgentSession, Agent, RoomInputOptions,function_tool
from livekit.plugins import (
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
    google
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from prompt import global_prompt,temporary_overide

load_dotenv()
@function_tool
async def publish_data(name: str, doc_category: str, datetime: str, email: str) -> str:
    """Publishes data to a Pub/Sub topic."""
    from google.cloud import pubsub_v1

    project_id = "gen-lang-client-0194953633"
    topic_id = "appointment-setter"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    data = f"{name} wants to meet for {doc_category} on {datetime}".encode("utf-8")
    attributes = {
        "name": name,
        "doc_category": doc_category,
        "datetime": datetime,
        "email": email
    }

    try:
        future = publisher.publish(topic_path, data, **attributes)
        message_id = future.result(timeout=10)
        print(f"✅ Pub/Sub: Published message ID: {message_id}")
        return f"Data published. Message ID: {message_id}"
    except Exception as e:
        print(f"❌ Pub/Sub publish failed: {e}")
        return f"Failed to publish data: {str(e)}"


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(tools=[publish_data],instructions=global_prompt)


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-2.0-flash-001"),
        tts=cartesia.TTS(),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

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

    await session.generate_reply(
        instructions=temporary_overide
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))