# from elevenlabs.client import ElevenLabs
# from elevenlabs import stream
# import os,dotenv
# from dotenv import load_dotenv
# load_dotenv()
# def tts(response:str):
#       # Initialize the ElevenLabs client with your API key
#       client = ElevenLabs(
#         api_key=os.getenv("elevenlabs_Api_key"),
#       )

#       # Get the list of voices
#       audio_stream = client.text_to_speech.convert_as_stream(
#           text=response,
#           voice_id="JBFqnCBsd6RMkjVDRZzb",
#           model_id="eleven_multilingual_v2"
#       )
#       # option 1: play the streamed audio locally
#       stream(audio_stream)
#       # option 2: process the audio bytes manually
#       for chunk in audio_stream:
#           if isinstance(chunk, bytes):
#               print(chunk)

# from elevenlabs import ElevenLabs
# import os
# from elevenlabs import stream

# client = ElevenLabs(api_key=os.getenv("elevenlabs_Api_key"))

# def elevenlabs_tts(text):
#     audio_stream = client.text_to_speech.convert_as_stream(
#         text=text,
#         voice_id="JBFqnCBsd6RMkjVDRZzb",
#         model_id="eleven_multilingual_v2"
#     )
#     stream(audio_stream)
#     # Collect MP3 bytes
#     mp3_bytes = b"".join(chunk for chunk in audio_stream if isinstance(chunk, bytes))
#     return mp3_bytes

# stream(elevenlabs_tts("Hello testing!"))
import pyttsx3
import wave
import os
import time

def tts(text):
    engine = pyttsx3.init()
    wav_path = "tts_output.wav"
    
    # Save to file
    engine.save_to_file(text, wav_path)
    engine.runAndWait()  # This waits until file is written

    # Wait to ensure file is closed and flushed
    time.sleep(0.5)

    # Validate file exists
    if not os.path.exists(wav_path):
        raise Exception("TTS output file not found!")

    # Read WAV and convert to PCM bytes
    with wave.open(wav_path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()

    return frames  # PCM bytes


