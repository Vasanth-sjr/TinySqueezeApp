import streamlit as st
from PIL import Image
import io

# --- Page Config ---
st.set_page_config(page_title="TinySqueeze - Image to PDF", page_icon="📄")

st.markdown("<h1 style='text-align: center;'>📄 Image to PDF</h1>", unsafe_allow_html=True)
st.caption("Capture or upload images and convert them into a single PDF. Simple. Fast. Free.")

# --- Sidebar ---
with st.sidebar:
    st.header("📚 How it Works")
    st.markdown("""
    - 📷 Capture photos using your phone camera  
    - 🖼️ Upload one or more existing images  
    - 📄 Combine all into one PDF  
    - 🔒 Your data never leaves your device
    """)

# --- Upload or Capture ---
st.subheader("Step 1: Upload or Take Photos")

uploaded_images = st.file_uploader(
    "Upload images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

camera_image = st.camera_input("Or take a photo")

# --- Process Images ---
image_list = []

if uploaded_images:
    for file in uploaded_images:
        img = Image.open(file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        image_list.append(img)

if camera_image:
    img = Image.open(camera_image)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    image_list.append(img)

# --- Convert to PDF ---
if image_list:
    st.success(f"✅ {len(image_list)} image(s) ready to convert.")
    if st.button("📄 Convert to PDF"):
        with st.spinner("Generating PDF..."):
            pdf_io = io.BytesIO()
            image_list[0].save(
                pdf_io, format="PDF", save_all=True, append_images=image_list[1:]
            )
            pdf_io.seek(0)

            st.success("🎉 PDF is ready!")
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_io,
                file_name="converted_images.pdf",
                mime="application/pdf"
            )
else:
    st.info("Upload or capture at least one image to proceed.")
