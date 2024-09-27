# import streamlit as st
# import requests
# import json

# # Set FastAPI endpoint URL
# API_URL = "http://127.0.0.1:8000/request/"

# st.title("NCERT-gpt LLM-based Question Answering")

# # Input fields
# query = st.text_input("Enter your query:")

# # Button to submit query
# if st.button("Submit Query"):
#     if query:
#         # Prepare the request body
#         request_body = {
#             "query": query,
#         }

#         try:
#             # Send POST request to the FastAPI server
#             response = requests.post(API_URL, json=request_body)

#             # Check for successful request
#             if response.status_code == 200:
#                 response_data = response.json()
#                 st.subheader("LLM Response:")
#                 st.write(response_data.get("response", "No response found."))
#             else:
#                 st.error(f"Error: {response.status_code} - {response.text}")
#         except Exception as e:
#             st.error(f"An error occurred: {e}")
#     else:
#         st.warning("Please enter a query before submitting.")

import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000/request/"

# Title and Sidebar
st.title("NCERT-gpt ")
st.markdown("This is a Question Answering System based on an LLM, RAG.")
st.caption("Enter your query in the text box and click on the 'Submit Query' button to get the answer.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello How can I help you?"}]

# # Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Sidebar - Clear Chats button
if st.sidebar.button("Clear Chats"):
    st.session_state.messages = []

# Input field for user query
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

                # Append user query and LLM response to chat history
                st.session_state.messages.append({"role": "user", "content": query})
                st.session_state.messages.append({"role": "assistant", "content": response_data.get("response", "No response found.")})
                # st.chat_message("assistant").write(response_data.get("response", "No response found."))

                # Display the chat history
                # for msg in st.session_state.messages:
                #     st.chat_message(msg["role"]).write(msg["content"])
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a query before submitting.")
