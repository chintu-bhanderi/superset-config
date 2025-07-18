import os
import requests
import json
from dotenv import load_dotenv

# --- Config ---
ZIP_FILE_PATH = "/Users/chintukumarbhanderi/Shipments/superset2/superset-config/assets/exported_dashboard1.zip"
ENV_PATH = ".env.local"

# --- Load environment variables ---
load_dotenv(ENV_PATH)

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

LOGIN_URL = f"{BASE_URL}/api/v1/security/login"
IMPORT_URL = f"{BASE_URL}/api/v1/assets/import/"
CSRF_URL = f"{BASE_URL}/api/v1/security/csrf_token/"

session = requests.Session()

# --- Step 1: Login ---
login_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True
}

print("🔐 Logging in...")
resp = session.post(LOGIN_URL, json=login_payload)
resp.raise_for_status()
access_token = resp.json()["access_token"]

# --- Step 2: Get CSRF Token ---
csrf_resp = session.get(
    CSRF_URL,
    headers={"Authorization": f"Bearer {access_token}"}
)
csrf_resp.raise_for_status()
csrf_token = csrf_resp.json()["result"]

# --- Step 3: Upload asset bundle ---
with open(ZIP_FILE_PATH, "rb") as zip_file:
    files = {
        "bundle": ("assets.zip", zip_file, "application/zip")
    }

    data = {
        "passwords": json.dumps({}),  # Example: {"databases/MyDatabase.yaml": "secret"}
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

    print(f"🚀 Uploading assets to {IMPORT_URL}...")
    response = session.post(IMPORT_URL, headers=headers, files=files, data=data)

    if response.status_code == 200:
        print("✅ Assets import successful!")
        print("📦 Response:", response.json())
    else:
        print(f"❌ Import failed ({response.status_code})")
        print(response.text)
