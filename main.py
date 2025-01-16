from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from zip_processing import process_zip
from image_processing import process_image
from pathlib import Path
import json
import os
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), minConfidence: float = Form(...), minSize: int = Form(...), maxObjects: int = Form(...), animals: str = Form(...)):
    animals_dict = json.loads(animals)
    print(animals_dict)

    clases = parse_clases(animals_dict)

    if file.filename.endswith('.zip'):

        results = await process_zip(file, minConfidence, minSize, clases, maxObjects)
        if results:
            return {"results": results}
        else:
            raise HTTPException(status_code=200, detail="Nothing found")
        
    else:
        
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())

        processed_image_path = process_image(file_path, minConfidence, minSize, clases, maxObjects)

        if processed_image_path:
            return {"results": [processed_image_path]}
        else:
            raise HTTPException(status_code=200, detail="Nothing found")

@app.get("/get_image/{image_name}")
async def get_image(image_name: str):
    return FileResponse(PROCESSED_DIR / image_name)

def parse_clases(clases_dict):
    clases = []
    print(clases_dict)
    for class_name in clases_dict:
        if clases_dict[class_name] == 'true':
            clases.append(class_name)
    return clases