import streamlit as st
from PIL import Image
import io
import os
import subprocess
import uuid

# --- Page Setup ---
st.set_page_config(page_title="TinySqueeze - Image & Video Compressor", page_icon="🧊")

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("assets/logo.png", width=120)
    except:
        st.warning("Logo not found in assets/logo.png")
    st.markdown("<h1 style='text-align: center;'>TinySqueeze</h1>", unsafe_allow_html=True)
    st.caption("Compress your images or videos instantly. Fast, free, and secure.")

# --- Sidebar ---
with st.sidebar:
    st.header("About TinySqueeze")
    st.markdown("""
    📷 Upload `.jpg`, `.png` or `.mp4` files  
    🎛️ Choose your compression quality  
    📉 Download reduced file instantly  
    🔒 Files are not saved or stored.
    """)

# --- File Upload ---
uploaded_file = st.file_uploader("Upload an image or video", type=["jpg", "jpeg", "png", "mp4"])

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    # --- Image Compression ---
    if file_ext in ["jpg", "jpeg", "png"]:
        st.image(uploaded_file, caption="Original Image", use_container_width=True)
        quality = st.slider("Select image compression quality", 10, 95, 60)

        if st.button("Compress Image"):
            with st.spinner("Compressing image..."):
                try:
                    image = Image.open(uploaded_file)
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")

                    compressed_io = io.BytesIO()
                    image.save(compressed_io, format="JPEG", optimize=True, quality=quality)
                    compressed_io.seek(0)

                    original_kb = len(uploaded_file.getvalue()) / 1024
                    compressed_kb = len(compressed_io.getvalue()) / 1024
                    percent_saved = 100 - (compressed_kb / original_kb * 100)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Original")
                        st.image(uploaded_file, use_container_width=True)
                        st.write(f"{original_kb:.2f} KB")

                    with col2:
                        st.markdown("#### Compressed")
                        st.image(compressed_io, use_container_width=True)
                        st.write(f"{compressed_kb:.2f} KB")
                        st.success(f"Saved: {percent_saved:.1f}%")

                    st.download_button(
                        label="⬇️ Download Compressed Image",
                        data=compressed_io,
                        file_name=f"{uploaded_file.name.split('.')[0]}_compressed.jpg",
                        mime="image/jpeg"
                    )
                except Exception as e:
                    st.error(f"Image compression failed: {e}")

    # --- Video Compression ---
    elif file_ext == "mp4":
        st.video(uploaded_file)
        crf = st.slider("Select video compression level (CRF)", 18, 40, 28)
        st.caption("Lower CRF = better quality, higher size")

        if st.button("Compress Video"):
            with st.spinner("Compressing video..."):
                try:
                    temp_input_path = f"temp_input_{uuid.uuid4()}.mp4"
                    temp_output_path = f"temp_output_{uuid.uuid4()}.mp4"

                    # Save uploaded video to disk
                    with open(temp_input_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # FFmpeg compression using CRF (Constant Rate Factor)
                    command = [
                        "ffmpeg", "-i", temp_input_path,
                        "-vcodec", "libx264", "-crf", str(crf),
                        "-preset", "fast",
                        "-y", temp_output_path
                    ]
                    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    with open(temp_output_path, "rb") as f:
                        compressed_video = f.read()

                    original_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                    compressed_mb = len(compressed_video) / (1024 * 1024)
                    saved = 100 - (compressed_mb / original_mb * 100)

                    st.video(compressed_video)
                    st.write(f"🎞️ Original: {original_mb:.2f} MB")
                    st.write(f"🧊 Compressed: {compressed_mb:.2f} MB")
                    st.success(f"Saved: {saved:.1f}%")

                    st.download_button(
                        label="⬇️ Download Compressed Video",
                        data=compressed_video,
                        file_name=f"{uploaded_file.name.split('.')[0]}_compressed.mp4",
                        mime="video/mp4"
                    )

                    # Clean up temp files
                    os.remove(temp_input_path)
                    os.remove(temp_output_path)

                except Exception as e:
                    st.error(f"Video compression failed: {e}")

# --- Footer ---
st.markdown("---")
st.markdown(
    "Made with ❤️ by **Vasanth** | [GitHub](https://github.com/Vasanth-sjr) | [Contact](mailto:sjrvasanth@gmail.com)"
)
