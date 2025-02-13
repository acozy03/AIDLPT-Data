import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def store_data():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    df = pd.read_csv("data/processed_text.csv")
    for _, row in df.iterrows():
        cursor.execute("INSERT INTO text_data (language, original_text, cleaned_text) VALUES (%s, %s, %s)",
                       (row["language"], row["text"], row["clean_text"]))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    store_data()
