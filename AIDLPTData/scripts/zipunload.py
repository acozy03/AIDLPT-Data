import os
import zipfile

# Define the directory where ZIP files are stored
download_dir = os.path.abspath("data/raw_opus")
extract_dir = os.path.abspath("data/extracted_opus")

# Ensure the extraction directory exists
os.makedirs(extract_dir, exist_ok=True)

# Loop through all ZIP files in the download directory
for file in os.listdir(download_dir):
    if file.endswith(".zip"):
        zip_path = os.path.join(download_dir, file)
        try:
            # Open and extract the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                print(f"✅ Extracted: {file}")
            
            # Delete the ZIP file after successful extraction
            os.remove(zip_path)
            print(f"🗑️ Deleted: {file}")
        
        except zipfile.BadZipFile:
            print(f"❌ Error: The file {file} is not a valid ZIP file.")
        except Exception as e:
            print(f"❌ Error extracting or deleting {file}: {e}")

print("🎯 All ZIP files processed successfully!")