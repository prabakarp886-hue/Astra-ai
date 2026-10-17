
import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """
You are Astra, a friendly personal AI assistant.
Speak naturally and helpfully.
Follow the user's requested language, including Telugu,
English, Tamil, and Malayalam.
Be honest about your capabilities.
"""

def ask_astra(message, history=None):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        for item in history[-10:]:
            if (
                isinstance(item, dict)
                and item.get("role") in ("user", "assistant")
                and isinstance(item.get("content"), str)
            ):
                messages.append({
                    "role": item["role"],
                    "content": item["content"][:6000]
                })

    messages.append({
        "role": "user",
        "content": message[:6000]
    })

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800
        },
        timeout=45
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"Groq returned HTTP {response.status_code}."
        )

    return response.json()["choices"][0]["message"]["content"].strip()
