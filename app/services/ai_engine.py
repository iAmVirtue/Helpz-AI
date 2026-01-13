import google.generativeai as genai
import os
import json

# Setup API Key (Make sure to set this in your environment or replace directly)
API_KEY = os.getenv("GOOGLE_API_KEY") 
genai.configure(api_key=API_KEY)

def analyze_resume(resume_text, job_description):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # The Prompt
    prompt = f"""
    You are a strict technical recruiter. Analyze this resume against the job description.
    
    RESUME TEXT:
    {resume_text}
    
    JOB DESCRIPTION:
    {job_description}
    
    Output strictly in JSON format with these keys: 
    - "match_percentage": (integer 0-100)
    - "missing_keywords": (list of strings)
    - "critical_gaps": (list of strings, focusing on hard skills)
    - "quick_fix": (one actionable tip to improve the resume immediately)
    
    Do not add Markdown formatting (like ```json). Just return the raw JSON string.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up potential markdown formatting from AI
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "match_percentage": 0,
            "missing_keywords": ["Error generating analysis"],
            "critical_gaps": ["Could not process request"],
            "quick_fix": "Try again later."
        }