from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import base64
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SnapShrink API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        img = Image.open(BytesIO(contents)).convert("RGB")

        if width and height:
            img = img.resize((width, height))

        output = BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True)
        compressed_bytes = output.getvalue()

        new_size = len(compressed_bytes)
        reduction = round(100 * (1 - new_size / original_size), 2)
        encoded = base64.b64encode(compressed_bytes).decode("utf-8")

        results.append({
            "filename": file.filename,
            "originalSize": original_size,
            "newSize": new_size,
            "reductionPercent": reduction,
            "compressedImageBase64": encoded
        })
    return JSONResponse(content=results)
