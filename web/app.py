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
if "page" not in st.session_state:  # FIXED: Changed st.session_session to st.session_state
    st.session_state.page = "home"  # Initial page state
if "history_log" not in st.session_state:
    st.session_state.history_log = []
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
# Flag to display warning after failed prediction attempt
if "show_predict_warning" not in st.session_state:
    st.session_state.show_predict_warning = False
# New state to store the page before navigating to History
if "history_source_page" not in st.session_state:
    st.session_state.history_source_page = "home"


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


# --- BUTTON HANDLER FUNCTION ---
def handle_predict_click():
    """
    Handles the prediction logic when the Streamlit button is clicked.
    This replaces the query parameter trigger for prediction.
    """
    file_to_analyze = st.session_state.uploaded_file_data

    if file_to_analyze is not None:
        # --- START: Simplified "Analysis" ---
        result_message = f"Displaying Sent Image for **{file_to_analyze.name}**."
        st.session_state.history_log.insert(0, result_message)
        # --- END: Simplified "Analysis" ---

        # Clear query params and switch page state to show the analysis view
        st.query_params.clear()
        st.session_state.page = "analysis_result"
        st.session_state.show_predict_warning = False  # Clear any pending warning
    else:
        # If no file is uploaded, stay on home and set flag to show warning
        st.session_state.page = "home"
        st.session_state.show_predict_warning = True


# --- QUERY PARAMETER CLICK HANDLING ---
query_params = st.query_params
if "action" in query_params:
    action = query_params["action"]

    # 1. Handle Toggle Click
    if action == "toggle":
        st.session_state.toggle = not st.session_state.toggle
        st.query_params.clear()

    # 2. Handle History Click (Toggles between home/analysis and history) - UPDATED
    elif action == "history":
        if st.session_state.page != "history":
            # Entering History: Store current page as source
            st.session_state.history_source_page = st.session_state.page
            st.session_state.page = "history"
        else:
            # Clicking History when already on History: treat as a toggle OFF, go back to source
            if "history_source_page" in st.session_state:
                st.session_state.page = st.session_state.history_source_page
            else:
                st.session_state.page = "home"  # Fallback

        st.query_params.clear()

    # 3. Handle Back Click (Used by Analysis Result and History pages) - UPDATED
    elif action == "back":
        if st.session_state.page == "history":
            # Coming from History: go back to stored source page
            target_page = st.session_state.get("history_source_page", "home")
            st.session_state.page = target_page

            # Clean up history state since we've returned
            if "history_source_page" in st.session_state:
                del st.session_state.history_source_page

        elif st.session_state.page == "analysis_result":
            # Coming from Analysis Result: always go to home
            st.session_state.page = "home"

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

/* Style for the emoji used in the back button to center it */
.round-action-btn span {
    padding: 10px; /* Adjust padding to make the emoji sit right in the center */
}

/* NEW STYLES for the Streamlit Predict/Send button (Targeting the native component) */
.stButton button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 12px !important;
    border: none !important;
    background-color: #3b82f6 !important; /* Blue background */
    color: white !important;
    height: 40px !important; 
    width: 100% !important; 
    transition: all 0.2s ease-in-out !important;
    cursor: pointer !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4) !important;
    margin: 0 !important;
    padding: 0 1rem !important;
}

