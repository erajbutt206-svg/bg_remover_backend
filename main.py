from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from PIL import Image
import io
import os
from typing import Optional
import torch
from rembg import remove, new_session
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production mein specific domains daal sakte ho
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models cache
models = {}

@app.on_event("startup")
async def load_models():
    """Load all 3 models on startup"""
    logger.info("=" * 60)
    logger.info("🚀 Loading 3 AI Models for Production")
    logger.info("=" * 60)
    
    # Model 1: rembg (U²-Net)
    try:
        models['rembg'] = {
            'session': new_session("u2net"),
            'name': 'U²-Net'
        }
        logger.info("✅ Model 1/3: rembg (U²-Net) loaded")
    except Exception as e:
        logger.error(f"❌ rembg failed: {e}")
        models['rembg'] = None
    
    # Model 2: MODNet (silueta)
    try:
        models['modnet'] = {
            'session': new_session("silueta"),
            'name': 'MODNet'
        }
        logger.info("✅ Model 2/3: MODNet (silueta) loaded")
    except Exception as e:
        logger.error(f"❌ MODNet failed: {e}")
        models['modnet'] = None
    
    # Model 3: InSPyReNet
    try:
        models['inspyrenet'] = {
            'session': new_session("isnet-general-use"),
            'name': 'InSPyReNet'
        }
        logger.info("✅ Model 3/3: InSPyReNet loaded")
    except Exception as e:
        logger.error(f"❌ InSPyReNet failed: {e}")
        models['inspyrenet'] = None
    
    logger.info("=" * 60)
    loaded = sum(1 for m in models.values() if m is not None)
    logger.info(f"🎉 Production ready! {loaded}/3 models loaded")
    logger.info("=" * 60)

@app.get("/")
def home():
    """Health check endpoint"""
    loaded_models = [m['name'] for m in models.values() if m is not None]
    return {
        "app": "Background Remover API - Production",
        "version": "2.0.0",
        "status": "running",
        "models_loaded": loaded_models,
        "total_models": len(loaded_models),
        "environment": "production"
    }

@app.get("/health")
def health():
    """Simple health check for monitoring"""
    return {"status": "healthy"}

@app.post("/remove-bg-ensemble")
async def remove_bg_ensemble(file: UploadFile = File(...)):
    """Production endpoint - uses all 3 models"""
    image_bytes = await file.read()
    
    # Priority: InSPyReNet > rembg > MODNet
    order = ['inspyrenet', 'rembg', 'modnet']
    
    for model_name in order:
        model = models.get(model_name)
        if model is None:
            continue
        
        try:
            result = remove(image_bytes, session=model['session'])
            if result:
                logger.info(f"✅ Success with {model['name']}")
                return Response(content=result, media_type="image/png")
        except Exception as e:
            logger.error(f"❌ {model['name']} failed: {e}")
    
    return {"error": "All models failed", "status": 500}

@app.post("/remove-bg/{model_name}")
async def remove_bg_specific(model_name: str, file: UploadFile = File(...)):
    """Production endpoint - specific model"""
    image_bytes = await file.read()
    
    valid_models = ["rembg", "modnet", "inspyrenet"]
    if model_name not in valid_models:
        return {"error": f"Invalid model. Choose: {valid_models}"}
    
    model = models.get(model_name)
    if model is None:
        return {"error": f"Model {model_name} not available"}
    
    try:
        result = remove(image_bytes, session=model['session'])
        return Response(content=result, media_type="image/png")
    except Exception as e:
        return {"error": str(e), "status": 500}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)