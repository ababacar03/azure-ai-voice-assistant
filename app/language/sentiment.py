
import os

from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()


def analyze_sentiment(text: str) -> dict:
    """
    Analyse le sentiment d'un texte avec Azure AI Language.
    """

    endpoint = os.getenv("AZURE_LANGUAGE_ENDPOINT")
    key = os.getenv("AZURE_LANGUAGE_KEY")

    if not endpoint or not key:
        raise ValueError("Configuration Azure Language manquante.")

    client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    results = client.analyze_sentiment(
        documents=[text]
    )

    result = results[0]

    if result.is_error:
        raise RuntimeError(result.error.message)

    return {
        "sentiment": result.sentiment,
        "positive": result.confidence_scores.positive,
        "neutral": result.confidence_scores.neutral,
        "negative": result.confidence_scores.negative
    }
