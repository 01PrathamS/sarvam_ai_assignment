import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import requests
import time 
import os
import base64
import pyaudio
import pathlib
import wavio 
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()

# dataframe path 
base_dir = pathlib.Path(__file__).resolve().parent.parent
df_path = base_dir / "data" / "extracted_data.csv"


#  Load the pre-trained model and the dataset
model = SentenceTransformer('all-MiniLM-L6-v2')
# here instead of using the  relative path, use the absolute pathnme
df = pd.read_csv(os.path.join(df_path))
df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))  # Convert embedding strings to numpy arrays


def similarity_search(query, top_n=5):
    """Search for similar content based on the input query."""
    query_embedding = model.encode(query)
    top_results = []
    for i, row in df.iterrows():
        row_embedding = np.array(row['embedding'])
        similarity = cosine_similarity([query_embedding], [row_embedding])[0][0]
        top_results.append({
            "index": i,
            "heading": row['heading'],
            "score": similarity,
            "content": row['content'],
            "word_count": len(row['content'].split())
        })
    # Sort results by similarity score and return the top N
    top_results = sorted(top_results, key=lambda x: x['score'], reverse=True)[:top_n]
    return top_results[0]['content'] if top_results[0]['score'] > 0.3 else None

def call_llm_subquestion(question):
    """Call the Groq LLM with user input and the context fetched via similarity search."""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # Ensure the API key is available in the environment
        
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": (
                        f"You are an expert in refining questions. Your task is to break down a question into subquestions only when necessary.\n\n"
                        f"Example 1:\n"
                        f"Question: What is infrasound and ultrasound?\n"
                        f"Answer: 1. What is infrasound?\n2. What is ultrasound?\n\n"
                        f"Example 2:\n"
                        f"Question: What is sound?\n"
                        f"Answer: What is sound?\n\n"
                        f"Example 3 (for comparative or implicit questions):\n"
                        f"Question: Guess which sound has a higher pitch: guitar or car horn?\n"
                        f"Answer: 1. What is the pitch of a guitar sound?\n2. What is the pitch of a car horn sound?\n\n"
                        f"Instructions: If the question contains comparisons or implicit questions, break it into subquestions that address each comparison or concept separately. If not, keep it as a single question.\n"
                        f"Do not provide any explanations, just list the subquestions (if any) or the refined question.\n\n"
                        f"Question: {question}\n\n"
                        f"Answer:"
                )
            }],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"Error calling Groq LLM: {e}")
        return "Sorry, the LLM service is not available at the moment."
    
# response from this function will be used to generate subquestions i wanted to convert the subquestions into list 
# so that i can use it in the streamlit app to display the subquestions
def format_subquestion_response(response): 
    subquestions = response.split("\n")
    subquestions = [subquestion.strip()[3:] for subquestion in subquestions if subquestion.strip()]
    return subquestions

def get_subquestion_answer(subquestions):
    context = []
    for subquestion in subquestions:
        sim_context = similarity_search(subquestion)
        if sim_context:
            context.append(sim_context)
        else: 
            return None
    return context

# Function to call Groq's LLM with the context
def call_llm_groq(user_input, context):
    """Call the Groq LLM with user input and the context fetched via similarity search."""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # Ensure the API key is available in the environment
        
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": (
                    f"You are a science teacher. You are provided with a question and context. "
                    f"Answer the question based only on the given context. No external resources are allowed.\n\n"
                    f"skip the introductory phrases and start with the main content.\n\n"
                    f"Context: {context}\n\n"
                    f"Question: {user_input}\n\nAnswer:"
                )
            }],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"Error calling Groq LLM: {e}")
        return "Sorry, the LLM service is not available at the moment."
    
# Speech-to-text function
def speech_to_text_translate(audio_file_path):
    url = "https://api.sarvam.ai/speech-to-text-translate"
    with open(audio_file_path, 'rb') as audio_file:
        files = {'file': (audio_file_path, audio_file, 'audio/wav')}
        headers = {
            "api-subscription-key": os.getenv("SARVAM_API_KEY"),
        }
        response = requests.post(url, files=files, headers=headers)
    return response.text
    
# Text-to-speech function
def text_to_speech(text: str): # returns base64 encoded audio string
    url = "https://api.sarvam.ai/text-to-speech"
    payload = {
        "inputs": [text],
        "target_language_code": "hi-IN",
        "pitch": 1,
        "speaker": "maitreyi",
        "pace": 1,
        "loudness": 2,
        "speech_sample_rate": 16000,
        "enable_preprocessing": True,
        "model": "bulbul:v1"
    }
    headers = {
        "api-subscription-key": os.getenv("SARVAM_API_KEY"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response = response.text
    response = response[12:-3]  # Extract base64 encoded audio string
    return response


# write a code to stream the audio file
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
