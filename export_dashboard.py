import os
import json
import requests
from dotenv import load_dotenv

# --- Load .env file ---
load_dotenv(".env.staging")  # or use ".env.local"

BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
EXPORT_IDS = "41,38"
EXPORT_DIR = "assets"
EXPORT_FILE = "exported_dashboard1.zip"

LOGIN_URL = f"{BASE_URL}/api/v1/security/login"
CSRF_URL = f"{BASE_URL}/api/v1/security/csrf_token/"
EXPORT_URL = f"{BASE_URL}/api/v1/assets/export/"

# --- Authenticate ---
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

# --- Get CSRF Token ---
csrf_headers = {"Authorization": f"Bearer {access_token}"}
csrf_resp = session.get(CSRF_URL, headers=csrf_headers)
csrf_resp.raise_for_status()
csrf_token = csrf_resp.json()["result"]

# --- Export Dashboard ---
dashboard_ids = EXPORT_IDS.split(",")
q_param = f"!({','.join(dashboard_ids)})"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {access_token}",
    "X-CSRFToken": csrf_token,
    "Referer": BASE_URL,
    "Origin": BASE_URL,
}

print(f"🚀 Requesting dashboard export: {dashboard_ids}")
export_resp = session.get(EXPORT_URL, headers=headers)

# --- Save File ---
if export_resp.status_code == 200:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    file_path = os.path.join(EXPORT_DIR, EXPORT_FILE)
    with open(file_path, "wb") as f:
        f.write(export_resp.content)
    print(f"✅ Exported dashboard ZIP saved to: {file_path}")
else:
    print(f"❌ Export failed ({export_resp.status_code})")
    print(export_resp.text)