import streamlit as st
from openai import OpenAI
import os

# -------------------------------------------------
# Helper: read text file (UTF-8)
# -------------------------------------------------
def rfile(name_file: str) -> str:
    try:
        with open(name_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Không tìm thấy file: `{name_file}`")
        st.stop()
    except Exception as e:
        st.error(f"Lỗi đọc file `{name_file}`: {e}")
        st.stop()

# -------------------------------------------------
# UI: Logo (optional)
# -------------------------------------------------
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("israel-flag.png", use_container_width=True)
except Exception:
    pass

# -------------------------------------------------
# UI: Title
# -------------------------------------------------
title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px;">{title_content}</h1>""",
    unsafe_allow_html=True,
)

# -------------------------------------------------
# OpenAI client
# -------------------------------------------------
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OPENAI_API_KEY chưa được cấu hình trong Secrets!")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# -------------------------------------------------
# System & initial assistant messages
# -------------------------------------------------
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# -------------------------------------------------
# CSS for chat bubbles
# -------------------------------------------------
st.markdown(
    """
    <style>
        .assistant {
            padding: 10px;
            border-radius: 10px;
            max-width: 75%;
            background: none;
            text-align: left;
            margin-bottom: 8px;
        }
        .user {
            padding: 10px;
            border-radius: 10px;
            max-width: 75%;
            background: none;
            text-align: right;
            margin-left: auto;
            margin-bottom: 8px;
        }
        .assistant::before { content: "🤖 "; font-weight: bold; }
        .user::before     { content: "👤 "; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# Render chat history (skip system)
# -------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(f'<div class="assistant">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "user":
        st.markdown(f'<div class="user">{msg["content"]}</div>', unsafe_allow_html=True)

# -------------------------------------------------
# User input
# -------------------------------------------------
if prompt := st.chat_input("Sếp nhập nội dung cần trao đổi ở đây nhé?"):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user">{prompt}</div>', unsafe_allow_html=True)

    # Load model name safely
    model_name = rfile("module_chatgpt.txt").strip()
    if not model_name:
        st.error("File `module_chatgpt.txt` trống hoặc không hợp lệ!")
        st.stop()

    # Call OpenAI with streaming
    try:
        stream = client.chat.completions.create(
            model=model_name,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
            temperature=0.7,
        )

        response = ""
        response_placeholder = st.empty()  # For live update

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
                response_placeholder.markdown(
                    f'<div class="assistant">{response}</div>', unsafe_allow_html=True
                )

        # Save final assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"Lỗi gọi OpenAI API: {str(e)}")
        if "authentication" in str(e).lower():
            st.error("Kiểm tra lại `OPENAI_API_KEY` trong Secrets.")
        elif "model" in str(e).lower():
            st.error(f"Model không tồn tại hoặc không được phép: `{model_name}`")