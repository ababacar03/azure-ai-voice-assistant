
from app.language.pii_detection import detect_pii

text = (
    "Jean Dupont habite au 10 rue de la Paix à Paris. "
    "Son adresse e-mail est jean.dupont@example.com "
    "et son numéro de téléphone est 0612345678."
)

entities = detect_pii(text)

print("\n--- DÉTECTION DES DONNÉES PERSONNELLES ---")

for entity in entities:
    print(
        f"Information : {entity['text']} | "
        f"Catégorie : {entity['category']} | "
        f"Confiance : {entity['confidence_score']:.2f}"
    )
