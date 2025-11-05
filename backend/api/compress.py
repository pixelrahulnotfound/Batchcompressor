from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import base64
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Batchresizer API")

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

        current_quality = quality
        min_quality = 20
        new_size = float('inf')
        compressed_bytes = None

        while new_size >= original_size and current_quality >= min_quality:
            output = BytesIO()
            img.save(output, format="JPEG", quality=current_quality, optimize=True)
            compressed_bytes = output.getvalue()
            new_size = len(compressed_bytes)

            if new_size >= original_size:
                current_quality -= 5
        
        if new_size >= original_size:
            new_size = original_size
            reduction = 0.0
            encoded = base64.b64encode(contents).decode("utf-8")
        else:
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
