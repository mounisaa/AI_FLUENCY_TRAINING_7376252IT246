import os

PROVIDER = os.getenv("PROVIDER", "groq")
MODEL = os.getenv("MODEL", "openai/gpt-oss-20b")


class MissingClient:
    def __getattr__(self, name):
        raise RuntimeError(
            "The OpenAI client is unavailable. "
            "Install openai and python-dotenv to run the live agent."
        )


try:
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()

    if PROVIDER == "groq":
        client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
    else:
        raise ValueError("Unsupported provider")

except ImportError:
    client = MissingClient()


def banner(title):
    print("=" * 70)
    print(title)
    print("=" * 70)