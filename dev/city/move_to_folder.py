"""
Move all City Builder items in Fabric Arcade Test into a folder
named "City Builder".
"""
from __future__ import annotations
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dev" / "cathedral"))
from upload_notebook import WORKSPACE_ID, FABRIC_API, _headers  # noqa: E402

FOLDER_NAME = "City Builder"
ITEM_NAMES = {
    "Datapolis_LH",
    "Datapolis_DW",
    "Datapolis_EH",
    "CityBuilder_Seed",
    "CityBuilder_Mayor",
    "CityBuilder_Dashboard",
}


def list_items() -> list[dict]:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items",
                     headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json().get("value", [])


def list_folders() -> list[dict]:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/folders",
                     headers=_headers(), timeout=60)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json().get("value", [])


def get_or_create_folder(name: str) -> str:
    for f in list_folders():
        if f.get("displayName") == name:
            print(f"[folder] reuse '{name}' -> {f['id']}")
            return f["id"]
    r = requests.post(
        f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/folders",
        headers=_headers(),
        json={"displayName": name},
        timeout=60,
    )
    if r.status_code not in (200, 201):
        print(f"[folder] create failed: {r.status_code} {r.text}")
        r.raise_for_status()
    fid = r.json().get("id")
    print(f"[folder] created '{name}' -> {fid}")
    return fid


def move_item(item_id: str, item_name: str, folder_id: str) -> bool:
    url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items/{item_id}/move"
    r = requests.post(url, headers=_headers(),
                      json={"targetFolderId": folder_id}, timeout=60)
    if r.status_code in (200, 202):
        print(f"[move]  {item_name:<24} OK")
        return True
    print(f"[move]  {item_name:<24} {r.status_code} {r.text[:300]}")
    return False


def main() -> int:
    folder_id = get_or_create_folder(FOLDER_NAME)
    items = list_items()
    # Prefer the parent over its auto-provisioned sibling with same name
    # (e.g. Eventhouse vs KQLDatabase share displayName; Warehouse vs SQLEndpoint).
    type_priority = {
        "Lakehouse": 0, "Warehouse": 0, "Eventhouse": 0,
        "SemanticModel": 0, "Notebook": 0,
        "KQLDatabase": 9, "SQLEndpoint": 9, "SQLAnalyticsEndpoint": 9,
    }
    by_name: dict[str, dict] = {}
    for it in items:
        name = it["displayName"]
        cur = by_name.get(name)
        if cur is None or type_priority.get(it["type"], 5) < type_priority.get(cur["type"], 5):
            by_name[name] = it
    missing = ITEM_NAMES - set(by_name)
    if missing:
        print(f"[warn] not found in workspace: {sorted(missing)}")

    targets = ITEM_NAMES & set(by_name)
    ok = 0
    for name in sorted(targets):
        it = by_name[name]
        if it.get("folderId") == folder_id:
            print(f"[skip]  {name:<24} already in folder")
            ok += 1
            continue
        if move_item(it["id"], name, folder_id):
            ok += 1
    print(f"\n{ok}/{len(targets)} items in '{FOLDER_NAME}'")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    sys.exit(main())
