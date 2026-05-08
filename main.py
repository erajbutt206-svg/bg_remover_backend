from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import uvicorn
import os

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"app": "AI Background Remover", "status": "Running ✅"}

@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    image_bytes = await file.read()
    output_bytes = remove(image_bytes)
    return Response(content=output_bytes, media_type="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # HF Spaces ka port
    uvicorn.run(app, host="0.0.0.0", port=port)