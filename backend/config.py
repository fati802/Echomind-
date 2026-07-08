import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/echomind.db")
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")

# Default LLM provider is "amd" for mandatory integration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "amd").lower()
AMD_DEV_CLOUD_API_URL = os.getenv("AMD_DEV_CLOUD_API_URL")
AMD_DEV_CLOUD_API_KEY = os.getenv("AMD_DEV_CLOUD_API_KEY")
