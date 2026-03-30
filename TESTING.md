# RoleReady-AI Testing Guide

## Setup Requirements

Before running tests, ensure dependencies are installed:

```bash
# Create virtual environment (if not done)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_DEBUG=True
export GOOGLE_API_KEY=your_key_here  # Optional for API tests
```

## Running Local Dev Server

```bash
python3 manage.py runserver 0.0.0.0:8000
```

Server will be available at: `http://localhost:8000`

## Testing Checklist

### 1. Home App (apps/home/)
- [ ] `GET /` → Renders index.html (resume analyzer page)
- [ ] `GET /about/` → Renders about_me.html
- [ ] Both pages load without errors
- [ ] Tailwind CSS loads (styling appears correct)

### 2. Resume App (apps/resume/)
- [ ] `POST /analyze` → Upload PDF + job desc (test with sample files)
  - Should return: analysis, resume_text, plan JSON
- [ ] `POST /api/explore_graph/` → Query parameter
  - Should return: knowledge graph JSON with nodes/links
- [ ] Error handling for missing files
- [ ] Error handling for invalid PDFs

### 3. Interview App (apps/interview/)
- [ ] `GET /interview/` → Renders coach.html
- [ ] `POST /interview/api/chat/start` → Initialize interview
  - Input: role, company, experience_level
  - Should return: session_id, first_question, role_confirmed
- [ ] `POST /interview/api/chat/message` → Send answer
  - Input: session_id, message, role, experience_level, current_question
  - Should return: feedback, technical_depth, relevance, confidence, next_question
- [ ] `POST /interview/api/chat/evaluate` → Get results
  - Input: session_id, evaluations array, role
  - Should return: overall_score, metrics, strengths, improvements

### 4. Static Files
- [ ] CSS files load (style.css, home.css)
- [ ] JavaScript files load (app.js, interview.js, about_me.js)
- [ ] Phosphor icons render correctly
- [ ] No 404 errors in console

### 5. Import Verification
- [ ] All apps import correctly
- [ ] No circular import errors
- [ ] Template paths resolve correctly
- [ ] Static file paths resolve correctly

### 6. URL Routing
- [ ] / → home app works
- [ ] /about/ → home app works
- [ ] /analyze → resume app works
- [ ] /api/explore_graph/ → resume app works
- [ ] /interview/ → interview app works
- [ ] /interview/api/chat/* → interview app works
- [ ] 404 for invalid routes

## Testing with cURL

### Test Home Page
```bash
curl http://localhost:8000/
curl http://localhost:8000/about/
```

### Test Resume Analysis
```bash
curl -X POST http://localhost:8000/analyze \
  -F "resume=@sample.pdf" \
  -F "job_desc=Python developer with 5 years experience"
```

### Test Interview Chat
```bash
# Start interview
curl -X POST http://localhost:8000/interview/api/chat/start \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Software Engineer",
    "company": "Google",
    "experience_level": "Mid Level (2-5 years)"
  }'

# Send message (use session_id from response)
curl -X POST http://localhost:8000/interview/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc12345",
    "message": "I have 5 years of experience in Python and system design",
    "role": "Software Engineer",
    "experience_level": "Mid Level (2-5 years)",
    "current_question": "Tell me about your experience"
  }'

# Evaluate interview
curl -X POST http://localhost:8000/interview/api/chat/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc12345",
    "role": "Software Engineer",
    "evaluations": [
      {"technical_depth": 8, "relevance": 7, "confidence": 8}
    ]
  }'
```

## Django Management Commands

```bash
# Check for configuration issues
python3 manage.py check

# Create superuser (admin)
python3 manage.py createsuperuser

# Run migrations (if DB changes made)
python3 manage.py migrate

# Collect static files (for production)
python3 manage.py collectstatic --noinput
```

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'apps.home'
```
- Ensure apps/ has __init__.py
- Check INSTALLED_APPS in settings.py
- Restart dev server

### Template Not Found
```
TemplateDoesNotExist: home/index.html
```
- Verify template paths: templates/home/, templates/resume/, templates/interview/
- Check app_name in urls.py

### Static Files Not Loading
- Run: `python3 manage.py collectstatic`
- Check STATIC_URL and STATIC_ROOT in settings.py
- Browser cache: Hard refresh (Ctrl+F5)

### CORS/CSRF Errors
- @csrf_exempt decorators are in place for API endpoints
- CORS is set to allow all origins in settings.py

## Next Steps
1. Run dev server and verify all endpoints work
2. Test with frontend (open in browser)
3. Check Django admin: http://localhost:8000/admin/
4. Test PDF upload and resume analysis
5. Test interview chatbot flow (requires GOOGLE_API_KEY set)

## Notes
- **API Key Required**: Resume analysis and interview features need GOOGLE_API_KEY in .env
- **No Database**: Current MVP uses no database (localStorage for chat sessions)
- **Debug Mode**: Debug=True in development, should be False in production
- **Static Files**: Generated staticfiles/ is ignored in .gitignore
