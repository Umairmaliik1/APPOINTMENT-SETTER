from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import os,dotenv
from dotenv import load_dotenv
load_dotenv()
def tts(response:str):
      # Initialize the ElevenLabs client with your API key
      client = ElevenLabs(
        api_key=os.getenv("elevenlabs_Api_key"),
      )

      # Get the list of voices
      audio_stream = client.text_to_speech.convert_as_stream(
          text=response,
          voice_id="JBFqnCBsd6RMkjVDRZzb",
          model_id="eleven_multilingual_v2"
      )
      # option 1: play the streamed audio locally
      stream(audio_stream)
      # option 2: process the audio bytes manually
      for chunk in audio_stream:
          if isinstance(chunk, bytes):
              print(chunk)

        