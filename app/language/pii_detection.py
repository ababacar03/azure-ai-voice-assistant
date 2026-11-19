
import os

from dotenv import load_dotenv
from pathlib import Path
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def detect_pii(text: str) -> dict:
    """
    Détecte les informations personnelles et retourne le texte masqué.
    """
    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    key = os.getenv("AZURE_LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError("Configuration Azure Language manquante.")

    if not text or not text.strip():
        raise ValueError("Le texte ne peut pas être vide.")

    client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    results = client.recognize_pii_entities(
        documents=[text],
        language="fr"
    )

    result = results[0]

    if result.is_error:
        raise ValueError(result.error.message)

    entities = [
        {
            "text": entity.text,
            "category": entity.category,
            "confidence_score": entity.confidence_score
        }
        for entity in result.entities
    ]

    return {
        "redacted_text": result.redacted_text,
        "entities": entities
    }
