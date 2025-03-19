import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def store_data():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Define the directory containing processed files
    processed_dir = os.path.abspath("data/processed_opus")

    # Step 1: Loop through the processed .txt files
    for root, dirs, files in os.walk(processed_dir):
        for file in files:
            if file.endswith("_aligned.txt"):  # Process only aligned text files
                lang_code = file.split("-")[1].split("_")[0]  # Extract language code from the filename
                file_path = os.path.join(root, file)

                # Step 2: Read the aligned sentences
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()  # Remove leading/trailing whitespace
                        if not line:  # Skip empty lines
                            continue

                        # Check if the line contains exactly two parts separated by a tab
                        if "\t" in line:
                            original_text, cleaned_text = line.split("\t", 1)
                            # Step 3: Insert original and cleaned text into the database
                            cursor.execute("""
                                INSERT INTO text_data (language, original_text, cleaned_text)
                                VALUES (%s, %s, %s)
                            """, (lang_code, original_text, cleaned_text))
                        else:
                            print(f"⚠️ Skipping malformed line in {file_path}: {line}")

                print(f"✅ Processed {file_path} and inserted data into the database.")

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    store_data()
