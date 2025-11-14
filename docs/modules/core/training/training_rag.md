# Module: `core/training/training_rag.py`

## Description

Modern RAG System (2025 Best Practices)
Uses: Vector DB + Reranking + LLM Generation (not just retrieval)
Replaces: Simple vector search with voting

**Last Modified**: 2025-11-11T12:06:13.110320

## Dependencies

- `anthropic`
- `chromadb`
- `chromadb.config`
- `dataclasses`
- `hashlib`
- `json`
- `numpy`
- `openai`
- `os`
- `rank_bm25`
- `sentence_transformers`
- `typing`

## Classes

### `RAGConfig`

Modern RAG configuration for 2025

**Decorators**: `dataclass`

### `ModernRAGSystem`

2025 RAG Architecture:
1. Query Expansion/HyDE (optional)
2. Hybrid Retrieval (Dense + Sparse)
3. Reranking with Cross-Encoder
4. LLM Generation with retrieved context

**Methods**:

- `__init__(self, config: RAGConfig)`
- `index_documents(self, documents: List[Dict[<ast.Tuple object at 0x7fa6f85c0090>]])`
  - Index documents with modern techniques
- `expand_query(self, query: str) -> List[str]`
  - Query expansion using LLM (2025 technique)
- `generate_hypothetical_document(self, query: str) -> str`
  - HyDE (Hypothetical Document Embeddings) - 2025 technique
- `hybrid_search(self, query: str, top_k: int) -> List[Tuple[<ast.Tuple object at 0x7fa6f8623b50>]]`
  - Hybrid search: Combine dense (vector) + sparse (BM25) retrieval
- `rerank(self, query: str, results: List[Tuple[<ast.Tuple object at 0x7fa6f86226d0>]]) -> List[Tuple[<ast.Tuple object at 0x7fa6f8578a50>]]`
  - Rerank results using cross-encoder (2025 standard)
- `generate_answer(self, query: str, retrieved_docs: List[Tuple[<ast.Tuple object at 0x7fa6f8579210>]]) -> str`
  - Generate answer using LLM with retrieved context (2025 RAG)
- `query(self, query: str, return_sources: bool) -> Dict`
  - Complete modern RAG pipeline
