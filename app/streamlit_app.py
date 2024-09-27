import streamlit as st
import requests
import base64
import pyaudio

def play_audio(audio_base64):
    """Play base64 encoded audio using PyAudio."""
    audio_data = base64.b64decode(audio_base64)
    pyaudio_instance = pyaudio.PyAudio()
    stream = pyaudio_instance.open(
        format=pyaudio.paInt16, 
        channels=1, 
        rate=16000, 
        output=True
    )
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    pyaudio_instance.terminate()

# API URLs
LLM_API_URL = "http://localhost:8000/request/"
TEXT_TO_SPEECH_API_URL = "http://localhost:8000/text-to-speech/"

# Streamlit app layout
st.title("Ask a Question")
input_query = st.text_area("Enter your query:", height=150, key="input_query")

# Text Button
if st.button("Text"): 
    response = requests.post(LLM_API_URL, json={"query": input_query})
    if response.status_code == 200: 
        response_data = response.json() 
        st.write(response_data.get("response", "No response"))
    else: 
        st.error(f"Error {response.status_code}: Unable to fetch the response")

# Speech Button
if st.button("Speech"): 
    response = requests.post(TEXT_TO_SPEECH_API_URL, json={"query": input_query}) 
    if response.status_code == 200: 
        response_data = response.json()
        audio_string = response_data.get("audio_base64", "No data Received")
        play_audio(audio_string) 
        st.success("Audio response played!")
    else: 
        st.error(f"Error {response.status_code}: Unable to fetch the response")
