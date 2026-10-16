"""Optional local OCR utility using Tesseract.""" # Module docstring

from pathlib import Path # File path handling

import pytesseract # Tesseract OCR library
from PIL import Image # Image processing

from utils.tracing_utils import traced_function # Tracing utility


@traced_function("extract_text") # Trace this function
def extract_text(image_path: str) -> str: # Define OCR function
    """
    Extract text from an image using the local Tesseract engine.

    This operation does not call OpenAI.
    """
    path = Path(image_path) # Create Path object

    if not path.is_file(): # Check if file exists
        raise FileNotFoundError(f"Image not found: {path}") # Halt with error

    # Open the image and convert it to a standard RGB image.
    with Image.open(path) as image: # Open image file
        normalized_image = image.convert("RGB") # Convert to standard RGB

        # Run OCR using the Tesseract executable installed locally.
        extracted_text = pytesseract.image_to_string( # Run text extraction
            normalized_image # Pass RGB image
        )

    return extracted_text.strip() # Return cleaned text