import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file using an absolute path relative to this file
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Temporary debug print
fw_key = os.getenv("FIREWORKS_API_KEY")
provider = os.getenv("LLM_PROVIDER")
fw_status = f"Exists (starts with {fw_key[:4]}... ends with {fw_key[-4:]})" if fw_key else "Not Set"
provider_status = provider if provider else "Not Set"
print(f"--- DEBUG .ENV LOAD --- FIREWORKS_API_KEY: {fw_status}, LLM_PROVIDER: {provider_status}")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/echomind.db")
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")

# Default LLM provider is "amd" for mandatory integration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "amd").lower()
AMD_DEV_CLOUD_API_URL = os.getenv("AMD_DEV_CLOUD_API_URL")
AMD_DEV_CLOUD_API_KEY = os.getenv("AMD_DEV_CLOUD_API_KEY")
