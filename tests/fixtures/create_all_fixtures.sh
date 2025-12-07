cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/

# Create the fixture file creation script
cat > create_all_fixtures.sh << 'SCRIPT'
#!/bin/bash

echo "🚀 Creating all fixture files..."

BASE="tests_new/fixtures"

# Ensure base directories exist
mkdir -p "$BASE"/{llm/{anthropic,google},ner/{sentences,entities},symbolic/{formulas,expressions},defi/{protocols,risk},data,models,common}

# LLM - Anthropic fixtures
cat > "$BASE/llm/anthropic/fixtures.py" << 'EOF'
"""Anthropic/Claude API fixtures"""
import pytest
from unittest.mock import Mock, MagicMock

@pytest.fixture
def anthropic_api_key():
    """Test Anthropic API key"""
    return "sk-ant-test-api-key-12345"

@pytest.fixture
def anthropic_mock_response():
    """Standard Anthropic API response"""
    return {
        "id": "msg_01XYZ123",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": "This is a test response from Claude"}],
        "model": "claude-sonnet-4-5-20250929",
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 25}
    }

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    client = Mock()
    mock_message = Mock()
    mock_message.content = [Mock(type="text", text="Mock response")]
    client.messages.create.return_value = mock_message
    return client
EOF

# LLM - Google fixtures
cat > "$BASE/llm/google/fixtures.py" << 'EOF'
"""Google/Gemini API fixtures"""
import pytest
from unittest.mock import Mock

@pytest.fixture
def google_api_key():
    """Test Google API key"""
    return "AIzaSy-test-api-key-67890"

