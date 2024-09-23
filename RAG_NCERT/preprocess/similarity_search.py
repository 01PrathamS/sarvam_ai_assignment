from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer('all-MiniLM-L6-v2')

def similarity_search(query, df, top_n=5):
    """Perform similarity search for a given query in the DataFrame.
    
    Args:
        query (str): The search query to find similar content.
        df (pd.DataFrame): DataFrame containing 'heading', 'content', and 'embedding'.
        top_n (int): Number of top similar results to return. Default is 5.
        
    Returns:
        str: The content of the most similar result or None if no result is found.
    """
    query_embedding = model.encode(query)
    top_results = []

    # Loop through the DataFrame rows and calculate cosine similarity
    for i, row in df.iterrows():
        # Ensure the embedding is a NumPy array
        row_embedding = np.array(row['embedding'])
        similarity = cosine_similarity([query_embedding], [row_embedding])[0][0]
        
        top_results.append({
            "index": i,
            "heading": row['heading'],
            "score": similarity,
            "content": row['content'],
            "word_count": len(row['content'].split())
        })

    # Sort results by similarity score and select the top N
    top_results = sorted(top_results, key=lambda x: x['score'], reverse=True)[:top_n]
    
    # Return the content of the top result, or None if no results
    # return top_results[0]['content'] if top_results else None
    return top_results 

if __name__ == '__main__':
    # Load the DataFrame from a CSV file
    df = pd.read_csv(r'data/json_data_4.csv')

    # Convert embedding from string to NumPy array
    df['embedding'] = df['embedding'].apply(lambda x: np.array(eval(x)))

    # Perform similarity search with a sample query
    response = similarity_search('Why are sound waves called mechanical waves?', df)
    print(response)
