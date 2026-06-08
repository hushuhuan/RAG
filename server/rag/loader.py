from PyPDF2 import PdfReader
from io import BytesIO

def load_pdf(content: bytes) -> str:
    """Load text from PDF content."""
    reader = PdfReader(BytesIO(content))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
    return text.strip()

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Split text into chunks."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        
        if end < len(text):
            last_period = chunk.rfind(".")
            last_newline = chunk.rfind("\n")
            split_point = max(last_period, last_newline)
            
            if split_point > start + chunk_size // 2:
                chunk = text[start:split_point + 1]
                start = split_point + 1
            else:
                start = end
        else:
            start = end
        
        chunk = chunk.strip()
        if len(chunk) > 20:
            chunks.append(chunk)
        start -= chunk_overlap
    
    return chunks
