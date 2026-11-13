
from app.rag.answer import generate_answer

question = "Quels sont les moyens de paiement acceptés ?"

result = generate_answer(question)

print("\nQuestion :", question)
print("\nRéponse de l'assistant :")
print(result["answer"])

print("\nDocuments utilisés :")
for source in result["sources"]:
    print("-", source)
