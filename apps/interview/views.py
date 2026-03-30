from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import traceback

from .services import (
    get_session_id,
    generate_interview_question,
    evaluate_answer,
    calculate_interview_score,
    generate_summary_feedback
)


def interview_coach(request):
    """Render the Interview Coach chatbot page"""
    return render(request, "interview/coach.html")


@csrf_exempt
def chat_start(request):
    """Initialize an interview session"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            role = data.get("role", "Software Engineer").strip()
            company = data.get("company", "").strip()
            experience_level = data.get("experience_level", "Entry Level").strip()

            if not role:
                return JsonResponse({"error": "Role is required"}, status=400)

            session_id = get_session_id()

            # Generate first question
            first_question_response = generate_interview_question(role, experience_level)

            return JsonResponse({
                "session_id": session_id,
                "question": first_question_response.get("next_question") or first_question_response.get("question"),
                "role_confirmed": first_question_response.get("role_confirmed", role.lower()),
                "company": company,
                "experience_level": experience_level,
                "tips": first_question_response.get("tips", ""),
                "error": first_question_response.get("error")
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"Error in chat_start: {str(e)}")
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def chat_message(request):
    """Process a chat message and return evaluation + next question"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id", "").strip()
            user_message = data.get("message", "").strip()
            role = data.get("role", "Software Engineer").strip()
            experience_level = data.get("experience_level", "Entry Level").strip()
            current_question = data.get("current_question", "").strip()

            if not session_id or not user_message:
                return JsonResponse({"error": "Session ID and message are required"}, status=400)

            if not current_question:
                return JsonResponse({"error": "Current question is required"}, status=400)

            # Evaluate the answer
            evaluation = evaluate_answer(
                question=current_question,
                user_answer=user_message,
                role=role,
                experience_level=experience_level
            )

            return JsonResponse({
                "feedback": evaluation.get("feedback", ""),
                "technical_depth": evaluation.get("technical_depth", 5),
                "relevance": evaluation.get("relevance", 5),
                "confidence": evaluation.get("confidence", 5),
                "next_question": evaluation.get("next_question"),
                "error": evaluation.get("error")
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"Error in chat_message: {str(e)}")
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def chat_evaluate(request):
    """Evaluate the interview and return final score"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id", "").strip()
            evaluations = data.get("evaluations", [])
            role = data.get("role", "Software Engineer").strip()

            if not session_id:
                return JsonResponse({"error": "Session ID is required"}, status=400)

            # Calculate overall score
            score_data = calculate_interview_score(evaluations)

            # Generate summary feedback
            summary = generate_summary_feedback(role, evaluations, score_data["overall_score"])

            return JsonResponse({
                "overall_score": score_data["overall_score"],
                "avg_technical_depth": score_data["avg_technical_depth"],
                "avg_relevance": score_data["avg_relevance"],
                "avg_confidence": score_data["avg_confidence"],
                "total_questions": score_data["total_questions"],
                "strengths": summary["strengths"],
                "improvements": summary["improvements"]
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"Error in chat_evaluate: {str(e)}")
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
