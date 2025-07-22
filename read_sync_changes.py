import os
import yaml
from datetime import datetime
from collections import defaultdict

LOG_FILE = "sync_changes.log"
CHARTS_FOLDER = "superset_assets/charts"
DASHBOARDS_FOLDER = "superset_assets/dashboards"
CHANGES_AFTER = "2025-07-21 17:00:00"  # Change this datetime as needed

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

def extract_chart_metadata(chart_files):
    chart_map = {}  # uuid → slice_name
    for file_path in chart_files:
        try:
            with open(file_path, "r") as f:
                chart = yaml.safe_load(f)
                uuid = chart.get("uuid")
                slice_name = chart.get("slice_name") or os.path.basename(file_path)
                if uuid:
                    chart_map[uuid] = slice_name
        except Exception as e:
            print(f"⚠️ Failed to read chart file {file_path}: {e}")
    return chart_map

def find_dashboard_chart_mapping(dashboard_folder, chart_uuid_map):
    dashboard_to_charts = defaultdict(list)

    for filename in os.listdir(dashboard_folder):
        if not filename.endswith(".yaml"):
            continue

        file_path = os.path.join(dashboard_folder, filename)
        try:
            with open(file_path, "r") as f:
                dashboard = yaml.safe_load(f)
                if not dashboard:
                    continue

                dashboard_title = dashboard.get("dashboard_title") or filename
                position_data = str(dashboard.get("position", {}))

                for uuid, slice_name in chart_uuid_map.items():
                    if uuid in position_data:
                        dashboard_to_charts[dashboard_title].append(slice_name)
        except Exception as e:
            print(f"⚠️ Failed to read dashboard file {file_path}: {e}")

    return dashboard_to_charts

if __name__ == "__main__":
    after_time = datetime.strptime(CHANGES_AFTER, "%Y-%m-%d %H:%M:%S")

    modified_chart_files = parse_logs(LOG_FILE, after_time)
    chart_uuid_map = extract_chart_metadata(modified_chart_files)
    dashboard_chart_map = find_dashboard_chart_mapping(DASHBOARDS_FOLDER, chart_uuid_map)

    if dashboard_chart_map:
        print(f"📊 Dashboards affected by modified charts ({len(dashboard_chart_map)}):")
        for dashboard_title, charts in sorted(dashboard_chart_map.items()):
            print(f"  {dashboard_title}")
            for chart_name in sorted(set(charts)):
                print(f"    - {chart_name}")
    else:
        print("✅ No dashboards affected.")
