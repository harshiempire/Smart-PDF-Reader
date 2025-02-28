import os
import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
genai.configure(api_key="AIzaSyCHBfiXfzFrehhldrjnWQDbBHkyXZEVXaA") 

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

class Payload(BaseModel):
    chat:str
    history:List
  
def get_message(text:str, history):
    # Create the model

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite-preview-02-05",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(
        history=history
    )

    response = chat_session.send_message(text,stream=True)
    for chunk in response:
        yield f"{ chunk.text }"

@app.post("/stream-chat")
def stream_chat(data:Payload=None):
    prompt = data.chat
    history = data.history
    return StreamingResponse(get_message(prompt, history=history), media_type="text/event-stream")

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level='debug')