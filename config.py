import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
COURSES_DIR = PROJECT_ROOT / "courses"

# Anthropic / LangChain
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

# Sandbox
SANDBOX_TIMEOUT = 5  # seconds
SANDBOX_MAX_OUTPUT = 10000  # characters
