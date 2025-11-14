from dataclasses import dataclass

@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k: int = 5
    similarity_threshold: float = 0.7
    output_dir: str = "./models/queries/tableau/rag"
