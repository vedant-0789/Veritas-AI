
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ No API key found")
    exit(1)

genai.configure(api_key=api_key)

print("--- Testing Gemini 2.0 Flash ---")
try:
    # Add delay to avoid rate limits from previous runs
    time.sleep(2)
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Reply with exactly one word: Verified")
    print(f"✅ Success! Response: {response.text}")
except Exception as e:
    print(f"❌ Failed: {e}")
