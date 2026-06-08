from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import asyncio

class VectorRetriever:
    def __init__(self):
        self.vector_store = None
        self.embeddings = OpenAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        )
        self.persist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma")
    
    async def initialize(self):
        """Initialize the vector store."""
        try:
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings,
                collection_name="rag-documents"
            )
        except Exception:
            self.vector_store = Chroma.from_documents(
                [],
                self.embeddings,
                persist_directory=self.persist_dir,
                collection_name="rag-documents"
            )
    
    async def add_documents(self, texts: list[str], source: str):
        """Add documents to the vector store."""
        if not self.vector_store:
            await self.initialize()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        docs = []
        for text in texts:
            chunks = splitter.split_text(text)
            for i, chunk in enumerate(chunks):
                docs.append(Document(
                    page_content=chunk,
                    metadata={"source": source, "chunkIndex": i}
                ))
        
        await asyncio.to_thread(self.vector_store.add_documents, docs)
        self.vector_store.persist()
    
    async def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Search for similar documents."""
        if not self.vector_store:
            await self.initialize()
        
        return await asyncio.to_thread(
            self.vector_store.similarity_search,
            query,
            k
        )
    
    async def clear(self):
        """Clear all documents from the vector store."""
        if not self.vector_store:
            await self.initialize()
        
        await asyncio.to_thread(self.vector_store.delete, {})
        self.vector_store.persist()
    
    async def get_collection_stats(self) -> dict:
        """Get collection statistics."""
        if not self.vector_store:
            await self.initialize()
        
        count = await asyncio.to_thread(self.vector_store._collection.count)
        return {"count": count}

retriever = VectorRetriever()
