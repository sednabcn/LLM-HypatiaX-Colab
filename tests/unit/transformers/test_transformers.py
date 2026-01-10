"""
Unit tests for transformer models and operations.
Path: tests/unit/transformers/test_transformers.py
"""

from unittest.mock import Mock

import numpy as np
import pytest
import torch


class TestTransformerTokenization:
    """Test tokenization for transformer models."""

    def test_basic_tokenization(self):
        """Test basic text tokenization."""
        text = "Hello world"
        mock_tokenizer = Mock()
        mock_tokenizer.encode = Mock(return_value=[101, 7592, 2088, 102])

        tokens = mock_tokenizer.encode(text)

        assert len(tokens) == 4
        assert tokens[0] == 101
        assert tokens[-1] == 102

    def test_tokenization_with_padding(self):
        """Test tokenization with padding."""
        texts = ["Short", "This is a longer sentence"]
        max_length = 10

        mock_tokenizer = Mock()
        mock_tokenizer.encode = Mock(
            side_effect=[
                [101, 2159, 102, 0, 0, 0, 0, 0, 0, 0],
                [101, 2023, 2003, 1037, 2936, 6251, 102, 0, 0, 0],
            ]
        )

        tokenized = [mock_tokenizer.encode(text) for text in texts]

        assert all(len(t) == max_length for t in tokenized)


class TestTransformerEmbeddings:
    """Test transformer embedding layers."""

    def test_token_embeddings(self):
        """Test token embedding creation."""
        vocab_size = 1000
        embedding_dim = 768

        embeddings = torch.nn.Embedding(vocab_size, embedding_dim)

        input_ids = torch.tensor([[1, 2, 3, 4]])
        embedded = embeddings(input_ids)

        assert embedded.shape == (1, 4, embedding_dim)

    def test_positional_embeddings(self):
        """Test positional encoding."""
        seq_length = 10
        d_model = 512

        position = torch.arange(seq_length).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * -(np.log(10000.0) / d_model))

        pos_encoding = torch.zeros(seq_length, d_model)
        pos_encoding[:, 0::2] = torch.sin(position * div_term)
        pos_encoding[:, 1::2] = torch.cos(position * div_term)

        assert pos_encoding.shape == (seq_length, d_model)


class TestAttentionMechanism:
    """Test attention mechanisms."""

    def test_scaled_dot_product_attention(self):
        """Test scaled dot-product attention."""
        batch_size = 2
        seq_len = 4
        d_k = 64

        Q = torch.randn(batch_size, seq_len, d_k)
        K = torch.randn(batch_size, seq_len, d_k)
        V = torch.randn(batch_size, seq_len, d_k)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(d_k)
        attention_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)

        assert output.shape == (batch_size, seq_len, d_k)

    def test_attention_mask(self):
        """Test attention masking."""
        seq_len = 4

        mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()

        scores = torch.randn(1, seq_len, seq_len)
        scores = scores.masked_fill(mask, float("-inf"))

        attention_weights = torch.softmax(scores, dim=-1)

        assert attention_weights[0, 0, 1:].sum() < 0.01


class TestTransformerLayers:
    """Test transformer layer components."""

    def test_feed_forward_network(self):
        """Test feed-forward network."""
        d_model = 512
        d_ff = 2048
        batch_size = 2
        seq_len = 10

        ffn = torch.nn.Sequential(
            torch.nn.Linear(d_model, d_ff),
            torch.nn.ReLU(),
            torch.nn.Linear(d_ff, d_model),
        )

        x = torch.randn(batch_size, seq_len, d_model)
        output = ffn(x)

        assert output.shape == (batch_size, seq_len, d_model)

    def test_layer_normalization(self):
        """Test layer normalization."""
        x = torch.randn(2, 10, 512)

        layer_norm = torch.nn.LayerNorm(512)
        normalized = layer_norm(x)

        assert torch.allclose(normalized.mean(dim=-1), torch.zeros(2, 10), atol=1e-5)


class TestModelInference:
    """Test transformer model inference."""

    def test_forward_pass(self):
        """Test forward pass through model."""
        batch_size = 2
        seq_len = 10
        vocab_size = 1000

        mock_model = Mock()
        mock_model.forward = Mock(
            return_value=torch.randn(batch_size, seq_len, vocab_size)
        )

        input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
        output = mock_model.forward(input_ids)

        assert output.shape == (batch_size, seq_len, vocab_size)

    def test_generate_predictions(self):
        """Test prediction generation."""
        logits = torch.randn(1, 5, 1000)

        predictions = torch.argmax(logits, dim=-1)

        assert predictions.shape == (1, 5)
        assert predictions.max() < 1000


class TestModelTraining:
    """Test transformer training components."""

    def test_loss_calculation(self):
        """Test loss calculation."""
        batch_size = 2
        seq_len = 10
        vocab_size = 1000

        predictions = torch.randn(batch_size, seq_len, vocab_size)
        targets = torch.randint(0, vocab_size, (batch_size, seq_len))

        criterion = torch.nn.CrossEntropyLoss()

        loss = criterion(predictions.view(-1, vocab_size), targets.view(-1))

        assert loss.item() > 0

    def test_gradient_clipping(self):
        """Test gradient clipping."""
        model = torch.nn.Linear(10, 10)

        for param in model.parameters():
            param.grad = torch.randn_like(param) * 10

        max_norm = 1.0
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)

        total_norm = 0
        for param in model.parameters():
            if param.grad is not None:
                total_norm += param.grad.data.norm(2).item() ** 2
        total_norm = total_norm**0.5

        assert total_norm <= max_norm + 0.01


@pytest.fixture
def sample_batch():
    """Fixture providing sample batch."""
    return {
        "input_ids": torch.randint(0, 1000, (4, 20)),
        "attention_mask": torch.ones(4, 20),
        "labels": torch.randint(0, 1000, (4, 20)),
    }


def test_batch_processing(sample_batch):
    """Test batch processing."""
    assert sample_batch["input_ids"].shape[0] == 4
    assert sample_batch["attention_mask"].shape == sample_batch["input_ids"].shape
