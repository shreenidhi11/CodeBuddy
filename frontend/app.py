import streamlit as st
import requests
from streamlit_ace import st_ace
from fpdf import FPDF
import warnings  # Import the warnings module
import base64  # Import base64 module

BACKEND_URL = "http://localhost:8000"


def get_pdf_download_html(text, filename="summary.pdf"):
    """Generates a base64-encoded PDF and returns an HTML download link."""
    try:
        pdf = FPDF()
        pdf.add_page()

        # Add a font that supports UTF-8 (like DejaVu)
        # This is a common requirement for FPDF to handle diverse characters.
        # We'll try Arial first, but fall back.
        try:
            pdf.set_font("Arial", size=11)
            # Encode to latin-1, replacing unsupported chars. A common FPDF workaround.
            safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        except (AttributeError, UnicodeEncodeError):
            # Fallback for complex characters - this may still fail on some environments
            # without a proper unicode font file (e.g., DejaVuSans.ttf)
            pdf.set_font("Times", size=11)
            safe_text = str(text).encode(
                'latin-1', 'replace').decode('latin-1')

        pdf.multi_cell(0, 5, safe_text)

        # Get PDF bytes output
        # Suppress FPDF deprecation warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pdf_bytes = pdf.output(dest='S').encode('latin-1')

        b64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Create the HTML download link with Streamlit-like button styling
        href = f"""
            <a href="data:application/pdf;base64,{b64}" download="{filename}" 
               style="display: inline-flex; align-items: center; justify-content: center;
                      background-color: #0d6efd; color: white; padding: .25rem .75rem; 
                      font-size: 1rem; font-weight: 400; line-height: 1.6;
                      border: 1px solid transparent; border-radius: .375rem; 
                      text-decoration: none; cursor: pointer; user-select: none;">
                Download Summary as PDF
            </a>
        """
        return href
    except Exception as e:
        # If PDF fails, show an error and don't provide the link
        st.error(f"Error generating PDF: {e}. Please use the TXT download.")
        return ""



