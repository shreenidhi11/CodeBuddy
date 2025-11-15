# CodeBuddy - Personal Coding Tutor

## Project Description
CodeBuddy is a personal coding tutor designed to help users build intuition for long-lasting concept understanding in programming. It aims to provide an interactive and supportive learning environment for various coding concepts.

## Features
*   Interactive coding exercises
*   Personalized learning paths
*   Concept explanations and examples

## Technologies Used
**Backend:**
*   Python
*   FastAPI (as indicated by uvicorn dependency)
*   Streamlit (for interactive applications, as indicated by streamlit dependency)
*   Pandas, Numpy, Altair, Pydeck (for data manipulation, analysis, and visualization)
*   GitPython (for Git integration)
*   dotenv (for environment variable management)

**Frontend:**
*   (Currently, no specific frontend framework is discernible from the provided files. This section can be updated if more information becomes available.)

## Installation

### Prerequisites
*   Python 3.8+
*   pip

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shreenidhi11/CodeBuddy.git
    cd CodeBuddy
    ```

2.  **Set up the backend virtual environment:**
    ```bash
    cd backend
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Run the backend application:**
    ```bash
    uvicorn main:app --reload
    ```
    (Note: Assuming `main.py` contains a FastAPI app named `app`. Please correct if this is not the case.)

## Usage
(To be filled in with instructions on how to use CodeBuddy once the features are more defined.)

## Contributing
(Guidelines for contributing to the project can be added here.)

## License
(License information can be added here.)

## Resources used
https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps -- to build the chat application
https://github.com/marcusschiesser/streamlit-monaco -- online code editor
