# Module: `core/training/training_rag_.py`

## Description

RAG (Retrieval Augmented Generation) Training for Formula Mapping
Uses vector embeddings and similarity search

**Last Modified**: 2025-11-07T15:14:41.683925

## Dependencies

- `dataclasses`
- `faiss`
- `json`
- `numpy`
- `pandas`
- `pathlib`
- `pickle`
- `sentence_transformers`
- `typing`

## Constants

- `FAISS_AVAILABLE`
- `ST_AVAILABLE`
- `FAISS_AVAILABLE`
- `ST_AVAILABLE`

## Classes

### `RAGConfig`

Configuration for RAG system

**Decorators**: `dataclass`

### `VectorStore`

Vector database for similarity search

**Methods**:

- `__init__(self, embedding_dim: int)`
- `add_examples(self, embeddings: np.ndarray, examples: List[Dict])`
  - Add examples to vector store
- `search(self, query_embedding: np.ndarray, k: int) -> List[Tuple[<ast.Tuple object at 0x7fa6f8623a50>]]`
  - Search for similar examples
- `save(self, path: str)`
  - Save vector store
- `load(self, path: str)`
  - Load vector store

### `RAGTrainer`

Train RAG system for formula mapping

**Methods**:

- `__init__(self, config: RAGConfig)`
- `load_data(self, train_path: str) -> List[Dict]`
  - Load training data
- `build_index(self, examples: List[Dict])`
  - Build vector index from examples
- `retrieve(self, query: str, k: int) -> List[Dict]`
  - Retrieve similar examples
- `generate_formula(self, query: str, use_voting: bool) -> str`
  - Generate formula using retrieved examples
- `save_model(self, output_dir: str)`
  - Save RAG model
- `load_model(self, model_dir: str)`
  - Load RAG model