def main():
    st.title("Interactive Problem Solving Session")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "topic" not in st.session_state:
        st.session_state.topic = None
    if "concept_understood" not in st.session_state:
        st.session_state.concept_understood = False
    if "code_review_feedback" not in st.session_state:
        st.session_state.code_review_feedback = None
    if "quiz_active" not in st.session_state:
        st.session_state.quiz_active = False
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_results" not in st.session_state:
        st.session_state.quiz_results = None
    if "conversation_summary" not in st.session_state:
        st.session_state.conversation_summary = None  # New state for summary

    conversation_tab, quiz_tab, summary_tab = st.tabs(
        ["Conversation / Code Editor", "Quiz", "Summary"])

    with conversation_tab:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Problem input area
        if st.session_state.topic is None:
            problem_text = st.text_area(
                "Paste your coding problem here:", height=150)
            if st.button("Submit Problem"):
                if problem_text:
                    st.session_state.topic = problem_text
                    st.session_state.messages.append(
                        {"role": "user", "content": f"Problem: {problem_text}"})

                    # Send initial problem to backend
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={
                                "topic": st.session_state.topic,
                                "conversation_history": [],
                                "end_conversation": False
                            }
                        )
                        if response.status_code == 200:
                            agent_response = response.json().get("answer")
                            st.session_state.messages.append(
                                {"role": "agent", "content": agent_response})
                        else:
                            st.error(
                                f"Error communicating with backend: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")
                    
                    st.rerun() # Rerun after submitting problem
                else:
                    st.warning("Please paste a problem to submit.")
                    
        # --- START OF MODIFICATION ---
        
        # Only show chat input if the problem is submitted AND the concept is NOT understood
        if not st.session_state.concept_understood and st.session_state.topic is not None:
            if prompt := st.chat_input("Your message:"):
                # Clear any existing code review feedback when a new message is entered
                st.session_state.code_review_feedback = None
                
                user_message = {"role": "user", "content": prompt}
                st.session_state.messages.append(user_message)
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                if "i have understood the concept" in prompt.lower():
                    st.session_state.concept_understood = True
                    # Add agent's response
                    st.session_state.messages.append(
                        {"role": "agent", "content": "Great! Now you can try coding your solution below. If you want to go back to discussing the concept, just click the 'Back to Discussion' button."}
                    )
                    st.rerun()

                # REMOVED "go back to concept" from here. It's now a button.

                else:
                    # Prepare conversation history for backend
                    conversation_history_for_backend = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
                    ]
                    
                    try:
                        # Send ongoing conversation to backend
                        response = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={
                                "topic": st.session_state.topic,
                                "conversation_history": conversation_history_for_backend,
                                "end_conversation": False
                            }
                        )
                        if response.status_code == 200:
                            agent_response = response.json().get("answer")
                            st.session_state.messages.append(
                                {"role": "agent", "content": agent_response})
                        else:
                            st.error(
                                f"Error communicating with backend: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")

                st.rerun()

        # Code editor appears only if concept is understood
        if st.session_state.concept_understood:
            st.subheader("Code your solution")
            
            # ADDED a button to go back to the discussion
            if st.button("Back to Discussion", key='back_to_discussion_code'):
                st.session_state.concept_understood = False
                st.session_state.messages.append(
                    {"role": "agent", "content": "Okay, let's go back to discussing the concept. What's your next question?"}
                )
                st.rerun()

            content = st_ace(language="python", theme="dracula",
                             value="# Write your Python code here")
            if st.button("Submit Code for Review"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/verify_code",
                        json={
                            "code": content,
                            "conversation_history": [
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
                            ]
                        }
                    )
                    if response.status_code == 200:
                        st.session_state.code_review_feedback = response.json().get("feedback")
                    else:
                        st.error(f"Error communicating with backend for code review: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
                
                st.rerun()

            if st.session_state.code_review_feedback:
                with st.chat_message("agent"):
                    st.markdown(
                        f"Code Review: {st.session_state.code_review_feedback}")

                # Clear feedback after displaying
                st.session_state.code_review_feedback = None
        
        # --- END OF MODIFICATION ---

    with quiz_tab:
        # Quiz functionality
        if st.session_state.topic and not st.session_state.quiz_active:
            if st.button("Take a Quiz!"):
                st.session_state.quiz_active = True
                st.rerun() # Use st.rerun

        if st.session_state.quiz_active and not st.session_state.quiz_questions:
            st.subheader("Quiz Time!")
            grade = st.selectbox("Select your grade level:", [
                                 "High School", "Undergraduate", "Graduate"])
            if st.button("Generate Quiz"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/generate_quiz",
                        json={
                            "topic": st.session_state.topic,
                            "grade": grade,
                            "conversation_history": [
                                {"role": msg["role"], "content": msg["content"]}
                                for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
                            ]
                        }
                    )
                    if response.status_code == 200:
                        st.session_state.quiz_questions = response.json().get("questions")
                        st.session_state.messages.append(
                            {"role": "agent", "content": "Here's your quiz!"})
                    else:
                        st.error(f"Error generating quiz: {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
                
                st.rerun() # Use st.rerun

        if st.session_state.quiz_active and st.session_state.quiz_questions:
            st.subheader("Answer the Quiz Questions")
            with st.form(key='quiz_form'):
                user_answers = {}
                for i, q_data in enumerate(st.session_state.quiz_questions):
                    st.markdown(f"**Question {i+1}:** {q_data["question"]}")
                    user_answers[q_data["question"]] = st.text_area(
                        f"Your answer for Question {i+1}:", key=f"q_{i}")

                submit_quiz = st.form_submit_button("Submit Quiz")
                if submit_quiz:
                    st.session_state.quiz_answers = user_answers
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/submit_quiz",
                            json={
                                "topic": st.session_state.topic,
                                "questions": st.session_state.quiz_questions,
                                "answers": st.session_state.quiz_answers,
                                "conversation_history": [
                                    {"role": msg["role"],
                                        "content": msg["content"]}
                                    for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
                                ]
                            }
                        )
                        if response.status_code == 200:
                            st.session_state.quiz_results = response.json().get("results")
                            st.session_state.messages.append(
                                {"role": "agent", "content": "Quiz submitted! Here are your results."})
                        else:
                            st.error(f"Error submitting quiz: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")
                    
                    st.rerun() # Use st.rerun

        if st.session_state.quiz_results:
            st.subheader("Quiz Results")
            st.markdown(st.session_state.quiz_results)
            if st.button("Back to next set of quiz", key='back_to_discussion_quiz'):
                st.session_state.quiz_active = False
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_results = None
                st.rerun() # Use st.rerun

    # ... (summary_tab code remains the same) ...
    with summary_tab:
        st.subheader("Conversation Summary")

        if not st.session_state.topic:
            st.info(
                "Start a conversation in the first tab to be able to generate a summary.")
        else:
            if st.button("Get Conversation Summary"):
                with st.spinner("Generating summary..."):
                    # Prepare conversation history
                    conversation_history_for_backend = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
                    ]

                    # Call the new /summarize endpoint
                    try:
                        response = requests.post(
                            # Assuming this is your new endpoint
                            f"{BACKEND_URL}/summarize",
                            # json={
                            #     "conversation_history": conversation_history_for_backend
                            # }
                            json={
                                "topic": st.session_state.topic,
                                "conversation_history": [
                                    {"role": msg["role"],
                                        "content": msg["content"]}
                                    for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
                                ]
                            }

                        )
                        if response.status_code == 200:
                            # --- 2. ADDED THIS LOGIC BLOCK ---
                            summary_data = response.json().get("summary")

                            if isinstance(summary_data, str):
                                st.session_state.conversation_summary = summary_data
                            elif isinstance(summary_data, dict):
                                # If it's a dict, warn the user and convert to string to prevent crashing
                                st.warning(
                                    "Received unexpected summary format (dictionary). Converting to string.")
                                st.session_state.conversation_summary = str(
                                    summary_data)
                            else:
                                # Handle any other unexpected types
                                st.warning(
                                    f"Received unknown summary format ({type(summary_data)}). Converting to string.")
                                st.session_state.conversation_summary = str(
                                    summary_data)
                            # --- End of added block ---

                            # st.success("Summary generated!")
                        else:
                            st.error(
                                f"Error generating summary: {response.text}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")

            # Display summary and download buttons if summary exists
            if st.session_state.conversation_summary:
                # Display the summary in a scrollable, non-editable text area
                st.text_area(
                    "Summary",
                    st.session_state.conversation_summary,
                    height=400,
                    disabled=True,
                    label_visibility="collapsed"
                )

                st.divider()

                # --- Download Buttons ---
                col1, col2 = st.columns(2)

                with col1:
                    # PDF Download
                    pdf_html = get_pdf_download_html(
                        st.session_state.conversation_summary)
                    if pdf_html: # Only show if PDF generation was successful
                        st.markdown(pdf_html, unsafe_allow_html=True)

                with col2:
                    # TXT Download (as a fallback)
                    st.download_button(
                        label="Download Summary as TXT",
                        data=st.session_state.conversation_summary,
                        file_name="conversation_summary.txt",
                        mime="text/plain"
                    )
            elif st.session_state.topic: # Show only if topic exists but summary doesn't
                st.info(
                    "Click the button above to generate a summary of your conversation.")


if __name__ == "__main__":
    main()