import os

# Define base directories
input_dir = os.path.abspath("data/raw_opus")  # Directory containing raw OPUS files
output_dir = os.path.abspath("data/processed_opus")  # Directory to save processed files
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

# List of target languages
target_languages = ["ms", "ta", "tg"]

# Function to process and align sentences
def process_and_align_sentences(en_file, tgt_file, output_file):
    try:
        with open(en_file, "r", encoding="utf-8", errors="replace") as en_f, open(tgt_file, "r", encoding="utf-8", errors="replace") as tgt_f:
            en_sentences = en_f.readlines()
            tgt_sentences = tgt_f.readlines()

        # Ensure the files have the same number of lines
        if len(en_sentences) != len(tgt_sentences):
            print(f"⚠️ Mismatch in line count: {len(en_sentences)} EN ↔ {len(tgt_sentences)} {tgt_file}, skipping...")
            return

        # Write aligned sentences to output file
        with open(output_file, "w", encoding="utf-8") as out_f:
            for en_sentence, tgt_sentence in zip(en_sentences, tgt_sentences):
                out_f.write(f"{en_sentence.strip()}\t{tgt_sentence.strip()}\n")

        print(f"✅ Aligned sentences saved to {output_file}")

    except Exception as e:
        print(f"⚠️ Error processing {en_file} ↔ {tgt_file}: {e}")

# Step 1: Process each language pair
for root, dirs, files in os.walk(input_dir):
    for lang_code in target_languages:
        # Find matching files for each target language
        en_file = None
        tgt_file = None
        for file in files:
            if file.endswith(f".en-{lang_code}.en"):  # English file
                en_file = os.path.join(root, file)
                tgt_file = os.path.join(root, file.replace(f".en-{lang_code}.en", f".en-{lang_code}.{lang_code}"))
                break
        
        # Ensure we found the corresponding files
        if not en_file or not tgt_file:
            print(f"⚠️ No matching files found for {lang_code} in {root}, skipping...")
            continue
        
        # Create output file for the target language
        output_file = os.path.join(output_dir, f"en-{lang_code}_aligned.txt")

        # Process and align sentences
        print(f"📖 Processing {en_file} ↔ {tgt_file}...")
        process_and_align_sentences(en_file, tgt_file, output_file)

print("🎯 All language pair processing complete!")
