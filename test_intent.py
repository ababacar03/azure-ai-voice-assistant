
from app.language.intent import detect_intent

messages = [
    "Je veux récupérer mon argent.",
    "Comment faire pour être remboursé ?",
    "Où est mon colis ?",
    "Je voudrais savoir quand ma commande va arriver.",
    "Comment puis-je contacter votre service client ?",
    "Avez-vous un numéro de téléphone ?",
    "Est-ce que vous acceptez PayPal ?",
    "Quels sont les moyens de paiement disponibles ?",
    "Bonjour, comment allez-vous ?"
]

for message in messages:
    intent = detect_intent(message)

    print("\nMessage :", message)
    print("Intention :", intent)
