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

# Sirf 2 models (less memory)
models = {}

@app.on_event("startup")
async def load_models():
    print("Loading 2 AI Models...")
    models['rembg'] = new_session("u2net")
    models['inspyrenet'] = new_session("isnet-general-use")
    print("✅ Models loaded!")

@app.get("/")
def home():
    return {
        "app": "Background Remover API",
        "status": "running",
        "models_loaded": list(models.keys())
    }

@app.post("/remove-bg-ensemble")
async def remove_bg_ensemble(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    for model_name in ['inspyrenet', 'rembg']:
        try:
            result = remove(image_bytes, session=models[model_name])
            return Response(content=result, media_type="image/png")
        except:
            continue
    
    return {"error": "All models failed"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)