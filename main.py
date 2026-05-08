from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import uvicorn
import os
import traceback

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home Route
@app.get("/")
def home():
    return {
        "app": "AI Background Remover",
        "status": "Running ✅"
    }

# Remove Background Route
@app.post("/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    try:
        # Read uploaded image
        image_bytes = await file.read()

        # Remove background
        output_bytes = remove(image_bytes)

        # Return PNG image
        return Response(
            content=output_bytes,
            media_type="image/png"
        )

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

# Run Server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )