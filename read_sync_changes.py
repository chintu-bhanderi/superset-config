import os
import yaml
from datetime import datetime

LOG_FILE = "sync_changes.log"
CHARTS_FOLDER = "superset_assets/charts"
DASHBOARDS_FOLDER = "superset_assets/dashboards"
CHANGES_AFTER = "2025-07-22 17:00:00"  # Change this datetime as needed

def parse_logs(log_file, after_dt):
    modified_charts = set()
    current_time = None

    with open(log_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# Sync run at:"):
                current_time = datetime.strptime(line.split(": ", 1)[1], "%Y-%m-%d %H:%M:%S")
            elif line and not line.startswith("#") and current_time and current_time >= after_dt:
                if line.startswith("charts/") and line.endswith(".yaml"):
                    modified_charts.add(os.path.join("superset_assets", line))

    return modified_charts

def extract_chart_uuids(chart_files):
    chart_uuids = set()
    for file_path in chart_files:
        try:
            with open(file_path, "r") as f:
                chart = yaml.safe_load(f)
                uuid = chart.get("uuid")
                if uuid:
                    chart_uuids.add(uuid)
        except Exception as e:
            print(f"⚠️ Failed to read chart file {file_path}: {e}")
    return chart_uuids

def find_dashboards_with_uuids(dashboard_folder, uuids_to_find):
    affected_dashboards = set()
    for filename in os.listdir(dashboard_folder):
        if not filename.endswith(".yaml"):
            continue
        file_path = os.path.join(dashboard_folder, filename)
        try:
            with open(file_path, "r") as f:
                dashboard = yaml.safe_load(f)
                if "position" in dashboard:
                    if any(uuid in str(dashboard["position"]) for uuid in uuids_to_find):
                        title = dashboard.get("dashboard_title")
                        if title:
                            affected_dashboards.add(title)
        except Exception as e:
            print(f"⚠️ Failed to read dashboard file {file_path}: {e}")
    return affected_dashboards

if __name__ == "__main__":
    after_time = datetime.strptime(CHANGES_AFTER, "%Y-%m-%d %H:%M:%S")

    modified_chart_files = parse_logs(LOG_FILE, after_time)
    chart_uuids = extract_chart_uuids(modified_chart_files)
    affected_dashboards = find_dashboards_with_uuids(DASHBOARDS_FOLDER, chart_uuids)

    if affected_dashboards:
        print(f"📊 Dashboards affected by modified charts ({len(affected_dashboards)}):")
        for title in sorted(affected_dashboards):
            print(f"  - {title}")
    else:
        print("✅ No dashboards affected.")
