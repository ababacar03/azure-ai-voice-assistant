from app.rag.answer import generate_answer

questions = [
    "Combien de temps faut-il pour recevoir un remboursement ?",
    "Quels sont les délais de livraison ?",
    "Est-ce que vous acceptez les paiements par PayPal ?"
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", question)

    result = generate_answer(question)

    print("RÉPONSE :", result["answer"])
    print("SOURCES :", result["sources"])