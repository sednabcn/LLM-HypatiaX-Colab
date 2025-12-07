Complete Test Directory Rebuild Plan
Overview
This plan reorganizes your test structure from the current mixed state into a clean, domain-organized structure with proper fixture management.

Phase 1: Preparation & Backup (30 minutes)
Step 1.1: Backup Current Tests

# Create backup of current test directories

cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/
cp -r tests/ tests_backup_$(date +%Y%m%d)/
cp -r hypatiax/tests/ hypatiax/tests_backup_$(date +%Y%m%d)/

# Verify backup

ls -la tests_backup_*/
ls -la hypatiax/tests_backup_*/
Step 1.2: Analyze Current Test Files

# Create inventory of all test files

cd tests/
find . -name "test_*.py" > ../test_inventory.txt

cd ../hypatiax/tests/
find . -name "test_*.py" >> ../test_inventory.txt

# Review inventory

cat ../test_inventory.txt | sort | uniq
Step 1.3: Identify Test Types
Create a mapping file: test_mapping.txt

# Categorize each test file by domain and type

# Format: current_path -> domain -> test_type

# Example entries

tests/test_desc_formulas.py -> symbolic -> unit
tests/integration/test_ner_desc.py -> ner -> integration
hypatiax/tests/unit/test_tools/test_symbolic_engine.py -> symbolic -> unit
Action: Manually review each test file and categorize it.
Step 1.4: Document Dependencies

# Find all imports in test files to understand dependencies

grep -r "^import\|^from" tests/ > test_dependencies.txt
grep -r "^import\|^from" hypatiax/tests/ >> test_dependencies.txt

# Identify fixture usage

grep -r "@pytest.fixture" tests/ > fixtures_used.txt
grep -r "@pytest.fixture" hypatiax/tests/ >> fixtures_used.txt

Phase 2: Create New Structure (1 hour)
Step 2.1: Create Base Directory Structure
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/

# Create new test structure

mkdir -p tests_new/{benchmark,unit,integration,e2e,fixtures,docs}

# Create domain subdirectories under unit/

mkdir -p tests_new/unit/{llm,ner,symbolic,validators,models,defi,data,transformers,agents,tableau}

# Create domain subdirectories under integration/

mkdir -p tests_new/integration/{llm,ner,symbolic,validators,models,defi,data,transformers,agents,tableau,extrapolation,performance}

# Create fixture domain directories

mkdir -p tests_new/fixtures/{llm,ner,symbolic,defi,data,models,common}

# Create subdirectories in fixture domains

mkdir -p tests_new/fixtures/llm/{anthropic,google}
mkdir -p tests_new/fixtures/ner/{entities,sentences}
mkdir -p tests_new/fixtures/symbolic/{formulas,expressions}
mkdir -p tests_new/fixtures/defi/{protocols,risk}
Step 2.2: Create init.py Files

# Create all __init__.py files

find tests_new -type d -exec touch {}/__init__.py \;

# Verify creation

find tests_new -name "__init__.py" | wc -l
Step 2.3: Create Root Configuration Files
Create tests_new/pytest.ini
[pytest]
testpaths = tests_new
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers for test organization

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (with dependencies)
    e2e: End-to-end tests (full system)
    benchmark: Performance and benchmark tests
    llm: LLM provider tests
    ner: Named entity recognition tests
    symbolic: Symbolic reasoning tests
    defi: DeFi domain tests
    slow: Slow running tests

# Test output

addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings

# Coverage settings (optional)

# --cov=hypatiax

# --cov-report=html

# --cov-report=term-missing

# Ignore patterns

norecursedirs = .git .tox dist build *.egg __pycache__ tests_backup_*
Create tests_new/conftest.py
"""
Root conftest.py - shared fixtures and configuration for all tests
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import all fixtures from fixture modules

pytest_plugins = [
    "tests_new.fixtures.conftest",
]

@pytest.fixture(scope="session")
def project_root_dir():
    """Project root directory"""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory"""
    return Path(__file__).parent / "fixtures" / "data"

