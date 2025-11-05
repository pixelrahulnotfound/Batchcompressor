from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import base64

app = FastAPI(title="SnapShrink API")

@app.post("/compress")
async def compress_images(
    files: list[UploadFile] = File(...),
    width: int = Form(None),
    height: int = Form(None),
    quality: int = Form(85)
):
    results = []

    for file in files:
        contents = await file.read()
        original_size = len(contents)

        img = Image.open(BytesIO(contents))
        img = img.convert("RGB")

        if width and height:
            img = img.resize((width, height))

        out_buffer = BytesIO()
        img.save(out_buffer, format="JPEG", quality=quality, optimize=True)
        compressed_bytes = out_buffer.getvalue()

        new_size = len(compressed_bytes)
        reduction = round(100 * (1 - new_size / original_size), 2)

        encoded_img = base64.b64encode(compressed_bytes).decode("utf-8")

        results.append({
            "filename": file.filename,
            "originalSize": original_size,
            "newSize": new_size,
            "reductionPercent": reduction,
            "compressedImageBase64": encoded_img
        })

    return JSONResponse(content=results)
