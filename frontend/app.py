import streamlit as st
import requests
from streamlit_ace import st_ace

BACKEND_URL = "http://localhost:8000"


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
                # st.experimental_rerun()
            else:
                st.warning("Please paste a problem to submit.")



    # Chat input for ongoing conversation
    if prompt := st.chat_input("Your message:"):
        # Clear any existing code review feedback when a new message is entered
        st.session_state.code_review_feedback = None

        print("I am here")
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(prompt)
        if "i have understood the concept" in prompt.lower():
            st.session_state.concept_understood = True
            st.session_state.messages.append(
                {"role": "agent", "content": "Great! Now you can try coding your solution below. If you want to go back to discussing the concept, just say so."})
            # st.experimental_rerun()

        elif "go back to concept" in prompt.lower() and st.session_state.concept_understood:
            st.session_state.concept_understood = False
            st.session_state.messages.append(
                {"role": "agent", "content": "Okay, let's go back to discussing the concept. What's your next question?"})
            # st.experimental_rerun()
        
        else:


        # Prepare conversation history for backend
            conversation_history_for_backend = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
            ]

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
                st.error(f"Error communicating with backend: {response.text}")
            
        st.rerun()
        # Code editor appears only if concept is understood
    # st.rerun()
    if st.session_state.concept_understood:
        st.subheader("Code your solution")
        # content = st_ace(language="python", theme="dracula", keybind="vscode",
        #                  font_size=14, tab_size=4, show_gutter=True, show_print_margin=True,
        #                  wrap=False, auto_update=True, readonly=False,
        #                  min_lines=20, value="# Write your Python code here")
        content = st_ace(language="python", theme="dracula", value="# Write your Python code here")
        if st.button("Submit Code for Review"):
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
            st.rerun()

        if st.session_state.code_review_feedback:
            with st.chat_message("agent"):
                st.markdown(f"Code Review: {st.session_state.code_review_feedback}")
            
            # Clear feedback after displaying
            st.session_state.code_review_feedback = None 

    # # Check for keywords to toggle concept_understood state
    # if prompt and "i have understood the concept" in prompt.lower():
    #     st.session_state.concept_understood = True
    #     st.session_state.messages.append(
    #         {"role": "agent", "content": "Great! Now you can try coding your solution below. If you want to go back to discussing the concept, just say so."})
    #     st.rerun()
    # elif prompt and "go back to concept" in prompt.lower() and st.session_state.concept_understood:
    #     st.session_state.concept_understood = False
    #     st.session_state.messages.append(
    #         {"role": "agent", "content": "Okay, let's go back to discussing the concept. What's your next question?"})
    #     st.rerun()

    # End conversation button
    # if st.session_state.topic is not None and st.button("End Conversation"):
    #     response = requests.post(
    #         f"{BACKEND_URL}/chat",
    #         json={
    #             "topic": st.session_state.topic,
    #             "conversation_history": [
    #                 {"role": msg["role"], "content": msg["content"]}
    #                 for msg in st.session_state.messages if msg["role"] in ["user", "agent"]
    #             ],
    #             "end_conversation": True
    #         }
    #     )
    #     if response.status_code == 200:
    #         summary = response.json().get("summary")
    #         st.session_state.messages.append({"role": "agent", "content": f"Conversation Summary: {summary}"})
    #         st.session_state.topic = None  # Reset topic to allow new problems
    #         st.success("Conversation ended and summarized.")
    #     else:
    #         st.error(f"Error communicating with backend for summarization: {response.text}")
    #     st.experimental_rerun()


if __name__ == "__main__":
    main()