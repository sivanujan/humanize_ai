import os
import toml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.standard.pipeline import run_standard_pipeline

app = FastAPI(title="AI Humanizer Web App")

class HumanizeRequest(BaseModel):
    text: str

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount static files for HTML, CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.post("/api/humanize")
async def api_humanize(req: HumanizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    config_path = "config/config.toml"
    if not os.path.exists(config_path):
        raise HTTPException(status_code=500, detail="config.toml not found. Please create it from config.example.toml")
        
    try:
        cfg = toml.load(config_path)
        # Using standard pipeline
        result = run_standard_pipeline(req.text, cfg, target_lang="en")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