@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for test files"""
    return tmp_path

# Configure test environment

def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
Step 2.4: Create Fixture Registry
Create tests_new/fixtures/conftest.py
"""
Central fixture registry - imports all domain fixtures
This makes all fixtures available to all tests automatically
"""

# LLM fixtures

from tests_new.fixtures.llm.anthropic.fixtures import *
from tests_new.fixtures.llm.google.fixtures import*

# NER fixtures

from tests_new.fixtures.ner.sentences.fixtures import *
from tests_new.fixtures.ner.entities.fixtures import*

# Symbolic fixtures

from tests_new.fixtures.symbolic.formulas.fixtures import *

# DeFi fixtures

from tests_new.fixtures.defi.protocols.fixtures import *
from tests_new.fixtures.defi.risk.fixtures import*

# Data fixtures

from tests_new.fixtures.data.fixtures import *

# Model fixtures

from tests_new.fixtures.models.fixtures import *

# Common fixtures

from tests_new.fixtures.common.fixtures import *

Phase 3: Extract and Organize Fixtures (2-3 hours)
Step 3.1: Create LLM Fixtures
Create tests_new/fixtures/llm/anthropic/fixtures.py
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
        "content": [
            {
                "type": "text",
                "text": "This is a test response from Claude"
            }
        ],
        "model": "claude-sonnet-4-5-20250929",
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 25
        }
    }

@pytest.fixture
def anthropic_error_response():
    """Anthropic API error response"""
    return {
        "type": "error",
        "error": {
            "type": "rate_limit_error",
            "message": "Rate limit exceeded"
        }
    }

@pytest.fixture
def anthropic_streaming_response():
    """Anthropic streaming response chunks"""
    return [
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""}
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "Hello "}
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "world"}
        },
        {
            "type": "content_block_stop",
            "index": 0
        }
    ]

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    client = Mock()

    # Configure mock response
    mock_message = Mock()
    mock_message.content = [Mock(type="text", text="Mock response")]
    mock_message.model = "claude-sonnet-4-5-20250929"
    mock_message.stop_reason = "end_turn"

    client.messages.create.return_value = mock_message

    return client

@pytest.fixture
def anthropic_test_prompts():
    """Common test prompts for Anthropic"""
    return {
        "simple": "What is 2+2?",
        "complex": "Explain quantum computing in simple terms",
        "creative": "Write a haiku about testing",
        "long": "Summarize the history of computer science in detail" * 10
    }
Create tests_new/fixtures/llm/google/fixtures.py
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
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "This is a test response from Gemini"}
                    ],
                    "role": "model"
                },
                "finish_reason": "STOP",
                "safety_ratings": []
            }
        ],
        "usage_metadata": {
            "prompt_token_count": 8,
            "candidates_token_count": 15,
            "total_token_count": 23
        }
    }

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing"""
    client = Mock()

    mock_response = Mock()
    mock_response.text = "Mock Gemini response"
    mock_response.candidates = [Mock(content=Mock(parts=[Mock(text="Mock response")]))]

    client.generate_content.return_value = mock_response

    return client
Step 3.2: Create NER Fixtures
Create tests_new/fixtures/ner/sentences/fixtures.py
"""NER sentence fixtures"""
import pytest

@pytest.fixture
def raw_sentences():
    """Plain text sentences for NER testing"""
    return [
        "Apple Inc. announced new products yesterday.",
        "John Smith works at Google in Mountain View, California.",
        "The S&P 500 rose 2.3% on Tuesday.",
        "Dr. Jane Doe published a paper on quantum computing.",
        "Tesla, Inc. opened a new factory in Austin, Texas."
    ]

@pytest.fixture
def annotated_sentences():
    """Sentences with entity annotations"""
    return [
        {
            "text": "Apple Inc. announced new products yesterday.",
            "entities": [
                {"start": 0, "end": 10, "label": "ORG", "text": "Apple Inc."}
            ]
        },
        {
            "text": "John Smith works at Google in Mountain View, California.",
            "entities": [
                {"start": 0, "end": 10, "label": "PERSON", "text": "John Smith"},
                {"start": 20, "end": 26, "label": "ORG", "text": "Google"},
                {"start": 30, "end": 43, "label": "GPE", "text": "Mountain View"},
                {"start": 45, "end": 55, "label": "GPE", "text": "California"}
            ]
        },
        {
            "text": "The S&P 500 rose 2.3% on Tuesday.",
            "entities": [
                {"start": 4, "end": 11, "label": "PRODUCT", "text": "S&P 500"},
                {"start": 25, "end": 32, "label": "DATE", "text": "Tuesday"}
            ]
        }
    ]

@pytest.fixture
def difficult_sentences():
    """Edge cases for NER testing"""
    return [
        "Dr. J.R.R. Tolkien wrote The Lord of the Rings.",  # Multiple periods
        "New York-based startup raised $10M.",  # Hyphenated, currency
        "Mr. O'Brien from McDonald's visited the U.S.",  # Apostrophes, abbreviations
        "€100,000 investment in AI/ML research.",  # Special chars, slash
        "Email support@company.com for info.",  # Email address
        "Visit https://example.com/path?query=value",  # URL
    ]

@pytest.fixture
def multilingual_sentences():
    """Sentences in different languages"""
    return {
        "spanish": "María García trabaja en Barcelona, España.",
        "chinese": "李明在北京工作。",
        "arabic": "محمد يعمل في دبي.",
        "mixed": "John works at 索尼 (Sony) in Tokyo."
    }

@pytest.fixture
def sentence_test_cases():
    """Comprehensive test cases with expected results"""
    return {
        "simple_org": {
            "text": "Google is in California",
            "expected": [
                {"text": "Google", "label": "ORG"},
                {"text": "California", "label": "GPE"}
            ]
        },
        "ambiguous": {
            "text": "Apple released new products",  # Apple = company or fruit?
            "expected": [
                {"text": "Apple", "label": "ORG"}
            ]
        },
        "nested": {
            "text": "Bank of America announced quarterly results",
            "expected": [
                {"text": "Bank of America", "label": "ORG"}
            ]
        }
    }
Create tests_new/fixtures/ner/entities/fixtures.py
"""NER entity fixtures"""
import pytest

@pytest.fixture
def sample_organizations():
    """Sample organization names"""
    return [
        "Apple Inc.",
        "Google LLC",
        "Microsoft Corporation",
        "Tesla, Inc.",
        "Amazon.com",
        "JPMorgan Chase & Co.",
        "Goldman Sachs",
        "Y Combinator"
    ]

