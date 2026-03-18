# This ai_engine.py main logic of ai resume analyzer and gap finder

import json
import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

# --- Load API Key from environment ---
API_KEY = os.getenv("GOOGLE_API_KEY") 
# ----------------------------------------------

def analyze_resume(resume_text, job_description):
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']
    
    if not API_KEY:
        return {
            "match_percentage": 0,
            "missing_keywords": ["Error"],
            "critical_gaps": ["GOOGLE_API_KEY is not set in environment."],
            "quick_fix": ["Please add your Gemini API key to .env"]
        }

    client = genai.Client(api_key=API_KEY)
    
    for model_name in models_to_try:
        try:
            print(f"Attempting to use model: {model_name}...")
            
            prompt = f"""
            You are a technical recruiter. Compare this resume to the job description.
            
            RESUME: {resume_text[:4000]}
            JOB DESC: {job_description[:4000]}
            
            Return ONLY raw JSON with these exact keys:
            "match_percentage" (integer from 0 to 100),
            "missing_keywords" (list of strings),
            "critical_gaps" (list of strings),
            "quick_fix" (list of strings with actionable advice bullet points).
            """
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
            
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue


    return {
        "match_percentage": 0,
        "missing_keywords": ["Models Failed"],
        "critical_gaps": ["Could not connect to accurate Gemini API using available models."],
        "quick_fix": ["Check check_models.py for valid model names and GOOGLE_API_KEY environment variable."]
    }