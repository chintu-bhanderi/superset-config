import os
import zipfile
import yaml  # Requires PyYAML
from datetime import datetime

# --- Config ---
DYNAMIC_TYPE = "Dashboard"  # <-- Change this dynamically as needed
FOLDER_TO_ZIP = "/Users/chintukumarbhanderi/Shipments/superset2/superset-config/superset_assets"
OUTPUT_ZIP = f"/Users/chintukumarbhanderi/Shipments/superset2/superset-config/assets/{DYNAMIC_TYPE.lower()}_data.zip"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_ZIP), exist_ok=True)

# --- Update metadata.yaml ---
metadata_path = os.path.join(FOLDER_TO_ZIP, "metadata.yaml")

if os.path.exists(metadata_path):
    with open(metadata_path, "r") as f:
        metadata = yaml.safe_load(f)

    metadata["type"] = DYNAMIC_TYPE
    metadata["timestamp"] = datetime.utcnow().isoformat()

    with open(metadata_path, "w") as f:
        yaml.dump(metadata, f)

    print(f"🔁 metadata.yaml updated with type: {DYNAMIC_TYPE}")
else:
    print("❌ metadata.yaml not found. Skipping update.")

# --- Create ZIP ---
with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(FOLDER_TO_ZIP):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, os.path.dirname(FOLDER_TO_ZIP))
            zipf.write(file_path, arcname)
            print(f"✅ Added: {arcname}")

print(f"\n📦 ZIP file created at: {OUTPUT_ZIP}")
