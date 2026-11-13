
from app.language.entities import recognize_entities

text = (
    "Jean Dupont travaille chez Microsoft à Paris. "
    "Il doit participer à une réunion le 13 novembre 2026."
)

entities = recognize_entities(text)

print("\n--- RECONNAISSANCE DES ENTITÉS ---")

for entity in entities:
    print(
        f"Texte : {entity['text']} | "
        f"Catégorie : {entity['category']} | "
        f"Confiance : {entity['confidence_score']:.2f}"
    )
