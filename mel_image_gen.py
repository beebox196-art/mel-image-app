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
st.caption("Powered by Google Gemini 2.0 Flash • Created by Bee for Mel")

# 3. Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("Using Gemini 2.0 Flash (experimental). For production, we'll switch to Vertex AI with your $300 credit.")
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
                
                # Use Gemini 2.0 Flash for image generation
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # Generate the image
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_modalities": ["TEXT", "IMAGE"],
                    }
                )
                
                # Process the response
                if response.candidates and response.candidates[0].content.parts:
                    images = []
                    text_response = ""
                    
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # This is an image
                            img_data = base64.b64decode(part.inline_data.data)
                            img = Image.open(io.BytesIO(img_data))
                            images.append(img)
                        elif hasattr(part, 'text') and part.text:
                            text_response = part.text
                    
                    if images:
                        # Display the first image
                        st.success("Here's your creation!")
                        st.image(images[0], caption=prompt, use_container_width=True)
                        
                        # Download button
                        buffered = io.BytesIO()
                        images[0].save(buffered, format="PNG")
                        st.download_button(
                            label="📥 Download Image",
                            data=buffered.getvalue(),
                            file_name=f"mel_creation_{prompt[:20].replace(' ', '_')}.png",
                            mime="image/png"
                        )
                        
                        # Store in session for gallery
                        if 'gallery' not in st.session_state:
                            st.session_state.gallery = []
                        st.session_state.gallery.append({
                            'prompt': prompt,
                            'image': images[0]
                        })
                        
                        # Show text response if any
                        if text_response:
                            st.info(f"📝 {text_response}")
                    else:
                        st.error("No image was generated. The model returned text only.")
                        if text_response:
                            st.write(text_response)
                        
                else:
                    st.error("Could not generate image. Try again with a different prompt.")
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"Something went wrong: {error_msg}")
                
                # Helpful error messages
                if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                    st.warning("⚠️ You've hit the free tier limit. Time to switch to Vertex AI with your $300 credit!")
                elif "api key" in error_msg.lower() or "invalid" in error_msg.lower():
                    st.warning("🔑 The API key might be wrong. Check the secrets configuration.")
                elif "not found" in error_msg.lower() or "not supported" in error_msg.lower():
                    st.warning("🔧 Model not available. Bee needs to update the app.")
                else:
                    with st.expander("🔍 Technical Details"):
                        st.code(error_msg)

# 6. Gallery (shows previous generations in this session)
# ---------------------------
if 'gallery' in st.session_state and len(st.session_state.gallery) > 1:
    st.divider()
    st.header("🖼️ This Session's Gallery")
    
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.gallery[:-1]):
        with cols[idx % 3]:
            st.image(item['image'], caption=item['prompt'][:40] + "...", use_column_width=True)
