import streamlit as st
from PIL import Image
import os
import io

# --- Page Setup ---
st.set_page_config(page_title="TinySqueeze - Image Compressor", page_icon="🧊")

# --- Centered Header with Logo ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("assets/logo.png", width=120)
    except:
        st.warning("Logo not found in assets/logo.png")
    st.markdown("<h1 style='text-align: center;'>TinySqueeze</h1>", unsafe_allow_html=True)
    st.caption("Compress your images instantly. Fast, free, and secure.")

# --- Sidebar ---
with st.sidebar:
    st.header("About TinySqueeze")
    st.markdown("""
    📷 Upload `.jpg`, `.png` files  
    🎛️ Choose your compression quality  
    📉 Download reduced file instantly  
    🔒 Your files are not saved or stored.
    """)

# --- Title & Caption ---
st.title("🧊 TinySqueeze")
st.caption("Compress your images instantly. Fast, free, and secure.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your image", type=["jpg", "jpeg", "png"])

# --- Compression Quality Slider ---
quality = st.slider("Select compression quality", 10, 95, 60)

# --- Image Handling & Compression ---
if uploaded_file is not None:
    st.image(uploaded_file, caption="Original Image", use_container_width=True)

    if st.button("Compress"):
        with st.spinner("Compressing..."):
            try:
                # Load image
                image = Image.open(uploaded_file)

                # Convert RGBA or P mode to RGB
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")

                # Compress image to memory
                compressed_io = io.BytesIO()
                image.save(compressed_io, format="JPEG", optimize=True, quality=quality)
                compressed_io.seek(0)

                # File Size Comparison
                original_kb = len(uploaded_file.getvalue()) / 1024
                compressed_kb = len(compressed_io.getvalue()) / 1024

                st.success("✅ Compression complete!")
                st.image(compressed_io, caption="Compressed Image", use_container_width=True)
                st.write(f"📦 **Original Size:** {original_kb:.2f} KB")
                st.write(f"📉 **Compressed Size:** {compressed_kb:.2f} KB")

                # Dynamic file name
                filename = os.path.splitext(uploaded_file.name)[0]
                download_name = f"{filename}_compressed.jpg"

                # Download button
                st.download_button(
                    label="⬇️ Download Compressed Image",
                    data=compressed_io,
                    file_name=download_name,
                    mime="image/jpeg"
                )

            except Exception as e:
                st.error(f"Compression failed: {e}")

# --- Footer ---
st.markdown("---")
st.markdown(
    "Made with ❤️ by **Vasanth** | [GitHub](https://github.com/Vasanth-sjr) | [Contact](mailto:your@email.com)"
)
