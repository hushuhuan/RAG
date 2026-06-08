from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
import os
import asyncio

# 支持的模型列表
AVAILABLE_MODELS = {
    # OpenAI 模型
    "gpt-4o-mini": "GPT-4o Mini (OpenAI - 快速、经济)",
    "gpt-4o": "GPT-4o (OpenAI - 最新、强大)",
    "gpt-4-turbo": "GPT-4 Turbo (OpenAI - 高性能)",
    "gpt-3.5-turbo": "GPT-3.5 Turbo (OpenAI - 经济)",
    "gpt-4": "GPT-4 (OpenAI - 经典)",
    # DeepSeek 模型
    "deepseek-chat": "DeepSeek Chat (DeepSeek - 通用对话)",
    "deepseek-reasoner": "DeepSeek Reasoner (DeepSeek - 推理模型)",
    # Minimax 模型
    "abab6.5s-chat": "MiniMax Chat (MiniMax - 对话模型)",
    "abab6.5-chat": "MiniMax Pro (MiniMax - 高级模型)",
    # Qwen 模型
    "qwen-turbo": "Qwen Turbo (通义千问 - 快速)",
    "qwen-plus": "Qwen Plus (通义千问 - 平衡)",
    "qwen-max": "Qwen Max (通义千问 - 强大)",
    # Claude 模型
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (Anthropic - 最新)",
    "claude-3-opus-20240229": "Claude 3 Opus (Anthropic - 最强)",
    "claude-3-sonnet-20240229": "Claude 3 Sonnet (Anthropic - 平衡)",
}

# 模型提供商配置
MODEL_PROVIDERS = {
    "openai": {
        "base_url": None,
        "env_key": "OPENAI_API_KEY"
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "env_key": "DEEPSEEK_API_KEY"
    },
    "minimax": {
        "base_url": "https://api.minimax.chat/v1",
        "env_key": "MINIMAX_API_KEY"
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "env_key": "QWEN_API_KEY"
    },
    "claude": {
        "base_url": None,
        "env_key": "ANTHROPIC_API_KEY",
        "use_anthropic": True
    }
}

# 模型到提供商的映射
MODEL_TO_PROVIDER = {
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

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

class RagState:
    question: str
    context: str
    answer: str
    documents: list[Document]
    needs_more_context: bool
    
    def __init__(self):
        self.question = ""
        self.context = ""
        self.answer = ""
        self.documents = []
        self.needs_more_context = False

def get_llm(model_name: str = None, api_key: str = None):
    """获取指定模型的 LLM 实例"""
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    provider = MODEL_TO_PROVIDER.get(model_name, "openai")
    provider_config = MODEL_PROVIDERS.get(provider, MODEL_PROVIDERS["openai"])
    
    # 获取 API Key（优先使用传入的，其次使用环境变量）
    if api_key:
        selected_api_key = api_key
    else:
        selected_api_key = os.getenv(provider_config["env_key"], os.getenv("OPENAI_API_KEY", ""))
    
    # Claude 使用 Anthropic
    if provider_config.get("use_anthropic"):
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=model_name,
                temperature=0,
                anthropic_api_key=selected_api_key
            )
        except ImportError:
            # 如果没有安装 langchain-anthropic，使用 OpenAI 兼容模式
            return ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=selected_api_key,
                base_url="https://api.anthropic.com/v1"
            )
    
    # 其他使用 OpenAI 兼容 API
    return ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=selected_api_key,
        base_url=provider_config.get("base_url")
    )

async def retrieve(state: RagState) -> RagState:
    """Retrieve relevant documents from vector store."""
    from .retriever import retriever
    
    documents = await retriever.similarity_search(state.question, k=4)
    
    context = "\n\n---\n\n".join([doc.page_content for doc in documents])
    
    state.documents = documents
    state.context = context
    
    return state

async def generate_answer(state: RagState, llm: ChatOpenAI = None) -> RagState:
    """Generate answer based on context."""
    if llm is None:
        llm = get_llm()
    
    prompt = f"""
基于以下提供的上下文信息，回答用户的问题。

上下文：
{state.context or '没有可用的上下文信息'}

问题：
{state.question}

请按照以下要求回答：
1. 仅使用提供的上下文信息
2. 如果上下文信息不足以回答问题，请明确说明
3. 回答要清晰、简洁
4. 如果有相关的来源信息，请在回答中提及
"""
    
    response = await asyncio.to_thread(llm.invoke, prompt)
    state.answer = response.content
    
    state.needs_more_context = (
        "不足以回答" in state.answer or
        "没有足够的信息" in state.answer or
        "无法回答" in state.answer
    )
    
    return state

def decide_next_step(state: RagState) -> str:
    """Decide whether to retrieve more context or finish."""
    if state.needs_more_context and len(state.documents) > 0:
        return "retrieve"
    return END

def build_graph(llm: ChatOpenAI = None):
    """Build the LangGraph workflow."""
    if llm is None:
        llm = get_llm()
    
    workflow = StateGraph(RagState)
    
    # 异步节点需要正确注册
    workflow.add_node("retrieve", retrieve)
    
    # 创建一个包装函数来处理异步的 generate_answer
    async def generate_wrapper(state: RagState) -> RagState:
        return await generate_answer(state, llm)
    
    workflow.add_node("generate", generate_wrapper)
    
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_conditional_edges(
        "generate",
        decide_next_step,
        {
            "retrieve": "retrieve",
            END: END
        }
    )
    
    return workflow.compile()

async def run_rag(question: str, model_name: str = None, api_key: str = None) -> dict:
    """Run the RAG workflow with specified model."""
    llm = get_llm(model_name, api_key)
    
    # 直接执行检索和生成，绕过 LangGraph 的异步问题
    from .retriever import retriever
    
    # 检索相关文档
    documents = await retriever.similarity_search(question, k=4)
    context = "\n\n---\n\n".join([doc.page_content for doc in documents])
    
    # 生成回答
    prompt = f"""
基于以下提供的上下文信息，回答用户的问题。

上下文：
{context or '没有可用的上下文信息'}

问题：
{question}

请按照以下要求回答：
1. 仅使用提供的上下文信息
2. 如果上下文信息不足以回答问题，请明确说明
3. 回答要清晰、简洁
4. 如果有相关的来源信息，请在回答中提及
"""
    
    response = await asyncio.to_thread(llm.invoke, prompt)
    answer = response.content
    
    sources = list(set([doc.metadata.get("source", "") for doc in documents]))
    
    return {
        "answer": answer,
        "sources": sources
    }

def get_available_models():
    """获取可用模型列表"""
    return AVAILABLE_MODELS
