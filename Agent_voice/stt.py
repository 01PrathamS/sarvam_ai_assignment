import os 
import requests

def speech_to_text(audio_file_path):
    """Convert speech to text using the Sarvam API."""

    url = "https://api.sarvam.ai/speech-to-text-translate"
    data = {
        "language-code": "en-IN", 
        "model": "saaras:v1",
    }

    files = {
        "file": ("output.wav", open(audio_file_path, "rb"), "audio/wav")
    }

    headers = {"API-Subscription-Key": "762a32ee-b69f-464b-9311-140901e684f3"}

    response = requests.post(url, data=data, files=files, headers=headers)
    return response.text

def record_audio(): 
    """Record audio using the microphone and save it to a file."""
    import sounddevice as sd

    fs = 16000  # Sample rate
    seconds = 5  # Duration of recording

    print("Recording...")
    my_recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")

    ## TO DO: speech to text 

    return text 