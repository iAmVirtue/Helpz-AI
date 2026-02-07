import google.generativeai as genai
import json

# --- PASTE YOUR KEY INSIDE THE QUOTES BELOW ---
API_KEY = "AIzaSyA2wCqUoE4DdDEBEr9sSF07qgsM7VaZPZE" 
# ----------------------------------------------
genai.configure(api_key=API_KEY)

def analyze_resume(resume_text, job_description):
    # CHANGED: We are now using the models explicitly listed in your terminal
    # Primary: Gemini 2.0 Flash (Fast & Powerful)
    # Backup: Gemini Flash Latest (Generic pointer to newest version)
    models_to_try = ['gemini-2.0-flash', 'gemini-flash-latest']
    
    for model_name in models_to_try:
        try:
            print(f"Attempting to use model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            You are a technical recruiter. Compare this resume to the job description.
            
            RESUME: {resume_text[:4000]}
            JOB DESC: {job_description[:4000]}
            
            Return ONLY raw JSON (no markdown) with these keys:
            "match_percentage" (int), "missing_keywords" (list), "critical_gaps" (list), "quick_fix" (string).
            """
            
            response = model.generate_content(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
            
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    return {
        "match_percentage": 0,
        "missing_keywords": ["Models Failed"],
        "critical_gaps": ["Could not connect to Gemini 2.0 or Latest"],
        "quick_fix": "Check check_models.py for valid model names."
    }