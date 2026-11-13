
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
    Recherche les documents, vérifie leur pertinence
    et génère une réponse avec GPT-5.
    """

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    # 1. Rechercher les documents
    documents = search_documents(question, top=3)

    if not documents:
        return {
            "answer": "Je ne dispose pas d'informations pour répondre à votre question.",
            "sources": []
        }

    # 2. Préparer les documents pour GPT-5
    context = "\n\n".join(
        f"Nom du fichier : {doc['file_name']}\n"
        f"Contenu : {doc['content']}"
        for doc in documents
    )

    # 3. Vérifier la pertinence des documents
    relevance_response = client.responses.create(
        model=DEPLOYMENT,
        instructions=(
            "Tu es un évaluateur de pertinence documentaire. "
            "Tu dois déterminer quels documents contiennent des "
            "informations répondant directement à la question. "
            "Une simple proximité de thème ne suffit pas. "
            "N'infère aucune information absente des documents. "
            "Retourne uniquement les noms exacts des fichiers pertinents, "
            "un par ligne. "
            "Si aucun document ne répond directement à la question, "
            "retourne exactement : AUCUN."
        ),
        input=f"""
Question du client :
{question}

Documents disponibles :
{context}
"""
    )

    relevant_names = {
        line.strip().lstrip("- ").strip("`")
        for line in relevance_response.output_text.splitlines()
        if line.strip()
    }

    relevant_documents = [
        doc for doc in documents
        if doc["file_name"] in relevant_names
    ]

    # 4. Si aucun document n'est pertinent, ne pas inventer
    if not relevant_documents:
        return {
            "answer": (
                "Je ne dispose pas d'informations suffisantes "
                "dans ma base documentaire pour répondre à votre question."
            ),
            "sources": []
        }

    # 5. Générer une réponse avec les documents pertinents uniquement
    relevant_context = "\n\n".join(
        f"Document : {doc['file_name']}\n{doc['content']}"
        for doc in relevant_documents
    )

    response = client.responses.create(
        model=DEPLOYMENT,
        instructions=(
            "Tu es un assistant de service client. "
            "Réponds en français, de manière claire et naturelle. "
            "Utilise exclusivement les informations des documents fournis. "
            "Réponds uniquement à la question posée. "
            "Ne donne aucune information sans rapport avec la demande. "
            "Si les documents ne contiennent pas la réponse, "
            "dis que tu ne disposes pas de cette information. "
            "N'invente aucune information."
        ),
        input=f"""
Question du client :
{question}

Documents pertinents :
{relevant_context}
"""
    )

    return {
        "answer": response.output_text,
        "sources": [doc["file_name"] for doc in relevant_documents]
    }
