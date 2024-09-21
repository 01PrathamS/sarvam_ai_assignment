import streamlit as st
import requests

# Set up the Streamlit interface
st.title("Similarity Search Engine")
st.write("Enter a query to find the most relevant content")

# Input box for the query
query = st.text_input("Enter your query", "")

# Number of results
top_n = st.slider("Number of results", 1, 10, 5)

# Button to trigger search
if st.button("Search"):
    # Make request to FastAPI endpoint
    response = requests.post("http://localhost:8000/similarity_search/", json={"query": query, "top_n": top_n})
    
    # Display the results
    if response.status_code == 200:
        results = response.json()["results"]
        st.write(f"Top {top_n} results:")
        for result in results:
            st.write(f"**Heading:** {result['heading']}")
            st.write(f"**Content:** {result['content']}")
            st.write(f"**Score:** {result['score']:.3f}")
            st.write(f"**Word Count:** {result['word_count']}")
            st.write("---")
    else:
        st.error("Error in API request")

