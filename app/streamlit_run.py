import streamlit as st
import requests
import base64
import pyaudio
import threading
import sounddevice as sd
import wavio

# FastAPI URLs
LLM_API_URL = "http://localhost:8000/request/"
TTS_API_URL = "http://localhost:8000/tts-response"
AUDIO_INPUT_URL = "http://localhost:8000/audio-input/"

# Streamlit Configuration
st.set_page_config(page_title="GPT-like Interface", layout="wide")

# Sidebar for user options
st.sidebar.title("Options")
response_format = st.sidebar.selectbox("Choose response format", ["Text", "Speech"])
top_n = st.sidebar.slider("Number of contexts to fetch (Top N)", 1, 10, 5)

# Main Interface
st.title("Ask a Question")
st.markdown("### Powered by FastAPI and Groq LLM")

# Fixed Input Space
input_query = st.text_area("Enter your query:", height=150, key="input_query")

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

    # Set up PyAudio
    pyaudio_instance = pyaudio.PyAudio()
    stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)

    # Stream the audio
    stream.write(audio_data)

    # Clean up
    stream.stop_stream()
    stream.close()
    pyaudio_instance.terminate()

def handle_text_response(query, top_n):
    """Fetch and display the text response from the LLM API."""
    st.info("Fetching text response...")
    response = requests.post(LLM_API_URL, json={"query": query, "top_n": top_n})

    if response.status_code == 200:
        response_data = response.json()
        st.write("### Response:")
        st.write(response_data.get("response", "No response generated."))
    else:
        st.error(f"Error {response.status_code}: Unable to fetch the response.")

def handle_speech_response(query, top_n):
    """Fetch and play the speech response from the TTS API."""
    st.info("Fetching speech response...")
    response = requests.post(TTS_API_URL, json={"query": query, "top_n": top_n})

    if response.status_code == 200:
        response_data = response.json()
        audio_base64 = response_data.get("audio_base64", "")
        if audio_base64 != "No relevant context found.":
            st.write("### Streaming Audio Response:")
            threading.Thread(target=play_audio, args=(audio_base64,)).start()
        else:
            st.error("No relevant context found.")
    else:
        st.error(f"Error {response.status_code}: Unable to fetch the speech response.")

# Button to submit query
if st.button("Submit Query"):
    if not input_query.strip():
        st.warning("Please enter a query before submitting!")
    else:
        if response_format == "Text":
            handle_text_response(input_query, top_n)
        elif response_format == "Speech":
            handle_speech_response(input_query, top_n)

# Recording and Sending Audio Input
if st.button("Record and Send"):
    audio_file = record_audio()

    # Send the audio file to FastAPI for processing
    with open(audio_file, "rb") as f:
        files = {"file": f}
        response = requests.post(AUDIO_INPUT_URL, files=files)

    if response.status_code == 200:
        audio_base64 = response.json().get("audio_base64")
        play_audio(audio_base64)
        st.success("Audio response played!")
    else:
        st.error(f"Error: {response.status_code}")
