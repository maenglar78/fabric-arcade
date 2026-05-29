"""
Move all Calc Groups Cathedral items in Fabric Arcade Test into a folder
named "Calc Groups Cathedral".

Uses the Fabric REST API:
  POST /v1/workspaces/{ws}/folders                    (create folder)
  POST /v1/workspaces/{ws}/items/{itemId}             (move via update)
  POST /v1/workspaces/{ws}/items/{itemId}/move        (preferred move)
"""
from __future__ import annotations
import sys

import requests

from upload_notebook import WORKSPACE_ID, FABRIC_API, _headers

FOLDER_NAME = "Calc Groups Cathedral"
ITEM_NAMES = {
    "Cathedral_LH",
    "Cathedral_EH",
    "Cathedral_Model",
    "01_Setup",
    "02_Quest",
    "03_Check",
    "04_Dashboard",
}


def list_items() -> list[dict]:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items", headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json().get("value", [])


def list_folders() -> list[dict]:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/folders", headers=_headers(), timeout=60)
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
    r = requests.post(url, headers=_headers(), json={"targetFolderId": folder_id}, timeout=60)
    if r.status_code in (200, 202):
        print(f"[move]  {item_name:<20} OK")
        return True
    # Fallback: try the LRO-style 'moveTo' shape
    print(f"[move]  {item_name:<20} {r.status_code} {r.text[:300]}")
    return False


def main() -> int:
    folder_id = get_or_create_folder(FOLDER_NAME)
    items = list_items()
    # Build by_name preferring the parent over its like-named child
    # (e.g. Cathedral_EH has both an Eventhouse and an auto KQLDatabase).
    type_priority = {"Eventhouse": 0, "Lakehouse": 0, "SemanticModel": 0, "Notebook": 0, "KQLDatabase": 9}
    by_name: dict[str, dict] = {}
    for it in items:
        name = it["displayName"]
        cur = by_name.get(name)
        if cur is None or type_priority.get(it["type"], 5) < type_priority.get(cur["type"], 5):
            by_name[name] = it
    missing = ITEM_NAMES - set(by_name)
    if missing:
        print(f"[warn] not found in workspace: {sorted(missing)}")

    ok = 0
    for name in sorted(ITEM_NAMES & set(by_name)):
        it = by_name[name]
        if it.get("folderId") == folder_id:
            print(f"[skip]  {name:<20} already in folder")
            ok += 1
            continue
        if move_item(it["id"], name, folder_id):
            ok += 1
    print(f"\n{ok}/{len(ITEM_NAMES)} items in '{FOLDER_NAME}'")
    return 0 if ok == len(ITEM_NAMES & set(by_name)) else 1


if __name__ == "__main__":
    sys.exit(main())