@pytest.fixture
def sample_persons():
    """Sample person names"""
    return [
        "John Smith",
        "Dr. Jane Doe",
        "Mr. Robert Johnson Jr.",
        "María García",
        "李明",  # Chinese
        "Mohammed Al-Rashid",
        "Prof. Elizabeth Warren"
    ]

@pytest.fixture
def sample_locations():
    """Sample location names"""
    return [
        "New York City",
        "San Francisco, California",
        "London, UK",
        "Mount Everest",
        "Pacific Ocean",
        "Silicon Valley",
        "Wall Street"
    ]

@pytest.fixture
def entity_types():
    """Standard NER entity types"""
    return {
        "PERSON": "People, including fictional",
        "ORG": "Companies, agencies, institutions",
        "GPE": "Countries, cities, states",
        "LOC": "Non-GPE locations, mountain ranges, bodies of water",
        "PRODUCT": "Objects, vehicles, foods, etc.",
        "DATE": "Absolute or relative dates or periods",
        "TIME": "Times smaller than a day",
        "MONEY": "Monetary values",
        "PERCENT": "Percentage values"
    }
Step 3.3: Create Symbolic Fixtures
Create tests_new/fixtures/symbolic/formulas/fixtures.py
"""Symbolic formula fixtures"""
import pytest

@pytest.fixture
def basic_formulas():
    """Simple arithmetic formulas"""
    return [
        "a + b",
        "x * y",
        "(a + b) / c",
        "2 * pi * r",
        "x^2 + 2*x + 1"
    ]

@pytest.fixture
def financial_formulas():
    """Financial calculation formulas"""
    return {
        "sharpe_ratio": "(return - risk_free_rate) / volatility",
        "compound_interest": "principal *(1 + rate)^time",
        "present_value": "future_value / (1 + rate)^periods",
        "var_95": "portfolio_value* volatility *1.645* sqrt(time)",
        "black_scholes": "S *N(d1) - K* exp(-r*T)* N(d2)",
        "capm": "risk_free + beta * (market_return - risk_free)"
    }

@pytest.fixture
def defi_formulas():
    """DeFi-specific formulas"""
    return {
        "impermanent_loss": "2*sqrt(price_ratio)/(1+price_ratio) - 1",
        "liquidity_ratio": "total_liquidity / total_volume",
        "apy": "(1 + apr/n)^n - 1",
        "tvl_ratio": "protocol_tvl / market_tvl",
        "utilization_rate": "borrowed / supplied"
    }

@pytest.fixture
def statistical_formulas():
    """Statistical formulas"""
    return {
        "mean": "sum(values) / count(values)",
        "variance": "sum((x - mean)^2) / n",
        "std_dev": "sqrt(variance)",
        "correlation": "covariance(x, y) / (std(x) * std(y))",
        "z_score": "(x - mean) / std_dev"
    }

@pytest.fixture
def invalid_formulas():
    """Formulas that should fail parsing"""
    return [
        "a +",              # Incomplete expression
        "/ b",              # Missing left operand
        "(a + b",           # Unmatched parenthesis
        "a ** ** b",        # Invalid operator sequence
        "sin(",             # Incomplete function call
        "a b",              # Missing operator
        "1 2 3",            # Multiple values without operators
    ]

@pytest.fixture
def formula_with_variables():
    """Formula paired with variable values"""
    return {
        "formula": "a *x^2 + b* x + c",
        "variables": {
            "a": 1,
            "b": -3,
            "c": 2,
            "x": 5
        },
        "expected_result": 12  # 1*25 + (-3)*5 + 2 = 12
    }

@pytest.fixture
def formula_evaluation_cases():
    """Multiple formula evaluation test cases"""
    return [
        {
            "formula": "2 * x + 5",
            "variables": {"x": 3},
            "expected": 11
        },
        {
            "formula": "(a + b) * c",
            "variables": {"a": 2, "b": 3, "c": 4},
            "expected": 20
        },
        {
            "formula": "sqrt(x^2 + y^2)",
            "variables": {"x": 3, "y": 4},
            "expected": 5.0
        }
    ]
Step 3.4: Create DeFi Fixtures
Create tests_new/fixtures/defi/protocols/fixtures.py
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
            "apy": 0.15,
            "type": "dex"
        },
        "aave_v3": {
            "name": "Aave V3",
            "tvl": 5_800_000_000,
            "volume_24h": 450_000_000,
            "apy": 0.03,
            "type": "lending"
        },
        "curve": {
            "name": "Curve Finance",
            "tvl": 4_200_000_000,
            "volume_24h": 800_000_000,
            "apy": 0.08,
            "type": "dex"
        }
    }

@pytest.fixture
def liquidity_pool_data():
    """Sample liquidity pool data"""
    return {
        "pool_id": "ETH-USDC-0.3",
        "token0": {"symbol": "ETH", "amount": 1000, "price": 2500},
        "token1": {"symbol": "USDC", "amount": 2_500_000, "price": 1},
        "fee_tier": 0.003,
        "tvl": 5_000_000,
        "volume_24h": 10_000_000
    }
