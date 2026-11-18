
from azure.core.exceptions import (
    HttpResponseError,
    ClientAuthenticationError,
    ServiceRequestError
)

from openai import (
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
    APIConnectionError,
    InternalServerError
)


def get_error_message(error: Exception) -> str:
    """Retourne un message compréhensible selon le type d'erreur."""

    if isinstance(error, ClientAuthenticationError):
        return "Erreur d'authentification auprès d'Azure."

    if isinstance(error, AuthenticationError):
        return "Authentification Azure OpenAI impossible."

    if isinstance(error, PermissionDeniedError):
        return "Accès refusé : vérifiez les permissions Azure."

    if isinstance(error, RateLimitError):
        return "Limite de requêtes ou quota Azure OpenAI dépassé."

    if isinstance(error, ServiceRequestError):
        return "Impossible de contacter le service Azure."

    if isinstance(error, APIConnectionError):
        return "Problème de connexion avec Azure OpenAI."

    if isinstance(error, InternalServerError):
        return "Le service Azure OpenAI rencontre une erreur interne."

    if isinstance(error, HttpResponseError):
        status = error.status_code

        if status == 403:
            return "Accès refusé par Azure (403)."

        if status == 429:
            return "Quota ou limite de requêtes Azure dépassé (429)."

        if status and status >= 500:
            return f"Le service Azure est temporairement indisponible ({status})."

        return f"Erreur HTTP Azure ({status})."

    return f"Erreur inattendue : {error}"
