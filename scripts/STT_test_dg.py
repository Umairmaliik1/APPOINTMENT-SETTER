# import asyncio
# import websockets
# import json
# import os
# import sounddevice as sd
# import numpy as np
# import soundfile as sf
# from io import BytesIO

# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# async def deepgram_stt(pcm_audio_bytes, sample_rate=16000):
#     uri = f"wss://api.deepgram.com/v1/listen?punctuate=true&language=en-US&encoding=linear16&sample_rate={sample_rate}"
#     headers = [("Authorization", f"Token {DEEPGRAM_API_KEY}")]

#     async with websockets.connect(uri, extra_headers=headers) as websocket:
#         # Task to send audio in chunks
#         async def send_audio():
#             CHUNK_SIZE = 1024
#             for i in range(0, len(pcm_audio_bytes), CHUNK_SIZE):
#                 await websocket.send(pcm_audio_bytes[i:i + CHUNK_SIZE])
#                 await asyncio.sleep(0.01)  # mimic real-time streaming
#             await websocket.send(b'')  # indicate end of stream

#         # Task to receive transcripts
#         async def receive_transcript():
#             transcript = ""
#             while True:
#                 try:
#                     response = await asyncio.wait_for(websocket.recv(), timeout=5)
#                 except asyncio.TimeoutError:
#                     break
#                 response_json = json.loads(response)
#                 if 'channel' in response_json and 'alternatives' in response_json['channel']:
#                     alt = response_json['channel']['alternatives'][0]
#                     if alt.get("transcript"):
#                         print(f"📝 Interim: {alt['transcript']}")
#                         transcript = alt['transcript']
#                 if response_json.get("is_final", False):
#                     break
#             return transcript

#         transcript = await asyncio.gather(send_audio(), receive_transcript())
#         return transcript[1]


# def record_audio(duration=5, sample_rate=16000):
#     print("Recording...")
#     audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
#     sd.wait()  # Blocking call
#     print("Recording complete")
#     return audio

# def audio_to_bytes(audio, sample_rate):
#     buffer = BytesIO()
#     sf.write(buffer, audio, sample_rate, format='WAV')
#     return buffer.getvalue()
# def audio_to_raw_pcm(audio):
#     pcm_audio = (audio * 32767).astype(np.int16)  # Convert float32 to int16 PCM
#     return pcm_audio.tobytes()

# async def main():
#     # Record audio
#     sample_rate = 16000  # Must match Deepgram parameters
#     audio = record_audio(duration=5, sample_rate=sample_rate)
    
#     # Convert to bytes
#     audio_bytes = audio_to_raw_pcm(audio)
#     # Get transcription
#     transcript = await deepgram_stt(audio_bytes, sample_rate)
#     print(f"Final Transcript: {transcript}")

# if __name__ == "__main__":
#     asyncio.run(main())


import tempfile
import numpy as np
import wave
import whisper

model = whisper.load_model("base")  # or "tiny" for faster inference

def process_audio_pcm_to_text(pcm_data: bytes, sample_rate: int = 48000, channels: int = 2) -> str:
    # Save raw PCM to temp WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        with wave.open(f.name, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_data)

        # Run Whisper STT
        result = model.transcribe(f.name)
        return result["text"]
