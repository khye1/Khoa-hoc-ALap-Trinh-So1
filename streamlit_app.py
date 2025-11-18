import streamlit as st
from openai import OpenAI
import os


# ====================== UTILITIES ======================
def read_file(filename: str) -> str:
    """Đọc nội dung file text (utf-8) một cách an toàn."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        st.error(f"Không tìm thấy file: {filename}")
        st.stop()


def get_openai_client() -> OpenAI:
    """Lấy API key và khởi tạo OpenAI client."""
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "🔑 Không tìm thấy OPENAI_API_KEY.\n\n"
            "Vui lòng thêm vào **Secrets** của Streamlit Community Cloud "
            "hoặc đặt biến môi trường `OPENAI_API_KEY`."
        )
        st.stop()
    return OpenAI(api_key=api_key)


# ====================== CONFIG ======================
# Đọc các file cấu hình một lần duy nhất
TITLE           = read_file("00.xinchao.txt")
SYSTEM_PROMPT   = read_file("01.system_trainning.txt")
ASSISTANT_GREET = read_file("02.assistant.txt")
MODEL_NAME      = read_file("gpt-4o-mini").strip()  # hoặc bạn có thể hard-code nếu muốn

# Khởi tạo client
client = get_openai_client()

# Sidebar info
st.sidebar.write("🔐 Đã có API key:", "✅" if client.api_key else "❌")
st.sidebar.caption(f"Model: `{MODEL_NAME}`")


# ====================== LAYOUT ======================
# Logo + Tiêu đề
col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    try:
        st.image("israel-flag.png", use_container_width=True)
    except:
        pass

st.markdown(
    f'<h1 style="text-align: center; font-size: 28px; margin-bottom: 30px;">{TITLE}</h1>',
    unsafe_allow_html=True,
)

# CSS đẹp hơn, hỗ trợ dark mode nhẹ và avatar
st.markdown("""
<style>
    .chat-message {
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        max-width: 80%;
        line-height: 1.5;
    }
    .assistant {
        background-color: #f1f3f5;
        border-left: 4px solid #0a7cff;
    }
    .user {
        background-color: #e3f2fd;
        margin-left: auto;
        border-right: 4px solid #0a7cff;
    }
    .assistant::before { content: "🤖 "; font-size: 1.3em; }
    .user::after     { content: "👤 "; font-size: 1.3em; }
    @media (prefers-color-scheme: dark) {
        .assistant { background-color: #2d3748; }
        .user     { background-color: #1e3a8a; }
    }
</style>
""", unsafe_allow_html=True)


# ====================== SESSION STATE ======================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system",    "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": ASSISTANT_GREET},
    ]


# ====================== HIỂN THỊ LỊCH SỬ CHAT ======================
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        st.markdown(
            f'<div class="chat-message assistant">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    elif msg["role"] == "user":
        st.markdown(
            f'<div class="chat-message user">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )


# ====================== INPUT & STREAMING ======================
if prompt := st.chat_input("Nhập câu hỏi của bạn tại đây..."):
    # Thêm tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(
        f'<div class="chat-message user">{prompt}</div>',
        unsafe_allow_html=True,
    )

    # Placeholder để stream phản hồi
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Gọi API với stream=True
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
            temperature=0.7,
        )

        # Hiển thị từng chunk ngay lập tức
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(
                    f'<div class="chat-message assistant">{full_response}▌</div>',
                    unsafe_allow_html=True,
                )

        # Xóa con trỏ nhấp nháy khi hoàn thành
        message_placeholder.markdown(
            f'<div class="chat-message assistant">{full_response}</div>',
            unsafe_allow_html=True,
        )

    # Lưu phản hồi vào lịch sử
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Tự động reruns để cập nhật giao diện
    st.rerun()