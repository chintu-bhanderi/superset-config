import os
import yaml
from datetime import datetime

LOG_FILE = "sync_changes.log"
ASSETS_BASE = "superset_assets"
CHANGES_AFTER = "2025-07-21 17:00:00"

def parse_logs(log_file, after_dt):
    modified = {"charts": [], "dashboards": [], "datasets": []}
    current_time = None

    with open(log_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# Sync run at:"):
                current_time = datetime.strptime(line.split(": ", 1)[1], "%Y-%m-%d %H:%M:%S")
            elif line and not line.startswith("#") and current_time and current_time >= after_dt:
                if line.startswith("charts/"):
                    modified["charts"].append(os.path.join(ASSETS_BASE, line))
                elif line.startswith("dashboards/"):
                    modified["dashboards"].append(os.path.join(ASSETS_BASE, line))
                elif line.startswith("datasets/"):
                    modified["datasets"].append(os.path.join(ASSETS_BASE, line))
    return modified

def get_titles_from_yaml(paths, key):
    titles = []
    for path in paths:
        try:
            with open(path, "r") as f:
                content = yaml.safe_load(f)
                title = content.get(key)
                if title:
                    titles.append(title)
        except Exception as e:
            print(f"⚠️ Error reading {path}: {e}")
    return sorted(set(titles))

def get_chart_info(chart_paths):
    charts = []
    for path in chart_paths:
        try:
            with open(path, "r") as f:
                content = yaml.safe_load(f)
                slice_name = content.get("slice_name")
                if slice_name:
                    charts.append(slice_name)
        except Exception as e:
            print(f"⚠️ Error reading chart {path}: {e}")
    return sorted(set(charts))

def get_chart_uuid_map(chart_paths):
    uuid_map = {}
    for path in chart_paths:
        try:
            with open(path, "r") as f:
                content = yaml.safe_load(f)
                uuid_map[content.get("uuid")] = content.get("slice_name")
        except Exception:
            pass
    return uuid_map

def get_affected_dashboards(chart_uuid_map):
    affected = {}
    dashboards_dir = os.path.join(ASSETS_BASE, "dashboards")

    for fname in os.listdir(dashboards_dir):
        fpath = os.path.join(dashboards_dir, fname)
        try:
            with open(fpath, "r") as f:
                data = yaml.safe_load(f)
                dashboard_title = data.get("dashboard_title")
                chart_uuids = [uuid for uuid in chart_uuid_map if uuid in str(data)]
                if chart_uuids:
                    affected[dashboard_title] = [chart_uuid_map[u] for u in chart_uuids]
        except Exception:
            pass
    return affected

if __name__ == "__main__":
    after_dt = datetime.strptime(CHANGES_AFTER, "%Y-%m-%d %H:%M:%S")
    modified = parse_logs(LOG_FILE, after_dt)

    dataset_names = get_titles_from_yaml(modified["datasets"], "table_name")
    chart_uuid_map = get_chart_uuid_map(modified["charts"])
    affected_dashboards = get_affected_dashboards(chart_uuid_map)

    modified_chart_names = sorted(set(chart_uuid_map.values()))

    if dataset_names:
        print(f"\n🧮 Modified Datasets ({len(dataset_names)}):")
        for name in dataset_names:
            print(f"  - {name}")

    if modified_chart_names:
        print(f"\n📈 Modified Charts ({len(modified_chart_names)}):")
        for name in modified_chart_names:
            print(f"  - # {name}")

    if affected_dashboards:
        print(f"\n📊 Dashboards affected by modified charts ({len(affected_dashboards)}):")
        for dash, charts in affected_dashboards.items():
            print(f"  {dash}")
            for chart in charts:
                print(f"    - # {chart}")
