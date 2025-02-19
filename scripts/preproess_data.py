import spacy
import jieba
import pandas as pd
from langdetect import detect

def preprocess_text(text):
    lang = detect(text)
    if lang == "en":
        nlp = spacy.load("en_core_web_sm")
        return " ".join([token.text for token in nlp(text)])
    elif lang == "zh":
        return " ".join(jieba.cut(text))
    return text

df = pd.read_csv("data/raw_text.csv")
df["clean_text"] = df["text"].apply(preprocess_text)
df.to_csv("data/processed_text.csv", index=False)