from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from PIL import Image
import io

app = FastAPI()

# CORS for Flutter app
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
    # Image receive karo
    image_bytes = await file.read()
    
    # AI background remove
    input_image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    output_image = remove(input_image)
    
    # PNG return karo
    output_bytes = io.BytesIO()
    output_image.save(output_bytes, format="PNG")
    
    return Response(content=output_bytes.getvalue(), media_type="image/png")