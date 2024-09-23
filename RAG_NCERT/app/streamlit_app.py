import streamlit as st
import requests
import json

# Set FastAPI endpoint URL
API_URL = "http://127.0.0.1:8000/request/"

st.title("NCERT-gpt LLM-based Question Answering")

# Input fields
query = st.text_input("Enter your query:")

# Button to submit query
if st.button("Submit Query"):
    if query:
        # Prepare the request body
        request_body = {
            "query": query,
        }

        try:
            # Send POST request to the FastAPI server
            response = requests.post(API_URL, json=request_body)

            # Check for successful request
            if response.status_code == 200:
                response_data = response.json()
                st.subheader("LLM Response:")
                st.write(response_data.get("response", "No response found."))
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query before submitting.")

