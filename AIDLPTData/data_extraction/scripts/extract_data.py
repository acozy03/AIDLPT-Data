import os
import subprocess
import time

# Define OPUS tools directory (where opus_get is located)
opus_dir = r"D:\Adrian\AIDLPTData\AIDLPTData\myenv\Scripts"

# Define download directory
download_dir = os.path.abspath("data/raw_opus")
os.makedirs(download_dir, exist_ok=True)  # Ensure the folder exists

# OPUS datasets to download
datasets = [
    ("en", "tg", "TED2020"), # English-Tajik
    ("en", "ta", "Josuha-IPC"), # English-Tamil
    ("en", "ms", "QED"), # English-Malay
]

def download_opus_data(src, tgt, dataset):
    """Download OPUS dataset using opus_get"""
    command = f'cd /d "{opus_dir}" && python opus_get -s {src} -t {tgt} -d {dataset} -p raw -dl "{download_dir}"'
    
    print(f"Downloading {dataset} ({src}-{tgt}) into {download_dir}...")
    print(f"Running command: {command}")
    
    # Run the command and capture output
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)
    
    # Check if download was successful
    if process.returncode != 0:
        print(f"⚠️ Download process returned non-zero exit code: {process.returncode}")
        return False
    
    # Give some time for file system operations to complete
    print("Waiting for file operations to complete...")
    time.sleep(3)
    
    # List files in download directory to verify
    print(f"Contents of download directory ({download_dir}):")
    for file in os.listdir(download_dir):
        print(f"  - {file}")
    
    return True

def main():
    print(f"Starting OPUS data download...")
    print(f"Download directory: {download_dir}")
    
    for src, tgt, dataset in datasets:
        print(f"\n{'='*80}\nDownloading {dataset} ({src}-{tgt})\n{'='*80}")
        
        if download_opus_data(src, tgt, dataset):
            print(f"✅ Download completed for {dataset} ({src}-{tgt})")
        else:
            print(f"⚠️ Download failed for {dataset} ({src}-{tgt})")
    
    print("\n✅ All OPUS downloads completed!")
    print(f"Downloaded data is available in: {download_dir}")

if __name__ == "__main__":
    main()