from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os


from typing import List, Dict, Union

# Configure Gemini API
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI()

class ChatRequest(BaseModel):
    topic: str
    conversation_history: List[Dict[str, str]] = []
    end_conversation: bool = False

@app.post("/chat")
async def chat(request: ChatRequest):
    if request.end_conversation:
        # Summarization logic using Gemini
        prompt = f"Please summarize the following conversation about {request.topic}:\n\n"
        for message in request.conversation_history:
            prompt += f"{message["role"]}: {message["content"]}\n"
        response = model.generate_content(prompt)
        summary = response.text
        return {"summary": summary, "conversation_ended": True}
    else:
        # LLM interaction using Gemini
        initial_prompt = f"You are an AI assistant specialized in {request.topic}. Please engage in a helpful and informative conversation.\n\n"
        
        # Format conversation history for Gemini
        formatted_history = []
        for message in request.conversation_history:
            formatted_history.append(message)
            
        # Add current user message
        if not request.conversation_history:
            user_message = f"Hello! I want to talk about {request.topic}."
        else:
            user_message = request.conversation_history[-1].get("content", "")

        response = model.generate_content(initial_prompt + user_message)
        answer = response.text
        return {"answer": answer}