Create tests_new/fixtures/defi/risk/fixtures.py
"""DeFi risk calculation fixtures"""
import pytest

@pytest.fixture
def risk_metrics():
    """Standard risk metrics"""
    return {
        "volatility": 0.15,
        "var_95": 0.025,
        "var_99": 0.05,
        "sharpe_ratio": 1.5,
        "sortino_ratio": 2.0,
        "max_drawdown": 0.20,
        "beta": 1.2,
        "alpha": 0.03
    }

@pytest.fixture
def risk_free_rate():
    """Risk-free rate for calculations"""
    return 0.04  # 4%

@pytest.fixture
def market_conditions():
    """Market condition scenarios"""
    return {
        "bull_market": {
            "trend": "up",
            "volatility": 0.10,
            "sentiment": 0.8
        },
        "bear_market": {
            "trend": "down",
            "volatility": 0.25,
            "sentiment": 0.2
        },
        "sideways": {
            "trend": "neutral",
            "volatility": 0.12,
            "sentiment": 0.5
        }
    }
Step 3.5: Create Common Fixtures
Create tests_new/fixtures/common/fixtures.py
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
def temp_csv_file(tmp_path):
    """Temporary CSV file"""
    file_path = tmp_path / "test.csv"
    content = "name,value\nitem1,100\nitem2,200\n"
    file_path.write_text(content)
    return file_path

@pytest.fixture
def mock_config():
    """Mock configuration object"""
    return {
        "api_timeout": 30,
        "max_retries": 3,
        "batch_size": 32,
        "enable_caching": True
    }

Phase 4: Migrate Test Files (3-4 hours)
Step 4.1: Create Migration Script
Create migrate_tests.py:
"""
Script to migrate tests from old structure to new structure
"""
import shutil
from pathlib import Path
import re

# Mapping of old test files to new locations

TEST_MIGRATIONS = {
    # Format: "old_path": ("new_path", "test_type", "domain")

    # LLM tests
    "hypatiax/tests/unit/test_tools/test_anthropic_provider.py":
        ("tests_new/unit/llm/test_anthropic_provider.py", "unit", "llm"),
    "hypatiax/tests/unit/test_tools/test_anthropic_provider_mock.py":
        ("tests_new/unit/llm/test_anthropic_provider_mock.py", "unit", "llm"),
    "hypatiax/tests/unit/test_tools/test_google_provider.py":
        ("tests_new/unit/llm/test_google_provider.py", "unit", "llm"),
    "hypatiax/tests/integration/test_real_llm_integration.py":
        ("tests_new/integration/llm/test_real_llm_integration.py", "integration", "llm"),

    # NER tests
    "tests/integration/test_ner_desc.py":
        ("tests_new/integration/ner/test_ner_desc.py", "integration", "ner"),
    "tests/integration/test_ner_formulas.py":
        ("tests_new/integration/ner/test_ner_formulas.py", "integration", "ner"),
    "tests/unit/test_entity_desc.py":
        ("tests_new/unit/ner/test_entity_desc.py", "unit", "ner"),
    "tests/unit/test_entity_formulas.py":
        ("tests_new/unit/ner/test_entity_formulas.py", "unit", "ner"),

    # Symbolic tests
    "hypatiax/tests/unit/test_tools/test_symbolic_engine.py":
        ("tests_new/unit/symbolic/test_symbolic_engine.py", "unit", "symbolic"),
    "hypatiax/tests/unit/test_tools/test_symbolic_validator.py":
        ("tests_new/unit/symbolic/test_symbolic_validator.py", "unit", "symbolic"),
    "tests/test_formulas.py":
        ("tests_new/unit/symbolic/test_formulas.py", "unit", "symbolic"),

    # Validator tests
    "hypatiax/tests/unit/test_tools/test_ensemble_validator.py":
        ("tests_new/unit/validators/test_ensemble_validator.py", "unit", "validators"),
    "hypatiax/tests/unit/test_tools/test_suite_validators.py":
        ("tests_new/unit/validators/test_suite_validators.py", "unit", "validators"),

    # Model tests
    "tests/unit/test_description_model.py":
        ("tests_new/unit/models/test_description_model.py", "unit", "models"),
    "tests/unit/test_formulas_model.py":
        ("tests_new/unit/models/test_formulas_model.py", "unit", "models"),
    "tests/integration/test_training_spacy.py":
        ("tests_new/integration/models/test_training_spacy.py", "integration", "models"),

    # DeFi tests
    "hypatiax/tests/unit/test_tools/test_risk_formulas_30.py":
        ("tests_new/unit/defi/test_risk_formulas_30.py", "unit", "defi"),
    "hypatiax/tests/unit/test_tools/test_suite_defi_formulas.py":
        ("tests_new/unit/defi/test_suite_defi_formulas.py", "unit", "defi"),

    # Data tests
    "tests/integration/test_normalize.py":
        ("tests_new/integration/data/test_normalize.py", "integration", "data"),
    "tests/integration/test_tableau_data_csv.py":
        ("tests_new/integration/data/test_tableau_data_csv.py", "integration", "data"),

    # E2E tests
    "hypatiax/tests/e2e/test_hybrid_system_e2e.py":
        ("tests_new/e2e/test_hybrid_system_e2e.py", "e2e", "system"),

    # Benchmark tests
    # Add your benchmark tests here when identified
}

