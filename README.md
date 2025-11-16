# CodeBuddy - Personal Coding Tutor

## Project Description
CodeBuddy is a web-based personal coding tutor designed to assist students in understanding and solving coding problems. It provides an engaging environment where users can paste a coding problem, discuss concepts with AI, and then proceed to code their solution in an integrated editor.

## 📸 Demo

![Demo GIF](https://your-demo-link.com/demo.gif)

## 📦 Installation steps
Follow these steps to get CodeBuddy up and running:

### 1. Clone the Repository

First, clone the project repository to your local machine and change the directory to Codebuddy

`git clone https://github.com/shreenidhi11/CodeBuddy`

### 2. Backend Setup

The backend is a Python application.

1. Navigate into the  backend  directory:
`cd backend`

2. Create and activate a Python virtual environment:
`python -m venv venv && source venv/bin/activate`
On Windows, use `venv\Scripts\activate`

3. Install the required Python packages:
`pip install -r requirements.txt`

4. Start the backend server:
`uvicorn main:app --reload`
(The backend server will typically run on  http://localhost:8000 .)

### 3. Frontend Setup

The frontend is a Streamlit application.

1. Open a new terminal window or tab and navigate back to the root  CodeBuddy  directory, then into the  frontend  directory:
`cd .. && cd frontend`

2. Create and activate a Python virtual environment:
`python -m venv venv && source venv/bin/activate`
 On Windows, use `venv\Scripts\activate`

4. Install the required Python packages:
`pip install -r requirements.txt`

5. Start the Streamlit frontend application:
`streamlit run app.py`
(The frontend application will typically open in your web browser at  http://localhost:8501  or a similar port.)

## 🛠 Usage
Once both the backend and frontend servers are running, open your web browser and navigate to the Streamlit application (usually `http://localhost:8501`).

### 1. Start a Conversation

*   **Submit Your Problem**: In the "Conversation / Code Editor" tab, paste your coding problem into the provided text area and click "Submit Problem." The AI agent will respond, initiating the discussion.
*   **Chat with the AI**: Continue the conversation by typing your messages in the chat input box. Ask questions, seek clarifications, or delve deeper into concepts.

### 2. Code Your Solution

*   **Indicate Understanding**: When you feel you have grasped the concept and are ready to code, type "**i have understood the concept**" into the chat.
*   **Access the Code Editor**: The "Code your solution" section with the integrated Python editor will now appear.
*   **Write and Submit Code**: Write your Python code in the editor. Once complete, click "Submit Code for Review."
*   **Receive Feedback**: The AI agent will provide feedback on your submitted code, highlighting potential issues or suggesting improvements.

### 3. Take a Quiz

*   **Navigate to Quiz Tab**: Switch to the "Quiz" tab.
*   **Generate Quiz**: Click "Take a Quiz!" and then select your desired grade level (High School, Undergraduate, or Graduate). Click "Generate Quiz" to get questions based on your conversation topic.
*   **Answer and Submit**: Answer the quiz questions in the provided text areas and click "Submit Quiz."
*   **View Results**: Review your quiz results provided by the AI agent.

### 4. Review Summary

*   **Navigate to Summary Tab**: Switch to the "Summary" tab.
*   **Get Conversation Summary**: Click "Get Conversation Summary" to generate a concise summary of your entire discussion with the AI agent.
*   **Download Summary**: You can download the summary as a PDF or a plain TXT file for your records.

Once both the backend and frontend are running, you can interact with the application in your browser.

## ✨ Features
- **Guided Conversation**: Users can interact with an AI agent to clarify problem statements and deepen their understanding of concepts.
- **Code Editor**: A dedicated code editor allows users to write and submit their Python solutions for review.
- **Code Review Feedback**: The AI agent provides feedback on submitted code, helping users identify errors and improve their solutions.
- **Interactive Quizzes**: Users can take quizzes generated based on the discussed topic and their selected grade level (High School, Undergraduate, Graduate) to test their understanding.
- **Conversation Summary**: The application can generate a summary of the entire conversation, which can be downloaded as a PDF or TXT file for later review.

## 🧰 Tech Stack
**Backend:**
*   Python 3.12
*   FastAPI (as indicated by uvicorn dependency)
*   Gemini LLM

**Frontend:**
*   Streamlit (for interactive applications, as indicated by streamlit dependency)

**Prerequisites:**
*   Python 3.8+
*   pip
*   Gemini Account and API key

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

## Credits used
* **Build a basic LLM chat app** - https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps 
  * To build the chat application using streamlit
* **Code editor** -https://github.com/marcusschiesser/streamlit-monaco
  * To integrate a code editor directly in the conversation with AI and user
* **Cline (Vibe Coding)** -  https://app.cline.bot/dashboard
  * End-to-end building, troubleshooting, debugging and testing of the web application
* **Github ReadMe** - https://medium.com/@fulton_shaun/readme-rules-structure-style-and-pro-tips-faea5eb5d252
