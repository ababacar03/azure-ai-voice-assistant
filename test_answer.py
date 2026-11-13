
from app.rag.answer import generate_answer


questions = [
"Comment obtenir un remboursement ?",
"Quel est le délai de livraison ?",
"Quels sont les tarifs des restaurants ?",
"Quels moyens de paiement sont acceptés ?"
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", question)

    result = generate_answer(question)

    print("\nRÉPONSE :", result["answer"])
    print("SOURCES :", result["sources"])