import os
import zipfile

# --- Config ---
FOLDER_TO_ZIP = "/Users/chintukumarbhanderi/Shipments/superset2/superset-config/superset_assets"
OUTPUT_ZIP = "/Users/chintukumarbhanderi/Shipments/superset2/superset-config/assets/superset_assets_export.zip"
# OUTPUT_ZIP = "/Users/chintukumarbhanderi/Downloads/superset_assets_export.zip"

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_ZIP), exist_ok=True)

print(f"thiss0")
# --- Create ZIP ---
with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
    print(f"thiss1")
    for root, dirs, files in os.walk(FOLDER_TO_ZIP):
        print(f"thiss2")
        for file in files:
            print(f"thiss21")
            file_path = os.path.join(root, file)
            # This preserves the "superset_assets/" top-level path
            print(f"thiss3")
            arcname = os.path.relpath(file_path, os.path.dirname(FOLDER_TO_ZIP))
            zipf.write(file_path, arcname)
            print(f"✅ Added: {arcname}")

print(f"\n📦 ZIP file created at: {OUTPUT_ZIP}")
