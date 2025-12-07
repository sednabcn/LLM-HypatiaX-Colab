"""
Central fixture registry - imports all domain fixtures
This makes all fixtures available to all tests automatically
"""

# Common fixtures
from tests.fixtures.common.fixtures import *

# Data fixtures
from tests.fixtures.data.fixtures import *

# DeFi fixtures
from tests.fixtures.defi.protocols.fixtures import *
from tests.fixtures.defi.risk.fixtures import *

# LLM fixtures
from tests.fixtures.llm.anthropic.fixtures import *
from tests.fixtures.llm.google.fixtures import *

# Model fixtures
from tests.fixtures.models.fixtures import *
from tests.fixtures.ner.entities.fixtures import *

# NER fixtures
from tests.fixtures.ner.sentences.fixtures import *

# Symbolic fixtures
from tests.fixtures.symbolic.formulas.fixtures import *
