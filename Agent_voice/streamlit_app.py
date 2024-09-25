import streamlit as st
import requests
import base64
import pyaudio

# Streamlit app
st.title("Text to Speech Application")

text_input = st.text_area("Enter your query:")
if st.button("Generate Audio"):
    if text_input:
        # Call the FastAPI endpoint
        response = requests.post("http://localhost:8000/generate-audio/", json={"text": text_input})
        
        if response.status_code == 200:
            audio_base64 = response.json().get("audio_base64")
            audio_data = base64.b64decode(audio_base64)

            # Play the audio using PyAudio
            pyaudio_instance = pyaudio.PyAudio()
            stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)

            stream.write(audio_data)  # Stream the audio_data 
            stream.stop_stream()
            stream.close()
            pyaudio_instance.terminate()

            st.success("Audio has been played successfully!")
        else:
            st.error("Error generating audio.")
    else:
        st.warning("Please enter a query.")
