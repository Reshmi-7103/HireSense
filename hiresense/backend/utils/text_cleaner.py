import re
import spacy

nlp = spacy.load("en_core_web_sm")
STOP_WORDS = nlp.Defaults.stop_words

def clean_text(text):
    text = text.replace('\n', ' ')   
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = " ".join(word for word in text.split() if word not in STOP_WORDS)
    return text
