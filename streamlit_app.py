import streamlit as st
from openai import OpenAI
import os

# ======================
# Hàm đọc file văn bản
# ======================
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        st.error(f"Không tìm thấy file: `{name_file}`")
        st.stop()
    except Exception as e:
        st.error(f"Lỗi đọc file `{name_file}`: {e}")
        st.stop()

# ======================
# Cấu hình trang
# ======================
st.set_page_config(page_title="Trợ lý AI", page_icon="🇮🇱", layout="centered")

# ======================
# Hiển thị logo & tiêu đề
# ======================
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("israel-flag.png", use_container_width=True)
except:
    pass

title_content = rfile("00.xinchao.txt")
st.markdown(
    f"""<h1 style="text-align: center; font-size: 24px; margin-bottom: 30px;">{title_content}</h1>""",
    unsafe_allow_html=True
)

# ======================
# Kiểm tra API Key
# ======================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("**Lỗi cấu hình**: Không tìm thấy `OPENAI_API_KEY` trong `.streamlit/secrets.toml`.")
    st.info("Hãy tạo file `.streamlit/secrets.toml` với nội dung:\n\n```toml\nOPENAI_API_KEY = \"sk-...\"\n```")
    st.stop()

openai_api_key = st.secrets["OPENAI_API_KEY"].strip()
if not openai_api_key:
    st.error("**API Key rỗng**: Vui lòng kiểm tra `OPENAI_API_KEY` trong `secrets.toml`.")
    st.stop()

# ======================
# Khởi tạo OpenAI Client
# ======================
try:
    client = OpenAI(api_key=openai_api_key)
except Exception as e:
    st.error(f"**Không thể kết nối OpenAI**: {str(e)}")
    st.stop()

# ======================
# Khởi tạo tin nhắn hệ thống
# ======================
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# ======================
# Hiển thị lịch sử trò chuyện
# ======================
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(message["content"])
    elif message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])

# ======================
# Ô nhập liệu người dùng
# ======================
if prompt := st.chat_input("Nhập câu hỏi của bạn..."):
    # Hiển thị tin nhắn người dùng
    with st.chat_message("user"):
        st.markdown(prompt)

    # Thêm vào lịch sử
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Tạo phản hồi từ OpenAI với streaming
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=rfile("module_chatgpt.txt").strip(),
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
                temperature=0.7,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = f"**Lỗi kết nối OpenAI**: {str(e)}"
            st.error(error_msg)
            full_response = "Xin lỗi, tôi không thể xử lý yêu cầu lúc này. Vui lòng thử lại sau."

    # Lưu phản hồi vào lịch sử
    st.session_state.messages.append({"role": "assistant", "content": full_response})