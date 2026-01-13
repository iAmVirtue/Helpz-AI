from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from app.services.parser import extract_text_from_pdf
from app.services.ai_engine import analyze_resume
import os  # <--- IMPORT THIS

app = FastAPI()

# --- FIX START ---
# Get the absolute path of the current folder where main.py is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Point exactly to app/templates
templates_dir = os.path.join(BASE_DIR, "app", "templates")

# Initialize templates with the absolute path
templates = Jinja2Templates(directory=templates_dir)
# --- FIX END ---

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(
    request: Request, 
    resume: UploadFile = File(...), 
    job_desc: str = Form(...)
):
    resume_text = extract_text_from_pdf(resume.file)
    
    if not resume_text:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Could not read PDF."})
        
    analysis_result = analyze_resume(resume_text, job_desc)
    
    return templates.TemplateResponse("result.html", {
        "request": request, 
        "analysis": analysis_result
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)