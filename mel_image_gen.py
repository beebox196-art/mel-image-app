import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import os

# 1. Configuration & Secrets
# ---------------------------
google_api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# 2. Page Setup
# ---------------------------
st.set_page_config(
    page_title="Mel's Image Studio",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Mel's Image Studio")
st.write("Welcome! Type what you want to see below and click Generate.")
st.caption("Powered by Google Gemini 2.5 Flash Image • Created by Bee for Mel")

# 3. Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("Using Gemini 2.5 Flash Image. For production, we'll switch to Vertex AI with your $300 credit.")
    st.divider()
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Be specific with details
    - Include style (photo, painting, cartoon)
    - Add lighting (sunset, dramatic, soft)
    - Mention mood (peaceful, energetic)
    """)
    st.divider()
    st.markdown("### 🐝 About")
    st.markdown("Built by Bee for the Box family AI team.")

# 4. Main Interface
# ---------------------------
prompt = st.text_area(
    "What should I create?",
    height=120,
    placeholder="A serene landscape with a mountain lake at sunset, photorealistic style..."
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_button = st.button("✨ Generate Image", type="primary", use_container_width=True)

# 5. The Logic
# ---------------------------
if generate_button:
    if not prompt:
        st.warning("Please enter a prompt first!")
    elif not google_api_key:
        st.error("No API key configured. Add GEMINI_API_KEY to Streamlit secrets.")
    else:
        with st.spinner("Creating your image... (usually 10-30 seconds)"):
            try:
                # Configure the client
                genai.configure(api_key=google_api_key)
                
                # Use Gemini 2.5 Flash Image for image generation
                model = genai.GenerativeModel('gemini-2.5-flash-image')
                
                # Generate the image
                response = model.generate_content(prompt)
                
                # Extract the image from response
                image_found = False
                
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                # Check for inline_data (image)
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    try:
                                        # The data might be base64 string or bytes
                                        raw_data = part.inline_data.data
                                        
                                        # Try to decode as base64 first
                                        try:
                                            img_data = base64.b64decode(raw_data)
                                        except:
                                            # If that fails, it might already be bytes
                                            img_data = raw_data
                                        
                                        # Try to open the image
                                        img = Image.open(io.BytesIO(img_data))
                                        
                                        st.success("Here's your creation!")
                                        st.image(img, caption=prompt, use_column_width=True)
                                        
                                        # Download button
                                        buffered = io.BytesIO()
                                        img.save(buffered, format="PNG")
                                        st.download_button(
                                            label="📥 Download Image",
                                            data=buffered.getvalue(),
                                            file_name=f"mel_creation.png",
                                            mime="image/png"
                                        )
                                        image_found = True
                                        
                                    except Exception as img_error:
                                        st.error(f"Image decode error: {img_error}")
                                        # Show what we got for debugging
                                        st.write(f"Data type: {type(raw_data)}")
                                        st.write(f"Data length: {len(raw_data) if raw_data else 0}")
                                
                                # Show text response if any
                                elif hasattr(part, 'text') and part.text:
                                    st.info(f"📝 {part.text}")
                
                if not image_found:
                    st.error("No image found in the response.")
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"Something went wrong: {error_msg}")
                
                # Helpful error messages
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    st.warning("⚠️ You've hit the free tier limit. Time to switch to Vertex AI with your $300 credit!")
                elif "api key" in error_msg.lower() or "invalid" in error_msg.lower():
                    st.warning("🔑 The API key might be wrong. Check the secrets configuration.")
