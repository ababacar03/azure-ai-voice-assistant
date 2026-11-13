
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.rag.search import search_documents

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not ENDPOINT or not DEPLOYMENT:
    raise ValueError("Configuration Azure OpenAI manquante.")

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
)

client = OpenAI(
    base_url=ENDPOINT,
    api_key=token_provider
)


def generate_answer(question: str) -> dict:
    """
    Recherche les documents pertinents puis génère
    une réponse avec GPT-5 à partir de leur contenu.
    """

    if not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    documents = search_documents(question, top=1)

    if not documents:
        return {
            "answer": "Je n'ai pas trouvé d'information pertinente dans ma base documentaire.",
            "sources": []
        }

    context = "\n\n".join(
        f"Document : {doc['file_name']}\n{doc['content']}"
        for doc in documents
    )

    response = client.responses.create(
        model=DEPLOYMENT,
        instructions=(
            "Tu es un assistant de service client. "
            "Réponds en français en utilisant uniquement les informations "
            "présentes dans les documents fournis. "
            "Si les documents ne permettent pas de répondre, "
            "indique clairement que tu ne disposes pas de cette information. "
            "N'invente aucune information."
        ),
        input=f"""
Question du client :
{question}

Documents disponibles :
{context}

Formule une réponse claire et naturelle au client.
"""
    )

    return {
        "answer": response.output_text,
        "sources": [doc["file_name"] for doc in documents]
    }
