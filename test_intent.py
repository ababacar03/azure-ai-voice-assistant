
from app.language.intent import detect_intent

questions = [
    ("Comment obtenir un remboursement ?", "remboursement"),
    ("Quels sont les délais de livraison ?", "suivi_livraison"),
    ("Comment modifier mon compte client ?", "autre"),
    ("Quelle est la capitale de la France ?", "hors_sujet"),
    ("Explique-moi comment fonctionne Python.", "hors_sujet"),
    ("Quel temps fait-il aujourd'hui ?", "hors_sujet"),
]

for question, expected in questions:
    intent = detect_intent(question)

    print("=" * 60)
    print("QUESTION :", question)
    print("INTENTION :", intent)
    print("ATTENDU :", expected)
    print("RÉSULTAT :", "OK" if intent == expected else "À VÉRIFIER")
