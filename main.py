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

# Global models dictionary
models = {}

@app.on_event("startup")
async def load_models():
    """Load isnet-general-use model on startup"""
    print("=" * 50)
    print("Loading isnet-general-use model...")
    print("(Best quality - high accuracy)")
    print("=" * 50)
    
    try:
        # ✅ isnet-general-use model
        models['isnet'] = new_session("isnet-general-use")
        print("✅ Model loaded successfully!")
        print(f"   Model: isnet-general-use")
        print("   Best for: Complex edges, hair, fine details")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        models['isnet'] = None
    
    print("=" * 50)

@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "app": "Background Remover API",
        "status": "running",
        "model": "isnet-general-use",
        "description": "Best quality background removal",
        "models_loaded": ["isnet-general-use"] if models.get('isnet') else []
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/remove-bg-ensemble")
async def remove_bg_ensemble(file: UploadFile = File(...)):
    """Remove background using isnet-general-use model"""
    if models.get('isnet') is None:
        return {"error": "Model not loaded"}, 500
    
    try:
        image_bytes = await file.read()
        result = remove(image_bytes, session=models['isnet'])
        return Response(content=result, media_type="image/png")
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500

@app.post("/remove-bg/{model_name}")
async def remove_bg_specific(model_name: str, file: UploadFile = File(...)):
    """Use specific model (isnet-general-use only now)"""
    if model_name not in ["isnet", "isnet-general-use"]:
        return {"error": f"Model {model_name} not available. Use 'isnet'"}, 404
    
    if models.get('isnet') is None:
        return {"error": "Model not loaded"}, 500
    
    try:
        image_bytes = await file.read()
        result = remove(image_bytes, session=models['isnet'])
        return Response(content=result, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)