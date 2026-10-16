"""Command-line smoke test for the Multimodal Tutor Agent.

Usage:
    uv run python main.py path/to/test_image.png
""" # Module docstring

import argparse # CLI arguments parser
from pathlib import Path # File path handling

from utils.openai_utils import analyze_image # Import analysis func


def main() -> None: # Define main entry point
    """Analyze one image and print the result.""" # Function docstring
    parser = argparse.ArgumentParser( # Initialize argument parser
        description="Analyze a study image using OpenAI." # Set description
    ) # End parser init

    parser.add_argument( # Define expected CLI argument
        "image_path", # Argument name
        type=Path, # Enforce Path type
        help="Path to a local PNG, JPG, or WEBP image.", # Provide help text
    ) # End argument definition

    args = parser.parse_args() # Parse provided arguments

    if not args.image_path.is_file(): # Check if file exists
        parser.error(f"File does not exist: {args.image_path}") # Halt with error

    # Call the same function used by the Streamlit application.
    result = analyze_image(str(args.image_path.resolve())) # Run image analysis

    print("\n=== Tutor Analysis ===\n") # Print output header
    print(result) # Print generated analysis


if __name__ == "__main__": # Check if run as main script
    main() # Execute main function