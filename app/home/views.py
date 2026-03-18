from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from app.engine.services.parser import extract_text_from_pdf
from app.engine.services.ai_engine import analyze_resume
import json
import traceback
import os
from django.conf import settings
from google import genai

def home(request):
    return render(request, "pages/index.html")

def about(request):
    return render(request, "pages/about_me.html")

@ensure_csrf_cookie
def explore(request):
    return render(request, "pages/explore.html")

@csrf_exempt
def generate_explore_graph(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get("query", "Software Engineering")

            models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']

            prompt = (
                f'You are a knowledge graph generator. The user searched for: "{query}".\n\n'
                'Create a rich connected knowledge graph. Return ONLY a valid JSON object with this EXACT structure:\n'
                '{\n'
                '  "center": "<topic>",\n'
                '  "nodes": [\n'
                '    {"id": "center", "label": "<topic>", "description": "2-3 sentence overview", "relevance": 1.0, "category": "core"},\n'
                '    {"id": "node_1", "label": "Related Concept", "description": "2-3 sentences", "relevance": 0.9, "category": "secondary"},\n'
                '    {"id": "node_2", "label": "Outer Concept", "description": "2-3 sentences", "relevance": 0.4, "category": "outer"}\n'
                '  ],\n'
                '  "links": [\n'
                '    {"source": "center", "target": "node_1", "strength": 0.9},\n'
                '    {"source": "center", "target": "node_2", "strength": 0.4}\n'
                '  ]\n'
                '}\n\n'
                'Rules:\n'
                '- Include EXACTLY 1 node with id "center" and relevance 1.0 and category "core". Its label should be the search topic.\n'
                '- Include 12 to 18 secondary nodes (relevance 0.7-0.95, category "secondary") — these are core subtopics.\n'
                '- Include 20 to 30 outer nodes (relevance 0.3-0.65, category "outer") — broader related ideas.\n'
                '- strength values between 0.3 and 1.0\n'
                '- All link source/target must reference valid node ids\n'
                '- The center node should link to all secondary nodes\n'
                '- Create MANY interconnections (links) between secondary and outer nodes to form a dense universe-like web.\n'
                f'- Replace <topic> with: {query}\n'
                '- Descriptions must be 2-3 insightful sentences explaining real connections.'
            )

            # Ensure API Key is configured specifically for this view
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return JsonResponse({"error": "GOOGLE_API_KEY environment variable is missing."}, status=500)

            client = genai.Client(api_key=api_key)

            last_error = "Unknown error"
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=genai.types.GenerateContentConfig(
                            response_mime_type="application/json",
                        )
                    )
                    
                    # Defensively clean the text in case Gemini ignored mime_type and wrapped it in markdown
                    clean_text = response.text.strip()
                    if clean_text.startswith("```"):
                        clean_text = clean_text.replace("```json", "").replace("```", "").strip()

                    graph_data = json.loads(clean_text)
                    return JsonResponse(graph_data)
                except Exception as e:
                    last_error = str(e)
                    print(f"Model {model_name} failed graph gen: {last_error}")
                    traceback.print_exc()
                    continue

            return JsonResponse({"error": f"Failed to generate graph. Last model error: {last_error}"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def analyze(request):
    if request.method == "POST":
        resume = request.FILES.get("resume")
        job_desc = request.POST.get("job_desc")
        
        if not resume or not job_desc:
            return JsonResponse({"error": "Missing resume or job description."}, status=400)
            
        try:
            resume_text = extract_text_from_pdf(resume.file)
        except Exception as e:
            return JsonResponse({"error": f"Parser Error: {str(e)}"}, status=400)
            
        if not resume_text:
            return JsonResponse({"error": "Could not extract text from PDF."}, status=400)
            
        analysis_result = analyze_resume(resume_text, job_desc)
        missing_skills = analysis_result.get('missing_keywords', [])
        
        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']
        plan_data = None
        last_error = None

        if missing_skills:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                plan_data = {"error": "GOOGLE_API_KEY is missing.", "interview_questions": [], "micro_project": []}
            else:
                client = genai.Client(api_key=api_key)
                for model_name in models_to_try:
                    try:
                        prompt = f"""
                        You are a technical mentor. The user is missing the following skills based on their resume compared to a job description: {', '.join(missing_skills)}.
                        
                        Return ONLY a strict JSON object with two keys:
                        "interview_questions": A list of 5 dictionaries, each containing a "question" (testing a missing skill) and an "ideal_answer".
                        "micro_project": A list of dictionaries each containing a "title" and a "desc" (a quick 1 sentence task description), output EXACTLY 3 objects here.
                        """
                        
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=genai.types.GenerateContentConfig(
                                response_mime_type="application/json",
                            )
                        )
                        plan_data = json.loads(response.text)
                        
                        # Defensively handle wrapping if it returned markdown
                        if isinstance(plan_data, str) and plan_data.startswith("```"):
                             plan_data = json.loads(plan_data.replace("```json", "").replace("```", "").strip())

                        if "checklist" in plan_data.get("micro_project", {}) and isinstance(plan_data["micro_project"], dict):
                            # Convert legacy format to list format
                            arr = []
                            for step in plan_data["micro_project"]["checklist"]:
                                arr.append({"title": plan_data["micro_project"]["title"], "desc": step})
                            plan_data["micro_project"] = arr
                        break
                    except Exception as e:
                        print(f"Model {model_name} failed: {e}")
                        last_error = str(e)
                        continue
                
        if not plan_data:
            plan_data = {
                "error": f"Failed to connect to accurate Gemini API: {last_error}", 
                "interview_questions": [], 
                "micro_project": []
            }

        return JsonResponse({
            "analysis": analysis_result,
            "resume_text": resume_text,
            "plan": plan_data
        })
        
    return JsonResponse({"error": "Invalid request method"}, status=405)
