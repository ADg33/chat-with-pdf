import streamlit as st
import requests
import PyPDF2

# 🔑 API setup
OPENROUTER_API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# 🎨 Page config
st.set_page_config(page_title="📄 Chat with PDF", layout="centered")

# 🎨 Custom styling with left shaded sidebar
st.markdown("""
<style>
/* Global font */
html, body, [class*="css"] {
    font-family: 'Times New Roman', Times, serif;
}

/* Left colored sidebar */
.left-panel {
    position: fixed;
    top: 0;
    left: 0;
    width: 22%;
    height: 100%;
    background-color: #333333;  /* Change this to any color */
    padding: 2rem 1.5rem;
    color: #ffffff;
    font-weight: 900;
    box-shadow: 2px 0px 6px rgba(0, 0, 0, 0.1);
    z-index: 999;
}

/* Main content shifts right */
.main-panel {
    margin-left: 24%;
    padding: 2rem;
}

/* Chat box styling */
.chat-box {
    background-color: white;
    border-radius: 1rem;
    padding: 1rem;
    margin-top: 1rem;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}

/* TextArea */
.stTextArea textarea {
    font-family: 'Courier New', monospace;
}
</style>

<div class="left-panel">
    <h2>📘 Aritra Dasgupta</h2>
    <p>&nbsp;&nbsp;&nbsp;PhD, CEng(I).</p>
    <p>&nbsp;&nbsp;&nbspSenior Engineer (MEP)</p>
    <hr>
    <p style="font-size: 15px; color: white;">&nbsp;&nbsp;&nbsp<b>ZURU TECH<b></p>
    
</div>

<div class="main-panel">
""", unsafe_allow_html=True)

# 🧠 Get OpenRouter models
@st.cache_data(ttl=3600)
def get_available_models():
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    res = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
    if res.status_code == 200:
        data = res.json().get("data", [])
        return sorted([m["id"] for m in data])
    else:
        st.error("❌ Could not fetch model list.")
        return []

# 📄 PDF text extraction
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text.strip()

# 🤖 Generate a chat response using OpenRouter
def generate_response(model_id, context, user_input):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Answer based on the document provided."},
            {"role": "user", "content": f"The document content is:\n\n{context}"},
            {"role": "user", "content": f"Question: {user_input}"}
        ],
        "max_tokens": 5000
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return "⚠️ Unable to parse response from API."
    else:
        return f"❌ API error: {response.status_code}\n{response.text}"

# 🚀 Streamlit UI
def main():
    st.title("📄 Chat with Your PDF")

    uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_pdf:
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        st.markdown("✅ PDF uploaded and processed.")
        st.text_area("📄 Extracted Document Content", value=pdf_text[:2000], height=200)

        models = get_available_models()
        selected_model = st.selectbox("Choose a model", models)

        user_question = st.text_area("❓ Ask a question about the document:", height=100)

        if st.button("Ask"):
            if not user_question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Getting answer..."):
                    response = generate_response(selected_model, pdf_text[:4000], user_question)
                    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
                    st.markdown(f'**🤖 Response:**\n\n{response}')
                    st.markdown('</div>', unsafe_allow_html=True)

    # Close the main content div
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
