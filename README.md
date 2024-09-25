# sarvam_ai_assignment
Pre Screening Task @SarvamAI

# Task 1: RAG-Based NCERT Solution

## My Approach

1. I am familiar with Langchain and LlamaIndex, but using them here doesn't seem ideal for this specific case.

2. Instead of directly splitting the text, I extract the text from the PDF because this is a special case (direct text splitting won't work here). The text in each page is separated into two blocks, which requires a more careful extraction approach.

3. After extraction, I map the content to its relevant headings. These headings act as metadata when performing similarity searches or any other method of searching.

4. After successfully extracting the data and mapping it to the relevant headings, I considered how to store it.

5. To evaluate the system, I first thought of collecting all the questions from the PDF and extracting answers from online solutions.

6. Most of the answers are 2-3 lines long, so we need to pass a smaller context to the LLM with the user query to provide the best answer, rather than passing large contexts (entire paragraphs).

7. I decided to merge sentences and save them with overlapping previous sentences to ensure no context is lost.

8. To determine the best context window, I plan to use an iterative approach. I will adjust the context window size if it improves the accuracy.

**Note**: I have not yet used any vector databases. For now, I have stored all the extracted and preprocessed data in a CSV file, but I will update it once the complete pipeline is running efficiently.

---

## How to Run This Project

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
   set GROQ_API_KEY=xxx

5. Extract text from PDF
   ```bash
   python preprocess/extract.py 
   python preprocess/preprocess_csv.py

6. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
7. Start the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
---
# Resources 

1. Umar Jamil : RAG https://www.youtube.com/watch?v=rhZgXNdhWDY
2. Text chunking from KX: https://www.youtube.com/watch?v=uhVMFZjUOJI&t=2407s
3. Full Stack Retrieval: https://retrieval-tutorials.vercel.app/
4. RAG and Beyond: https://www.youtube.com/watch?v=fDmQnB8Ga6g&t=1273s
5. Langchain Advance Retrieval : https://www.youtube.com/watch?v=DY3sT4yIezs

# Future: 
1. Muti Query for better retrieval of user query becasue for query asking two questions same time won't work here
so need to convert it into to separate questions and handle it using either multiquery or parallel function calling

2. 



