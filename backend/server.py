import google.generativeai as genai
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.db import DBClient

client = None
async def lifespan(app: FastAPI):
    client = await DBClient.getInstance()  # ✅ Correct way to access DBClient
    yield
    DBClient.disconnect() 


app = FastAPI(lifespan=lifespan)

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

        # DBClient._client = AsyncIOMotorClient("mongodb+srv://alleharshith:dnKUfZ1JnrmAoJt5@cluster0.5bitg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


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

@app.get("/testing-client")
async def testing_client():
    instance1 = await DBClient.getInstance()
    instance2 = await DBClient.getInstance()
    return {
        "connected": instance1 is not None and instance2 is not None,
        "is_singleton": instance1 is instance2
    }

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level='debug')