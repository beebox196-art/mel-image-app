import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import os

# 1. Configuration & Secrets
# ---------------------------
# The API key is stored securely in Streamlit Cloud secrets
google_api_key = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

# 2. Page Setup
# ---------------------------
st.set_page_config(
    page_title="Mel's Imagen Studio",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Mel's Imagen Studio")
st.write("Welcome! Type what you want to see below and click Generate.")
st.caption("Powered by Google Imagen • Created by Bee for Mel")

# 3. Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("This app uses Adam's $300 Google Cloud credit for image generation.")
    st.divider()
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Be specific with details
    - Include style (photo, painting, cartoon)
    - Add lighting (sunset, dramatic, soft)
    - Mention mood (peaceful, energetic, mysterious)
    """)
    st.divider()
    st.markdown("### 🐝 About")
    st.markdown("Built by Bee for the Box family AI team.")

# 4. Main Interface
# ---------------------------
prompt = st.text_area(
    "What should I create?",
    height=120,
    placeholder="A serene landscape with a mountain lake at sunset, photorealistic style with warm golden lighting..."
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
        st.error("No API key configured. Adam needs to add GOOGLE_API_KEY to Streamlit secrets.")
    else:
        with st.spinner("Creating your image... (this usually takes 10-20 seconds)"):
            try:
                # Configure the client
                genai.configure(api_key=google_api_key)
                
                # Use the Imagen model for image generation
                # Note: imagen-3.0-generate-001 is the model name
                model = genai.GenerativeModel('imagen-3.0-generate-001')
                
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "response_modalities": ["IMAGE"],
                    }
                )
                
                # Process the response
                if response.candidates and response.candidates[0].content.parts:
                    image_part = None
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_part = part
                            break
                    
                    if image_part and image_part.inline_data:
                        # Decode the image
                        img_data = base64.b64decode(image_part.inline_data.data)
                        img = Image.open(io.BytesIO(img_data))
                        
                        # Display the image
                        st.success("Here's your creation!")
                        st.image(img, caption=prompt, use_container_width=True)
                        
                        # Download button
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")
                        st.download_button(
                            label="📥 Download Image",
                            data=buffered.getvalue(),
                            file_name=f"mel_creation_{prompt[:20].replace(' ', '_')}.png",
                            mime="image/png"
                        )
                        
                        # Store in session for gallery (optional)
                        if 'gallery' not in st.session_state:
                            st.session_state.gallery = []
                        st.session_state.gallery.append({
                            'prompt': prompt,
                            'image': img
                        })
                        
                    else:
                        st.error("The model didn't return an image. Try a different prompt.")
                        st.json(response.candidates[0].content.parts)
                else:
                    st.error("Could not generate image. Response was empty.")
                    st.write(response)
                    
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                with st.expander("🔍 Technical Details"):
                    st.code(str(e))

# 6. Gallery (Optional - shows previous generations in this session)
# ---------------------------
if 'gallery' in st.session_state and len(st.session_state.gallery) > 1:
    st.divider()
    st.header("🖼️ This Session's Gallery")
    
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.gallery[:-1]):  # Exclude current
        with cols[idx % 3]:
            st.image(item['image'], caption=item['prompt'][:50] + "...", use_column_width=True)
