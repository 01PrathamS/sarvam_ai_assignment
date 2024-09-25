import pandas as pd
import numpy as np
import pyaudio
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import os

# Load the pre-trained model and the dataset
model = SentenceTransformer('all-MiniLM-L6-v2')
df = pd.read_csv('D:\SARVAM\data\json_data_4.csv')
df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))  # Convert embedding strings to numpy arrays

# Similarity search function
def similarity_search(query, df, top_n=5):
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
    return top_results[0]['content'] if top_results else None

# Function to call Groq's LLM with the context
def call_llm_groq(user_input, context):
    """Call the Groq LLM with user input and the context fetched via similarity search."""
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))  # Ensure the API key is available in the environment
        
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

    
def text_to_speech(text: str):
    import requests

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

    response = requests.request("POST", url, json=payload, headers=headers)

    response = response.text
    response = response[12:-3] ## this gonna be the byte64 encoded audio string
    return response 

import base64

def stream_audio(audio_base64): 
    audio_data = base64.b64decode(audio_base64)

    # Play the audio using PyAudio 
    pyaudio_instance = pyaudio.PyAudio()
    stream = pyaudio_instance.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)

    stream.write(audio_data) # Stream the audio_data 
    stream.stop_stream()
    stream.close()
    pyaudio_instance.terminate()
    
    print("Audio stream completed")

    return 

if __name__ == "__main__":
    df = pd.read_csv('D:\SARVAM\data\json_data_4.csv')
    df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x))) \
    
    query = "Why are the ceilings of concert halls curved?"
    context = similarity_search(query, df, top_n=5)
    response = call_llm_groq(query, context)
    audio_string = text_to_speech(response)
    stream_audio(audio_string) 
    # print(response)
    # print("Audio saved to", audio_file_path)

    


    


