# How to Run RoleReady-AI Locally

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd /Users/philia/ai-interviewer/RoleReady-AI/.claude/worktrees/quirky-satoshi

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 2: Set Environment Variables

```bash
# Set Django debug mode
export DJANGO_DEBUG=True

# Set Google API Key (optional - only needed for resume/interview features)
export GOOGLE_API_KEY=your_actual_api_key_here

# Or create a .env file instead (optional)
echo "DJANGO_DEBUG=True" > .env
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

### Step 3: Run the Development Server

```bash
# Start the server
python3 manage.py runserver

# Or specify a different port:
python3 manage.py runserver 0.0.0.0:8000

# Or use this for external access:
python3 manage.py runserver 0.0.0.0:8000
```

**You should see:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## Access the Application

Once the server is running, open these URLs in your browser:

### 🏠 Home Pages
- **Home/Resume Analyzer**: http://localhost:8000/
- **About Page**: http://localhost:8000/about/

### 📄 Resume Features
- **Upload & Analyze Resume**: http://localhost:8000/ (form on home page)
- **Explore Knowledge Graph**: http://localhost:8000/api/explore_graph/ (API only)

### 🎤 Interview Coach
- **Interview Chatbot**: http://localhost:8000/interview/

---

## Testing with cURL (Terminal)

### Test 1: Check if Server is Running
```bash
curl http://localhost:8000/
# Should return HTML of the home page
```

### Test 2: Test Home Page
```bash
curl http://localhost:8000/about/
# Should return HTML of the about page
```

### Test 3: Test Interview API (Start)
```bash
curl -X POST http://localhost:8000/interview/api/chat/start \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Software Engineer",
    "company": "Google",
    "experience_level": "Mid Level (2-5 years)"
  }'
```

**Response should look like:**
```json
{
  "session_id": "abc12345",
  "question": "Tell me about a complex system design...",
  "role_confirmed": "software engineer",
  "tips": "Focus on technical depth...",
  "company": "Google",
  "experience_level": "Mid Level (2-5 years)"
}
```

### Test 4: Send Chat Message
```bash
curl -X POST http://localhost:8000/interview/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc12345",
    "message": "I have experience with system design and can explain my approach",
    "role": "Software Engineer",
    "experience_level": "Mid Level (2-5 years)",
    "current_question": "Tell me about a complex system design you have solved"
  }'
```

---

## Stop the Server

Press `CTRL + C` in your terminal to stop the server.

---

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'django'"

**Solution**: Virtual environment not activated
```bash
# Activate virtual environment
source venv/bin/activate
```

### ❌ "Port 8000 already in use"

**Solution**: Use a different port
```bash
python3 manage.py runserver 8001
# Access at: http://localhost:8001
```

### ❌ "ModuleNotFoundError: No module named 'apps.home'"

**Solution**: Run from the correct directory
```bash
# Make sure you're in the project root
cd /Users/philia/ai-interviewer/RoleReady-AI/.claude/worktrees/quirky-satoshi
python3 manage.py runserver
```

### ❌ "GOOGLE_API_KEY is not set"

**Solution**: Set the environment variable
```bash
export GOOGLE_API_KEY=your_key_here
python3 manage.py runserver
```

Or the resume/interview features will work but show "API Key not set" error.

### ❌ Static files not loading (CSS/JS not working)

**Solution**: Collect static files
```bash
python3 manage.py collectstatic --noinput
```

Then restart the server.

---

## Useful Django Management Commands

```bash
# Check for configuration issues
python3 manage.py check

# Create an admin/superuser (optional)
python3 manage.py createsuperuser
# Then access admin at: http://localhost:8000/admin/

# Run migrations (if database changes made)
python3 manage.py migrate

# Collect static files (production)
python3 manage.py collectstatic --noinput

# Clear Django cache
python3 manage.py clear_cache
```

---

## Full Setup Script (Copy & Paste)

```bash
#!/bin/bash

# Navigate to project
cd /Users/philia/ai-interviewer/RoleReady-AI/.claude/worktrees/quirky-satoshi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_DEBUG=True
export GOOGLE_API_KEY=your_key_here

# Run the server
python3 manage.py runserver 0.0.0.0:8000

# Open in browser
# http://localhost:8000
```

---

## IDE Integration (VS Code)

Add to `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

Then in VS Code terminal, it will auto-activate the venv.

---

## Next Steps After Running Locally

1. ✅ Verify all pages load without errors
2. ✅ Test resume upload and analysis (if API key set)
3. ✅ Test interview chat flow (if API key set)
4. ✅ Check CSS/JS are loading (should see styling)
5. ✅ Visit Django admin panel (optional)
6. ✅ Test with different browsers
7. ✅ Deploy to Vercel when ready

---

## Common URLs Reference

| URL | Purpose |
|-----|---------|
| http://localhost:8000/ | Home page (resume analyzer) |
| http://localhost:8000/about/ | About page |
| http://localhost:8000/interview/ | Interview coach |
| http://localhost:8000/admin/ | Django admin panel |
| http://localhost:8000/api/explore_graph/ | Knowledge graph API |

---

## Performance Tips

- Use `--reload` is on by default (auto-reloads on file changes)
- Static files auto-refresh in browser (Ctrl+F5 for hard refresh)
- Database is SQLite (local only, file-based)
- No need for external database for development

---

## Additional Help

- View full test report: `cat TEST_REPORT.md`
- See testing guide: `cat TESTING.md`
- Check launch config: `cat .claude/launch.json`
