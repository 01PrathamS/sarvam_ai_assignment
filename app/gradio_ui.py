import gradio as gr
import requests
import base64
import sounddevice as sd
import wavio
import threading
import pyaudio

# FastAPI URLs
LLM_API_URL = "http://localhost:8000/request/"
TTS_API_URL = "http://localhost:8000/tts-response"
AUDIO_INPUT_URL = "http://localhost:8000/audio-input/"

def record_audio(duration=3, fs=16000):
    """Record audio from the microphone and save to a file."""
    my_recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()  # Wait until recording is finished
    output_file = "output.wav"
    wavio.write(output_file, my_recording, fs, sampwidth=2)
    return output_file

def play_audio(audio_base64):
    """Play base64 encoded audio."""
    audio_data = base64.b64decode(audio_base64)
    pyaudio_instance = pyaudio.PyAudio()
    stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    pyaudio_instance.terminate()

def handle_text_response(query, top_n):
    """Fetch and return the text response from the LLM API."""
    response = requests.post(LLM_API_URL, json={"query": query, "top_n": top_n})
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("response", "No response generated.")
    else:
        return f"Error {response.status_code}: Unable to fetch the response."

def handle_speech_response(query, top_n):
    """Fetch and return the speech response from the TTS API."""
    response = requests.post(TTS_API_URL, json={"query": query, "top_n": top_n})
    if response.status_code == 200:
        response_data = response.json()
        audio_base64 = response_data.get("audio_base64", "")
        return audio_base64 if audio_base64 != "No relevant context found." else "No relevant context found."
    else:
        return f"Error {response.status_code}: Unable to fetch the speech response."

def process_query(input_query, response_format, top_n):
    """Process user query based on the chosen response format."""
    if response_format == "Text":
        return handle_text_response(input_query, top_n)
    elif response_format == "Speech":
        audio_base64 = handle_speech_response(input_query, top_n)
        if audio_base64 != "No relevant context found.":
            threading.Thread(target=play_audio, args=(audio_base64,)).start()
            return "Streaming audio response..."
        else:
            return audio_base64

def record_and_send_audio():
    """Record audio and send it to the FastAPI for processing."""
    audio_file = record_audio()
    with open(audio_file, "rb") as f:
        files = {"file": f}
        response = requests.post(AUDIO_INPUT_URL, files=files)
    
    if response.status_code == 200:
        audio_base64 = response.json().get("audio_base64")
        play_audio(audio_base64)
        return "Audio response played!"
    else:
        return f"Error: {response.status_code}"

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# Ask a Question\n### Powered by FastAPI and Groq LLM")
    
    with gr.Row():
        input_query = gr.Textbox(label="Enter your query:", lines=4)
        response_format = gr.Radio(["Text", "Speech"], label="Choose response format")
        top_n = gr.Slider(minimum=1, maximum=10, label="Number of contexts to fetch (Top N)", value=5)
    
    submit_button = gr.Button("Submit Query")
    output_text = gr.Textbox(label="Response", interactive=False)
    
    submit_button.click(process_query, inputs=[input_query, response_format, top_n], outputs=output_text)
    
    record_button = gr.Button("Record and Send")
    record_output = gr.Textbox(label="Recording Status", interactive=False)
    
    record_button.click(record_and_send_audio, outputs=record_output)

demo.launch()
