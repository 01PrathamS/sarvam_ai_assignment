from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import os

app = FastAPI()

# Load the pre-trained model and the dataset
model = SentenceTransformer('all-MiniLM-L6-v2')
df = pd.read_csv('D:\SARVAM\data\json_data_4.csv')
df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))  # Convert embedding strings to numpy arrays

# Define the Pydantic model for the request body
class QueryRequest(BaseModel):
    query: str
    top_n: int = 5  # Default to top 5 results

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

# Endpoint for calling the LLM with context
@app.post("/request/")
async def call_llm_with_context(request: QueryRequest):
    """API endpoint to handle query and context-based response generation using Groq LLM."""
    # Fetch the most relevant context using similarity search
    context = similarity_search(request.query, df, request.top_n)
    
    if context:
        response = call_llm_groq(request.query, context)
        return {"response": response}
    else:
        return {"response": "No relevant context found."}
