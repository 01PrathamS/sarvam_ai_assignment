from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import time 
from utils import similarity_search, call_llm_groq, speech_to_text, text_to_speech
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


# Define the Pydantic model for the request body
class QueryRequest(BaseModel):
    query: str
    top_n: int = 5  # Default to top 5 results


# Endpoint for calling the LLM with context
@app.post("/request/")
async def call_llm_with_context(request: QueryRequest):
    """API endpoint to handle query and context-based response generation using Groq LLM."""
    # Fetch the most relevant context using similarity search
    # check out how much time does it take to fetch the context
    context_time = time.time()
    context = similarity_search(request.query, request.top_n)
    print(f"Context fetched in {time.time() - context_time:.2f} seconds.")
    llm_response_time = time.time()
    if context:
        response = call_llm_groq(request.query, context)
        print(f"LLM response generated in {time.time() - llm_response_time:.2f} seconds.")
        return {"response": response}
    else:
        return {"response": "No relevant context found."}

# Endpoint for response in speech 
@app.post("/tts-response")
async def tts_response(request: QueryRequest):
    """API endpoint to handle query and context-based response generation using Groq LLM."""
    # Fetch the most relevant context using similarity search
    context = similarity_search(request.query, request.top_n)
    if context:
        response = call_llm_groq(request.query, context)
        audio_string = text_to_speech(response)
        return {"audio_base64": audio_string}
    else:
        return {"audio_base64": "No relevant context found."}
    
# Endpoint for input in speech and output in speech 
@app.post("/audio-input/")
async def process_audio(file: UploadFile = File(...)):
    """Process audio input, convert to text, respond with speech."""
    audio_text = speech_to_text(file.file)
    
    # Similarity search
    context = similarity_search(audio_text, top_n=5)
    
    # Get LLM response based on the context
    response = call_llm_groq(audio_text, context)
    
    # Convert response to speech
    audio_string = text_to_speech(response)
    
    return {"audio_base64": audio_string}



## ACTION AGENTS SHOULD PERFORM

## agent can perform the smart actions based on users' query 
# extend the service and host another endpoint for the agent 

#1. Scheduling & Remainders (Schedule zoom meetings)
#2. check if the question is related to the science subject then call llm and answer question
#3. Arrange appintment --> MAKE A LOG FOR TOO MANY CALLS
#4. summarize top 5 news today
#5. Agent that do taxes for you twice a year 