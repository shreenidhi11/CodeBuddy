import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

def main():
    st.title("Interactive Problem Solving Session")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "topic" not in st.session_state:
        st.session_state.topic = None

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Problem input area
    if st.session_state.topic is None:
        problem_text = st.text_area("Paste your coding problem here:", height=150)
        if st.button("Submit Problem"):
            if problem_text:
                st.session_state.topic = problem_text
                st.session_state.messages.append({"role": "user", "content": f"Problem: {problem_text}"})
                
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
                    st.session_state.messages.append({"role": "agent", "content": agent_response})
                else:
                    st.error(f"Error communicating with backend: {response.text}")
                st.experimental_rerun()
            else:
                st.warning("Please paste a problem to submit.")
    
    # Chat input for ongoing conversation
    if prompt := st.chat_input("Your message:"):
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(prompt)

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
            st.session_state.messages.append({"role": "agent", "content": agent_response})
        else:
            st.error(f"Error communicating with backend: {response.text}")
        st.experimental_rerun()

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