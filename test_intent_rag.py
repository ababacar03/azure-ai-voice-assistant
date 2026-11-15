
from app.language.intent import detect_intent
from app.rag.answer import generate_answer

questions = [
    "Je veux récupérer mon argent.",
    "Où est mon colis ?",
    "Comment contacter votre service client ?",
    "Est-ce que vous acceptez PayPal ?"
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", question)

    intent = detect_intent(question)
    print("INTENTION :", intent)

    result = generate_answer(question)

    print("RÉPONSE :", result["answer"])
    print("SOURCES :", result["sources"])
