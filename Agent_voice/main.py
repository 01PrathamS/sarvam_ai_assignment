from fastapi import FastAPI, File, UploadFile
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import os
import requests
import sounddevice as sd

# Initialize FastAPI
app = FastAPI()

# Load the pre-trained model and the dataset
model = SentenceTransformer('all-MiniLM-L6-v2')
df = pd.read_csv('D:\SARVAM\data\json_data_4.csv')
df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))  # Convert embedding strings to numpy arrays

# Similarity search function
def similarity_search(query, df, top_n=5):
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

    top_results = sorted(top_results, key=lambda x: x['score'], reverse=True)[:top_n]
    return top_results[0]['content'] if top_results else None

# Function to call Groq's LLM with the context
def call_llm_groq(user_input, context):
    try:
        client = Groq(api_key="")  # Ensure the API key is available in the environment
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": (
                    f"You are a science teacher. You are provided with a question and context. "
                    f"Answer the question based only on the given context. No external resources are allowed.\n\n"
                    f"Context: {context}\n\n"
                    f"Question: {user_input}\nAnswer:"
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
def speech_to_text(audio_file):
    url = "https://api.sarvam.ai/speech-to-text-translate"
    data = {
        "language-code": "en-IN",
        "model": "saaras:v1",
    }
    headers = {"API-Subscription-Key": ""}

    response = requests.post(url, data=data, files={"file": ("output.wav", audio_file, "audio/wav")}, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}, {response.text}"

# Text-to-speech function
def text_to_speech(text):
    url = "https://api.sarvam.ai/text-to-speech"
    payload = {
        "inputs": [text],
        "target_language_code": "gu-IN",
        "pitch": 1,
        "speaker": "maitreyi",
        "pace": 1,
        "loudness": 2,
        "speech_sample_rate": 16000,
        "enable_preprocessing": True,
        "model": "bulbul:v1"
    }
    headers = {
        "api-subscription-key": "",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response = response.text
    response = response[12:-3]  # Extract base64 encoded audio string
    return response

@app.post("/audio-input/")
async def process_audio(file: UploadFile = File(...)):
    """Process audio input, convert to text, respond with speech."""
    audio_text = speech_to_text(file.file)
    
    # Similarity search
    context = similarity_search(audio_text, df, top_n=5)
    
    # Get LLM response based on the context
    response = call_llm_groq(audio_text, context)
    
    # Convert response to speech
    audio_string = text_to_speech(response)
    
    return {"audio_base64": audio_string}
