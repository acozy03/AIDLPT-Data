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
    processed_dir = os.path.abspath("data/rated_opus")

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

                        # Check if the line contains exactly two parts separated by a tab and the ILR rating at the end
                        if "\t" in line:
                            parts = line.rsplit("\t", 2)  # Split into original text, translated text, and ILR rating
                            if len(parts) == 3:
                                original_text, translated_text, ilr_rating = parts
                                # Clean up and extract ILR rating (strip spaces)
                                ilr_rating = ilr_rating.strip()  # Keep it as a string, e.g., "1+", "2", etc.
                                
                                # Step 3: Insert original, translated text, and ILR rating into the database
                                cursor.execute("""
                                    INSERT INTO text_data (language, english_text, translated_text, ilr_level)
                                    VALUES (%s, %s, %s, %s)
                                """, (lang_code, original_text, translated_text, ilr_rating))
                            else:
                                print(f"⚠️ Skipping malformed line in {file_path}: {line}")
                        else:
                            print(f"⚠️ Skipping malformed line in {file_path}: {line}")

                print(f"✅ Processed {file_path} and inserted data into the database.")

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    store_data()
