"""Shared configuration: chooses the LLM provider and holds the lab data."""

import os

from dotenv import load_dotenv
from openai import OpenAI


# Load values from .env
load_dotenv()


# Read the provider
PROVIDER = os.getenv(
    "PROVIDER",
    "ollama"
).strip().lower()


# Configure the selected provider
if PROVIDER == "ollama":

    BASE_URL = "http://localhost:11434/v1"

    API_KEY = "ollama"

    MODEL = os.getenv(
        "MODEL",
        "qwen2.5:1.5b"
    )


elif PROVIDER == "groq":

    BASE_URL = "https://api.groq.com/openai/v1"

    API_KEY = os.getenv(
        "GROQ_API_KEY"
    )

    MODEL = os.getenv(
        "MODEL",
        "openai/gpt-oss-20b"
    )


elif PROVIDER == "huggingface":

    BASE_URL = "https://router.huggingface.co/v1"

    API_KEY = os.getenv(
        "HF_TOKEN"
    )

    MODEL = os.getenv(
        "MODEL",
        "openai/gpt-oss-20b"
    )


else:

    raise SystemExit(
        f"Unknown PROVIDER '{PROVIDER}'. "
        "Use ollama, groq or huggingface."
    )


# Check whether the API key exists
if not API_KEY:

    raise SystemExit(
        f"No API key found for PROVIDER={PROVIDER}. "
        "Check your .env file."
    )


# Create OpenAI-compatible client
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)


# Private college fee data
COURSE_FEES = {
    "CS101": 12000,
    "AI202": 18000,
    "DS303": 15000
}


# Questions used for testing
QUESTIONS = [
    "What is the fee for AI202?",

    "What is the total fee for CS101 and AI202 "
    "after a 10% scholarship?",

    "Is DS303 more expensive than CS101, "
    "and by how much?",

    "Write a two-line welcome message "
    "for new AI students."
]


def banner(system_name):

    print(
        f"\n=== {system_name} | "
        f"provider: {PROVIDER} | "
        f"model: {MODEL} ===\n"
    )