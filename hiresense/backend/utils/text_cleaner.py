import re
import spacy

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    text = text.lower()

    # Remove special chars
    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Fix merged words issue
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize and remove stopwords
    doc = nlp(text)
    clean_words = [token.text for token in doc if not token.is_stop and len(token.text) > 2]

    return " ".join(clean_words)