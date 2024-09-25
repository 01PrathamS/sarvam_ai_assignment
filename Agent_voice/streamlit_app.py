import streamlit as st
import requests
import sounddevice as sd
import wavio
import base64
import pyaudio

def record_audio(output_file="output.wav", duration=3, fs=16000):
    """Record audio from the microphone and save to a file."""
    st.write("Recording...")
    my_recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    wavio.write(output_file, my_recording, fs, sampwidth=2)
    st.write("Recording finished.")
    return output_file

def play_audio(audio_base64):
    """Play base64 encoded audio."""
    audio_data = base64.b64decode(audio_base64)

    # Play the audio using PyAudio
    pyaudio_instance = pyaudio.PyAudio()
    stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    pyaudio_instance.terminate()

# Streamlit UI
st.title("Speech to Text to Speech Application")

if st.button("Record and Send"):
    audio_file = record_audio()

    # Send the audio file to FastAPI
    with open(audio_file, "rb") as f:
        files = {"file": f}
        response = requests.post("http://localhost:8000/audio-input/", files=files)

    if response.status_code == 200:
        audio_base64 = response.json().get("audio_base64")
        play_audio(audio_base64)
        st.success("Audio response played!")
    else:
        st.error(f"Error: {response.status_code}")
