from app.language.pii_detection import detect_pii

text = (
    "Bonjour, je m'appelle Jean Dupont. "
    "Mon adresse email est jean.dupont@example.com."
)

result = detect_pii(text)

print("--- TEXTE MASQUÉ ---")
print(result["redacted_text"])

print("--- INFORMATIONS DÉTECTÉES ---")
for entity in result["entities"]:
    print(entity)