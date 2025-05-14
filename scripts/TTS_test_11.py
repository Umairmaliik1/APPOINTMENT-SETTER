from elevenlabs.client import ElevenLabs
from elevenlabs import stream

def tts(response:str):
      # Initialize the ElevenLabs client with your API key
      client = ElevenLabs(
        api_key='sk_9f4f6e511bd80a3447c3efbff73e2b6293099c4695b87cb4',
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