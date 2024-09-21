import streamlit as st
import requests

# Define the FastAPI backend URL
api_url = "http://localhost:8000/agent"

st.title("Smart Action Agent")

# User selects the type of activity
activity = st.selectbox("Choose an activity:", 
                        ["Chat", "Play Number Guessing Game", "Play Character Guessing Game"])

# Button to start the selected game or chat
if activity == "Chat":
    user_input = st.text_input("Say something to the agent:")
    if st.button("Send"):
        if user_input:
            try:
                response = requests.post(api_url, json={"query": "chat"})
                if response.status_code == 200:
                    st.write(response.json()['response'])
            except Exception as e:
                st.error(f"Chat failed: {e}")

elif activity == "Play Number Guessing Game":
    if st.button("Start Number Game"):
        try:
            response = requests.post(api_url, json={"query": "start number game"})
            if response.status_code == 200:
                st.session_state["game_started"] = True
                st.session_state["feedback"] = response.json()['response']
        except Exception as e:
            st.error(f"Failed to start the game: {e}")
    
    if st.session_state.get("game_started", False):
        guess = st.number_input("Enter your guess", min_value=1, max_value=100, step=1)
        if st.button("Submit Guess"):
            try:
                response = requests.post(api_url, json={"query": "number guess", "guess": guess})
                if response.status_code == 200:
                    st.write(response.json()['response'])
                    if "Game over" in response.json()['response']:
                        st.session_state["game_started"] = False
            except Exception as e:
                st.error(f"Failed to submit guess: {e}")

elif activity == "Play Character Guessing Game":
    if st.button("Start Character Game"):
        try:
            response = requests.post(api_url, json={"query": "start character game"})
            if response.status_code == 200:
                st.session_state["game_started"] = True
                st.session_state["feedback"] = response.json()['response']
        except Exception as e:
            st.error(f"Failed to start the game: {e}")
    
    if st.session_state.get("game_started", False):
        char_guess = st.text_input("Enter your guess (A to E):").upper()
        if st.button("Submit Character Guess"):
            try:
                response = requests.post(api_url, json={"query": "character guess", "char_guess": char_guess})
                if response.status_code == 200:
                    st.write(response.json()['response'])
                    if "Game over" in response.json()['response']:
                        st.session_state["game_started"] = False
            except Exception as e:
                st.error(f"Failed to submit guess: {e}")
