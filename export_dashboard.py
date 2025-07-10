import requests
import os
import urllib.parse

# --- Config ---
dashboard_id = 38
api_token = "Iy11hoWxD"  # You should move this to env var for production

# Encode the q parameter properly
query_param = urllib.parse.quote(f"!({dashboard_id})")
url = f"https://superset.staging.shipmnts.com/api/v1/dashboard/export/?q={query_param}"

headers = {
    "Authorization": f"Bearer {api_token}",
    "Accept": "application/zip",
    "Content-Type": "application/json"
}

output_dir = "assets"
output_file = f"dashboard_{dashboard_id}_export.zip"
os.makedirs(output_dir, exist_ok=True)

print(f"Requesting dashboard export from: {url}")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    file_path = os.path.join(output_dir, output_file)
    with open(file_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Exported dashboard ZIP saved to {file_path}")
else:
    print(f"❌ Failed. Status: {response.status_code}")
    print(response.text)
