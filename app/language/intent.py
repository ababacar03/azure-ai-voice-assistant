
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
            "dans un assistant de service client.\n"
            "Analyse le message et identifie son intention principale.\n\n"

            "Catégories possibles :\n"
            "- remboursement : demande de remboursement ou de retour d'argent.\n"
            "- suivi_livraison : suivi de commande, colis ou livraison.\n"
            "- contact : recherche des coordonnées ou moyens de contact.\n"
            "- paiement : questions sur les moyens ou modalités de paiement.\n"
            "- information_produit : questions sur les caractéristiques, "
            "fonctionnalités ou informations concernant un produit ou service.\n"
            "- question_prix : questions sur les tarifs, prix, coûts ou budgets.\n"
            "- recommandation : demande de conseils, suggestions ou comparaisons.\n"
            "- reclamation : insatisfaction, problème rencontré ou plainte.\n"
            "- autre : question qui concerne le service client, mais ne correspond "
            "à aucune catégorie précédente.\n"
            "- hors_sujet : question sans rapport avec les produits, services "
            "ou activités de l'entreprise.\n\n"

            "Règles de classification :\n"
            "- Choisis une seule intention principale.\n"
            "- Base-toi uniquement sur le contenu du message.\n"
            "- Ne confonds pas une question sur le prix avec une question sur le paiement.\n"
            "- Une demande de conseil ou de suggestion correspond à recommandation.\n"
            "- Un problème ou une insatisfaction exprimée correspond à reclamation.\n"
            "- Une question générale sur un compte client ou une demande métier inconnue "
            "correspond à autre.\n"
            "- Une question de culture générale, de programmation, de météo ou "
            "un sujet sans rapport avec l'entreprise correspond à hors_sujet.\n"
            "- Si plusieurs intentions sont présentes, choisis celle qui domine.\n"
            "- Ne déduis pas une intention qui n'est pas exprimée."
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
                                "information_produit",
                                "question_prix",
                                "recommandation",
                                "reclamation",
                                "autre",
                                "hors_sujet"
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
