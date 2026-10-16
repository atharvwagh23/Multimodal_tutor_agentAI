"""Analyze notes, diagrams, charts, and screenshots using OpenAI.""" # Module docstring

import base64 # Base64 encoding
import mimetypes # MIME type detection
from pathlib import Path # File path handling

from utils.config import OPENAI_VISION_MODEL # Import vision model config
from utils.tracing_utils import get_openai_client, traced_function # Import API and tracing utilities


TUTOR_INSTRUCTIONS = """
You are a precise, patient multimodal tutor.

Analyze the uploaded educational material and produce these sections:

1. DETAILED EXPLANATION
Explain the content in simple language. Define technical terms
and describe diagrams, relationships, formulas, and code where visible.

2. SUMMARY NOTES
Provide concise notes that a student can revise later.

3. IMPORTANT CONCEPTS
List the important concepts and explain why each matters.

4. ASSIGNMENT QUESTIONS
Create five questions based on the material, mixing conceptual
and application-oriented questions. Include answers separately.

5. TEXT-BASED MIND MAP
Represent the main topic and its subtopics as a readable
hierarchical outline.

6. UNCERTAINTIES
Mention anything illegible, cropped, ambiguous, or inferred.
Never invent text that cannot be read from the image.

Use clear headings and explain acronyms when they first appear.
If the input is a code screenshot, explain the code's purpose,
control flow, important statements, and likely failure cases.
""" # Multiline prompt instructions


def image_to_data_url(image_path: str) -> str: # Define conversion func
    """
    Convert a local image to a base64 data URL.

    The data URL lets the API receive the image content directly,
    without requiring a publicly accessible image URL.
    """
    path = Path(image_path) # Create Path object

    if not path.is_file(): # Check if file exists
        raise FileNotFoundError(f"Image not found: {path}") # Halt with error

    # Detect the MIME type from the image extension.
    mime_type, _ = mimetypes.guess_type(path.name) # Guess MIME type

    # Only allow the image formats used by this application.
    allowed_types = { # Define allowed formats
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    if mime_type not in allowed_types: # Check if format is supported
        raise ValueError(f"Unsupported image format: {mime_type}") # Halt on unsupported format

    # Encode the file bytes as base64.
    image_bytes = path.read_bytes() # Read file bytes
    encoded_image = base64.b64encode(image_bytes).decode("utf-8") # Encode to base64 string

    return f"data:{mime_type};base64,{encoded_image}" # Return formatted data URL


@traced_function("analyze_image") # Trace this function
def analyze_image(image_path: str) -> str: # Define analysis func
    """
    Send an image to OpenAI and return a tutoring explanation.
    """
    client = get_openai_client() # Get API client

    # Convert the image to the format accepted by the API.
    image_url = image_to_data_url(image_path) # Convert to data URL

    # Request an explanation grounded in the supplied image.
    response = client.responses.create( # Call API
        model=OPENAI_VISION_MODEL, # Set vision model
        instructions=TUTOR_INSTRUCTIONS, # Pass instructions
        input=[ # Define inputs
            { # Start user message
                "role": "user", # Set role
                "content": [ # Start content list
                    { # Start text part
                        "type": "input_text", # Specify text type
                        "text": ( # Provide prompt text
                            "Analyze this educational material " # Prompt part 1
                            "and follow the tutoring instructions." # Prompt part 2
                        ),
                    }, # End text part
                    { # Start image part
                        "type": "input_image", # Specify image type
                        "image_url": image_url, # Pass data URL
                        "detail": "high", # Request high detail
                    }, # End image part
                ], # End content list
            } # End user message
        ], # End inputs
        max_output_tokens=3000, # Limit output tokens
    ) # End API call

    # The SDK exposes the generated text through output_text.
    return response.output_text.strip() # Return cleaned text