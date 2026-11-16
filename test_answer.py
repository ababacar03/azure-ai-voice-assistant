from app.rag.answer import generate_answer

questions = [
"Est-ce que vous acceptez les paiements par PayPal ?",
"Quels sont vos horaires d'ouverture ?",
"Est-ce que vous livrez gratuitement ?"
"Combien coûte le service premium ?",
"Quel est le prix du service entreprise ?"
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", question)

    result = generate_answer(question)

    print("RÉPONSE :", result["answer"])
    print("SOURCES :", result["sources"])