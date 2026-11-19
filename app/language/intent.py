
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def detect_intent(text: str) -> list[str]:
    """
    Identifie une ou plusieurs intentions dans un message client.
    """
    if not ENDPOINT or not DEPLOYMENT:
        raise ValueError("Configuration Azure OpenAI manquante.")

    if not text or not text.strip():
        raise ValueError("Le message ne peut pas être vide.")

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default"
    )

    client = OpenAI(
        base_url=ENDPOINT,
        api_key=token_provider
    )

    response = client.responses.create(
        model=DEPLOYMENT,
        instructions=(
            "Tu es un système de classification des intentions "
            "dans un assistant de service client.\n"
            "Identifie toutes les intentions clairement exprimées "
            "dans le message du client.\n\n"

            "Catégories possibles :\n"
            "- remboursement\n"
            "- suivi_livraison\n"
            "- contact\n"
            "- paiement\n"
            "- information_produit\n"
            "- question_prix\n"
            "- recommandation\n"
            "- reclamation\n"
            "- autre\n"
            "- hors_sujet\n\n"

            "Règles de classification :\n"
            "- Retourne une liste contenant une ou plusieurs intentions.\n"
            "- Identifie toutes les demandes distinctes réellement exprimées.\n"
            "- N'ajoute pas une intention simplement parce qu'elle est liée au sujet.\n"
            "- Une insatisfaction explicite correspond à reclamation.\n"
            "- Une demande de suivi correspond à suivi_livraison.\n"
            "- Une demande de remboursement correspond à remboursement.\n"
            "- Une question sur les prix correspond à question_prix.\n"
            "- Une demande de conseil correspond à recommandation.\n"
            "- Si aucune catégorie métier ne correspond, utilise autre.\n"
            "- Si le message est sans rapport avec l'entreprise, utilise "
            "uniquement hors_sujet.\n"
            "- Ne retourne jamais hors_sujet avec une autre intention."
        ),
        input=f"Message du client : {text}",
        text={
            "format": {
                "type": "json_schema",
                "name": "intent_classification",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "intents": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "remboursement",
                                    "suivi_livraison",
                                    "contact",
                                    "paiement",
                                    "information_produit",
                                    "question_prix",
                                    "recommandation",
                                    "reclamation",
                                    "autre",
                                    "hors_sujet"
                                ]
                            }
                        }
                    },
                    "required": ["intents"],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(response.output_text)
    intents = result["intents"]

    if not intents:
        raise ValueError("Aucune intention détectée.")

    if "hors_sujet" in intents and len(intents) > 1:
        raise ValueError("Classification incohérente : hors_sujet combiné.")

    return intents
