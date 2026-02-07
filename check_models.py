import google.generativeai as genai
import os

# --- PASTE KEY HERE ---
API_KEY = "AIzaSyA2wCqUoE4DdDEBEr9sSF07qgsM7VaZPZE" 
genai.configure(api_key=API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")