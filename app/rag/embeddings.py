
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = "text-embedding-3-small"

if not ENDPOINT:
    raise ValueError("Configuration Azure OpenAI manquante.")

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

client = OpenAI(
    base_url=ENDPOINT,
    api_key=token_provider
)


def generate_embedding(text: str) -> list:
    """
    Transforme un texte en vecteur numérique
    avec Azure OpenAI Embeddings.
    """

    if not text or not text.strip():
        raise ValueError("Le texte à vectoriser est vide.")

    response = client.embeddings.create(
        model=DEPLOYMENT,
        input=text
    )

    return response.data[0].embedding