def migrate_test_file(old_path: str, new_path: str):
    """Copy test file to new location"""
    old_file = Path(old_path)
    new_file = Path(new_path)

    if not old_file.exists():
        print(f"⚠️  Source not found: {old_path}")
        return False

    # Create parent directory
    new_file.parent.mkdir(parents=True, exist_ok=True)

    # Copy file
    shutil.copy2(old_file, new_file)
    print(f"✅ Migrated: {old_path} -> {new_path}")
    return True

def update_imports_in_file(file_path: Path):
    """Update import statements in migrated test file"""
    if not file_path.exists():
        return

    content = file_path.read_text()

    # Update common import patterns
    updates = {
        r'from tests\.fixtures\.': 'from tests_new.fixtures.',
        r'from tests\.': 'from tests_new.',
        r'from hypatiax\.tests\.': 'from tests_new.',
    }

    for pattern, replacement in updates.items():
        content = re.sub(pattern, replacement, content)

    file_path.write_text(content)
    print(f"  📝 Updated imports in: {file_path}")

def main():
    """Run migration"""
    print("🚀 Starting test migration...\n")

    migrated = 0
    failed = 0

    for old_path, (new_path, test_type, domain) in TEST_MIGRATIONS.items():
        if migrate_test_file(old_path, new_path):
            update_imports_in_file(Path(new_path))
            migrated += 1
        else:
            failed += 1

    print(f"\n📊 Migration Summary:")
    print(f"  ✅ Migrated: {migrated}")
    print(f"  ❌ Failed: {failed}")
    print(f"\n✨ Migration complete!")

if __name__ == "__main__":
    main()
Step 4.2: Run Migration
cd ~/Downloads/GITHUB/LLM-HypatiaX-Colab/

# Review the migration mapping first

python migrate_tests.py --dry-run  # If you add this option

# Execute migration

python migrate_tests.py
Step 4.3: Manual Migration for Unmapped Tests

# List tests not in migration script

find tests/ -name "test_*.py" > all_old_tests.txt
find hypatiax/tests/ -name "test_*.py" >> all_old_tests.txt

# Compare with migrated tests

# Manually categorize and move remaining tests

Phase 5: Create Domain-Specific conftest.py (1 hour)
Step 5.1: Unit Test Conftest Files
Create tests_new/unit/conftest.py
"""Unit test level fixtures"""
import pytest

@pytest.fixture
def mock_logger():
    """Mock logger for unit tests"""
    from unittest.mock import Mock
    return Mock()

@pytest.fixture
def unit_test_config():
    """Standard config for unit tests"""
    return {
        "timeout": 5,
        "strict_mode": True,
        "verbose": False
    }
Create tests_new/unit/llm/conftest.py
"""LLM unit test fixtures"""
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_llm_client():
    """Generic mock LLM client"""
    client = Mock()
    client.generate.return_value = "Mock response"
    return client

@pytest.fixture
def llm_test_config():
    """LLM test configuration"""
    return {
        "model": "test-model",
        "temperature": 0.7,
        "max_tokens": 1000
    }

@pytest.fixture
def mock_api_call():
    """Mock external API calls"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"result": "success"}
        yield mock_post
Create tests_new/unit/symbolic/conftest.py
"""Symbolic unit test fixtures"""
import pytest

@pytest.fixture
def symbolic_engine():
    """Symbolic engine instance for unit tests"""
    from hypatiax.symbolic import SymbolicEngine
    return SymbolicEngine()

@pytest.fixture
def formula_parser():
    """Formula parser instance"""
    from hypatiax.symbolic import FormulaParser
    return FormulaParser()

@pytest.fixture
def validator():
    """Formula validator instance"""
    from hypatiax.symbolic import FormulaValidator
    return FormulaValidator()
Create tests_new/unit/ner/conftest.py
"""NER unit test fixtures"""
import pytest

@pytest.fixture
def ner_model():
    """Mock NER model for unit tests"""
    from unittest.mock import Mock
    model = Mock()
    model.extract.return_value = [
        {"text": "Apple Inc.", "label": "ORG", "start": 0, "end": 10}
    ]
    return model

@pytest.fixture
def tokenizer():
    """Mock tokenizer"""
    from unittest.mock import Mock
    tokenizer = Mock()
    tokenizer.tokenize.return_value = ["token1", "token2", "token3"]
    return tokenizer
Step 5.2: Integration Test Conftest Files
Create tests_new/integration/conftest.py
"""Integration test level fixtures"""
import pytest
import os

@pytest.fixture(scope="module")
def integration_test_db():
    """Test database for integration tests"""
    # Setup
    db = create_test_database()
    yield db
    # Teardown
    db.cleanup()

@pytest.fixture
def skip_if_no_api_key():
    """Skip test if API keys not configured"""
    def _skip(key_name):
        if not os.getenv(key_name):
            pytest.skip(f"{key_name} not set")
    return _skip
Create tests_new/integration/llm/conftest.py
"""LLM integration test fixtures"""
import pytest
import os

@pytest.fixture
def real_anthropic_client():
    """Real Anthropic client for integration tests"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")

    from anthropic import Anthropic
    return Anthropic(api_key=api_key)

@pytest.fixture
def real_google_client():
    """Real Google client for integration tests"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        pytest.skip("GOOGLE_API_KEY not set")

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    return genai

@pytest.fixture
def llm_integration_config():
    """Configuration for LLM integration tests"""
    return {
        "timeout": 30,
        "max_retries": 3,
        "backoff_factor": 2
    }
Step 5.3: E2E Test Conftest
Create tests_new/e2e/conftest.py
"""E2E test fixtures"""
import pytest

@pytest.fixture(scope="session")
def e2e_test_environment():
    """Setup complete test environment for E2E tests"""
    # Setup: database, models, API clients, etc.
    env = {
        "db": setup_test_db(),
        "models": load_test_models(),
        "config": load_test_config()
    }

    yield env

    # Teardown
    cleanup_test_environment(env)

@pytest.fixture
def full_pipeline():
    """Complete processing pipeline for E2E tests"""
    from hypatiax.pipeline import Pipeline
    return Pipeline(
        ner_enabled=True,
        symbolic_enabled=True,
        llm_enabled=True
    )

Phase 6: Update Import Statements (1-2 hours)
Step 6.1: Create Import Update Script
Create update_imports.py:
"""
Update import statements in migrated test files
"""
import re
from pathlib import Path
from typing import Dict, List

IMPORT_MAPPINGS = {
    # Old fixture imports -> New fixture imports
    r'from tests\.fixtures\.raw_sentences import':
        'from tests_new.fixtures.ner.sentences.fixtures import',
    r'from tests\.fixtures\.sample_sentences import':
        'from tests_new.fixtures.ner.sentences.fixtures import',

    # Old test imports -> New test imports
    r'from tests\.unit\.': 'from tests_new.unit.',
    r'from tests\.integration\.': 'from tests_new.integration.',
    r'from hypatiax\.tests\.': 'from tests_new.',

    # Fixture usage (just parameter names - auto-discovered by pytest)
    # No changes needed for fixture parameters
}

def update_file_imports(file_path: Path) -> bool:
    """Update imports in a single file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Apply all import mappings
        for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
            content = re.sub(old_pattern, new_pattern, content)

        # Write back if changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all test file imports"""
    tests_dir = Path("tests_new")

    # Find all Python test files
    test_files = list(tests_dir.rglob("test_*.py"))
    conftest_files = list(tests_dir.rglob("conftest.py"))
    all_files = test_files + conftest_files

    print(f"Found {len(all_files)} files to update")

    updated = 0
    for file_path in all_files:
        if update_file_imports(file_path):
            print(f"✅ Updated: {file_path}")
            updated += 1
        else:
            print(f"⏭️  No changes: {file_path}")

    print(f"\n📊 Updated {updated}/{len(all_files)} files")

if __name__ == "__main__":
    main()
Step 6.2: Run Import Updates
python update_imports.py
Step 6.3: Manual Import Verification

# Check for any remaining old import patterns

grep -r "from tests\." tests_new/
grep -r "from hypatiax\.tests\." tests_new/

# Fix any remaining issues manually

Phase 7: Verification & Testing (1-2 hours)
Step 7.1: Verify Structure

# Check directory structure

tree tests_new -L 3

# Verify all __init__.py files exist

find tests_new -type d ! -path "*/__pycache__*" -exec test -f {}/__init__.py \; -print

# Count test files by domain

echo "Unit tests:"
find tests_new/unit -name "test_*.py" | wc -l

echo "Integration tests:"
find tests_new/integration -name "test_*.py" | wc -l

echo "E2E tests:"
find tests_new/e2e -name "test_*.py" | wc -l
Step 7.2: Run Test Discovery
cd tests_new/

# Discover all tests (don't run yet)

pytest --collect-only

# Check for any collection errors

pytest --collect-only -v 2>&1 | grep "ERROR"
Step 7.3: Fix Collection Errors

# If there are import errors, fix them

# Common issues

# 1. Missing dependencies

# 2. Incorrect import paths

# 3. Missing fixture files

# Example fix for missing fixture

# Create the fixture file or update the import

Step 7.4: Run Smoke Tests

# Run a few simple tests to verify setup

pytest tests_new/unit/symbolic/test_formulas.py -v

# Run tests by marker

pytest tests_new -m "unit" --collect-only

# Run specific domain

pytest tests_new/unit/llm/ -v
Step 7.5: Run Full Test Suite

# Run all unit tests (should be fast)

pytest tests_new/unit/ -v

# Run integration tests (may be slow)

pytest tests_new/integration/ -v --tb=short

# Run specific test with verbose output

pytest tests_new/unit/symbolic/test_symbolic_engine.py::test_parse_basic_formula -vv

Phase 8: Create Documentation (1 hour)
Step 8.1: Create Testing Guide
Create tests_new/docs/testing_guide.md:

# HypatiaX Testing Guide

## Test Structure

tests_new/ ├── unit/ # Fast, isolated tests ├── integration/ # Tests with dependencies ├── e2e/ # Full system tests ├── benchmark/ # Performance tests └── fixtures/ # Reusable test data

## Running Tests

