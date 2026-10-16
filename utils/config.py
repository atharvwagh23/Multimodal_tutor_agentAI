import os # OS module for env vars
from pathlib import Path # File path handling

from dotenv import load_dotenv # Load .env files

# Find the project root relative to this file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent # Get project root dir

# Load environment variables from the root .env file.
load_dotenv(PROJECT_ROOT / ".env") # Load env vars

def required_env(name: str) -> str: # Get required env var
    """Return a required environment variable or raise an error."""
    value = os.getenv(name) # Fetch value

    if not value: # If missing or empty
        raise ValueError( # Halt with error
            f"Missing environment variable: {name}. "
            "Check your project-root .env file."
        )

    return value # Return valid value

# Model settings can be overridden through .env.
OPENAI_VISION_MODEL = os.getenv( # Get vision model
    "OPENAI_VISION_MODEL", "gpt-4o-mini" # Default to gpt-4o-mini
)

OPENAI_TTS_MODEL = os.getenv( # Get TTS model
    "OPENAI_TTS_MODEL", "gpt-4o-mini-tts" # Default to gpt-4o-mini-tts
)

OPENAI_TTS_VOICE = os.getenv( # Get TTS voice
    "OPENAI_TTS_VOICE", "coral" # Default to coral
)

# Resolve data directories relative to the project root.
UPLOAD_DIR = PROJECT_ROOT / os.getenv("UPLOAD_DIR", "uploads") # Set uploads dir
AUDIO_DIR = PROJECT_ROOT / os.getenv("AUDIO_DIR", "audio") # Set audio dir

# Keep uploaded files within a configurable size limit.
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20")) # Set max upload limit

# Create directories if they do not exist.
UPLOAD_DIR.mkdir(parents=True, exist_ok=True) # Create uploads dir
AUDIO_DIR.mkdir(parents=True, exist_ok=True) # Create audio dir