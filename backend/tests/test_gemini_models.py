
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API key found in .env")
    exit(1)

genai.configure(api_key=api_key)

print("\n--- Listing Available Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\n--- Testing Generation (gemini-1.5-flash) ---")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, suggest a name for a security AI.")
    print(f"✅ Response: {response.text}")
except Exception as e:
    print(f"❌ Error with gemini-1.5-flash: {e}")

print("\n--- Testing Generation (gemini-pro) ---")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, suggest a name for a security AI.")
    print(f"✅ Response: {response.text}")
except Exception as e:
    print(f"❌ Error with gemini-pro: {e}")
