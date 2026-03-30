# Interview Coach AI Engine - Gemini-powered mock interview chatbot

import json
import os
import uuid
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

# Role-specific interview configurations
ROLE_CONFIGS = {
    "software engineer": {
        "example_questions": [
            "Tell me about a complex system design problem you've solved",
            "How would you design a scalable social media feed?",
            "Explain your approach to debugging a memory leak",
            "How do you handle technical debt in your projects?",
        ],
        "focus_areas": ["system design", "coding ability", "problem-solving", "scalability"],
        "tips": "Focus on technical depth, explain your reasoning, and discuss tradeoffs."
    },
    "product manager": {
        "example_questions": [
            "How would you prioritize features for our mobile app?",
            "Tell me about a product decision you made and why",
            "How do you measure product success?",
            "How would you approach a market where we're not the leader?",
        ],
        "focus_areas": ["strategic thinking", "user empathy", "data-driven decisions", "communication"],
        "tips": "Demonstrate user-centric thinking, data-driven decisions, and clear communication."
    },
    "data scientist": {
        "example_questions": [
            "Walk me through your approach to a machine learning project",
            "How would you handle missing data in a dataset?",
            "Explain a statistical concept you use frequently",
            "How do you validate model performance?",
        ],
        "focus_areas": ["statistics", "ML algorithms", "data handling", "experimentation"],
        "tips": "Show deep understanding of ML concepts and discuss tradeoffs in your approaches."
    },
    "design": {
        "example_questions": [
            "Walk me through your design process for a new feature",
            "How do you balance aesthetics with usability?",
            "Tell me about a design decision you had to defend",
            "How do you conduct user research?",
        ],
        "focus_areas": ["user research", "design thinking", "visual communication", "problem-solving"],
        "tips": "Demonstrate user empathy, design thinking process, and attention to detail."
    },
}

def get_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())[:8]

def get_system_prompt(role, experience_level, conversation_history=None):
    """Create a role-specific system prompt for Gemini"""

    role_lower = role.lower()
    config = ROLE_CONFIGS.get(role_lower, ROLE_CONFIGS["software engineer"])

    history_context = ""
    if conversation_history and len(conversation_history) > 0:
        history_context = f"\nPrevious questions asked: {[msg.get('question') for msg in conversation_history if msg.get('role') == 'assistant' and msg.get('question')]}"

    examples_text = "\n".join([f"- {q}" for q in config['example_questions']])

    prompt = f"""You are an expert technical interviewer conducting a {role} interview.

Your role:
- Ask thoughtful, progressive interview questions
- Evaluate answers on 3 criteria: technical depth (0-10), relevance to {role} role (0-10), confidence level (0-10)
- Provide constructive feedback
- Guide the interview toward a score of 0-100

Candidate experience level: {experience_level}
Focus areas for {role}: {', '.join(config['focus_areas'])}

Interview tips: {config['tips']}

Example questions for this role:
{examples_text}{history_context}

When the candidate sends a message:
1. Respond conversationally
2. Provide feedback on their answer
3. Either ask a follow-up or move to the next question
4. Return ONLY valid JSON with keys: feedback, technical_depth (0-10), relevance (0-10), confidence (0-10), next_question

IMPORTANT: Always return valid JSON only. No markdown, no other text."""

    return prompt

def generate_interview_question(role, experience_level, conversation_history=None):
    """Generate the first interview question for a role"""

    if not API_KEY:
        return {
            "error": "GOOGLE_API_KEY is not set",
            "question": "Unable to initialize interview. Please check API configuration."
        }

    role_lower = role.lower()
    config = ROLE_CONFIGS.get(role_lower, ROLE_CONFIGS["software engineer"])
    role_confirmed = role_lower if role_lower in ROLE_CONFIGS else "software engineer"

    system_prompt = get_system_prompt(role_confirmed, experience_level, conversation_history)

    user_message = f"Start the interview. Ask me your first question for a {role_confirmed} position. I have {experience_level} of experience."

    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']

    for model_name in models_to_try:
        try:
            print(f"Attempting to generate question with model: {model_name}...")
            client = genai.Client(api_key=API_KEY)

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
                    {"role": "user", "parts": [{"text": user_message}]}
                ],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )

            result = json.loads(response.text)
            result['role_confirmed'] = role_confirmed
            result['tips'] = config['tips']
            return result

        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    return {
        "error": "Failed to generate question",
        "question": "Sorry, I'm having trouble generating questions. Please try again.",
        "role_confirmed": role_confirmed
    }

