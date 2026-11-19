
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import re
import unicodedata
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def detect_simple_intent(text: str) -> list[str] | None:
    normalized = unicodedata.normalize("NFD", text.lower())
    normalized = "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = " ".join(normalized.split())

    greetings = {
        "bonjour", "bonsoir", "salut", "coucou",
        "hello", "hey"
    }

    thanks = {
        "merci", "merci beaucoup", "merci bien",
        "je vous remercie", "je te remercie"
    }

    goodbyes = {
        "au revoir", "a bientot", "a la prochaine",
        "bonne journee", "bonne soiree", "a plus"
    }

    if normalized in greetings:
        return ["salutation"]

    if normalized in thanks:
        return ["remerciement"]

    if normalized in goodbyes:
        return ["fin_conversation"]

    return None


def detect_intent(
    text: str,
    conversation_history: list[dict] | None = None
) -> list[str]:
    if conversation_history is None:
        conversation_history = []

    recent_history = conversation_history[-6:]

    history_context = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_history
    )
    """
    Identifie une ou plusieurs intentions dans un message client.
    """
    if conversation_history is None:
        conversation_history = []

    recent_history = conversation_history[-6:]

    history_context = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_history
    )
    """
    Identifie une ou plusieurs intentions dans un message client.
    """
    if not ENDPOINT or not DEPLOYMENT:
        raise ValueError("Configuration Azure OpenAI manquante.")

    if not text or not text.strip():
        raise ValueError("Le message ne peut pas être vide.")
    simple_intent = detect_simple_intent(text)

    if simple_intent:
        return simple_intent

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
            "- salutation\n"
            "- remerciement\n"
            "- fin_conversation\n"
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
            "- Une salutation simple correspond à salutation.\n"
            "- Un remerciement simple correspond à remerciement.\n"
            "- Un message qui prend congé correspond à fin_conversation.\n"
            "- Les formules de politesse peuvent être combinées avec une intention métier "
            "si le client formule également une demande.\n"
            "- N'utilise pas autre lorsqu'une intention de politesse correspond au message.\n"
            "- Ne retourne jamais hors_sujet avec une autre intention."
            "- Utilise l'historique pour comprendre les questions complémentaires "
            "et les références implicites du client.\n"
            "- Si le message actuel est une question de suivi liée à une demande "
            "précédente, identifie l'intention correspondante grâce au contexte.\n"
            "- Classe uniquement le message actuel, sans reprendre automatiquement "
            "toutes les intentions des messages précédents.\n"
        ),
        input=(
            f"Historique de la conversation :\n{history_context}\n\n"
            f"Message actuel du client : {text}"
            if history_context
            else f"Message du client : {text}"
        ),
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
                                    "salutation",
                                    "remerciement",
                                    "fin_conversation",
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
    intents = list(dict.fromkeys(result["intents"]))

    if not intents:
        raise ValueError("Aucune intention détectée.")

    if "hors_sujet" in intents and len(intents) > 1:
        raise ValueError("Classification incohérente : hors_sujet combiné.")

    return intents
