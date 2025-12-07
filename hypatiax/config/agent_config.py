"""Agent system configurations"""


class AgentConfig:
    """Configuration for AI agent system"""

    # Agent types
    PARSER_AGENT = "parser_agent"
    GENERATOR_AGENT = "generator_agent"
    VALIDATOR_AGENT = "validator_agent"
    REFINER_AGENT = "refiner_agent"
    EXPLAINER_AGENT = "explainer_agent"

    # Workflow settings
    MAX_ITERATIONS = 10
    TIMEOUT_SECONDS = 300

    # Memory settings
    WORKING_MEMORY_SIZE = 10
    EPISODIC_MEMORY_SIZE = 100

    # Learning settings
    ENABLE_LEARNING = True
    FEEDBACK_STORAGE_PATH = "datasets/queries/tableau/agent/feedback_data.json"

    # Paths
    AGENT_MODELS_DIR = "models/queries/tableau/agents"
    AGENT_DATA_DIR = "datasets/queries/tableau/agent"
