# sarvam_ai_assignment
Pre Screening Task @SarvamAI

# You Tube video 
[![AI Healthcare Receptionist](https://img.youtube.com/vi/12q6XbdCjTg/maxresdefault.jpg)](https://youtube.com/shorts/12q6XbdCjTg)

# Adhyayanam
This project provides Question-Answer with NCERT book chapter with text and voice capability. 
Efficiently answer user query.

# Project Structure

## Getting Started

1. Set up a virtual environment in Python:
   ```bash
   python -m venv env

2. Activate the virtual environment
   ```bash 
   .\evn\Scripts\activate

3. Install Dependencies:
   ```bash
   pip install -r requirements.txt

4. Set up GROQ API KEY:
   ```bash
   set GROQ_API_KEY=<your-api-key>

5. Extract text from PDF
   ```bash
   python preprocess/extract.py 

6. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload

7. Start the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
---

# Project Structure 

# Resources I've used

1. Umar Jamil : RAG https://www.youtube.com/watch?v=rhZgXNdhWDY
2. Text chunking from KX: https://www.youtube.com/watch?v=uhVMFZjUOJI&t=2407s
3. Full Stack Retrieval: https://retrieval-tutorials.vercel.app/
4. RAG and Beyond: https://www.youtube.com/watch?v=fDmQnB8Ga6g&t=1273s
5. Langchain Advance Retrieval : https://www.youtube.com/watch?v=DY3sT4yIezs

# Future: 
1. Using Multi Query method for better answers 



