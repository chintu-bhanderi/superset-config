import os
import yaml
from datetime import datetime

LOG_FILE = "sync_changes.log"
ASSETS_BASE = "superset_assets"
CHANGES_AFTER = "2025-07-22 18:43:38"

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

def load_yaml(path):
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}

def get_titles_from_yaml(paths, key):
    titles = []
    for path in paths:
        content = load_yaml(path)
        title = content.get(key)
        if title:
            titles.append(title)
    return sorted(set(titles))

def get_chart_info(chart_paths):
    chart_map = {}
    for path in chart_paths:
        content = load_yaml(path)
        uuid = content.get("uuid")
        name = content.get("slice_name")
        dataset_uuid = content.get("dataset_uuid")
        if uuid and name:
            chart_map[uuid] = {
                "name": name,
                "dataset_uuid": dataset_uuid
            }
    return chart_map

def get_dataset_uuid_map(dataset_paths):
    dataset_uuid_map = {}
    for path in dataset_paths:
        content = load_yaml(path)
        uuid = content.get("uuid")
        name = content.get("table_name")
        if uuid and name:
            dataset_uuid_map[uuid] = name
    return dataset_uuid_map

def find_charts_by_dataset(dataset_uuids, charts_dir):
    affected_charts = {}
    for fname in os.listdir(charts_dir):
        chart_path = os.path.join(charts_dir, fname)
        chart = load_yaml(chart_path)
        if chart.get("dataset_uuid") in dataset_uuids:
            affected_charts[chart.get("uuid")] = chart.get("slice_name")
    return affected_charts

def get_affected_dashboards(chart_uuid_map):
    affected = {}
    dashboards_dir = os.path.join(ASSETS_BASE, "dashboards")

    for fname in os.listdir(dashboards_dir):
        fpath = os.path.join(dashboards_dir, fname)
        content = load_yaml(fpath)
        dashboard_title = content.get("dashboard_title")
        chart_uuids = [uuid for uuid in chart_uuid_map if uuid in str(content)]
        if dashboard_title and chart_uuids:
            affected.setdefault(dashboard_title, [])
            for uuid in chart_uuids:
                affected[dashboard_title].append(chart_uuid_map[uuid]["name"])
    return affected

if __name__ == "__main__":
    after_dt = datetime.strptime(CHANGES_AFTER, "%Y-%m-%d %H:%M:%S")
    modified = parse_logs(LOG_FILE, after_dt)

    dataset_names = get_titles_from_yaml(modified["datasets"], "table_name")
    dataset_uuid_map = get_dataset_uuid_map(modified["datasets"])

    # Existing modified charts
    chart_map_direct = get_chart_info(modified["charts"])

    # Charts affected by modified datasets
    affected_charts_by_dataset = find_charts_by_dataset(dataset_uuid_map.keys(), os.path.join(ASSETS_BASE, "charts"))
    chart_map_dataset = {
        uuid: {"name": name, "dataset_uuid": None}
        for uuid, name in affected_charts_by_dataset.items()
    }

    # Merge all charts
    merged_chart_map = {**chart_map_direct, **chart_map_dataset}

    # Get affected dashboards (from all modified/affected charts)
    affected_dashboards = get_affected_dashboards(merged_chart_map)

    # Unique chart names
    all_chart_names = sorted({v["name"] for v in merged_chart_map.values()})

    if dataset_names:
        print(f"\n🧮 Modified Datasets ({len(dataset_names)}):")
        for name in dataset_names:
            print(f"  - {name}")

    if all_chart_names:
        print(f"\n📈 Modified Charts ({len(all_chart_names)}):")
        for name in all_chart_names:
            print(f"  - {name}")

    if affected_dashboards:
        print(f"\n📊 Dashboards affected by modified charts ({len(affected_dashboards)}):")
        for dash, charts in affected_dashboards.items():
            print(f"  {dash}")
            for chart in sorted(set(charts)):
                print(f"    - {chart}")
