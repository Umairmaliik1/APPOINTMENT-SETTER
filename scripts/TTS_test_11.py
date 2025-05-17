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
from pydub import AudioSegment
import pyttsx3
import os
import time
import io

def tts(text):
    engine = pyttsx3.init()
    wav_path = "tts_output.wav"
    
    engine.save_to_file(text, wav_path)
    engine.runAndWait()
    time.sleep(0.5)  # Ensure file is written

    if not os.path.exists(wav_path):
        raise Exception("TTS output file not found!")

    # Load with pydub, convert to 48kHz stereo PCM16
    audio = AudioSegment.from_wav(wav_path)
    audio = audio.set_frame_rate(48000).set_channels(2).set_sample_width(2)  # 16-bit

    # Export raw PCM bytes to memory
    pcm_io = io.BytesIO()
    audio.export(pcm_io, format="raw")
    pcm_bytes = pcm_io.getvalue()

    return pcm_bytes
