import streamlit as st
from moviepy.editor import VideoFileClip
import os
import io
import tempfile

# --- Page Setup ---
st.set_page_config(page_title="TinySqueeze - Video Compressor", page_icon="🎥")

# --- Header ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png", width=120)
    st.markdown("<h1 style='text-align: center;'>TinySqueeze</h1>", unsafe_allow_html=True)
    st.caption("Compress your videos instantly. Fast, free, and secure.")

# --- Sidebar ---
with st.sidebar:
    st.header("About TinySqueeze")
    st.markdown("""
    🎥 Upload `.mp4` video files  
    🎛️ Choose your compression bitrate  
    📉 Download reduced file instantly  
    🔒 Your files are not saved or stored.
    """)

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your video", type=["mp4"])

# --- Bitrate Slider ---
bitrate = st.slider("Select bitrate for compression (lower = smaller size)", 300, 3000, 800, step=100)
bitrate_str = f"{bitrate}k"

# --- Compression Logic ---
if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("Compress Video"):
        with st.spinner("Compressing video..."):
            try:
                # Save uploaded file to a temp location
                temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_input.write(uploaded_file.read())
                temp_input.close()

                # Output path
                temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_output.close()

                # Load and compress using moviepy
                clip = VideoFileClip(temp_input.name)
                clip.write_videofile(
                    temp_output.name,
                    codec="libx264",
                    audio_codec="aac",
                    bitrate=bitrate_str,
                    threads=4,
                    logger=None  # Disable verbose logging
                )

                # Read compressed file
                with open(temp_output.name, "rb") as f:
                    compressed_data = f.read()

                # Size Comparison
                original_size = len(uploaded_file.getvalue()) / (1024 * 1024)
                compressed_size = len(compressed_data) / (1024 * 1024)
                st.success(f"✅ Compression complete! 🎉")
                st.write(f"📦 **Original Size:** {original_size:.2f} MB")
                st.write(f"📉 **Compressed Size:** {compressed_size:.2f} MB")
                st.write(f"💡 Saved: {100 - (compressed_size / original_size * 100):.1f}%")

                # Download button
                st.download_button(
                    label="⬇️ Download Compressed Video",
                    data=compressed_data,
                    file_name="compressed_video.mp4",
                    mime="video/mp4"
                )

                # Clean up
                os.remove(temp_input.name)
                os.remove(temp_output.name)

            except Exception as e:
                st.error(f"Compression failed: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by **Vasanth** | [GitHub](https://github.com/Vasanth-sjr) | [Contact](mailto:sjrvasanth@gmail.com)")
