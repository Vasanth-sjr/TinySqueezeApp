import streamlit as st
from PIL import Image
import io
import tempfile
import subprocess
import os
import fitz  # PyMuPDF
import json
from streamlit_lottie import st_lottie

# --- Page Config ---
st.set_page_config(page_title="TinySqueeze - Smart Compressor", layout="wide")

# --- Load Lottie Animation ---
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

celebration_anim = load_lottie_file("animations/celebration.json")

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 💡 TinySqueeze Tips")
    st.markdown("""
- 📷 Upload clear, high-quality images for better compression results.
- 🎥 Long videos may take a few extra seconds — hang tight!
- 📄 For scanned/image-heavy PDFs, compression works best.

🔐 Your files are processed locally. We never store or share your content.

🕒 Typical compression time: **3–5 seconds**.
    """)
    st.markdown("---")
    st.markdown("Need help? [Contact Me](mailto:sjrvasanth@gmail.com)")

# --- Title & Description ---
st.markdown("<h1 style='text-align: center;'>🧊TinySqueeze</h1>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; font-size: 18px; margin-bottom: 1rem;'>
  Compress or reduce the size of your <b>image</b>, <b>video</b>, or <b>PDF</b> in under <b>5 seconds</b>. <br>
  100% safe, secure, and smart compression — right in your browser.
</div>
""", unsafe_allow_html=True)

# --- File Type Selection ---
option = st.selectbox("🔘 What do you want to compress?", ("Image (JPG, PNG)", "Video (MP4, MOV)", "PDF"))

# ---------------- Compression Logic ---------------- #

def compress_image_exact(image_bytes, target_kb):
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ["RGBA", "P"]:
        img = img.convert("RGB")
    min_q, max_q = 5, 95
    best_result, best_diff = None, float("inf")
    for _ in range(15):
        q = (min_q + max_q) // 2
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=q)
        size_kb = len(buffer.getvalue()) / 1024
        diff = abs(size_kb - target_kb)
        if diff < best_diff:
            best_result = buffer.getvalue()
            best_diff = diff
        if size_kb > target_kb:
            max_q = q - 1
        else:
            min_q = q + 1
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

def compress_pdf_exact(pdf_data, target_kb):
    best_result = pdf_data
    best_diff = float("inf")
    for scale in [1.0, 0.9, 0.8, 0.7, 0.6]:
        for q in range(90, 4, -10):
            pdf_in = fitz.open(stream=pdf_data, filetype="pdf")
            out_pdf = fitz.open()
            for page in pdf_in:
                mat = fitz.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_img:
                    img.save(tmp_img.name, format="JPEG", quality=q)
                    tmp_img.seek(0)
                    img_data = tmp_img.read()
                rect = page.rect
                img_page = out_pdf.new_page(width=rect.width, height=rect.height)
                img_page.insert_image(rect, stream=img_data)
            buffer = io.BytesIO()
            out_pdf.save(buffer)
            buffer.seek(0)
            compressed = buffer.getvalue()
            size_kb = len(compressed) / 1024
            diff = abs(size_kb - target_kb)
            if diff < best_diff:
                best_result = compressed
                best_diff = diff
            pdf_in.close()
            out_pdf.close()
            if size_kb <= target_kb * 1.02:
                return compressed
    return best_result

# ---------------- UI Logic ---------------- #

def show_celebration():
    with st.container():
        st_lottie(
            celebration_anim,
            speed=1,
            reverse=False,
            loop=False,
            quality="high",
            height=300,
            key="celebration"
        )



if option == "Image (JPG, PNG)":
    uploaded_file = st.file_uploader("📄 Upload Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_data = uploaded_file.read()
        original_kb = len(image_data) / 1024
        st.success(f"📦 Original Image Size: {original_kb:.2f} KB")
        st.image(image_data, use_container_width=True)
        target_kb = st.slider("🎯 Target size (KB)", 10, int(original_kb), int(original_kb * 0.7))
        if st.button("📉 Compress Image"):
            with st.spinner("Compressing..."):
                result = compress_image_exact(image_data, target_kb)
                compressed_kb = len(result) / 1024
                st.image(result)
                st.write(f"📏 Size: {compressed_kb:.2f} KB")
                st.write(f"💡 Saved: {100 - (compressed_kb/original_kb * 100):.1f}%")
                show_celebration()
                st.download_button("⬇️ Download", result, "compressed_image.jpg", "image/jpeg")

elif option == "Video (MP4, MOV)":
    uploaded_file = st.file_uploader("📄 Upload Video", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_file:
        video_data = uploaded_file.read()
        original_mb = len(video_data) / (1024 * 1024)
        st.success(f"📦 Original Video Size: {original_mb:.2f} MB")
        st.video(video_data)
        target_mb = st.slider("🎯 Target size (MB)", 1, int(original_mb), max(1, int(original_mb * 0.6)))
        if st.button("📉 Compress Video"):
            with st.spinner("Compressing..."):
                result = compress_video_to_target(video_data, target_mb)
                compressed_mb = len(result) / (1024 * 1024)
                st.video(result)
                st.write(f"📏 Size: {compressed_mb:.2f} MB")
                st.write(f"💡 Saved: {100 - (compressed_mb/original_mb * 100):.1f}%")
                show_celebration()
                st.download_button("⬇️ Download", result, "compressed_video.mp4", "video/mp4")

elif option == "PDF":
    uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])
    if uploaded_file:
        pdf_data = uploaded_file.read()
        original_kb = len(pdf_data) / 1024
        st.success(f"📦 Original PDF Size: {original_kb:.2f} KB")
        target_kb = st.slider("🎯 Target size (KB)", 30, int(original_kb), int(original_kb * 0.8))
        if st.button("📉 Compress PDF"):
            with st.spinner("Compressing PDF..."):
                result = compress_pdf_exact(pdf_data, target_kb)
                compressed_kb = len(result) / 1024
                st.write(f"📏 Size: {compressed_kb:.2f} KB")
                st.write(f"💡 Saved: {100 - (compressed_kb/original_kb * 100):.1f}%")
                show_celebration()
                st.download_button("⬇️ Download", result, "compressed.pdf", "application/pdf")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ by **Vasanth** | [GitHub](https://github.com/Vasanth-sjr)")
