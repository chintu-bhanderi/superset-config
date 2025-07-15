import os
import requests
import json
from dotenv import load_dotenv

ZIP_FILE_PATH = "/Users/chintukumarbhanderi/Shipments/superset2/superset-config/assets/dashboard_export_20250715T053933.zip"

# --- Choose which .env file to load ---
ENV_PATH = ".env.local"  # or ".env.local"
load_dotenv(ENV_PATH)

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

LOGIN_URL = f"{BASE_URL}/api/v1/security/login"
IMPORT_URL = f"{BASE_URL}/api/v1/dashboard/import/"
CSRF_URL = f"{BASE_URL}/api/v1/security/csrf_token/"

session = requests.Session()

# Step 1: Login
login_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True
}

resp = session.post(LOGIN_URL, json=login_payload)
resp.raise_for_status()
access_token = resp.json()["access_token"]

# Step 2: Get CSRF Token
csrf_resp = session.get(
    CSRF_URL,
    headers={"Authorization": f"Bearer {access_token}"}
)
csrf_resp.raise_for_status()
csrf_token = csrf_resp.json()["result"]

# Step 3: Upload dashboard
with open(ZIP_FILE_PATH, "rb") as zip_file:
    files = {
        "formData": zip_file
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
        "X-CSRFToken": csrf_token,
        "Authorization": f"Bearer {access_token}",
        "Referer": BASE_URL,
        "Origin": BASE_URL,
    }

    print(f"🚀 Uploading dashboard to {BASE_URL}...")
    response = session.post(IMPORT_URL, headers=headers, data=data, files=files)

    if response.status_code == 200:
        print("✅ Import successful!")
    else:
        print(f"❌ Import failed ({response.status_code})")
        print(response.text)
