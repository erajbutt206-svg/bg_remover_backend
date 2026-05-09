from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove, new_session
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

models = {}

@app.on_event("startup")
async def load_models():
    print("Loading silueta model (lightweight)...")
    models['silueta'] = new_session("silueta")  # ~44 MB only!
    print("✅ Model loaded!")

@app.get("/")
def home():
    return {
        "app": "Background Remover API",
        "status": "running",
        "model": "silueta",
        "description": "Lightweight, fast processing"
    }

@app.post("/remove-bg-ensemble")
async def remove_bg_ensemble(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = remove(image_bytes, session=models['silueta'])
    return Response(content=result, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)