from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"app": "AI Background Remover", "status": "Running ✅"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    image_bytes = await file.read()
    input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    output_image = remove(input_image)
    output_bytes = io.BytesIO()
    output_image.save(output_bytes, format="PNG")
    return Response(content=output_bytes.getvalue(), media_type="image/png")

# This MUST be at the bottom
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)