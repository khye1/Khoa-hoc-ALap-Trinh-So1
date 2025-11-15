import streamlit as st
from openai import OpenAI
from pathlib import Path
import os

# ======================
# Configuration & Setup
# ======================

# File reading utility
def read_file(filename: str) -> str:
    """Read and return content of a text file."""
    try:
        return Path(filename).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        st.error(f"File not found: {filename}")
        return ""

# Initialize OpenAI client
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OPENAI_API_KEY not found in secrets.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# Load static content
TITLE = read_file("00.xinchao.txt")
SYSTEM_PROMPT = read_file("01.system_trainning.txt")
ASSISTANT_GREETING = read_file("02.assistant.txt")
MODEL_NAME = read_file("module_chatgpt.txt").strip()

# Validate required files
if not all([TITLE, SYSTEM_PROMPT, ASSISTANT_GREETING, MODEL_NAME]):
    st.error("One or more required files are missing or empty.")
    st.stop()

# ======================
# UI Layout
# ======================

# Logo (centered)
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("israel-flag.png", use_container_width=True)
except Exception:
    pass  # Silently ignore if logo missing

# Title
st.markdown(
    f'<h1 style="text-align: center; font-size: 24px;">{TITLE}</h1>',
    unsafe_allow_html=True
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": ASSISTANT_GREETING}
    ]

# ======================
# Display Chat History
# ======================

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue  # Skip system prompt
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ======================
# User Input & Streaming Response
# ======================

if prompt := st.chat_input("Sếp nhập nội dung cần trao đổi ở đây nhé?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate assistant response with streaming
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")  # Cursor effect

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error communicating with OpenAI: {e}")
            full_response = "Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của Sếp."

        # Save assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})