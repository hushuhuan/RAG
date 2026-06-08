import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = f"http://localhost:{os.getenv('PORT', 5174)}"

st.set_page_config(
    page_title="RAG LangGraph",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG LangGraph App")
st.subheader("Upload documents and ask questions")

with st.sidebar:
    st.header("Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            with st.spinner(f"Uploading {file.name}..."):
                files = {"file": (file.name, file, file.type)}
                try:
                    response = requests.post(f"{API_URL}/api/rag/upload", files=files)
                    if response.ok:
                        st.success(f"✅ {file.name} uploaded successfully")
                    else:
                        st.error(f"❌ Failed to upload {file.name}: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Failed to upload {file.name}: {str(e)}")
    
    st.divider()
    
    if st.button("Clear All Documents"):
        try:
            response = requests.delete(f"{API_URL}/api/rag/clear")
            if response.ok:
                st.success("✅ All documents cleared")
            else:
                st.error("❌ Failed to clear documents")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    try:
        response = requests.get(f"{API_URL}/api/rag/stats")
        if response.ok:
            stats = response.json()
            st.info(f"📊 Documents in database: {stats.get('count', 0)}")
    except Exception as e:
        st.info("📊 Documents in database: Connecting...")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption(f"Sources: {', '.join(message['sources'])}")

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/rag/query",
                    json={"question": prompt}
                )
                
                if response.ok:
                    result = response.json()
                    st.markdown(result["answer"])
                    if result.get("sources"):
                        st.caption(f"Sources: {', '.join(result['sources'])}")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result.get("sources", [])
                    })
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Failed to connect to API: {str(e)}")
