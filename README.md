# sarvam_ai_assignment
Pre Screening Task @SarvamAI

# You Tube video 
[![AI Healthcare Receptionist](https://img.youtube.com/vi/12q6XbdCjTg/maxresdefault.jpg)](https://youtube.com/shorts/12q6XbdCjTg)

# Project : Adhyayanam
This project provides Question-Answer with NCERT book chapter with text and voice capability. 
Efficiently answer user query.

# My Approach 
1. I first extract the pdf data with the help of Fitz python package, with the text color, font size, font shape and style. then classify the content with relevant headings or markdowns such as activity, conclusion, questions, and figure descriptions for figures.
2. Then I split the text in sliding window manner overlapping sentences, to keep up with the context  based on the markdowns/headings. so i can take markdowns/headings as a metadata this helps while searching similar context.
3. save the data to csv file(easy to debug things).
4. converting user_queries in subqueries if needed and then perform similary search, return most similar text as a context for each subquery.
5. make a condition only respond if similarity_score > threshold, better for handling unrelevant queries.
6. pass the context with user query to Groq(LLM).
7. based on the that give response in speech or text, as per preferance.

> [!TIP]  
> Improvements in result after adding support for MultiQuery.

<div>
    <img src="https://github.com/01PrathamS/sarvam_ai_assignment/blob/main/images/before_multiquery.png" width="400" alt="Before MultiQuery" style="display: inline-block; margin-right: 20px;">
    <img src="https://github.com/01PrathamS/sarvam_ai_assignment/blob/main/images/after_mutliquery.png" width="400" alt="After MultiQuery" style="display: inline-block;">
</div>


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
1. ```preprocess/extract.py``` Extract pdf , text with heading, figure with figure description, questions, conclusions, activities
2. ```preprocess/helper.py``` helper functions for reformat extracted information
3. ```preprocess/similarity_search.py``` helper function to find similar text to user_query to pass as a context to llm
4. ```app/main.py``` fastapi endpoints
5. ```app/streamlit_run.py``` streamlit UI for endpoints

# Resources I've used

1. Umar Jamil : RAG https://www.youtube.com/watch?v=rhZgXNdhWDY
2. Text chunking from KX: https://www.youtube.com/watch?v=uhVMFZjUOJI&t=2407s
3. Full Stack Retrieval: https://retrieval-tutorials.vercel.app/
4. RAG and Beyond: https://www.youtube.com/watch?v=fDmQnB8Ga6g&t=1273s
5. Langchain Advance Retrieval : https://www.youtube.com/watch?v=DY3sT4yIezs
