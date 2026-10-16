"""Convert PDF documents into image files.""" # Module docstring

from pathlib import Path # File path handling
from uuid import uuid4 # Unique IDs

from pdf2image import convert_from_path # PDF conversion lib

from utils.config import UPLOAD_DIR # Upload dir config
from utils.tracing_utils import traced_function # Tracing utility


@traced_function("pdf_to_images") # Trace this function
def pdf_to_images(pdf_path: str) -> list[str]: # Define conversion func
    """
    Convert every page of a PDF into a PNG image.

    Args:
        pdf_path: Path to the uploaded PDF.

    Returns:
        List of generated image paths, ordered by page.
    """
    source = Path(pdf_path) # Create Path object

    if not source.exists(): # Check if file exists
        raise FileNotFoundError(f"PDF not found: {source}") # Halt with error

    # Render pages at 180 DPI, a practical starting point
    # for readable notes without unnecessarily huge images.
    pages = convert_from_path( # Convert PDF to images
        str(source), # Pass string path
        dpi=180, # Set resolution to 180 DPI
    ) # End conversion

    image_paths = [] # Init paths list

    # Use unique names to avoid overwriting another document.
    for page_number, page_image in enumerate(pages, start=1): # Loop through pages
        output_path = UPLOAD_DIR / ( # Create output path
            f"{uuid4().hex}_page_{page_number}.png" # Unique filename per page
        ) # End path creation

        # Save the rendered page in PNG format.
        page_image.save(output_path, format="PNG") # Save as PNG
        image_paths.append(str(output_path)) # Add to list

    return image_paths # Return list of paths