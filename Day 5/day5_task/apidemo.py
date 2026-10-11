"""Day 5, Part C: call the REST API directly, and measure what you get.
Contains both Local Ollama (commented out) and Groq API (active)."""
import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()


BASE = "https://api.groq.com/openai/v1"
MODEL = os.getenv("MODEL", "llama3-8b-8192")
PROMPT = "In three sentences, explain what an AI agent is."
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("Error: GROQ_API_KEY not found in .env file.")
    exit(1)

def openai_compatible_groq(model=MODEL, prompt=PROMPT):
    """POST /v1/chat/completions - using the Groq API which is OpenAI compatible."""
    print(f"Calling Groq API with model: {model}...")
    start = time.time()
    
    response = requests.post(
        f"{BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        },
        timeout=30
    ).json()
    
    elapsed = time.time() - start
    
    print(f"\n[/v1/chat/completions] Response in {elapsed:.2f}s:")
    if "choices" in response:
        print(response["choices"][0]["message"]["content"].strip())
    else:
        print(f"Error or unexpected response: {json.dumps(response, indent=2)}")

if __name__ == "__main__":
    
    
   
    openai_compatible_groq()