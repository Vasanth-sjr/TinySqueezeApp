import streamlit as st
from PIL import Image
import io
import tempfile
import subprocess
import os

st.set_page_config(page_title="TinySqueeze - Smart Compressor", page_icon="🧊")
st.markdown("<h1 style='text-align: center;'>🧊 TinySqueeze</h1>", unsafe_allow_html=True)
st.caption("Compress images or videos to an exact file size. Smart. Precise. Secure.")

with st.sidebar:
    st.header("About TinySqueeze")
    st.markdown("""
    📷 Compress `.jpg`, `.jpeg`, `.png` images  
    🎥 Compress `.mp4`, `.mov`, `.avi`, `.mkv` videos  
    🎯 Specify **exact file size target**  
    🔒 Secure — No files are saved  
    🚀 Smart compression with quality preservation  
    📄 Convert images to PDF (see sidebar navigation)
    """)

# -- File Upload --
uploaded_file = st.file_uploader("Upload image or video", type=["jpg", "jpeg", "png", "mp4", "mov", "mkv", "avi"])

def compress_image_exact(image_bytes, target_kb):
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ["RGBA", "P"]:
        img = img.convert("RGB")
    min_q, max_q = 5, 95
    best_result, best_diff, final_q = None, float("inf"), 95
    for _ in range(15):
        q = (min_q + max_q) // 2
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=q)
        size_kb = len(buffer.getvalue()) / 1024
        diff = abs(size_kb - target_kb)
        if diff < best_diff:
            best_result = buffer.getvalue()
            best_diff = diff
            final_q = q
        if size_kb > target_kb:
            max_q = q - 1
        else:
            min_q = q + 1
    if len(best_result) / 1024 < target_kb * 0.9:
        scale = 1.05
        while True:
            width, height = img.size
            img = img.resize((int(width * scale), int(height * scale)))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", optimize=True, quality=final_q)
            size_kb = len(buffer.getvalue()) / 1024
            if size_kb >= target_kb or scale > 2.0:
                break
            best_result = buffer.getvalue()
            scale += 0.05
    return best_result

def compress_video_to_target(video_data, target_mb):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_in:
        temp_in.write(video_data)
        input_path = temp_in.name
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration = float(result.stdout.decode().strip() or 1.0)
    target_bitrate = int(target_mb * 8388608 / duration)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_out:
        output_path = temp_out.name
    cmd = ["ffmpeg", "-i", input_path, "-b:v", f"{target_bitrate}",
           "-bufsize", f"{target_bitrate}", "-preset", "medium",
           "-c:a", "aac", "-b:a", "128k", "-y", output_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(output_path, "rb") as f:
        compressed_data = f.read()
    os.remove(input_path)
    os.remove(output_path)
    return compressed_data

if uploaded_file:
    file_type = uploaded_file.type
    if "image" in file_type:
        image_data = uploaded_file.read()
        original_kb = len(image_data) / 1024
        st.success(f"📦 Original file size: {original_kb:.2f} KB")
        st.image(image_data, caption="🖼️ Original Image", use_container_width=True)
        target_kb = st.slider("🎯 Target file size (KB)", 10, int(original_kb), int(original_kb * 0.7), step=1)
        if st.button("📉 Compress Image"):
            with st.spinner("Compressing image..."):
                compressed = compress_image_exact(image_data, target_kb)
                compressed_kb = len(compressed) / 1024
                st.markdown("#### 🧊 Compressed Image")
                st.image(compressed, use_container_width=True)
                st.write(f"Size: {compressed_kb:.2f} KB")
                st.write(f"💡 Saved: {100 - (compressed_kb/original_kb * 100):.1f}%")
                st.download_button("⬇️ Download Compressed Image", compressed, "compressed_image.jpg", "image/jpeg")

    elif "video" in file_type:
        video_data = uploaded_file.read()
        original_mb = len(video_data) / (1024 * 1024)
        st.success(f"📦 Original file size: {original_mb:.2f} MB")
        st.video(video_data)
        target_mb = st.slider("🎯 Target size (MB)", 1, int(original_mb), max(1, int(original_mb * 0.6)), step=1)
        if st.button("📉 Compress Video"):
            with st.spinner("Compressing video..."):
                compressed_data = compress_video_to_target(video_data, target_mb)
                compressed_mb = len(compressed_data) / (1024 * 1024)
                st.markdown("#### 🧊 Compressed Video")
                st.video(compressed_data)
                st.write(f"📉 Compressed Size: {compressed_mb:.2f} MB")
                st.write(f"💡 Saved: {100 - (compressed_mb/original_mb * 100):.1f}%")
                st.download_button("⬇️ Download Compressed Video", compressed_data, "compressed_video.mp4", "video/mp4")

st.markdown("---")
st.markdown("Made with ❤️ by **Vasanth** | [GitHub](https://github.com/Vasanth-sjr) | [Contact](mailto:sjrvasanth@gmail.com)")
