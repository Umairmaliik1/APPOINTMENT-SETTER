import os
import asyncio
import tempfile
from livekit import rtc, api
from dotenv import load_dotenv
from scripts.STT_test_dg import process_audio_pcm_to_text
from scripts.TTS_test_11 import tts
from backend.end_point_functions import get_agent_response

# Load environment variables
load_dotenv()

LIVEKIT_URL = os.getenv("NEXT_PUBLIC_LIVEKIT_URL")  # e.g., "your-livekit-url.livekit.cloud"
LIVEKIT_API_KEY = os.getenv("LiveKit_APIKey")
LIVEKIT_SECRET = os.getenv("LiveKit_Secret")
BOT_IDENTITY = "AI-Assistant-Bot"

# Your imports for STT, TTS, and chatbot
# from your_chatbot_module import chat  # Your Langchain + Gemini logic
# from your_tts_module import elevenlabs_text_to_pcm  # Your TTS logic
# from your_stt_module import process_audio_pcm_to_text  # Your STT logic

async def run_ai_bot(room_name: str):
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_SECRET) \
        .with_identity(BOT_IDENTITY) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        )).to_jwt()

    room = rtc.Room()

    # Local audio source and track for TTS output
    source = rtc.AudioSource(48000, 2)
    track = rtc.LocalAudioTrack.create_audio_track("ai-audio-output", source)

    @room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO and participant.identity != BOT_IDENTITY:
            print(f"Subscribed to audio track from {participant.identity}")
            asyncio.create_task(handle_audio_track(track))

    async def handle_audio_track(track: rtc.Track):
        audio_stream = rtc.AudioStream(track)

        async for audio_frame_event in audio_stream:
            pcm_data = audio_frame_event.frame.data
            transcribed_text =  process_audio_pcm_to_text(pcm_data)
            print("User said:", transcribed_text)

            ai_response = get_agent_response(transcribed_text)
            print("AI Responds:", ai_response["output"])

            pcm_bytes = tts(ai_response["output"])

            if pcm_bytes:
                frame = rtc.AudioFrame(
                    data=pcm_bytes,
                    sample_rate=48000,
                    num_channels=2,
                    samples_per_channel=len(pcm_bytes) // 4
                )
                await source.capture_frame(frame)


    try:
        await room.connect(LIVEKIT_URL, token)
        print(f"AI Bot '{BOT_IDENTITY}' connected to room '{room_name}'")

        await room.local_participant.publish_track(track)
        print("AI Bot published its audio track.")

        await asyncio.sleep(3600)  # Stay connected for 1 hour

    except Exception as e:
        print("Bot error:", e)

    finally:
        await room.disconnect()
        print("AI Bot disconnected.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", required=True, help="Room name to join")
    args = parser.parse_args()
    
    asyncio.run(run_ai_bot(args.room))