### Run All Tests

```bash
pytest tests_new/
Run by Test Level
# Unit tests only (fast)
pytest tests_new/unit/

# Integration tests (slower)
pytest tests_new/integration/

# E2E tests (slowest)
pytest tests_new/e2e/
Run by Domain
# LLM tests
pytest tests_new/unit/llm/ tests_new/integration/llm/

# NER tests
pytest tests_new/unit/ner/ tests_new/integration/ner/

# Symbolic tests
pytest tests_new/unit/symbolic/ tests_new/integration/symbolic/
Run by Marker
# Fast tests only
pytest tests_new/ -m "not slow"

# Specific domain
pytest tests_new/ -m "llm"

# Multiple markers
pytest tests_new/ -m "unit and symbolic"
Writing Tests
Unit Test Example
# tests_new/unit/symbolic/test_new_feature.py
def test_formula_parsing(basic_formulas, formula_parser):
    \"\"\"Test formula parsing with basic formulas\"\"\"
    for formula in basic_formulas:
        result = formula_parser.parse(formula)
        assert result is not None
Using Fixtures
Fixtures are auto-discovered from:
    • tests_new/fixtures/domain/
    • tests_new/unit/domain/conftest.py
    • tests_new/integration/domain/conftest.py
def test_with_fixtures(anthropic_response, symbolic_engine):
    # Fixtures automatically injected by pytest
    result = symbolic_engine.evaluate(anthropic_response)
    assert result
Creating New Fixtures
Add fixtures to appropriate domain:
# tests_new/fixtures/symbolic/formulas/fixtures.py
@pytest.fixture
def my_new_formula_fixture():
    return "x^2 + 2*x + 1"
Fixture is now available in all tests automatically!

### Step 8.2: Create Fixture Guide

Create `tests_new/docs/fixture_guide.md`:
```markdown
# Fixture Organization Guide

## Fixture Locations

### Domain Fixtures
Located in `tests_new/fixtures/domain/`:
- `llm/` - LLM provider fixtures
- `ner/` - NER entity and sentence fixtures
- `symbolic/` - Formula and expression fixtures
- `defi/` - DeFi protocol and risk fixtures
- `data/` - Dataset fixtures
- `models/` - ML model fixtures
- `common/` - Shared utilities

### Test-Level Fixtures
Located in `conftest.py` at each level:
- `tests_new/unit/domain/conftest.py` - Unit test fixtures
- `tests_new/integration/domain/conftest.py` - Integration fixtures
- `tests_new/e2e/conftest.py` - E2E fixtures

## Adding New Fixtures

### Step 1: Choose Location
- Reused across many tests? → `tests_new/fixtures/domain/`
- Specific to test level? → `tests_new/unit|integration/domain/conftest.py`

### Step 2: Create Fixture
```python
@pytest.fixture
def my_fixture():
    return "test data"
Step 3: Import in Registry (if in fixtures/)
# tests_new/fixtures/conftest.py
from tests_new.fixtures.domain.module import *
Step 4: Use in Tests
def test_something(my_fixture):
    assert my_fixture == "test data"
Fixture Scopes
    • function (default) - New instance per test
    • class - Shared within test class
    • module - Shared within test file
    • session - Shared across entire test run
Example:
@pytest.fixture(scope="session")
def expensive_setup():
    # Runs once for entire test session
    return setup_database()

### Step 8.3: Create Domain Test Documentation

Create `tests_new/docs/domain_testing.md`:
```markdown
# Domain-Specific Testing

## LLM Domain

### Unit Tests
Location: `tests_new/unit/llm/`
- Provider-specific logic
- Response parsing
- Error handling
- Mock client behavior

### Integration Tests
Location: `tests_new/integration/llm/`
- Real API calls (requires API keys)
- End-to-end provider integration
- Rate limiting behavior

### Fixtures
- `anthropic_mock_response` - Mock API response
- `mock_anthropic_client` - Mock client object
- `anthropic_test_prompts` - Standard test prompts

## NER Domain

### Unit Tests
Location: `tests_new/unit/ner/`
- Entity extraction logic
- Label mapping
- Edge case handling

### Integration Tests
Location: `tests_new/integration/ner/`
- Pipeline integration
- Model loading
- Training workflows

### Fixtures
- `raw_sentences` - Plain text samples
- `annotated_sentences` - Pre-labeled data
- `sample_organizations` - Entity examples

## Symbolic Domain

### Unit Tests
Location: `tests_new/unit/symbolic/`
- Formula parsing
- Expression evaluation
- Validation logic

### Integration Tests
Location: `tests_new/integration/symbolic/`
- Formula execution pipeline
- Complex calculations
- Error propagation

### Fixtures
- `basic_formulas` - Simple arithmetic
- `financial_formulas` - Finance calculations
- `invalid_formulas` - Error test cases

Phase 9: Cleanup & Finalization (30 minutes)
Step 9.1: Remove Old Test Directories
# Verify new tests work first!
pytest tests_new/unit/ -v

# If all tests pass, remove old directories
rm -rf tests/
rm -rf hypatiax/tests/

# Keep backups just in case
# Don't delete tests_backup_* directories yet
Step 9.2: Rename tests_new to tests
mv tests_new/ tests/

