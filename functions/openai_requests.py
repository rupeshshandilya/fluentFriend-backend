import os
from functions.database import get_recent_messages
from dotenv import load_dotenv
from openai import OpenAI

# Load configurations from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Convert audio to text
def convert_audio_to_text(audio_file):
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )
        return transcript
    except Exception as e:
        print(f"Error in OpenAI API call (convert_audio_to_text): {e}")
        raise


# Chat GPT
def get_chat_response(message_input):
    messages = get_recent_messages()
    user_message = {"role": "user", "content": message_input}
    messages.append(user_message)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        message_text = response.choices[0].message.content
        return message_text
    except Exception as e:
        print(f"Error in OpenAI API call (get_chat_response): {e}")
        return None


# Convert text to speech
def convert_text_to_speech(message):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=message
        )
        if response:
            return response.content
        else:
            return None
    except Exception as e:
        print(f"Error in OpenAI API call (convert_text_to_speech): {e}")
        return None
