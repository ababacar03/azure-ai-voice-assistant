
import os

from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()


def detect_pii(text: str) -> list:
    """
    Détecte les informations personnelles (PII)
    avec Azure AI Language.
    """

    if not text or not text.strip():
        raise ValueError("Le texte à analyser est vide.")

    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    key = os.getenv("AZURE_LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError("Configuration Azure Language manquante.")

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
        raise RuntimeError(result.error.message)

    return [
        {
            "text": entity.text,
            "category": entity.category,
            "confidence_score": entity.confidence_score
        }
        for entity in result.entities
    ]
