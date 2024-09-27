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
from dotenv import load_dotenv

load_dotenv()




#  Load the pre-trained model and the dataset
model = SentenceTransformer('all-MiniLM-L6-v2')
# here instead of using the  relative path, use the absolute path
df = pd.read_csv(os.path.join(r'C:\Users\saval\Desktop\sarvam_ai\sarvam_ai_assignment\RAG_NCERT\data\json_data_4.csv'))
df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))  # Convert embedding strings to numpy arrays


def similarity_search(query, top_n=5):
    """Search for similar content based on the input query."""
    query_embedding_time = time.time()
    query_embedding = model.encode(query)
    print(f"Query embedding generated in {time.time() - query_embedding_time:.2f} seconds.")
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
    return top_results[0]['content'] if top_results else None

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
    headers = {"API-Subscription-Key": "762a32ee-b69f-464b-9311-140901e684f3"}

    response = requests.post(url, data=data, files={"file": ("output.wav", audio_file, "audio/wav")}, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}, {response.text}"
    
# Text-to-speech function
def text_to_speech(text): # returns base64 encoded audio string
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
        "api-subscription-key": "762a32ee-b69f-464b-9311-140901e684f3",
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


    
