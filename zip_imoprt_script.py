import requests
import json

# --- Config ---
API_URL = "http://10.0.0.119:9000/api/v1/dataset/import/"
ZIP_FILE_PATH = "/Users/chintukumarbhanderi/Shipments/superset2/superset-config/assets/superset_assets_export.zip"

# Use the session cookie from your browser (copy from DevTools > Application > Cookies)
SESSION_COOKIE = "session=.eJwljktqBDEMRO_idRaSbcnyXKaR9SEhQwa6Z1Zh7h5DdlVFPXi_5cgzrs9ye56v-CjHl5dbyeDwwB42VYgTvSbi2mEiYR8TljZtU0lUcImECAMhLxdq3XOZ9umYlbH2YTFzv6zCgsUcROpNobHBWOaOoFDFQCdgzgajbJHXFee_De5q15nH8_EdP3vg7ElqXN1bKMAYNerI7Fs4KZUmylC1zd0fpvfYzAbff8A8RFQ.aHDFGw.KMD-bVSiOf1IW_Y41YIvEv2Z2o0"

# --- Prepare headers and cookies ---
headers = {
    "Accept": "application/json"
}

cookies = {
    "session": SESSION_COOKIE
}

# --- Prepare the multipart form data ---
with open(ZIP_FILE_PATH, 'rb') as zip_file:
    # "files" is used for binary fields (like formData); these fields simulate a form-data payload
    multipart_data = {
        "formData": zip_file,  # <- not a tuple! just file object
        "overwrite": True,
        "passwords": (None, json.dumps({}), "application/json"),
        "ssh_tunnel_passwords": (None, json.dumps({}), "application/json"),
        "ssh_tunnel_private_keys": (None, json.dumps({}), "application/json"),
        "ssh_tunnel_private_key_passwords": (None, json.dumps({}), "application/json"),
    }

    # --- Make POST request ---
    print(f"🚀 Importing dashboard to {API_URL}")
    response = requests.post(API_URL, headers=headers, cookies=cookies, files=multipart_data)
    print('response', response)

# --- Check result ---
if response.status_code == 200:
    print("✅ Import successful!")
else:
    print(f"❌ Import failed. Status code: {response.status_code}")
    print(response.text)