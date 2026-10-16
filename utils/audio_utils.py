"""Generate spoken explanations using OpenAI text-to-speech.""" # Module docstring explaining the script's purpose

from pathlib import Path # Import Path for object-oriented filesystem paths
from uuid import uuid4 # Import uuid4 to generate unique random identifiers for filenames

from utils.config import AUDIO_DIR, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE # Import configuration constants for directories and models
from utils.tracing_utils import get_openai_client, traced_function # Import custom utilities for tracing and initializing the API client


@traced_function("generate_audio") # Decorator to trace/monitor this function's execution and performance
def generate_audio(text: str) -> str: # Define the function taking a text string and returning a file path string
    """
    Convert text into speech and return the generated MP3 path.

    Args:
        text: Explanation that should be narrated.

    Returns:
        Absolute path to the saved MP3 file.
    """
    if not text or not text.strip(): # Check if the provided text is empty, None, or only contains whitespace
        raise ValueError("Cannot generate audio from empty text.") # Halt execution and raise an error if the text is invalid

    client = get_openai_client() # Initialize or retrieve the authenticated OpenAI API client

    # Create a unique output filename for this narration.
    output_path = AUDIO_DIR / f"{uuid4().hex}.mp3" # Generate a unique 32-character hex string and append '.mp3' to the target directory

    # The speech endpoint returns audio bytes.
    # Use a tutor-like instruction to influence delivery.
    with client.audio.speech.with_streaming_response.create( # Open a context manager for a streaming connection to the TTS endpoint
        model=OPENAI_TTS_MODEL, # Specify which TTS model to use (e.g., tts-1 or tts-1-hd)
        voice=OPENAI_TTS_VOICE, # Specify the chosen voice personality (e.g., alloy, echo, onyx)
        input=text[:4000], # Pass the text, truncating it to 4000 characters to stay within API limits
        instructions=( # Provide custom system instructions to guide the voice model's tone and pacing
            "Speak clearly at a moderate pace, like a tutor " # First half of the string literal
            "explaining study material to a student." # Second half of the string literal (implicitly concatenated)
        ),
        response_format="mp3", # Explicitly request the audio output format to be MP3
    ) as response: # Bind the active stream object to the 'response' variable

        # Stream the response to a file instead of keeping
        # the complete audio response in memory.
        response.stream_to_file(output_path) # Write the incoming audio chunks directly to the disk at output_path

    return str(output_path.resolve()) # Convert the Path object to an absolute system file path string and return it