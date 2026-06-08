from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
import os
import asyncio

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

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    temperature=0
)

async def retrieve(state: RagState) -> RagState:
    """Retrieve relevant documents from vector store."""
    from .retriever import retriever
    
    documents = await retriever.similarity_search(state.question, k=4)
    
    context = "\n\n---\n\n".join([doc.page_content for doc in documents])
    
    state.documents = documents
    state.context = context
    
    return state

async def generate_answer(state: RagState) -> RagState:
    """Generate answer based on context."""
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

def build_graph():
    """Build the LangGraph workflow."""
    workflow = StateGraph(RagState)
    
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate_answer)
    
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

rag_graph = build_graph()

async def run_rag(question: str) -> dict:
    """Run the RAG workflow."""
    result = await rag_graph.invoke({
        "question": question,
        "context": "",
        "answer": "",
        "documents": [],
        "needs_more_context": False
    })
    
    sources = list(set([doc.metadata.get("source", "") for doc in result.documents]))
    
    return {
        "answer": result.answer,
        "sources": sources
    }
