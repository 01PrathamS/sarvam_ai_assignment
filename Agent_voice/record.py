import os
import requests
import sounddevice as sd
import numpy as np
import wavio  # To save the audio in WAV format

def speech_to_text(audio_file_path):
    """Convert speech to text using the Sarvam API."""
    url = "https://api.sarvam.ai/speech-to-text-translate"
    data = {
        "language-code": "en-IN",
        "model": "saaras:v1",
    }

    headers = {"API-Subscription-Key": ""}

    try:
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": ("output.wav", audio_file, "audio/wav")
            }
            response = requests.post(url, data=data, files=files, headers=headers)
            
            if response.status_code == 200:
                return response.text
            else:
                return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def record_audio(output_file="output.wav"):
    """Record audio using the microphone and save it to a file."""
    fs = 16000  # Sample rate
    seconds = 2  # Duration of recording

    print("Recording...")
    my_recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")

    # Save the recording to a WAV file
    wavio.write(output_file, my_recording, fs, sampwidth=2)

    return output_file

def main():
    # Record the audio and get the filename
    audio_file_path = record_audio()

    # Convert speech to text using the Sarvam API
    text = speech_to_text(audio_file_path)

    print(f"Transcribed Text: {text}")

if __name__ == "__main__":
    main()
