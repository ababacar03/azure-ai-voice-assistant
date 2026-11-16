
from app.language.intent import detect_intent

test_cases = [
    "Je veux récupérer mon argent.",
    "Où est mon colis ?",
    "Est-ce que vous acceptez PayPal ?",
    "Quels sont les horaires de votre service client ?",
    "Quelles sont les caractéristiques de ce produit ?",
    "Combien coûte ce service ?",
    "Quel restaurant me recommandez-vous ?",
    "Je suis très déçu de votre service, c'est inadmissible.",
    "Bonjour, comment allez-vous ?"
]

for question in test_cases:
    intent = detect_intent(question)

    print(f"\nMESSAGE : {question}")
    print(f"INTENTION : {intent}")