.stButton button:hover {
    background-color: #4f90f9 !important; 
    transform: translateY(-2px) scale(1.02) !important; 
    box-shadow: 0 6px 15px rgba(59, 130, 246, 0.6) !important;
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

/* Centering the entire app content using max-width */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
</style>
""", unsafe_allow_html=True)


# --- MODULAR COMPONENTS ---

def top_bar():
    """Renders the top bar: action button (toggle or back), title+logo, and history button.
    All anchor tags now include target="_self" to prevent opening new tabs."""
    # Columns [Action Button (1), Title (4), History Button (1)]
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        # Show Back button if on analysis_result OR history pages
        if st.session_state.page in ["analysis_result", "history"]:
            # Display Back button on the analysis result page
            # Uses the unified 'back' action
            st.markdown(f"""
                <a href="?action=back" target="_self" class="round-action-btn" title="Go Back">
                    <span style='font-size: 1.5em;'>⬅️</span> 
                </a>
            """, unsafe_allow_html=True)
        else:
            # Display Toggle button on home page
            image_name = "brain.png" if st.session_state.toggle else "eye.png"
            toggle_src = get_base64_image(f"images/{image_name}")

            st.markdown(f"""
                <a href="?action=toggle" target="_self" class="round-action-btn" title="Toggle Mode">
                    <img src='{toggle_src}' class='round-button-img' alt='Toggle Mode'>
                </a>
            """, unsafe_allow_html=True)

    with col3:
        # History button is always shown
        history_src = get_base64_image("images/history.png")
        action_param = "history"

        # FIX: Added target="_self"
        st.markdown(f"""
            <a href="?action={action_param}" target="_self" class="round-action-btn" title="View History">
                <img src='{history_src}' class='round-button-img' alt='History Log'>
            </a>
        """, unsafe_allow_html=True)

    with col2:
        # Logo remains as emoji and is always shown
        st.markdown(f"""
        <div class='title-bar'>
            <h2 style='margin:0; color: #3b82f6;'>Cancer Detector</h2>
            <span style='font-size: 1.5em;'>⚕️</span>
        </div>
        """, unsafe_allow_html=True)


def upload_and_predict_row():
    """
    Renders the file uploader and the 'Predict' button side-by-side,
    centered horizontally on the screen. This is only visible on the "home" view.
    Includes logic to show the previously uploaded image when returning from analysis.
    """
    # Spacing to vertically center content
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)

    # Outer columns for centering the entire row (2:4:2 ratio for narrower center)
    col_outer_left, col_center, col_outer_right = st.columns([2, 4, 2])

    with col_center:

        # --- PREVIEW: Display previously uploaded image if available ---
        if st.session_state.uploaded_file_data:
            # Use columns inside col_center for precise centering of the preview
            preview_col_left, preview_col_center, preview_col_right = st.columns([1, 2, 1])
            with preview_col_center:
                # Text confirmation
                st.markdown(
                    f"<div style='text-align: center; color: #9ca3af; margin-bottom: 5px; font-weight: bold;'>File Loaded: {st.session_state.uploaded_file_data.name}</div>",
                    unsafe_allow_html=True
                )
                # Image preview (small, centered)
                st.image(
                    st.session_state.uploaded_file_data,
                    caption=None,
                    width=150
                )

            # Separator and vertical space
            st.markdown("<div style='height: 10px; border-bottom: 1px solid #1f2937;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            # Inner columns for the upload and button side-by-side (5:1 ratio)
        col_upload, col_button = st.columns([5, 1])

        with col_upload:
            # The st.file_uploader must be called to allow the user to clear/change the file.
            # It should ideally retain the file object since we are not clearing session state data.
            uploaded_file = st.file_uploader(
                "Upload Image (JPG, PNG, JPEG) for Analysis:",
                type=["jpg", "png", "jpeg"],
                label_visibility="visible"
            )

            # Store the uploaded file data for prediction trigger later
            if uploaded_file is not None:
                # If a new file is uploaded or the existing file is different, reset page if not home
                if st.session_state.uploaded_file_data is None or uploaded_file.name != st.session_state.uploaded_file_data.name:
                    if st.session_state.page != "home":
                        st.session_state.page = "home"  # Go back to home when new file is uploaded
                st.session_state.uploaded_file_data = uploaded_file
            # If the user clears the uploader, clear the session state too
            elif st.session_state.uploaded_file_data and uploaded_file is None:
                st.session_state.uploaded_file_data = None
                st.session_state.page = "home"  # Return to home on clear

        with col_button:
            # Spacer to align the button vertically with the uploader
            st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

            # Use Base64 helper to get the image source for CSS
            send_src = get_base64_image("images/send.png")

            # Inject CSS to set the image as the background for the target button
            # We use the key to target this specific button instance
            st.markdown(f"""
            <style>
            /* Target the specific Streamlit button element by its data-testid */
            [data-testid*="stButton-predict_button_native"] button {{
                /* Embed the image using Base64 in CSS */
                background-image: url('{send_src}') !important;
                background-size: 60% !important; /* Adjust size of image inside button */
                background-repeat: no-repeat !important;
                background-position: center !important;

                /* Remove text content of the button */
                color: transparent !important;
                font-size: 0 !important;
                line-height: 0 !important;

                /* Ensure it still has the blue background */
                background-color: #3b82f6 !important;

                /* Invert colors if needed (for white icon on blue background) */
                filter: invert(1); 
            }}

            /* Apply hover/active styles to ensure visual feedback */
            [data-testid*="stButton-predict_button_native"] button:hover {{
                filter: invert(1) brightness(1.2); /* Slight brightening on hover */
            }}
            </style>
            """, unsafe_allow_html=True)

            # The st.button handles the click without navigating
            # We use a single space as the label, which is made transparent by the CSS above
            st.button(
                " ",
                key="predict_button_native",
                on_click=handle_predict_click,
                use_container_width=True
            )


# --- PAGE RENDERING LOGIC ---

# 1. Always call the top bar, which handles hiding its buttons based on state
top_bar()

# 2. Render the rest of the content based on the session state page
if st.session_state.page == "home":
    # HOME PAGE - Shows the upload/predict row
    upload_and_predict_row()

    # Show warning if needed after a failed predict attempt
    if st.session_state.show_predict_warning and st.session_state.uploaded_file_data is None:
        st.warning("🚨 Please upload an image file to begin the prediction.")
        st.session_state.show_predict_warning = False  # Clear flag after showing

elif st.session_state.page == "analysis_result":
    # ANALYSIS RESULT PAGE - Minimal Display

    # Ensure uploaded data exists
    if st.session_state.uploaded_file_data:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
        st.title("Sent Image")
        st.markdown("---")

        # Display the uploaded image with a small width, centered.
        col_spacer_left, col_img, col_spacer_right = st.columns([4, 1, 4])

        with col_img:
            st.image(
                st.session_state.uploaded_file_data,
                caption=f"File: {st.session_state.uploaded_file_data.name}",
                use_container_width=True
            )

    else:
        # Fallback if somehow they land here without data
        st.error("No image data available. Please upload an image on the Home page.")
        st.session_state.page = "home"


elif st.session_state.page == "history":
    # HISTORY PAGE
    st.title("Prediction History")

    st.markdown("---")

    if st.session_state.history_log:
        for i, item in enumerate(st.session_state.history_log, 1):
            st.markdown(
                f"<div style='background-color:#1a1a1a; padding:10px; border-radius:8px; margin-bottom:10px;'>**{i}.** {item}</div>",
                unsafe_allow_html=True)
    else:
        st.info("No previous predictions recorded yet. Use the Home page to start analyzing!")
