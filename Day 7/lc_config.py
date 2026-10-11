
import hashlib
import math
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings


# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE, override=True)


# --------------------------------------------------
# 2. CONFIGURATION
# --------------------------------------------------

PROVIDER = os.getenv("PROVIDER", "groq").strip().lower()

EMBED_PROVIDER = os.getenv(
    "EMBED_PROVIDER", "fastembed"
).strip().lower()

DB_DIR = "chroma_db"
COLLECTION = "college_helpdesk"


# --------------------------------------------------
# 3. CHAT MODEL
# --------------------------------------------------

def get_model(temperature=0):
    """Return the configured chat model."""

    if PROVIDER == "groq":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise SystemExit(
                "GROQ_API_KEY is missing. Check your .env file."
            )

        return ChatOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
            model=os.getenv("MODEL", "openai/gpt-oss-20b"),
            temperature=temperature,
        )

    elif PROVIDER == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("MODEL", "qwen2.5:1.5b"),
            temperature=temperature,
        )

    elif PROVIDER == "huggingface":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("HF_TOKEN")
        if not api_key:
            raise SystemExit(
                "HF_TOKEN is missing. Check your .env file."
            )

        return ChatOpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key,
            model=os.getenv("MODEL", "openai/gpt-oss-20b"),
            temperature=temperature,
        )

    else:
        raise SystemExit(
            f"Unknown PROVIDER '{PROVIDER}'. "
            "Use groq, ollama or huggingface."
        )


# --------------------------------------------------
# 4. HASH EMBEDDINGS (OFFLINE FALLBACK)
# --------------------------------------------------

class HashEmbeddings(Embeddings):
    """Simple keyword-based embeddings without model downloads."""

    STOP = set(
        "a an the is are was to of in on for and or by at "
        "be it this that with what how do does i my can".split()
    )

    def _vec(self, text):
        vector = [0.0] * 256

        for word in re.findall(r"[a-z0-9]+", text.lower()):
            if word in self.STOP:
                continue

            if word.endswith("s") and len(word) > 3:
                word = word[:-1]

            index = int(
                hashlib.md5(word.encode()).hexdigest(), 16
            ) % 256

            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0

        return [value / norm for value in vector]

    def embed_documents(self, texts):
        return [self._vec(text) for text in texts]

    def embed_query(self, text):
        return self._vec(text)


# --------------------------------------------------
# 5. EMBEDDING MODEL
# --------------------------------------------------

def get_embeddings():
    """Return the selected embedding model."""

    if EMBED_PROVIDER == "fastembed":
        from langchain_community.embeddings import FastEmbedEmbeddings

        return FastEmbedEmbeddings(
            model_name=os.getenv(
                "EMBED_MODEL",
                "BAAI/bge-small-en-v1.5",
            )
        )

    elif EMBED_PROVIDER == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(
            model=os.getenv(
                "EMBED_MODEL",
                "nomic-embed-text",
            )
        )

    elif EMBED_PROVIDER == "hash":
        return HashEmbeddings()

    else:
        raise SystemExit(
            f"Unknown EMBED_PROVIDER '{EMBED_PROVIDER}'. "
            "Use fastembed, ollama or hash."
        )


# --------------------------------------------------
# 6. CHROMA VECTOR DATABASE
# --------------------------------------------------

def get_vectorstore():
    """Open or create the Chroma collection."""

    from langchain_chroma import Chroma

    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=DB_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )
