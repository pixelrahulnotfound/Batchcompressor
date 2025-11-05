import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile
import requests
import base64

st.set_page_config(page_title="SnapShrink", page_icon="📸", layout="centered")

st.markdown(
    "<h1 style='text-align:center;color:#e4edec;margin-top:-40px;text-shadow:-3px 1px 5px #d3ccdb;'>SnapShrink – Batch Resizer</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h6 style='color:#d8e3db;font-size:18px;'>Resize and compress your images efficiently before sharing.</h6>",
    unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "Upload your files",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

preset = st.selectbox(
    "Select resize preset",
    ["keep original size", "Insta(1080x1080)", "Story (1080x1920)", "Twitter (1200x675)"]
)

quality = st.slider("Compressed quality", 60, 100, 85)

# 🧩 IMPORTANT: update this AFTER you deploy backend on Vercel
BACKEND_URL = "https://YOUR-VERCEL-BACKEND.vercel.app/compress"

if uploaded_files:
    st.info(f"{len(uploaded_files)} file(s) uploaded. Click below to compress.")

    if st.button("🧠 Optimise all images"):
        files_to_send = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]

        if preset == "Insta(1080x1080)": width, height = 1080, 1080
        elif preset == "Story (1080x1920)": width, height = 1080, 1920
        elif preset == "Twitter (1200x675)": width, height = 1200, 675
        else: width, height = None, None

        with st.spinner("Processing images..."):
            res = requests.post(
                BACKEND_URL,
                files=files_to_send,
                data={"width": width, "height": height, "quality": quality}
            )

        if res.status_code == 200:
            results = res.json()
            total_original = sum(r["originalSize"] for r in results)
            total_compressed = sum(r["newSize"] for r in results)
            reduction = 100 * (1 - total_compressed / total_original)

            st.success(f"✅ Done! Total size reduced by {reduction:.1f}%")

            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for r in results:
                    img_data = BytesIO(base64.b64decode(r["compressedImageBase64"]))
                    zipf.writestr(r["filename"], img_data.getvalue())

                    with st.expander(r["filename"]):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"Original: {r['originalSize']/1024:.1f} KB")
                        with col2:
                            st.write(f"Compressed: {r['newSize']/1024:.1f} KB")
                        st.image("data:image/jpeg;base64," + r["compressedImageBase64"], caption="Compressed")

            zip_buffer.seek(0)
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_buffer,
                file_name="snapshrink_batch.zip",
                mime="application/zip",
            )

        else:
            st.error("⚠️ Error: Could not reach backend or process images.")
