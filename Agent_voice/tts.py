import requests
from IPython.display import display, Audio
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_sarvam_api_key():
    """Retrieve the Sarvam API key from the environment variables."""
    return os.environ.get("SARVAM_API_KEY")

def create_payload(user_text, target_language="en-IN", speaker="maitreyi", pitch=1, pace=1, loudness=1, speech_sample_rate=16000, enable_preprocessing=True, model="bulbul:v1"):
    """Create a payload for the API request."""
    return {
        "inputs": [user_text],
        "target_language_code": target_language,
        "speaker": speaker,
        "pitch": pitch,
        "pace": pace,
        "loudness": loudness,
        "speech_sample_rate": speech_sample_rate,
        "enable_preprocessing": enable_preprocessing,
        "model": model
    }

def make_request(payload, api_key):
    """Make the POST request to the Sarvam API."""
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.text

def decode_audio_string(response_text):
    """Decode the base64-encoded audio string from the API response."""
    audio_string = response_text[12:-3]
    audio_data = base64.b64decode(audio_string)
    return audio_data

def save_audio_to_file(audio_data, audio_file_path):
    """Save the audio data to a file."""
    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_data)

    print(f"Audio saved to {audio_file_path}")
    return audio_file_path



# Main function to convert text to speech
def text_to_speech(user_text, audio_file_path):
    """Complete flow to convert text to speech and play the audio."""
    try:
        api_key = os.environ.get("SARVAM_API_KEY")
    except: 
        print("API key not found")
        return

    payload = create_payload(user_text)
    response_text = make_request(payload, api_key)
    print("Response:", response_text)

    audio_data = decode_audio_string(response_text)
    audio_file_path = save_audio_to_file(audio_data, audio_file_path)
    
    
if __name__ == "__main__":
    user_text = "તમારુ નામ શુ છે તામે ક્યા રહો છો"
    audio_file_path = "output.wav"
    text_to_speech(user_text, audio_file_path)



