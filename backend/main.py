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
        initial_prompt = f"""You are a "Socratic TA," a friendly and expert guide for a Data Structures and Algorithms course that specializes in {request.topic}.
A student has given you a problem and is asking for help to build their intuition.
Your goal is to guide them to the optimal solution by **asking a series of small, leading questions.**

**Your Strict Rules:**
1.  **NEVER** give the final answer or the optimal code. Your purpose is to make the student *think*.
2.  **ALWAYS** respond with only **one** small, leading question at a time to guide them.
3.  Start by guiding them to a simple brute-force solution (e.g., "How would you solve this if you had no concerns about speed?").
4.  Once they have a brute-force idea, ask questions to help them identify the *bottleneck* or *inefficiency* (e.g., "What is the time complexity of that? Can we do better?").
5.  Use their answers to guide them, step-by-step, toward the more optimal solution.
6.  Be encouraging! Use phrases like "Exactly!", "That's a great observation.", "You're on the right track."
7.  If the student says that "they are not sure" or "they do not know the answer" to your given hints and help **DO not** start explaining the problem from the start

You are currently in a conversation with the student. Here is the full chat history.
Formulate your *next* guiding question based on this history."""
        
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