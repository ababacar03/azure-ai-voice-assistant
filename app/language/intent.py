
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


def detect_intent(text: str) -> str:
    """
    Identifie l'intention principale d'un message client.
    """

    if not text or not text.strip():
        raise ValueError("Le message ne peut pas être vide.")

    response = client.responses.create(
        model=DEPLOYMENT,
        instructions=(
            "Tu es un système de classification des intentions "
            "dans un service client.\n"
            "Analyse le message et identifie son intention principale.\n\n"
            "Catégories possibles :\n"
            "- remboursement : demande de remboursement ou retour d'argent.\n"
            "- suivi_livraison : suivi de commande, colis ou livraison.\n"
            "- contact : recherche des coordonnées ou moyens de contact.\n"
            "- paiement : questions sur les moyens ou modalités de paiement.\n"
            "- autre : toute demande ne correspondant pas aux catégories précédentes.\n\n"
            "Choisis une seule catégorie. "
            "Ne déduis pas une intention qui n'est pas exprimée."
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
                        "intent": {
                            "type": "string",
                            "enum": [
                                "remboursement",
                                "suivi_livraison",
                                "contact",
                                "paiement",
                                "autre"
                            ]
                        }
                    },
                    "required": ["intent"],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(response.output_text)

    return result["intent"]
