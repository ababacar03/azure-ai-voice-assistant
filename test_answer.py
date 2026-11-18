from app.rag.answer import generate_answer

questions = [
    ("Quels sont les avantages du Pack Premium ?", "information_produit"),
    ("Quel pack me recommandez-vous pour une entreprise ?", "recommandation"),
    ("Combien coûte le Pack Essentiel ?", "question_prix"),
    ("Est-ce que vous proposez une livraison gratuite ?", "suivi_livraison"),
    ("Acceptez-vous les paiements en cryptomonnaies ?", "paiement"),
    ("Avez-vous une application mobile ?", "autre"),
    ("Quelle est la capitale de la France ?", "autre"),
    ("Explique-moi comment fonctionne Python.", "autre"),
    ("Quel temps fait-il aujourd'hui ?", "autre"),
]

for question, intent in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", question)

    result = generate_answer(question, intent)

    print("RÉPONSE :", result["answer"])
    print("SOURCES :", result["sources"])