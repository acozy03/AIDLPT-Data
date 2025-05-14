import json
import random
import nltk
import spacy
from pathlib import Path

nltk.download("punkt")
nlp = spacy.load("en_core_web_sm")

# Path to your original file
raw_path = Path("english.json")

# Output files
train_file = open("trainEnglish.json", "w", encoding="utf-8")
dev_file = open("devEnglish.json", "w", encoding="utf-8")
test_file = open("testEnglish.json", "w", encoding="utf-8")

def clean_label(label_str):
    # Converts "ILR3" -> 3 (or handle however your labels are formatted)
    return int("".join([c for c in label_str if c.isdigit()]))

with open(raw_path, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        text = obj.get("text", "")
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        label = clean_label(obj.get("label", "ILR0"))
        example = {
            "text": sentences,
            "label": label
        }
        u = random.random()
        if u < 0.8:
            json.dump(example, train_file)
            train_file.write("\n")
        elif u < 0.9:
            json.dump(example, dev_file)
            dev_file.write("\n")
        else:
            json.dump(example, test_file)
            test_file.write("\n")

train_file.close()
dev_file.close()
test_file.close()

print("✅ Done splitting and cleaning data!")
