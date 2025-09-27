import streamlit as st
from PIL import Image
import time
import base64  # Required for Base64 image embedding
import os  # Required to check file paths

# --- FILE PATH SETUP (NEW ROBUSTNESS) ---
# Get the absolute directory of the current script (app.py)
# This handles cases where the user runs streamlit from a different directory (e.g., the project root)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="Cancer Detector",
    page_icon="🧠",  # Keeping the page icon as an emoji/text for compatibility
    layout="wide"
)

# --- SESSION STATE (MOVED TO TOP FOR SAFETY) ---
if "toggle" not in st.session_state:
    st.session_state.toggle = True
if "page" not in st.session_state:
    st.session_state.page = "home"
if "history_log" not in st.session_state:
    st.session_state.history_log = []
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "show_image_preview" not in st.session_state:  # NEW: Flag to control image preview visibility
    st.session_state.show_image_preview = False


# --- BASE64 HELPER FUNCTION ---
def get_base64_image(relative_image_path):
    """Reads a local image and converts it to a base64 string for embedding in HTML."""
    try:
        # Construct the full absolute path
        full_path = os.path.join(CURRENT_DIR, relative_image_path)

        # Ensure the file exists before attempting to read
        if not os.path.exists(full_path):
            print(f"Error: Image file not found at {full_path}")
            return ""

        # Use standard Python open/read for Base64 encoding
        with open(full_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()

        # Determine MIME type (assuming png for all icons)
        mime_type = "image/png"

        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        # Catch any other file reading or encoding errors
        print(f"Failed to encode image {relative_image_path}: {e}")
        return ""


# --- QUERY PARAMETER CLICK HANDLING ---
# Check for clicks from the HTML anchor tags and update state immediately
# This block is now safe because st.session_state is guaranteed to be initialized above.
query_params = st.query_params
if "action" in query_params:
    action = query_params["action"]

    # 1. Handle Toggle Click
    if action == "toggle":
        st.session_state.toggle = not st.session_state.toggle
        st.query_params.clear()

        # 2. Handle History Click
    elif action == "history":
        new_page = "history" if st.session_state.page == "home" else "home"
        st.session_state.page = new_page
        st.query_params.clear()

        # 3. Handle Predict Click
    elif action == "predict":
        st.query_params.clear()

    # --- DARK THEME & CUSTOM CSS ---
st.markdown("""
<style>
/* Main container background and text color (Black background, White text) */
.main {
    background-color: #000000; 
    color: white;
    font-family: 'Arial', sans-serif;
}

/* Custom styling for round action elements (Toggle and History) - Now using anchor tags */
.round-action-btn {
    /* Base style for the containing element */
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px; 
    height: 50px;
    border-radius: 50%; 
    border: 2px solid #3b82f6; 
    background-color: #1f2937; /* Dark Gray */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5); 
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    text-decoration: none; /* Remove default anchor underline */
}

/* Hover effect for the anchor tag element */
.round-action-btn:hover {
    transform: scale(1.1);
    background-color: #2c3a4d;
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.7);
}

/* Styling for images inside the round action elements */
.round-button-img {
    width: 100%; 
    height: 100%;
    border-radius: 50%; 
    object-fit: cover;
    padding: 5px; 
}

/* NEW STYLES for the Predict/Send icon button (now an anchor tag) */
.predict-action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    border: none;
    background-color: #3b82f6; /* Blue background */
    color: white;
    height: 40px; 
    width: 100%; /* Use 100% width of the container column */
    transition: all 0.2s ease-in-out;
    cursor: pointer;
    text-decoration: none;
    font-weight: 600;
    /* Aesthetic enhancements: Shadow */
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4); /* Blue glow/shadow */
}

.predict-action-btn:hover {
    background-color: #4f90f9; /* Slightly lighter blue on hover */
    /* Aesthetic enhancements: Scale and darker shadow on hover */
    transform: translateY(-2px) scale(1.02); /* Slight lift and scale */
    box-shadow: 0 6px 15px rgba(59, 130, 246, 0.6); /* More pronounced shadow */
}

/* Styling for the image inside the rectangular Predict/Send button */
.predict-icon {
    height: 24px; 
    width: auto;
    object-fit: contain;
}

/* Input field styling (for the visible uploader label/text) */
.stFileUploader label p, .stFileUploader label span {
    color: white !important;
}

/* Custom style for the title bar alignment in the middle column (Centered) */
.title-bar {
    display: flex; 
    align-items: center; 
    justify-content: center; 
    gap: 15px;
    padding-top: 5px; 
}

/* Hide the Streamlit main menu and footer ("deploy thingy") */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- MODULAR COMPONENTS ---

def top_bar():
    """Renders the top bar: toggle button, title+logo, history button"""
    # Columns [Toggle (1), Title (4), History (1)]
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        # Toggle icon - now using Base64 embedding with robust path finding
        image_name = "brain.png" if st.session_state.toggle else "eye.png"
        toggle_src = get_base64_image(f"images/{image_name}")

        st.markdown(f"""
            <a href="?action=toggle" class="round-action-btn" title="Toggle Mode">
                <img src='{toggle_src}' class='round-button-img' alt='Toggle Mode'>
            </a>
        """, unsafe_allow_html=True)

    with col2:
        # Logo remains as emoji
        st.markdown(f"""
        <div class='title-bar'>
            <h2 style='margin:0; color: #3b82f6;'>Cancer Detector</h2>
            <span style='font-size: 1.5em;'>⚕️</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # History icon - now using Base64 embedding with robust path finding
        history_src = get_base64_image("images/history.png")
        action_param = "history"

        st.markdown(f"""
            <a href="?action={action_param}" class="round-action-btn" title="View History">
                <img src='{history_src}' class='round-button-img' alt='History Log'>
            </a>
        """, unsafe_allow_html=True)


def upload_and_predict_row():
    """
    Renders the file uploader and the 'Predict' button side-by-side,
    centered horizontally on the screen.
    """
    # The outer columns [1, 6, 1] already center the upload area.
    st.markdown("<br>", unsafe_allow_html=True)

    # Outer columns for centering the entire row (1:6:1 ratio for wide center)
    col_outer_left, col_center, col_outer_right = st.columns([1, 6, 1])

    uploaded_file = None
    predict_clicked = False  # Flag to track if the new HTML button was clicked

    with col_center:
        # Inner columns for the upload and button side-by-side (5:1 ratio)
        col_upload, col_button = st.columns([5, 1])

        with col_upload:
            # Use a callback to save the file data to session state immediately upon upload
            uploaded_file = st.file_uploader(
                "Upload Image (JPG, PNG, JPEG) for Analysis:",
                type=["jpg", "png", "jpeg"],
                label_visibility="visible"
            )

            # Store the uploaded file data for prediction trigger later
            if uploaded_file is not None:
                # If a new file is uploaded or the existing file is different, reset the preview flag
                if st.session_state.uploaded_file_data is None or uploaded_file.name != st.session_state.uploaded_file_data.name:
                    st.session_state.show_image_preview = False
                st.session_state.uploaded_file_data = uploaded_file
            # If the user clears the uploader, clear the session state and hide the preview
            elif st.session_state.uploaded_file_data and uploaded_file is None:
                st.session_state.uploaded_file_data = None
                st.session_state.show_image_preview = False

        with col_button:
            # Spacer to align the button vertically with the uploader
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

            # Predict icon - now using Base64 embedding with robust path finding
            predict_src = get_base64_image("images/send.png")
            predict_html = f"<img src='{predict_src}' class='predict-icon' alt='Send'>"

            # This HTML link element is what the user clicks on
            st.markdown(f"""
                <a href="?action=predict" class="predict-action-btn" title="Predict">
                    {predict_html}
                </a>
            """, unsafe_allow_html=True)

            # Check if the predict action was triggered by the query parameter (the HTML link click)
            if "action" in st.query_params and st.query_params["action"] == "predict":
                predict_clicked = True

    # --- Prediction Logic (executed if the HTML link was clicked) ---
    if predict_clicked:
        file_to_analyze = st.session_state.uploaded_file_data

        if file_to_analyze is not None:
            # 1. Simulate prediction/processing
            with st.spinner(f"Analyzing {file_to_analyze.name}..."):
                time.sleep(1)

                # 2. Determine a result (Dummy)
            result_type = "Malignant" if time.time() % 2 == 0 else "Benign"
            result_message = f"✅ Prediction Complete: **{result_type}** tissue detected for **{file_to_analyze.name}**."

            # 3. Log to history and show success
            st.session_state.history_log.insert(0, result_message)
            st.success(result_message)
            st.session_state.show_image_preview = True  # SET FLAG to show preview after successful prediction
        else:
            st.warning("🚨 Please upload an image file to begin the prediction.")

    return st.session_state.uploaded_file_data


# --- PAGE RENDERING LOGIC ---

top_bar()
# REMOVED: st.markdown("---")

if st.session_state.page == "home":
    # HOME PAGE
    uploaded_file = upload_and_predict_row()

    # CONDITION CHECK: Only show the image if a file is uploaded AND the preview flag is True
    if uploaded_file and st.session_state.show_image_preview:
        st.markdown("---")  # Keep the separator before the image preview
        # Centered Image Preview Title
        st.markdown("<h4 style='text-align: center;'>Image Preview</h4>", unsafe_allow_html=True)

        # Center the image preview itself
        col_img_spacer, col_img, col_img_spacer_2 = st.columns([1, 6, 1])
        with col_img:
            # We must pass the actual uploaded file object back to st.image
            # Since the prediction logic now relies on session state, we use that
            # or the immediate return value if available.
            st.image(uploaded_file, caption=f"File: {uploaded_file.name}", use_column_width=True)

elif st.session_state.page == "history":
    # HISTORY PAGE
    st.title("Prediction History")  # Changed title from "yo" for clarity

    st.markdown("---")

    if st.session_state.history_log:
        for i, item in enumerate(st.session_state.history_log, 1):
            st.markdown(
                f"<div style='background-color:#1a1a1a; padding:10px; border-radius:8px; margin-bottom:10px;'>**{i}.** {item}</div>",
                unsafe_allow_html=True)
    else:
        st.info("No previous predictions recorded yet. Use the Home page to start analyzing!")
