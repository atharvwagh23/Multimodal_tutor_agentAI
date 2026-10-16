"""Streamlit interface for the Multimodal Tutor Agent.""" # Module docstring

from pathlib import Path # Path handling
from uuid import uuid4 # Unique IDs

import streamlit as st # Streamlit UI lib

from utils.audio_utils import generate_audio # Audio generator
from utils.config import MAX_UPLOAD_MB, UPLOAD_DIR # Config vars
from utils.openai_utils import analyze_image # Image analyzer
from utils.pdf_utils import pdf_to_images # PDF converter


# Configure the page before creating other Streamlit elements.
st.set_page_config( # Set page config
    page_title="AI Tutor Agent", # Browser tab title
    page_icon="🎓", # Favicon
    layout="wide", # Use wide layout
    initial_sidebar_state="expanded" # Keep sidebar open
)

# --- Custom CSS for a sleeker look ---
st.markdown("""
<style>
    /* Soften the main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Style the audio player to blend better */
    audio {
        width: 100%;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Main App Header ---
st.title("🎓 Multimodal Tutor Agent") # App title
st.markdown("Transform your study materials into structured notes, quizzes, and audio explanations.")

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("Upload Material")
    st.write("Supports handwritten notes, diagrams, code screenshots, or PDFs.")
    
    # Restrict file types in the interface.
    uploaded_file = st.file_uploader( # File uploader widget
        "Choose an image or PDF", # Widget label
        type=["jpg", "jpeg", "png", "pdf"], # Allowed extensions
        help="Limit: 20MB per file"
    )

# --- Main Content Area ---
if not uploaded_file:
    # Empty state illustration/message
    st.info("👈 Please upload a document or image from the sidebar to begin.")
    st.stop()

# Check file size before saving or processing.
max_bytes = MAX_UPLOAD_MB * 1024 * 1024 # Calc max bytes

if uploaded_file.size > max_bytes: # Check size limit
    st.sidebar.error(f"The file exceeds the {MAX_UPLOAD_MB} MB limit.") # Show error
    st.stop() # Halt execution

# Create a safe, application-controlled filename.
extension = Path(uploaded_file.name).suffix.lower() # Get file extension
supported_extensions = {".jpg", ".jpeg", ".png", ".pdf"} # Valid extensions

if extension not in supported_extensions: # Validate extension
    st.sidebar.error("Unsupported file type.") # Show error
    st.stop() # Halt execution

upload_path = UPLOAD_DIR / f"{uuid4().hex}{extension}" # Generate unique path

# Save the uploaded bytes locally.
upload_path.write_bytes(uploaded_file.getvalue()) # Save file to disk
st.sidebar.success(f"Uploaded successfully!") # Show success msg

# Convert PDFs into images; use images directly otherwise.
try: # Start conversion block
    if extension == ".pdf": # If PDF file
        with st.status("Processing PDF...", expanded=True) as status:
            st.write("Extracting pages...")
            image_paths = pdf_to_images(str(upload_path)) # Convert PDF
            status.update(label="PDF converted to images!", state="complete", expanded=False)
    else: # If image file
        image_paths = [str(upload_path)] # Use image directly

    if not image_paths: # Check if images exist
        st.error("No images were available for analysis.") # Show error
        st.stop() # Halt execution

except Exception as exc: # Catch conversion errors
    st.error(f"File conversion failed: {exc}") # Show error
    st.stop() # Halt execution


# Analyze each image and preserve page-level results.
analysis_sections = [] # Init results list

try: # Start analysis block
    with st.spinner("🧠 AI is analyzing your material..."): # Show spinner
        for page_number, image_path in enumerate( # Loop through images
            image_paths, start=1 # Start counting at 1
        ):
            result = analyze_image(image_path) # Analyze image
            analysis_sections.append(f"## Page/Image {page_number}\n\n{result}")

    # Combine all page results for display and narration.
    combined_analysis = "\n\n---\n\n".join(analysis_sections) # Join results
    st.session_state["analysis"] = combined_analysis # Save to session

except Exception as exc: # Catch analysis errors
    st.error(f"AI analysis failed: {exc}") # Show error
    st.exception(exc) # Show traceback
    st.stop() # Halt execution

# --- Display Results in UI Cards ---
col1, col2 = st.columns([2, 1]) # Create a 2-column layout (wide left, narrow right)

with col1:
    # Use a bordered container to make the text look like a document card
    with st.container(border=True):
        st.subheader("📚 Learning Material") 
        st.markdown(st.session_state["analysis"]) # Render analysis markdown

with col2:
    # Use a bordered container for the Audio actions
    with st.container(border=True):
        st.subheader("🎧 Audio Tutor")
        st.write("Listen to a spoken explanation of this material.")
        
        # Generate narration only when the user requests it.
        if st.button("Generate Audio Explanation", use_container_width=True, type="primary"): 
            try: 
                with st.spinner("Generating voice..."): 
                    narration_text = st.session_state["analysis"][:4000] # Truncate text
                    audio_path = generate_audio(narration_text) # Generate audio
                
                st.session_state["audio_path"] = audio_path # Save audio path
                st.success("Audio ready!") 
            except Exception as exc: 
                st.error(f"Audio generation failed: {exc}") 
                
        # Display the audio player if audio has been generated.
        audio_path = st.session_state.get("audio_path") 

        if audio_path and Path(audio_path).is_file(): 
            with open(audio_path, "rb") as audio_file: 
                st.audio(audio_file.read(), format="audio/mp3")