def evaluate_answer(question, user_answer, role, experience_level, conversation_history=None):
    """Evaluate the user's answer to an interview question"""

    if not API_KEY:
        return {
            "error": "GOOGLE_API_KEY is not set",
            "feedback": "Unable to evaluate. Please check API configuration."
        }

    if not user_answer.strip():
        return {
            "feedback": "Please provide an answer to continue.",
            "technical_depth": 0,
            "relevance": 0,
            "confidence": 0,
            "next_question": question
        }

    role_lower = role.lower()
    system_prompt = get_system_prompt(role_lower, experience_level, conversation_history)

    user_message = f"Question: {question}\n\nCandidate Answer: {user_answer[:2000]}\n\nEvaluate this answer and ask a follow-up or next question."

    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']

    for model_name in models_to_try:
        try:
            print(f"Attempting to evaluate answer with model: {model_name}...")
            client = genai.Client(api_key=API_KEY)

            response = client.models.generate_content(
                model=model_name,
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt}]},
                    {"role": "user", "parts": [{"text": user_message}]}
                ],
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )

            return json.loads(response.text)

        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    return {
        "error": "Failed to evaluate answer",
        "feedback": "Sorry, I'm having trouble evaluating your answer. Please try again.",
        "technical_depth": 5,
        "relevance": 5,
        "confidence": 5,
        "next_question": question
    }

def calculate_interview_score(evaluations):
    """Calculate overall interview score and aggregates from evaluation list"""

    if not evaluations or len(evaluations) == 0:
        return {
            "overall_score": 0,
            "avg_technical_depth": 0,
            "avg_relevance": 0,
            "avg_confidence": 0,
            "total_questions": 0
        }

    technical_depths = [e.get('technical_depth', 5) for e in evaluations if isinstance(e.get('technical_depth'), int)]
    relevances = [e.get('relevance', 5) for e in evaluations if isinstance(e.get('relevance'), int)]
    confidences = [e.get('confidence', 5) for e in evaluations if isinstance(e.get('confidence'), int)]

    avg_technical = sum(technical_depths) / len(technical_depths) if technical_depths else 5
    avg_relevance = sum(relevances) / len(relevances) if relevances else 5
    avg_confidence = sum(confidences) / len(confidences) if confidences else 5

    # Calculate overall score (0-100) as average of the three metrics
    overall_score = int((avg_technical + avg_relevance + avg_confidence) / 3 * 10)
    overall_score = min(100, max(0, overall_score))

    return {
        "overall_score": overall_score,
        "avg_technical_depth": round(avg_technical, 1),
        "avg_relevance": round(avg_relevance, 1),
        "avg_confidence": round(avg_confidence, 1),
        "total_questions": len(evaluations)
    }

def generate_summary_feedback(role, evaluations, overall_score):
    """Generate summary feedback and recommendations"""

    if not evaluations or len(evaluations) == 0:
        return {
            "strengths": ["Completed initial setup"],
            "improvements": ["Complete an interview to receive feedback"]
        }

    # Identify strengths and weaknesses based on averages
    role_config = ROLE_CONFIGS.get(role.lower(), ROLE_CONFIGS["software engineer"])

    technical_avg = sum([e.get('technical_depth', 5) for e in evaluations]) / len(evaluations)
    relevance_avg = sum([e.get('relevance', 5) for e in evaluations]) / len(evaluations)
    confidence_avg = sum([e.get('confidence', 5) for e in evaluations]) / len(evaluations)

    strengths = []
    improvements = []

    if technical_avg >= 7:
        strengths.append("Strong technical understanding and depth")
    else:
        improvements.append("Work on deepening technical knowledge and explanations")

    if relevance_avg >= 7:
        strengths.append("Answers well-aligned with role requirements")
    else:
        improvements.append("Better connect your answers to specific role requirements")

    if confidence_avg >= 7:
        strengths.append("Clear and confident communication style")
    else:
        improvements.append("Build confidence in your delivery and communication")

    if not strengths:
        strengths = ["Continue practicing to improve across all areas"]

    if not improvements:
        improvements = ["Maintain your strong performance in future interviews"]

    return {
        "strengths": strengths[:2],
        "improvements": improvements[:2]
    }
