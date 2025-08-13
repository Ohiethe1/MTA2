#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY: {GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "GEMINI_API_KEY not found")

if GEMINI_API_KEY:
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini model created successfully")
        
        # Test with a simple prompt
        response = gemini_model.generate_content("Hello, can you respond with 'Gemini is working'?")
        print(f"Gemini response: {response.text}")
        
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No Gemini API key found") 