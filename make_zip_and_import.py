import os
import io
import zipfile
import yaml
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# --- Load environment ---
load_dotenv(".env.local")  # Change to ".env.staging" if needed

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
ASSETS_BASE_DIR = "superset_assets"  # Expects folders like: superset_assets/Dashboard, superset_assets/Slice, etc.

# --- Type to API path mapping ---
type_url_map = {
    "Dashboard": "dashboard",
    "Slice": "chart",
    "SqlaTable": "dataset",
}

# --- Superset API endpoints ---
LOGIN_URL = f"{BASE_URL}/api/v1/security/login"
CSRF_URL = f"{BASE_URL}/api/v1/security/csrf_token/"

# --- Step 1: Superset login session ---
print("🔐 Logging in...")
session = requests.Session()
login_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True
}
login_resp = session.post(LOGIN_URL, json=login_payload)
login_resp.raise_for_status()
access_token = login_resp.json()["access_token"]

# --- Step 2: Get CSRF Token ---
csrf_resp = session.get(CSRF_URL, headers={"Authorization": f"Bearer {access_token}"})
csrf_resp.raise_for_status()
csrf_token = csrf_resp.json()["result"]

# --- Step 3: Process each type ---
for DYNAMIC_TYPE, api_segment in type_url_map.items():
    folder_path = ASSETS_BASE_DIR  # Use the same base folder always
    metadata_path = os.path.join(folder_path, "metadata.yaml")
    IMPORT_URL = f"{BASE_URL}/api/v1/{api_segment}/import/"

    if not os.path.exists(metadata_path):
        print(f"⚠️ Skipping {DYNAMIC_TYPE} — metadata.yaml not found in {folder_path}")
        continue

    # Update metadata.yaml content in memory
    with open(metadata_path, "r") as f:
        metadata = yaml.safe_load(f)

    metadata["type"] = DYNAMIC_TYPE
    metadata["timestamp"] = datetime.utcnow().isoformat()

    # Collect updated files into memory
    updated_files = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, os.path.dirname(folder_path))

            if file == "metadata.yaml":
                updated_files[arcname] = yaml.dump(metadata)
            else:
                with open(file_path, "rb") as f:
                    updated_files[arcname] = f.read()

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arcname, content in updated_files.items():
            if isinstance(content, str):
                content = content.encode("utf-8")
            zipf.writestr(arcname, content)

    zip_buffer.seek(0)

    # Make the import request
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-CSRFToken": csrf_token,
        "Referer": BASE_URL,
        "Origin": BASE_URL,
    }
    files = {
        "formData": ("import.zip", zip_buffer, "application/zip")
    }
    data = {
        "overwrite": "true",
        "passwords": json.dumps({}),
        "ssh_tunnel_passwords": json.dumps({}),
        "ssh_tunnel_private_keys": json.dumps({}),
        "ssh_tunnel_private_key_passwords": json.dumps({})
    }

    print(f"🚀 Uploading {DYNAMIC_TYPE} to {IMPORT_URL}...")
    resp = session.post(IMPORT_URL, headers=headers, data=data, files=files)

    if resp.status_code == 200:
        print(f"✅ {DYNAMIC_TYPE} import successful!")
    else:
        print(f"❌ {DYNAMIC_TYPE} import failed ({resp.status_code})")
        print(resp.text)

print("\n🎯 All import processes complete.")
