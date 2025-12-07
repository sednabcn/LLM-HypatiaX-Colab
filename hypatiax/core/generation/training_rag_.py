#!/usr/bin/python3
"""
RAG (Retrieval Augmented Generation) Training for Formula Mapping
Uses vector embeddings and similarity search
"""

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Vector database
try:
    import faiss

    FAISS_AVAILABLE = True
except:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available. Install with: pip install faiss-cpu")

# Embeddings
try:
    from sentence_transformers import SentenceTransformer

    ST_AVAILABLE = True
except:
    ST_AVAILABLE = False
    print("Warning: sentence-transformers not available")


@dataclass
class RAGConfig:
    """Configuration for RAG system"""

    embedding_model: str = "all-MiniLM-L6-v2"
    index_type: str = "flat"  # or "ivf"
    top_k: int = 5
    similarity_threshold: float = 0.7
    output_dir: str = "./models/rag"


class VectorStore:
    """Vector database for similarity search"""

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.index = None
        self.examples = []

        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatL2(embedding_dim)

    def add_examples(self, embeddings: np.ndarray, examples: List[Dict]):
        """Add examples to vector store"""
        if FAISS_AVAILABLE and self.index is not None:
            self.index.add(embeddings.astype("float32"))
            self.examples.extend(examples)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[float, Dict]]:
        """Search for similar examples"""
        if not FAISS_AVAILABLE or self.index is None:
            return []

        distances, indices = self.index.search(query_embedding.astype("float32").reshape(1, -1), k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.examples):
                results.append((float(dist), self.examples[idx]))

        return results

    def save(self, path: str):
        """Save vector store"""
        if FAISS_AVAILABLE and self.index is not None:
            faiss.write_index(self.index, f"{path}/index.faiss")

        with open(f"{path}/examples.pkl", "wb") as f:
            pickle.dump(self.examples, f)

    def load(self, path: str):
        """Load vector store"""
        if FAISS_AVAILABLE:
            self.index = faiss.read_index(f"{path}/index.faiss")

        with open(f"{path}/examples.pkl", "rb") as f:
            self.examples = pickle.load(f)


class RAGTrainer:
    """Train RAG system for formula mapping"""

    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        self.encoder = None
        self.vector_store = None

        if ST_AVAILABLE:
            self.encoder = SentenceTransformer(self.config.embedding_model)
            embedding_dim = self.encoder.get_sentence_embedding_dimension()
            self.vector_store = VectorStore(embedding_dim)

    def load_data(self, train_path: str) -> List[Dict]:
        """Load training data"""
        with open(train_path, "r") as f:
            data = json.load(f)

        # Convert to dict format
        examples = []
        for item in data:
            if isinstance(item, list) and len(item) == 2:
                examples.append({"description": item[0], "formula": item[1]})
            elif isinstance(item, dict):
                examples.append(item)

        return examples

    def build_index(self, examples: List[Dict]):
        """Build vector index from examples"""
        if not ST_AVAILABLE:
            print("sentence-transformers not available. Cannot build index.")
            return

        print(f"Building vector index from {len(examples)} examples...")

        # Extract descriptions
        descriptions = [ex["description"] for ex in examples]

        # Generate embeddings
        embeddings = self.encoder.encode(descriptions, show_progress_bar=True, convert_to_numpy=True)

        # Add to vector store
        self.vector_store.add_examples(embeddings, examples)

        print(f"✅ Index built with {len(examples)} examples")

    def retrieve(self, query: str, k: int = None) -> List[Dict]:
        """Retrieve similar examples"""
        if not ST_AVAILABLE:
            return []

        k = k or self.config.top_k

        # Encode query
        query_embedding = self.encoder.encode(query, convert_to_numpy=True)

        # Search
        results = self.vector_store.search(query_embedding, k)

        # Filter by threshold
        filtered_results = [example for dist, example in results if dist < (1 - self.config.similarity_threshold)]

        return filtered_results

    def generate_formula(self, query: str, use_voting: bool = True) -> str:
        """Generate formula using retrieved examples"""
        similar_examples = self.retrieve(query)

        if not similar_examples:
            return "Error: No similar examples found"

        if use_voting:
            # Vote among similar formulas
            formula_votes = {}
            for ex in similar_examples:
                formula = ex["formula"]
                formula_votes[formula] = formula_votes.get(formula, 0) + 1

            # Return most common formula
            best_formula = max(formula_votes.items(), key=lambda x: x[1])[0]
            return best_formula
        else:
            # Return closest match
            return similar_examples[0]["formula"]

    def save_model(self, output_dir: str = None):
        """Save RAG model"""
        output_dir = output_dir or self.config.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Save vector store
        self.vector_store.save(output_dir)

        # Save config
        with open(f"{output_dir}/config.json", "w") as f:
            json.dump(self.config.__dict__, f, indent=2)

        print(f"✅ Model saved to {output_dir}")

    def load_model(self, model_dir: str):
        """Load RAG model"""
        # Load vector store
        self.vector_store.load(model_dir)

        # Load config
        with open(f"{model_dir}/config.json", "r") as f:
            config_dict = json.load(f)
            self.config = RAGConfig(**config_dict)

        print(f"✅ Model loaded from {model_dir}")


def evaluate_rag(trainer: RAGTrainer, test_data: List[Dict]) -> Dict:
    """Evaluate RAG system"""
    correct = 0
    total = len(test_data)

    predictions = []

    for example in test_data:
        query = example["description"]
        true_formula = example["formula"]

        predicted_formula = trainer.generate_formula(query)

        predictions.append(
            {
                "query": query,
                "true": true_formula,
                "predicted": predicted_formula,
                "correct": predicted_formula == true_formula,
            }
        )

        if predicted_formula == true_formula:
            correct += 1

    accuracy = correct / total if total > 0 else 0

    return {"accuracy": accuracy, "correct": correct, "total": total, "predictions": predictions}


def main():
    """Example usage"""
    print("=" * 70)
    print("RAG TRAINING FOR FORMULA MAPPING")
    print("=" * 70)

    if not ST_AVAILABLE:
        print("\n⚠️  sentence-transformers not installed.")
        print("Install with: pip install sentence-transformers")
        return

    # Configuration
    config = RAGConfig(
        embedding_model="all-MiniLM-L6-v2", top_k=5, similarity_threshold=0.7, output_dir="./models/rag_formula_mapper"
    )

    # Initialize trainer
    trainer = RAGTrainer(config)

    # Load data
    print("\nLoading training data...")
    examples = trainer.load_data("./preprocessed_data/mapping/train_mapping.json")
    print(f"Loaded {len(examples)} training examples")

    # Build index
    trainer.build_index(examples)

    # Save model
    trainer.save_model()

    # Test retrieval
    print("\n" + "=" * 70)
    print("TEST RETRIEVAL")
    print("=" * 70)

    test_queries = ["average of Sales", "sum of Revenue by Region", "count unique customers"]

    for query in test_queries:
        print(f"\nQuery: {query}")
        similar = trainer.retrieve(query, k=3)
        print("Similar examples:")
        for i, ex in enumerate(similar, 1):
            print(f"  {i}. {ex['description']} → {ex['formula']}")

        predicted = trainer.generate_formula(query)
        print(f"Predicted: {predicted}")


if __name__ == "__main__":
    main()
