# uvicorn main:app
# uvicorn main:app --reload
from dotenv import load_dotenv
import os

# Load configurations from .env file
load_dotenv()

# Main imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware



# import openai
import time

# Custom function imports
# from functions.text_to_speech import convert_text_to_speech
from functions.openai_requests import convert_audio_to_text, get_chat_response, convert_text_to_speech
from functions.database import store_messages, reset_messages


# Get Environment Vars
# raise Exception("The 'openai.organization' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(organization=os.getenv("OPEN_AI_ORG"))'")



# Initiate App
app = FastAPI()


# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "https://curious-faloodeh-7f2a85.netlify.app",
]


# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Check health
@app.get("/health")
async def check_health():
    return {"response": "healthy"}


# Reset Conversation
@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"response": "conversation reset"}


# Post bot response
# Note: Not playing back in browser when using post request.
@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):

    print(f"Received POST request to /post-audio/ with file: {file.filename}")

    # Convert audio to text - production
    # Save the file temporarily


    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())
    audio_input = open(file.filename, "rb")

    # Decode audio
    message_decoded = convert_audio_to_text(audio_input)
    print("Audio decoding completed.")

    # Guard: Ensure output
    if not message_decoded:
        raise HTTPException(status_code=400, detail="Failed to decode audio")
    print(f"Message Decoded: {message_decoded}")

    start_time = time.time()

    # Get chat response
    chat_response = get_chat_response(message_decoded)
    print(f"Chat Response: {chat_response}")

    # Calculate the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    # Store messages
    store_messages(message_decoded, chat_response)

    # Guard: Ensure output
    if not chat_response:
        raise HTTPException(status_code=400, detail="Failed chat response")

    # Convert chat response to audio
    audio_output = convert_text_to_speech(chat_response)

    # Guard: Ensure output
    if not audio_output:
        raise HTTPException(status_code=400, detail="Failed audio output")

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output


    # Print the elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")

    # Use for Post: Return output audio
    return StreamingResponse(iterfile(), media_type="application/octet-stream")
