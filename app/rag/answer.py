
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from app.rag.search import hybrid_search_documents

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")




def generate_answer(question: str, intent: str | list[str] = "autre") -> dict:
    """
    Recherche les documents et génère une réponse
    en tenant compte de l'intention du client.
    """
    if not ENDPOINT or not DEPLOYMENT:
        raise ValueError("Configuration Azure OpenAI manquante.")
    
    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")
    token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://ai.azure.com/.default"
    )

    client = OpenAI(
        base_url=ENDPOINT,
        api_key=token_provider
    )
    if isinstance(intent, str):
        intents = [intent]
    else:
        intents = intent

    if not intents:
        intents = ["autre"]
    # 1. Recherche hybride dans Azure AI Search
    documents = hybrid_search_documents(
    question,
    top=3,
    intent=intents
)

    if not documents:
        return {
            "answer": (
                "Je ne dispose pas d'informations suffisantes "
                "dans ma base documentaire pour répondre à votre question."
            ),
            "sources": []
        }

    # 2. Préparation du contexte documentaire
    context = "\n\n".join(
        f"Nom du fichier : {doc['file_name']}\n"
        f"Contenu : {doc['content']}"
        for doc in documents
    )

    # 3. Consignes adaptées à l'intention
    intent_instructions = {
        "remboursement": "Le client souhaite obtenir des informations sur un remboursement.",
        "suivi_livraison": "Le client souhaite obtenir des informations sur sa livraison ou sa commande.",
        "contact": "Le client cherche à contacter le service client.",
        "paiement": "Le client pose une question sur les moyens ou modalités de paiement.",
        "information_produit": "Le client souhaite obtenir des informations sur un produit ou un service.",
        "question_prix": "Le client souhaite connaître un prix, un tarif ou un coût.",
        "recommandation": "Le client attend un conseil ou une recommandation.",
        "reclamation": "Le client exprime une insatisfaction ou signale un problème. Adopte un ton empathique et professionnel.",
        "autre": "L'intention du client ne correspond pas aux catégories précédentes."
    }

    intent_context = "\n".join(
        intent_instructions.get(
            current_intent,
            intent_instructions["autre"]
        )
        for current_intent in intents
    )

    # 4. Génération de la réponse avec GPT-5
    response = client.responses.create(
        model=DEPLOYMENT,
        instructions=(
            "Tu es un assistant de service client. "
            "Tu dois répondre en français, de manière claire et naturelle.\n\n"
            f"Intentions détectées : {', '.join(intents)}\n"
            f"Contexte de l'intention : {intent_context}\n\n"
            "Consignes :\n"
            "- Utilise exclusivement les informations des documents fournis.\n"
            "- Vérifie que les documents répondent directement à la question.\n"
            "- Une simple proximité de thème ne suffit pas.\n"
            "- N'invente aucune information.\n"
            "- Adapte ton ton à l'intention du client.\n"
            "- Si aucune information ne permet de répondre, "
            "indique que tu ne disposes pas d'informations suffisantes "
            "et retourne une liste de sources vide.\n"
            "- Retourne uniquement les noms exacts des fichiers utilisés."
        ),
        input=f"""
Question du client :
{question}

Documents disponibles :
{context}
""",
        text={
            "format": {
                "type": "json_schema",
                "name": "customer_service_answer",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string"
                        },
                        "sources": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["answer", "sources"],
                    "additionalProperties": False
                }
            }
        }
    )

    # 5. Récupération du résultat JSON
    result = json.loads(response.output_text)

    # 6. Vérification des sources retournées
    available_sources = {
        doc["file_name"] for doc in documents
    }

    sources = list(dict.fromkeys(
        source for source in result["sources"]
        if source in available_sources
    ))

    if not sources:
        return {
            "answer": (
                "Je ne dispose pas d'informations suffisantes "
                "dans ma base documentaire pour répondre à votre question."
            ),
            "sources": []
        }

    return {
        "answer": result["answer"],
        "sources": sources
    }
