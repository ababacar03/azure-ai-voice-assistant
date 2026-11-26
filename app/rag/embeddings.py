
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider
)

from app.config import get_required_setting

load_dotenv()


def generate_embedding(text: str) -> list:
    """
    Transforme un texte en vecteur numérique
    avec Azure OpenAI Embeddings.
    """

    if not text or not text.strip():
        raise ValueError("Le texte à vectoriser est vide.")

    endpoint = get_required_setting("AZURE_OPENAI_ENDPOINT")
    deployment = get_required_setting(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    )

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default"
    )

    client = OpenAI(
        base_url=endpoint,
        api_key=token_provider
    )

    response = client.embeddings.create(
        model=deployment,
        input=text
    )

    return response.data[0].embedding
