from fastapi import FastAPI
from pydantic import BaseModel
import time
from utils import similarity_search, call_llm_groq, text_to_speech, call_llm_subquestion, format_subquestion_response, get_subquestion_answer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

# Endpoint for LLM text response
@app.post("/request")  # assuming request has contains multiple subquestions
async def call_llm_with_context(request: QueryRequest):
    """API endpoint to handle query and context-based response generation using Groq LLM."""
    response = call_llm_subquestion(request.query)
    subquestions = format_subquestion_response(response)
    subquestion_answers = get_subquestion_answer(subquestions)
    if subquestion_answers:
        llm_response = call_llm_groq(request.query, subquestion_answers) 
        return {"response": llm_response, "context": subquestion_answers}
    else:
        return {"response": "No relevant context found."}

# Endpoint for text-to-speech response
@app.post("/text-to-speech/")
async def text_to_speech(request: QueryRequest):
    """API endpoint to handle query and return a speech response."""
    context = similarity_search(request.query)
    
    if context:
        response = call_llm_groq(request.query, context)
        audio_string = text_to_speech(response)  # Convert text response to speech (base64 encoded)
        return {"audio_base64": audio_string}
    else:
        return {"audio_base64": "No relevant context found."}

    
# Endpoint for input in speech and output in speech 
# @app.post("/speech_to_text/")
# async def process_audio(file: UploadFile = File(...)):
#     """Process audio input, convert to text, respond with speech."""
#     audio_text = speech_to_text_translate(file.file)
    
#     # Similarity search
#     context = similarity_search(audio_text, top_n=5)
    
#     # Get LLM response based on the context
#     response = call_llm_groq(audio_text, context)
    
#     # Convert response to speech
#     audio_string = text_to_speech(response)
    
#     return {"audio_base64": audio_string}


