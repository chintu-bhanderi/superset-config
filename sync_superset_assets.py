import os
import json
import requests
import zipfile
import shutil
import io
from dotenv import load_dotenv
from datetime import datetime

# --- Load .env ---
load_dotenv(".env.staging")  # or .env.local

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
EXPORT_IDS = os.getenv("EXPORT_IDS", "62")
DEST_FOLDER = "superset_assets"

# --- URLs ---
LOGIN_URL = f"{BASE_URL}/api/v1/security/login"
CSRF_URL = f"{BASE_URL}/api/v1/security/csrf_token/"
EXPORT_URL = f"{BASE_URL}/api/v1/dashboard/export"

# --- Start session and authenticate ---
session = requests.Session()

print("🔐 Logging in...")
login_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True
}

login_resp = session.post(LOGIN_URL, json=login_payload)
login_resp.raise_for_status()
access_token = login_resp.json()["access_token"]

# --- Get CSRF token ---
csrf_headers = {"Authorization": f"Bearer {access_token}"}
csrf_resp = session.get(CSRF_URL, headers=csrf_headers)
csrf_resp.raise_for_status()
csrf_token = csrf_resp.json()["result"]

# --- Export dashboard (download ZIP in memory) ---
dashboard_ids = EXPORT_IDS.split(",")
q_param = f"!({','.join(dashboard_ids)})"
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {access_token}",
    "X-CSRFToken": csrf_token,
    "Referer": BASE_URL,
    "Origin": BASE_URL,
}

print(f"📦 Export URL: {EXPORT_URL}")
print(f"🚀 Exporting dashboards: {dashboard_ids}")
export_resp = session.get(EXPORT_URL, headers=headers, params={"q": q_param})
export_resp.raise_for_status()

# --- Extract ZIP from memory ---
print("📦 Extracting ZIP content from memory...")
TEMP_EXTRACT_PATH = "temp_extract"
if os.path.exists(TEMP_EXTRACT_PATH):
    shutil.rmtree(TEMP_EXTRACT_PATH)
os.makedirs(TEMP_EXTRACT_PATH, exist_ok=True)

with zipfile.ZipFile(io.BytesIO(export_resp.content)) as zip_ref:
    zip_ref.extractall(TEMP_EXTRACT_PATH)

# --- Detect root data folder ---
subfolders = [
    name for name in os.listdir(TEMP_EXTRACT_PATH)
    if os.path.isdir(os.path.join(TEMP_EXTRACT_PATH, name))
]
root_data_folder = (
    os.path.join(TEMP_EXTRACT_PATH, subfolders[0])
    if len(subfolders) == 1 else TEMP_EXTRACT_PATH
)

# --- Sync to superset_assets and detect changes ---
print(f"📁 Syncing to: {DEST_FOLDER}")
modified_files = []

for root, dirs, files in os.walk(root_data_folder):
    for file in files:
        rel_dir = os.path.relpath(root, root_data_folder)
        dest_dir = os.path.join(DEST_FOLDER, rel_dir)
        os.makedirs(dest_dir, exist_ok=True)

        src_file = os.path.join(root, file)
        dest_file = os.path.join(dest_dir, file)

        # Compare contents (if destination exists)
        if os.path.exists(dest_file):
            with open(src_file, "rb") as f1, open(dest_file, "rb") as f2:
                if f1.read() != f2.read():
                    modified_files.append(os.path.join(rel_dir, file))
                    shutil.copy2(src_file, dest_file)
        else:
            modified_files.append(os.path.join(rel_dir, file))
            shutil.copy2(src_file, dest_file)

# # --- Output modified files ---
# print("📝 Modified or new files:")
# if modified_files:
#     for f in modified_files:
#         print(f" - {f}")
# else:
#     print("✅ No files were modified.")

# --- Append changes to logs file ---
LOG_FILE = "sync_changes.log"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(LOG_FILE, "a") as log:
    log.write(f"# Sync run at: {timestamp}\n")
    if modified_files:
        for f in modified_files:
            log.write(f"{f}\n")
    else:
        log.write("No files modified.\n")
    log.write("\n")

# --- Cleanup temp folder ---
shutil.rmtree(TEMP_EXTRACT_PATH)
print("🧹 Cleanup complete.")
