import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os


from typing import List, Dict, Union, Literal

# Configure Gemini API
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Allow Streamlit's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class CodeVerificationRequest(BaseModel):
    code: str
    conversation_history: List[Dict[str, str]] = []


@app.post("/verify_code")
async def verify_code(request: CodeVerificationRequest):
    prompt = f"""You are a \"Socratic TA\" helping a student with a coding problem.
The student has submitted the following Python code:

```python
{request.code}
```

Your task is to review the code and provide constructive feedback without directly giving the solution.
Focus on logical errors, inefficiencies, or areas where the code doesn't align with the problem's requirements.
Ask leading questions to guide the student to discover and correct their own mistakes.
Consider the following conversation history for context (if any):

"""

    for message in request.conversation_history:
        prompt += f"{message["role"]}: {message["content"]}\n"
    prompt += f"\nBased on the above, please provide feedback on the student's submitted code using leading questions."

    response = model.generate_content(prompt)
    feedback = response.text
    return {"feedback": feedback}


class QuizRequest(BaseModel):
    topic: str
    grade: str
    conversation_history: List[Dict[str, str]] = []


class QuizSubmissionRequest(BaseModel):
    topic: str
    questions: List[Dict[str, str]]
    answers: Dict[str, str]
    conversation_history: List[Dict[str, str]] = []


@app.post("/generate_quiz")
async def generate_quiz(request: QuizRequest):
    prompt = f"""You are a Socratic TA creating a quiz for a student.
Based on the topic: {request.topic} and grade level: {request.grade}, generate 3-5 short answer quiz questions.
Provide only the questions and no answers. Format each question as a JSON object with a 'question' key.
"""

    response = model.generate_content(prompt)
    # Assuming the response text can be parsed as JSON directly or needs some cleaning
    questions_text = response.text.replace(
        "```json", "").replace("```", "").strip()
    try:
        questions = json.loads(questions_text)
    except json.JSONDecodeError:
        # Fallback for malformed JSON, try to extract questions heuristically or return an error
        questions = [
            {"question": f"Could not parse quiz question: {questions_text}"}]
    return {"questions": questions}


@app.post("/submit_quiz")
async def submit_quiz(request: QuizSubmissionRequest):
    prompt = f"""You are a Socratic TA evaluating a student's quiz answers.
Topic: {request.topic}
Questions and provided answers:
"""
    for q_data in request.questions:
        question = q_data["question"]
        answer = request.answers.get(question, "No answer provided")
        prompt += f"\nQuestion: {question}\nStudent Answer: {answer}\n"

    prompt += f"""\nBased on these answers and the conversation history, provide constructive feedback.\n
Identify areas where the student is lacking and suggest 2-3 specific topics or concepts they should review.\n
Do not give direct answers but guide them with leading questions."""

    for message in request.conversation_history:
        prompt += f"{message["role"]}: {message["content"]}\n"

    response = model.generate_content(prompt)
    results = response.text
    return {"results": results}


class ChatRequest(BaseModel):
    topic: str
    conversation_history: List[Dict[str, str]] = []
    end_conversation: bool = False


@app.post("/generate_quiz")
async def generate_quiz(request: QuizRequest):
    prompt = f"""You are a Socratic TA creating a quiz for a student.
Based on the topic: {request.topic} and grade level: {request.grade}, generate 3-5 short answer quiz questions.
Provide only the questions and no answers. Format each question as a JSON object with a 'question' key.
"""

    response = model.generate_content(prompt)
    # Assuming the response text can be parsed as JSON directly or needs some cleaning
    questions_text = response.text.replace(
        "```json", "").replace("```", "").strip()
    try:
        questions = json.loads(questions_text)
    except json.JSONDecodeError:
        # Fallback for malformed JSON, try to extract questions heuristically or return an error
        questions = [
            {"question": f"Could not parse quiz question: {questions_text}"}]
    return {"questions": questions}


@app.post("/submit_quiz")
async def submit_quiz(request: QuizSubmissionRequest):
    prompt = f"""You are a Socratic TA evaluating a student's quiz answers.
Topic: {request.topic}
Questions and provided answers:
"""
    for q_data in request.questions:
        question = q_data["question"]
        answer = request.answers.get(question, "No answer provided")
        prompt += f"\nQuestion: {question}\nStudent Answer: {answer}\n"

    prompt += f"""\nBased on these answers and the conversation history, provide constructive feedback.
Identify areas where the student is lacking and suggest 2-3 specific topics or concepts they should review.
Do not give direct answers but guide them with leading questions."""

    for message in request.conversation_history:
        prompt += f"{message["role"]}: {message["content"]}\n"

    response = model.generate_content(prompt)
    results = response.text
    return {"results": results}


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
8.  If the student says that "i have understood the concept" you can stop explaining

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


class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: Literal["user", "agent"]
    content: str


class SummarizeRequest(BaseModel):
    """The request body for the /summarize endpoint."""
    conversation_history: List[ChatMessage]


def get_summary_from_llm(history: ChatRequest) -> str:
    """
    Placeholder function for generating a summary.
    Replace this with your actual summarization model call.
    """
    print("Received request to summarize conversation...")

    if not history.conversation_history:
        return "The conversation was empty. No summary could be generated."

    # LLM interaction using Gemini
    prompt = "You are a summarization assistant. Summarize the conversation history in the simplest manner possible with respect to the topic {history.topic}. Highlight important concepts and learning tips for the " \
        "student"

    for message in history.conversation_history:
        prompt += f"{message["role"]}: {message["content"]}\n"

    # Combine the conversation into a single string for the LLM

    summary = model.generate_content(prompt)
    print(summary)
    print(summary.text)
    results = summary.text

    # --- START: Replace this mock logic ---
    # This is where you would call your LLM.
    # For example:
    # client = OpenAI()
    # response = client.chat.completions.create(
    #   model="gpt-4o-mini",
    #   messages=[
    #     {"role": "system", "content": ""},
    #     {"role": "user", "content": full_conversation}
    #   ]
    # )
    # summary = response.choices[0].message.content

    # Using placeholder logic for now:
    # summary = f"This is a placeholder summary of the conversation.\n\n"
    # summary += f"The conversation had {len(history)} messages.\n"
    # summary += f"The topic was about: {history[0].content[:50]}...\n"
    # summary += "Key points discussed include:\n"
    # summary += "- Conceptual understanding of the problem.\n"
    # summary += "- Code implementation and review.\n"
    # summary += "- A quiz to test knowledge."
    # # --- END: Replace this mock logic ---

    print("Summary generated.")
    return {"summary": results}


@app.post("/summarize")
async def summarize_conversation(request: ChatRequest):
    """
    Receives conversation history and returns a summary.
    This endpoint is called from the "Summary" tab in the Streamlit app.
    """
    if not request.conversation_history:
        return "The conversation was empty. No summary could be generated."
    try:

        # LLM interaction using Gemini
        prompt = "You are a summarization assistant. Summarize the conversation history in the simplest manner possible with respect to the topic {request.topic}. Highlight important concepts and learning tips for the " \
            "student." \
            "Restrict yourself from using any bold words."

        for message in request.conversation_history:
            prompt += f"{message["role"]}: {message["content"]}\n"

    # Combine the conversation into a single string for the LLM

        summary = model.generate_content(prompt)
        print(summary)
        print(summary.text)
        results = summary.text

        return {"summary": results}

    except Exception as e:
        # Log the error and return a 500 status
        print(f"Error during summarization: {e}")
        return {"summary": "An error occurred while generating the summary."}, 500
