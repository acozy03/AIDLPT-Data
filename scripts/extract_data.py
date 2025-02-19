import os
import subprocess

# Define OPUS tools directory (where opus_get is located)
opus_dir = r"D:\Adrian\AIDLPTData\myenv\Scripts"

# Define download directory
download_dir = os.path.abspath("data/raw_opus")
os.makedirs(download_dir, exist_ok=True)  # Ensure the folder exists

# OPUS datasets to download
datasets = [
    ("en", "fr", "OpenSubtitles"),
    ("en", "es", "Europarl"),
    ("en", "zh", "NewsCommentary")
]

# Loop through datasets and download them
for src, tgt, dataset in datasets:
    # Change directory to OPUS tools and run command
    command = f'cd /d "{opus_dir}" && python opus_get -s {src} -t {tgt} -d {dataset} -p raw -dl "{download_dir}"'
    
    print(f"Downloading {dataset} ({src}-{tgt}) into {download_dir}...")
    subprocess.run(command, shell=True)

print("✅ All OPUS datasets downloaded successfully!")
