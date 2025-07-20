import os
import json
import yaml
from dotenv import load_dotenv

load_dotenv(".env.local")  # Or .env.local / .env.staging as per your environment
ASSET_DIR = "superset_assets"

def get_replacements():
    try:
        replacements = json.loads(os.getenv("REPLACE_MAP", "[]"))
        return [(item["from"], item["to"]) for item in replacements if "from" in item and "to" in item]
    except json.JSONDecodeError as e:
        print("❌ Failed to parse REPLACE_MAP in .env:", e)
        return []

def replace_strings_in_yaml(filepath: str, replacements: list[tuple[str, str]]):
    with open(filepath, "r") as file:
        content = file.read()

    original_content = content
    for old, new in replacements:
        content = content.replace(old, new)

    if content != original_content:
        with open(filepath, "w") as file:
            file.write(content)
        # print(f"✅ Updated: {filepath}")
        return True
    return False

def update_all_yaml_files(replacements):
    count = 0
    for root, _, files in os.walk(ASSET_DIR):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                full_path = os.path.join(root, file)
                if replace_strings_in_yaml(full_path, replacements):
                    count += 1
    print(f"\n🎯 Total files updated: {count}")

if __name__ == "__main__":
    replacements = get_replacements()
    if not replacements:
        print("❌ No replacements found. Check REPLACE_MAP in your .env file.")
    else:
        print(f"🔁 Starting replacements for {len(replacements)} entries...")
        update_all_yaml_files(replacements)
