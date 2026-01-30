# 3. Where API Keys Are Usually Stored
# Common patterns in code:

# Option 1: Environment variables
import os
openai_key = os.environ.get("OPENAI_API_KEY")
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

# Option 2: Config files
from config import OPENAI_API_KEY

# Option 3: .env files
from dotenv import load_dotenv
load_dotenv()

# Option 4: Hardcoded (bad practice, but check for it)
api_key = "sk-..."
