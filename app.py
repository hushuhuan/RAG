import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = f"http://localhost:{os.getenv('PORT', 5174)}"

# API Key 提供商配置
API_KEY_PROVIDERS = {
    "openai": {"name": "OpenAI", "key": "OPENAI_API_KEY"},
    "deepseek": {"name": "DeepSeek", "key": "DEEPSEEK_API_KEY"},
    "minimax": {"name": "Minimax", "key": "MINIMAX_API_KEY"},
    "qwen": {"name": "Qwen (通义千问)", "key": "QWEN_API_KEY"},
    "claude": {"name": "Claude (Anthropic)", "key": "ANTHROPIC_API_KEY"},
}

# 获取可用模型列表
def get_available_models():
    try:
        response = requests.get(f"{API_URL}/api/rag/models")
        if response.ok:
            return response.json()["models"]
    except Exception as e:
        st.warning(f"获取模型列表失败: {str(e)}")
    return {"gpt-4o-mini": "GPT-4o Mini (快速、经济)"}

st.set_page_config(
    page_title="RAG LangGraph",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG LangGraph App")
st.subheader("Upload documents and ask questions")

# 初始化 session state
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gpt-4o-mini"

# 初始化 API Keys
for provider_key, config in API_KEY_PROVIDERS.items():
    if config["key"] not in st.session_state:
        st.session_state[config["key"]] = ""

with st.sidebar:
    st.header("⚙️ 模型设置")
    
    # 模型选择下拉框
    models = get_available_models()
    model_options = list(models.keys())
    model_labels = [f"{k} - {v}" for k, v in models.items()]
    
    selected_index = model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
    
    selected_label = st.selectbox(
        "选择大模型",
        options=model_labels,
        index=selected_index,
        help="选择用于回答问题的 AI 模型"
    )
    
    # 更新选中的模型
    st.session_state.selected_model = model_options[model_labels.index(selected_label)]
    
    st.divider()
    
    st.header("🔑 API Key 配置")
    
    # 获取当前选中模型对应的提供商
    model_to_provider = {
        # OpenAI
        "gpt-4o-mini": "openai",
        "gpt-4o": "openai",
        "gpt-4-turbo": "openai",
        "gpt-3.5-turbo": "openai",
        "gpt-4": "openai",
        # DeepSeek
        "deepseek-chat": "deepseek",
        "deepseek-reasoner": "deepseek",
        # Minimax
        "abab6.5s-chat": "minimax",
        "abab6.5-chat": "minimax",
        # Qwen
        "qwen-turbo": "qwen",
        "qwen-plus": "qwen",
        "qwen-max": "qwen",
        # Claude
        "claude-3-5-sonnet-20241022": "claude",
        "claude-3-opus-20240229": "claude",
        "claude-3-sonnet-20240229": "claude",
    }
    
    current_provider = model_to_provider.get(st.session_state.selected_model, "openai")
    current_provider_name = API_KEY_PROVIDERS[current_provider]["name"]
    current_api_key_env = API_KEY_PROVIDERS[current_provider]["key"]
    
    # 提示当前选中模型需要的 API Key
    st.info(f"当前模型需要 **{current_provider_name} API Key**")
    
    # API Key 输入区域 - 高亮显示当前模型需要的 API Key
    for provider_key, config in API_KEY_PROVIDERS.items():
        is_current_provider = (provider_key == current_provider)
        
        # 如果是当前模型需要的 API Key，添加提示
        if is_current_provider:
            with st.container(border=True):
                st.text_input(
                    f"🔴 {config['name']} API Key (当前模型需要)",
                    value=st.session_state.get(config["key"], ""),
                    type="password",
                    key=config["key"],
                    help=f"当前选中的模型需要此 API Key"
                )
        else:
            st.text_input(
                f"{config['name']} API Key",
                value=st.session_state.get(config["key"], ""),
                type="password",
                key=config["key"],
                help=f"输入您的 {config['name']} API Key"
            )
    
    st.divider()
    
    st.header("📤 上传文档")
    
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
                # 获取当前选中模型对应的 API Key
                api_key_env = API_KEY_PROVIDERS[current_provider]["key"]
                api_key = st.session_state[api_key_env]
                
                response = requests.post(
                    f"{API_URL}/api/rag/query",
                    json={
                        "question": prompt,
                        "model": st.session_state.selected_model,
                        "api_key": api_key
                    }
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