@pytest.fixture
def gemini_mock_response():
    """Standard Gemini API response"""
    return {
        "candidates": [{
            "content": {"parts": [{"text": "Test response from Gemini"}], "role": "model"},
            "finish_reason": "STOP"
        }]
    }

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing"""
    client = Mock()
    mock_response = Mock()
    mock_response.text = "Mock Gemini response"
    client.generate_content.return_value = mock_response
    return client
EOF

# NER - Sentences fixtures
cat > "$BASE/ner/sentences/fixtures.py" << 'EOF'
"""NER sentence fixtures"""
import pytest

@pytest.fixture
def raw_sentences():
    """Plain text sentences for NER testing"""
    return [
        "Apple Inc. announced new products yesterday.",
        "John Smith works at Google in Mountain View, California.",
        "The S&P 500 rose 2.3% on Tuesday."
    ]

@pytest.fixture
def annotated_sentences():
    """Sentences with entity annotations"""
    return [
        {
            "text": "Apple Inc. announced new products yesterday.",
            "entities": [{"start": 0, "end": 10, "label": "ORG", "text": "Apple Inc."}]
        },
        {
            "text": "John Smith works at Google in Mountain View.",
            "entities": [
                {"start": 0, "end": 10, "label": "PERSON", "text": "John Smith"},
                {"start": 20, "end": 26, "label": "ORG", "text": "Google"},
                {"start": 30, "end": 43, "label": "GPE", "text": "Mountain View"}
            ]
        }
    ]
EOF

# NER - Entities fixtures
cat > "$BASE/ner/entities/fixtures.py" << 'EOF'
"""NER entity fixtures"""
import pytest

@pytest.fixture
def sample_organizations():
    """Sample organization names"""
    return ["Apple Inc.", "Google LLC", "Microsoft Corporation", "Tesla, Inc."]

@pytest.fixture
def sample_persons():
    """Sample person names"""
    return ["John Smith", "Dr. Jane Doe", "María García"]

@pytest.fixture
def sample_locations():
    """Sample location names"""
    return ["New York City", "San Francisco, California", "London, UK"]
EOF

# Symbolic - Formulas fixtures
cat > "$BASE/symbolic/formulas/fixtures.py" << 'EOF'
"""Symbolic formula fixtures"""
import pytest

@pytest.fixture
def basic_formulas():
    """Simple arithmetic formulas"""
    return ["a + b", "x * y", "(a + b) / c", "2 * pi * r"]

@pytest.fixture
def financial_formulas():
    """Financial calculation formulas"""
    return {
        "sharpe_ratio": "(return - risk_free_rate) / volatility",
        "compound_interest": "principal * (1 + rate)^time",
        "var_95": "portfolio_value * volatility * 1.645 * sqrt(time)"
    }

@pytest.fixture
def invalid_formulas():
    """Formulas that should fail parsing"""
    return ["a +", "/ b", "(a + b", "a ** ** b"]

@pytest.fixture
def formula_with_variables():
    """Formula paired with variable values"""
    return {
        "formula": "a * x^2 + b * x + c",
        "variables": {"a": 1, "b": -3, "c": 2, "x": 5},
        "expected_result": 12
    }
EOF

# Symbolic - Expressions fixtures
cat > "$BASE/symbolic/expressions/fixtures.py" << 'EOF'
"""Symbolic expression fixtures"""
import pytest

@pytest.fixture
def simple_expressions():
    """Simple mathematical expressions"""
    return ["2 + 2", "10 - 3", "5 * 4", "20 / 4"]
EOF

# DeFi - Protocols fixtures
cat > "$BASE/defi/protocols/fixtures.py" << 'EOF'
"""DeFi protocol fixtures"""
import pytest

@pytest.fixture
def defi_protocols():
    """Sample DeFi protocol data"""
    return {
        "uniswap_v3": {
            "name": "Uniswap V3",
            "tvl": 3_500_000_000,
            "volume_24h": 1_200_000_000,
            "apy": 0.15
        },
        "aave_v3": {
            "name": "Aave V3",
            "tvl": 5_800_000_000,
            "volume_24h": 450_000_000,
            "apy": 0.03
        }
    }
EOF

# DeFi - Risk fixtures
cat > "$BASE/defi/risk/fixtures.py" << 'EOF'
"""DeFi risk calculation fixtures"""
import pytest

@pytest.fixture
def risk_metrics():
    """Standard risk metrics"""
    return {
        "volatility": 0.15,
        "var_95": 0.025,
        "sharpe_ratio": 1.5,
        "max_drawdown": 0.20
    }

@pytest.fixture
def risk_free_rate():
    """Risk-free rate for calculations"""
    return 0.04  # 4%
EOF

# Data fixtures
cat > "$BASE/data/fixtures.py" << 'EOF'
"""Data fixtures"""
import pytest

@pytest.fixture
def sample_csv_data():
    """Sample CSV data"""
    return "name,value\nitem1,100\nitem2,200\nitem3,300"

@pytest.fixture
def sample_dataframe_data():
    """Sample data for DataFrame creation"""
    return {
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "score": [85.5, 92.0, 78.5]
    }
EOF

# Models fixtures
cat > "$BASE/models/fixtures.py" << 'EOF'
"""Model fixtures"""
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_ml_model():
    """Mock ML model for testing"""
    model = Mock()
    model.predict.return_value = [0.8, 0.2]
    model.score.return_value = 0.95
    return model

@pytest.fixture
def model_config():
    """Standard model configuration"""
    return {
        "batch_size": 32,
        "learning_rate": 0.001,
        "epochs": 10
    }
EOF

# Common fixtures
cat > "$BASE/common/fixtures.py" << 'EOF'
"""Common fixtures shared across all domains"""
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_file(tmp_path):
    """Temporary file for testing"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")
    return file_path

@pytest.fixture
def temp_json_file(tmp_path):
    """Temporary JSON file"""
    import json
    file_path = tmp_path / "test.json"
    data = {"key": "value", "number": 42}
    file_path.write_text(json.dumps(data))
    return file_path

@pytest.fixture
def mock_config():
    """Mock configuration object"""
    return {
        "api_timeout": 30,
        "max_retries": 3,
        "batch_size": 32
    }
EOF

# Create all __init__.py files
find "$BASE" -type d -exec touch {}/__init__.py \;

echo ""
echo "✅ All fixture files created!"
echo ""
echo "📊 Created files:"
find "$BASE" -name "fixtures.py" -type f | sort
echo ""
echo "📊 Created __init__.py files:"
find "$BASE" -name "__init__.py" | wc -l
echo " __init__.py files created"

SCRIPT

# Make script executable and run it
chmod +x create_all_fixtures.sh
./create_all_fixtures.sh