# Update pytest.ini
sed -i 's/tests_new/tests/g' tests/pytest.ini

# Update all import statements
find tests/ -name "*.py" -exec sed -i 's/tests_new/tests/g' {} \;
Step 9.3: Update CI/CD Configuration
Update .github/workflows/tests.yml (if exists):
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
Step 9.4: Update Project Documentation
Update README.md:
## Testing

### Running Tests

```bash
# All tests
pytest tests/

# By level
pytest tests/unit/          # Fast unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests

# By domain
pytest tests/unit/llm/     # LLM tests
pytest tests/unit/ner/     # NER tests
pytest tests/unit/symbolic/ # Symbolic tests

# With coverage
pytest tests/ --cov=hypatiax --cov-report=html
Test Structure
tests/
├── unit/           # Isolated component tests
├── integration/    # Tests with dependencies
├── e2e/           # Full system tests
├── benchmark/     # Performance tests
└── fixtures/      # Reusable test data by domain
See Testing Guide for details.

### Step 9.5: Create Quick Reference

Create `tests/QUICK_REFERENCE.md`:
```markdown
# Test Quick Reference

## Common Commands

```bash
# Run all tests
pytest

# Run fast tests only
pytest -m "not slow"

# Run specific domain
pytest tests/unit/symbolic/

# Run with coverage
pytest --cov=hypatiax

# Run and stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Show print statements
pytest -s

# Very verbose
pytest -vv
Finding Fixtures
All fixtures in tests/fixtures/domain/:
    • LLM: tests/fixtures/llm/
    • NER: tests/fixtures/ner/
    • Symbolic: tests/fixtures/symbolic/
    • DeFi: tests/fixtures/defi/
Writing New Tests
    1. Choose location: tests/{unit|integration|e2e}/domain/
    2. Create test file: test_feature_name.py
    3. Use fixtures: def test_something(fixture_name):
    4. Run: pytest tests/unit/domain/test_feature_name.py
Adding Fixtures
    1. Choose domain: tests/fixtures/domain/
    2. Add to appropriate file: fixtures.py
    3. Import in registry: tests/fixtures/conftest.py
    4. Use in tests: Automatic discovery!

---


## Phase 10: Validation & Final Checks (30 minutes)

### Step 10.1: Run Complete Test Suite
```bash
# Run everything
pytest tests/ -v --tb=short

# Generate coverage report
pytest tests/ --cov=hypatiax --cov-report=html --cov-report=term

# Check coverage
open htmlcov/index.html  # or xdg-open on Linux
Step 10.2: Verify Test Organization
# Check test count by level
echo "Unit: $(find tests/unit -name 'test_*.py' | wc -l)"
echo "Integration: $(find tests/integration -name 'test_*.py' | wc -l)"
echo "E2E: $(find tests/e2e -name 'test_*.py' | wc -l)"
echo "Benchmark: $(find tests/benchmark -name 'test_*.py' | wc -l)"

# Check fixture organization
echo "Fixture domains:"
ls tests/fixtures/

# Verify no duplicates
find tests/ -name "test_*.py" | sort | uniq -d
Step 10.3: Create Validation Checklist
Create tests/VALIDATION_CHECKLIST.md:
# Test Structure Validation Checklist

## Structure
- [ ] All __init__.py files present
- [ ] No duplicate test files
- [ ] All tests categorized (unit/integration/e2e)
- [ ] Fixtures organized by domain
- [ ] Documentation complete

## Functionality
- [ ] All tests discoverable: `pytest --collect-only`
- [ ] Unit tests pass: `pytest tests/unit/`
- [ ] Integration tests pass: `pytest tests/integration/`
- [ ] No import errors
- [ ] Fixtures load correctly

## Documentation
- [ ] README updated
- [ ] Testing guide created
- [ ] Fixture guide created
- [ ] Quick reference created
- [ ] Domain docs created

## Cleanup
- [ ] Old test directories removed
- [ ] Backup created
- [ ] CI/CD updated
- [ ] Import statements updated
Step 10.4: Final Test Run
# Clean pytest cache
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null

# Fresh test run
pytest tests/ -v --cache-clear

# If all pass:
echo "✅ Test structure rebuild complete!"

Timeline Summary
Phase Duration Description
Phase 1 30 min Preparation & Backup
Phase 2 1 hour Create Structure
Phase 3 2-3 hours Extract Fixtures
Phase 4 3-4 hours Migrate Tests
Phase 5 1 hour Domain Conftest Files
Phase 6 1-2 hours Update Imports
Phase 7 1-2 hours Verification
Phase 8 1 hour Documentation
Phase 9 30 min Cleanup
Phase 10 30 min Validation
Total 12-16 hours Complete Rebuild
Next Steps After Completion
    1. Monitor CI/CD: Ensure all tests pass in CI
    2. Update Team: Share new structure with team
    3. Delete Backups: After 1-2 weeks of stable tests
    4. Continuous Improvement: Add tests using new structure
    5. Review Coverage: Identify gaps and add tests
Getting Help
If stuck during migration:
    1. Check tests/docs/ documentation
    2. Review fixture examples
    3. Run pytest --fixtures to see available fixtures
    4. Check test collection: pytest --collect-only -v
