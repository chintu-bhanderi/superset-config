import requests

BASE_URL = "http://localhost:9000"
USERNAME = "admin"
PASSWORD = "admin"

session = requests.Session()

# Step 1: Login
print("🔐 Logging in...")
login_url = f"{BASE_URL}/api/v1/security/login"
login_payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True,
}
resp = session.post(login_url, json=login_payload)
resp.raise_for_status()
access_token = resp.json()["access_token"]

# Step 2: Get CSRF Token
csrf_url = f"{BASE_URL}/api/v1/security/csrf_token/"
csrf_resp = session.get(csrf_url, headers={"Authorization": f"Bearer {access_token}"})
csrf_resp.raise_for_status()
csrf_token = csrf_resp.json()["result"]

# Set headers for further requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "X-CSRFToken": csrf_token,
    "Referer": BASE_URL,
    "Origin": BASE_URL,
    "Content-Type": "application/json",
}

# Step 3: Get all chart IDs
chart_ids = []
page = 0
page_size = 100

while True:
    params = {
        "q": f"(order_column:changed_on_delta_humanized,order_direction:desc,page:{page},page_size:{page_size})"
    }
    res = session.get(f"{BASE_URL}/api/v1/dataset", headers=headers, params=params)
    res.raise_for_status()
    result = res.json().get("result", [])
    if not result:
        break
    chart_ids.extend([str(chart["id"]) for chart in result])
    page += 1

if not chart_ids:
    print("✅ No charts found.")
else:
    print(f"🗑️ Deleting {len(chart_ids)} charts...")
    ids_str = ",".join(chart_ids)
    delete_url = f"{BASE_URL}/api/v1/dataset?q=!({ids_str})"
    delete_res = session.delete(delete_url, headers=headers)
    if delete_res.status_code == 200:
        print("✅ Bulk delete successful!")
    else:
        print(f"❌ Bulk delete failed ({delete_res.status_code})")
        print(delete_res.text)
