import zipfile
import os
import shutil

# --- Config ---
ZIP_PATH = "/Users/chintukumarbhanderi/Downloads/dashboard_export_20250710T160150.zip"
DEST_FOLDER = "superset_assets"

# --- Step 1: Unzip to temp folder ---
TEMP_EXTRACT_PATH = "temp_extract"

# --- Cleanup previous temp folder ---
if os.path.exists(TEMP_EXTRACT_PATH):
    shutil.rmtree(TEMP_EXTRACT_PATH)
os.makedirs(TEMP_EXTRACT_PATH, exist_ok=True)

# --- Step 1: Extract ZIP ---
print(f"🔍 Extracting ZIP: {ZIP_PATH}")
with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
    zip_ref.extractall(TEMP_EXTRACT_PATH)

# --- Step 2: Identify root folder (e.g., dashboard_export) ---
subfolders = [name for name in os.listdir(TEMP_EXTRACT_PATH) if os.path.isdir(os.path.join(TEMP_EXTRACT_PATH, name))]
if len(subfolders) == 1:
    root_data_folder = os.path.join(TEMP_EXTRACT_PATH, subfolders[0])
else:
    root_data_folder = TEMP_EXTRACT_PATH  # fallback if no single top folder

# --- Step 3: Sync contents to superset_assets ---
print(f"🚀 Syncing extracted files from: {root_data_folder} → {DEST_FOLDER}")

for root, dirs, files in os.walk(root_data_folder):
    for file in files:
        rel_dir = os.path.relpath(root, root_data_folder)
        dest_dir = os.path.join(DEST_FOLDER, rel_dir)
        os.makedirs(dest_dir, exist_ok=True)

        src_file = os.path.join(root, file)
        dest_file = os.path.join(dest_dir, file)

        shutil.copy2(src_file, dest_file)
        print(f"✅ Copied: {src_file} → {dest_file}")

# --- Step 4: Cleanup ---
shutil.rmtree(TEMP_EXTRACT_PATH)
print("🧹 Cleanup complete.")