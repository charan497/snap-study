import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import prompts

# --- Page Configuration ---
st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="wide"
)

# --- Initialize Gemini Client ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Missing `GEMINI_API_KEY` in `.streamlit/secrets.toml`. Please add it to continue.")
    st.stop()

# --- Sidebar Controls ---
with st.sidebar:
    st.title("📚 Study Settings")
    
    selected_mode = st.selectbox(
        "Study Mode",
        options=list(prompts.MODE_PROMPTS.keys()),
        index=0
    )
    
    academic_level = st.selectbox(
        "Target Level",
        options=["Middle School", "High School", "College / Undergraduate", "Exam Prep"],
        index=1
    )
    
    user_query = st.text_area(
        "Have a specific doubt on this page?",
        placeholder="e.g., Can you explain why step 2 substituted zero for v?",
        help="Optional: Ask a specific question about the material."
    )
    
    st.markdown("---")
    st.caption("Supports math notebooks, textbook scans, slide printouts, and diagrams.")

# --- App Header ---
st.title("📸 Snap & Study")
st.caption("Upload or snap a photo of any note, diagram, or problem to get instant tutor guidance.")

# --- Two-Column Layout ---
left_col, right_col = st.columns([1, 1], gap="medium")

with left_col:
    st.subheader("1. Input Material")
    
    capture_mode = st.radio(
        "Source:",
        options=["File Upload", "Webcam / Camera Snap"],
        horizontal=True
    )
    
    uploaded_image = None
    if capture_mode == "File Upload":
        uploaded_image = st.file_uploader(
            "Choose a file",
            type=["png", "jpg", "jpeg", "webp"],
            help="Upload a clear image of notes or textbook pages."
        )
    else:
        uploaded_image = st.camera_input("Take a photo of your notebook or book")

    if uploaded_image:
        image_obj = Image.open(uploaded_image)
        st.image(image_obj, caption="Uploaded Page", use_container_width=True)

with right_col:
    st.subheader("2. AI Tutor Workspace")
    
    if uploaded_image:
        if st.button("✨ Analyze & Generate", type="primary", use_container_width=True):
            with st.spinner("Analyzing your notes and writing response..."):
                try:
                    # Assemble instructions
                    mode_instruction = prompts.MODE_PROMPTS[selected_mode]
                    query_payload = [
                        image_obj,
                        f"Student Level: {academic_level}.\n\n{mode_instruction}"
                    ]
                    
                    if user_query.strip():
                        query_payload.append(f"\n\nStudent's specific question: {user_query.strip()}")

                    # Run multimodal Gemini model
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=query_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=prompts.SYSTEM_INSTRUCTION,
                            temperature=0.2
                        )
                    )
                    
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error communicating with Gemini: {e}")
    else:
        st.info("👈 Upload an image or snap a photo on the left to begin.")