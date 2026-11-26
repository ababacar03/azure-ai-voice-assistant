
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from app.config import get_required_setting

load_dotenv()


def analyze_sentiment(text: str) -> dict:
    """
    Analyse le sentiment d'un texte avec Azure AI Language.
    """

    if not text or not text.strip():
        raise ValueError("Le texte à analyser est vide.")

    endpoint = get_required_setting("AZURE_LANGUAGE_ENDPOINT")
    key = get_required_setting("AZURE_LANGUAGE_KEY")

    client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    results = client.analyze_sentiment(documents=[text])
    result = results[0]

    if result.is_error:
        raise RuntimeError(result.error.message)

    return {
        "sentiment": result.sentiment,
        "positive": result.confidence_scores.positive,
        "neutral": result.confidence_scores.neutral,
        "negative": result.confidence_scores.negative
    }
