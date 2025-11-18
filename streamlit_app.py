import streamlit as st
from openai import OpenAI
import os

# Function to read content from a text file
def read_file(file_name: str) -> str:
    with open(file_name, "r", encoding="utf-8") as file:
        return file.read().strip()

# Load configuration from files
SYSTEM_PROMPT_FILE = "01.system_trainning.txt"
ASSISTANT_PROMPT_FILE = "02.assistant.txt"
TITLE_FILE = "00.xinchao.txt"
MODEL_FILE = "gpt-4o-mini"  # Assuming this file contains the model name

INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": read_file(SYSTEM_PROMPT_FILE)}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": read_file(ASSISTANT_PROMPT_FILE)}
TITLE_CONTENT = read_file(TITLE_FILE)
MODEL_NAME = read_file(MODEL_FILE)

# Display logo if available
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("israel-flag.png", use_column_width=True)
except FileNotFoundError:
    pass  # Ignore if image is missing

# Display centered title
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px;">{TITLE_CONTENT}</h1>""",
    unsafe_allow_html=True
)

# Get OpenAI API key
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Display API key status in sidebar
st.sidebar.write("🔐 Has API key:", bool(openai_api_key))

# Halt if no API key
if not openai_api_key:
    st.error(
        "*Không tìm thấy OPENAI_API_KEY. "
        "Hãy đặt nó trong Secrets của Streamlit hoặc trong biến môi trường.*"
    )
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# Custom CSS for message styling
st.markdown(
    """
    <style>
        .assistant {
            padding: 10px;
            border-radius: 10px;
            max-width: 75%;
            background: none; /* Transparent background */
            text-align: left;
        }
        .user {
            padding: 10px;
            border-radius: 10px;
            max-width: 75%;
            background: none; /* Transparent background */
            text-align: right;
            margin-left: auto;
        }
        .assistant::before { content: "🤖 "; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

# Display chat history (exclude system messages)
for message in st.session_state.messages:
    if message["role"] == "assistant":
        st.markdown(f'<div class="assistant">{message["content"]}</div>', unsafe_allow_html=True)
    elif message["role"] == "user":
        st.markdown(f'<div class="user">{message["content"]}</div>', unsafe_allow_html=True)

# User input
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user">{prompt}</div>', unsafe_allow_html=True)
    
    # Prepare for streaming response
    response_placeholder = st.empty()
    full_response = ""
    
    # Stream response from OpenAI
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            # Update placeholder with current response
            response_placeholder.markdown(f'<div class="assistant">{full_response}</div>', unsafe_allow_html=True)
    
    # Append full response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})