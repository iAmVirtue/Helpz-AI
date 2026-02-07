import sys
import os
import uvicorn
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates

# 1. Fix Path to see 'app' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Import Logic
try:
    from app.services.parser import extract_text_from_pdf
    from app.services.ai_engine import analyze_resume
except ImportError as e:
    # Fallback if you are running inside app folder by mistake
    try:
        from services.parser import extract_text_from_pdf
        from services.ai_engine import analyze_resume
    except ImportError:
        print(f"CRITICAL IMPORT ERROR: {e}")
        sys.exit(1)

app = FastAPI()

# 3. Fix Template Directory (Points to app/templates)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "app", "templates")

# Verify path exists to avoid confusion
if not os.path.exists(templates_dir):
    print(f"WARNING: Template folder not found at {templates_dir}")
    print("Checking root folder...")
    templates_dir = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=templates_dir)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(
    request: Request, 
    resume: UploadFile = File(...), 
    job_desc: str = Form(...)
):
    try:
        resume_text = extract_text_from_pdf(resume.file)
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": f"Parser Error: {str(e)}"})
    
    if not resume_text:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Could not extract text from PDF."})
        
    analysis_result = analyze_resume(resume_text, job_desc)
    
    # CHANGED: Updated to "results.html" (Plural) to match your file
    return templates.TemplateResponse("results.html", {
        "request": request, 
        "analysis": analysis_result
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)