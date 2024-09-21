from fastapi import FastAPI, Query
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Load the pre-trained model and the dataset
model = SentenceTransformer('all-MiniLM-L6-v2')
df = pd.read_csv('data.csv')
df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))

class QueryRequest(BaseModel):
    query: str
    top_n: int = 5

def similarity_search(query, df, top_n=5):
    query_embedding = model.encode(query)
    top_results = [{"score": 0, "content": None, "word_count": 0} for _ in range(top_n)]

    for i in range(len(df)):
        similarity = cosine_similarity([query_embedding], [df['embedding'][i]])[0][0]
        for j in range(top_n):
            if similarity > top_results[j]["score"]:
                top_results = top_results[:j] + [
                    {"index": i, "heading": df['heading'][i], "score": similarity, "content": df['content'][i], "word_count": len(df['content'][i].split(" "))}] + top_results[j:-1]
                break
    return top_results

@app.post("/similarity_search/")
async def search_similarities(request: QueryRequest):
    results = similarity_search(request.query, df, request.top_n)
    return {"results": results}
