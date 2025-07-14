import requests
import os
import urllib.parse

# --- Config ---
dashboard_ids = [41, 38]

# Encode the q parameter properly
url = f"https://superset.staging.shipmnts.com/api/v1/dashboard/export"

params = {
    "q": f"!({','.join(map(str, dashboard_ids))})"
}

# Cookies (copied from your browser)
cookies = {
    "ajs_anonymous_id": '"d80bb9ec-0246-4532-8e66-6a6de3b4f8de"',
    "_clck": "jm05qb|2|fxf|0|2015",
    "cf_clearance": "oabkgS3kPz0WLHTbTUjGedLvXZ_FvlH6VrHqi3POzFw-1752036686-1.2.1.1-kqyz09HWLgh9wx2GtbONZzjx8EyxrFaj0s_eH4vH3z.h3Ff71_GFXcQNigoBgBa87WRdiuAzVFWAZYID0hMeQeGguqjk9fVYzbtYvm74vGCTeUXffvEWEDiecNZ9EWcU3yrlFMyvn.BJTSI78KYthapdFJu5VpIW5fWwsgczboAfN1kSlB7DLO7rNMnpUdLPazNEpejWslT6n_Ed5r51QphwVwZuvuIyh7HflH6Bvkc",
    "session": ".eJwljstKBTEQRP8laxfpR9LJ_Zkh_UJx8MKMrsR_N2Jtiio4cL7LkVfcr-WR67zjpRxvXh5FjFByhawOCrsJREbMqc3dqwINURJPzKbUq1TXZubedRBi0JiVsdYxkYRbN2AnckaEOgcuTeu9ayzmJAlHoFWxolrzvhzLFvm64_q3-Zt2X3l8Pt_jYx_ELQHRwYKThQeGWcJEJ2vWdibGcNnc-bR1xmY2-PMLfqJDIA.aG-LSg.Yg-sCuNktoca2-MhS0I_pGzbRmA"
}

output_dir = "assets"
output_file = f"exported_dashboard.zip"
os.makedirs(output_dir, exist_ok=True)

print(f"Requesting dashboard export from: {url}")
response = requests.get(url, params=params, cookies=cookies)

if response.status_code == 200:
    print('success->')
    file_path = os.path.join(output_dir, output_file)
    with open(file_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Exported dashboard ZIP saved to {file_path}")
else:
    print(f"❌ Failed. Status: {response.status_code}")
    print(response.text)
