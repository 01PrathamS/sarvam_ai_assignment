from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def similarity_search(query,df, top_n=5):
    query_embedding = model.encode(query)

    # Initialize list to store the top N similarity scores and corresponding content
    top_results = [{"score": 0, "content": None, "word_count": 0} for _ in range(top_n)]

    for i in range(len(df)):
        similarity = cosine_similarity([query_embedding], [df['embedding'][i]])[0][0]

        # Update top N results if the current similarity is higher than any of them
        for j in range(top_n):
            if similarity > top_results[j]["score"]:
                # Shift lower-ranked results downwards to make space for the new result
                top_results = top_results[:j] + [
                    {"index": i,"heading":df['heading'][i],"score": similarity, "content": df['content'][i], "word_count": len(df['content'][i].split(" "))}] + top_results[j:-1]
                break

    # Return the top N results
    return top_results


if __name__ == '__main__':
    df = pd.read_csv('data.csv')
    df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))
    response = similarity_search('What is the audible range of sound?', df)
    print(response)