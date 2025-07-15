import os
import io
import zipfile
import yaml
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# --- Load environment ---
load_dotenv(".env.local")  # or ".env.local"

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DYNAMIC_TYPE = os.getenv("DYNAMIC_TYPE", "SqlaTable")  # Optional override via .env

SUPSERSET_ASSETS_DIR = "superset_assets"

# --- Type to URL mapping ---
type_url_map = {
    "Dashboard": "dashboard",
    "Slice": "chart",
    "SqlaTable": "dataset",
}
resource_name = type_url_map.get(DYNAMIC_TYPE)
if not resource_name:
    raise ValueError(f"❌ Unknown DYNAMIC_TYPE: {DYNAMIC_TYPE}")

# --- Superset API endpoints ---
LOGIN_URL = f"{BASE_URL}/api/v1/security/login"
CSRF_URL = f"{BASE_URL}/api/v1/security/csrf_token/"
IMPORT_URL = f"{BASE_URL}/api/v1/{resource_name}/import/"

# --- Step 1: Update metadata.yaml in memory ---
metadata_path = os.path.join(SUPSERSET_ASSETS_DIR, "metadata.yaml")
if not os.path.exists(metadata_path):
    raise FileNotFoundError("❌ metadata.yaml not found in superset_assets/")

with open(metadata_path, "r") as f:
    metadata = yaml.safe_load(f)

metadata["type"] = DYNAMIC_TYPE
metadata["timestamp"] = datetime.utcnow().isoformat()

# Replace metadata.yaml content temporarily
updated_files = {}
for root, _, files in os.walk(SUPSERSET_ASSETS_DIR):
    for file in files:
        file_path = os.path.join(root, file)
        arcname = os.path.relpath(file_path, os.path.dirname(SUPSERSET_ASSETS_DIR))

        if file == "metadata.yaml":
            updated_files[arcname] = yaml.dump(metadata)
        else:
            with open(file_path, "rb") as f:
                updated_files[arcname] = f.read()

# --- Step 2: Create ZIP in memory ---
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for arcname, content in updated_files.items():
        if isinstance(content, str):
            content = content.encode("utf-8")
        zipf.writestr(arcname, content)
print(f"📦 ZIP archive prepared in memory for {DYNAMIC_TYPE}")
print(f"📦 Import URL: {IMPORT_URL}")

# --- Step 3: Superset Login ---
session = requests.Session()
login_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True
}
print("🔐 Logging in...")
login_resp = session.post(LOGIN_URL, json=login_payload)
login_resp.raise_for_status()
access_token = login_resp.json()["access_token"]

# --- Step 4: Get CSRF Token ---
csrf_resp = session.get(
    CSRF_URL,
    headers={"Authorization": f"Bearer {access_token}"}
)
csrf_resp.raise_for_status()
csrf_token = csrf_resp.json()["result"]

# --- Step 5: Import ZIP (in memory) ---
zip_buffer.seek(0)
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
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {access_token}",
    "X-CSRFToken": csrf_token,
    "Referer": BASE_URL,
    "Origin": BASE_URL,
}

print(f"🚀 Uploading {DYNAMIC_TYPE} to Superset...")
resp = session.post(IMPORT_URL, headers=headers, data=data, files=files)

if resp.status_code == 200:
    print(f"✅ {DYNAMIC_TYPE} import successful!")
else:
    print(f"❌ {DYNAMIC_TYPE} import failed ({resp.status_code})")
    print(resp.text)
