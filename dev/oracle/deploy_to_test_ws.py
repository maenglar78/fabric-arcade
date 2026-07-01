"""
Deploy Oracle's Forge to the Fabric Arcade Test workspace, inside a folder
named "Oracle's Forge".

Steps:
  1. Ensure Lakehouse  OraclesForge_LH
  2. Ensure Eventhouse OraclesForge_EH + default KQL DB
  3. Apply ProphecyEvents.kql schema (telemetry table)
  4. Upload 5 notebooks (Seed / Forge / Prophecy / Judge / Dashboard)
  5. Create folder "Oracle's Forge" and move every OraclesForge_* item into it
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG_NB = ROOT / "catalog" / "oracles-forge" / "notebooks"
KQL_SCHEMA = ROOT / "catalog" / "oracles-forge" / "schemas" / "ProphecyEvents.kql"

# Reuse Cathedral helpers (same workspace, same token logic).
sys.path.insert(0, str(ROOT / "dev" / "cathedral"))
from upload_notebook import (  # noqa: E402
    WORKSPACE_ID, FABRIC_API, _headers, _wait_lro, find_item, _az_token,
    upload_or_update_notebook,
)

EVENTHOUSE = "OraclesForge_EH"
LAKEHOUSE = "OraclesForge_LH"
FOLDER_NAME = "Oracle's Forge"
ITEM_PREFIX = "OraclesForge"

NOTEBOOKS = [
    ("oracle_seed.ipynb",      "OraclesForge_Seed",
     "Oracle's Forge — seed omens_train + omens_holdout in OraclesForge_LH"),
    ("oracle_forge.ipynb",     "OraclesForge_Forge",
     "Oracle's Forge — workbench for Levels 1-4 (EDA, AutoML, MLflow, registry)"),
    ("oracle_prophecy.ipynb",  "OraclesForge_Prophecy",
     "Oracle's Forge — Level 5 batch scoring, writes prophecy_scores"),
    ("oracle_judge.ipynb",     "OraclesForge_Judge",
     "Oracle's Forge — per-level briefing + validator judge.check_level(N)"),
    ("oracle_dashboard.ipynb", "OraclesForge_Dashboard",
     "Oracle's Forge — best metric over attempts + final rank"),
]


def _create_item(item_type: str, name: str, description: str = "") -> str:
    existing = find_item(name, item_type)
    if existing:
        print(f"[OK] {item_type} '{name}' already exists (id={existing['id']})")
        return existing["id"]
    print(f"[CREATE] {item_type} '{name}'...")
    body = {"displayName": name, "type": item_type}
    if description:
        body["description"] = description
    r = requests.post(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items",
                      headers=_headers(), json=body)
    if r.status_code == 202:
        item_id = _wait_lro(r.headers["Location"]).get("id", "?")
    elif r.status_code in (200, 201):
        item_id = r.json()["id"]
    else:
        raise RuntimeError(f"create {item_type} HTTP {r.status_code}: {r.text}")
    print(f"[CREATED] {item_type} '{name}' id={item_id}")
    return item_id


def _ensure_eventhouse(name: str) -> tuple[str, str]:
    eh_id = _create_item("Eventhouse", name, "Oracle's Forge telemetry")
    print(f"[WAIT]   default KQL DB '{name}'...")
    db = None
    for _ in range(40):
        for it in requests.get(
            f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items?type=KQLDatabase",
            headers=_headers(),
        ).json().get("value", []):
            if it.get("displayName") == name:
                db = it
                break
        if db:
            break
        time.sleep(3)
    if not db:
        raise RuntimeError(f"default KQL DB '{name}' never appeared")
    print(f"[OK]    default KQL DB id={db['id']}")
    return eh_id, db["id"]


def _kql_query_uri(db_id: str) -> str:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/kqlDatabases/{db_id}",
                     headers=_headers())
    r.raise_for_status()
    uri = r.json().get("properties", {}).get("queryServiceUri")
    if not uri:
        raise RuntimeError(f"no queryServiceUri for KQL DB {db_id}: {r.text}")
    return uri


def _exec_kql(db_id: str, db_name: str, csl: str) -> None:
    uri = _kql_query_uri(db_id)
    token = _az_token("https://kusto.kusto.windows.net")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(f"{uri}/v1/rest/mgmt", headers=headers,
                      json={"csl": csl, "db": db_name})
    if r.status_code != 200:
        raise RuntimeError(f"KQL mgmt HTTP {r.status_code}: {r.text[:400]}")


def _list_items() -> list[dict]:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items",
                     headers=_headers(), timeout=60)
    r.raise_for_status()
    return r.json().get("value", [])


def _get_or_create_folder(name: str) -> str:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/folders",
                     headers=_headers(), timeout=60)
    folders = r.json().get("value", []) if r.status_code == 200 else []
    for f in folders:
        if f.get("displayName") == name:
            print(f"[folder] reuse '{name}' -> {f['id']}")
            return f["id"]
    r = requests.post(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/folders",
                      headers=_headers(), json={"displayName": name}, timeout=60)
    r.raise_for_status()
    fid = r.json().get("id")
    print(f"[folder] created '{name}' -> {fid}")
    return fid


def _move_into_folder(folder_id: str) -> None:
    moved = 0
    for it in _list_items():
        if not it["displayName"].startswith(ITEM_PREFIX):
            continue
        if it.get("folderId") == folder_id:
            print(f"[skip]  {it['displayName']:<24} already in folder")
            moved += 1
            continue
        r = requests.post(
            f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items/{it['id']}/move",
            headers=_headers(), json={"targetFolderId": folder_id}, timeout=60)
        if r.status_code in (200, 202):
            print(f"[move]  {it['displayName']:<24} OK")
            moved += 1
        else:
            print(f"[move]  {it['displayName']:<24} {r.status_code} {r.text[:200]}")
    print(f"[folder] {moved} OraclesForge_* item(s) in '{FOLDER_NAME}'")


def main() -> int:
    print("=" * 60)
    print("Step 1: ensure Lakehouse OraclesForge_LH")
    print("=" * 60)
    _create_item("Lakehouse", LAKEHOUSE, "Oracle's Forge datasets + player output")

    print("\n" + "=" * 60)
    print("Step 2: ensure Eventhouse OraclesForge_EH")
    print("=" * 60)
    _eh_id, db_id = _ensure_eventhouse(EVENTHOUSE)

    print("\n" + "=" * 60)
    print("Step 3: apply ProphecyEvents.kql schema")
    print("=" * 60)
    csl = KQL_SCHEMA.read_text(encoding="utf-8")
    for block in [b.strip() for b in csl.split("\n\n") if b.strip()]:
        cmd = "\n".join(ln for ln in block.splitlines()
                        if not ln.strip().startswith("//")).strip()
        if not cmd:
            continue
        print(f"  exec: {cmd.splitlines()[0][:70]}...")
        _exec_kql(db_id, EVENTHOUSE, cmd)
    print("[OK] ProphecyEvents schema applied")

    print("\n" + "=" * 60)
    print("Step 4: upload 5 notebooks")
    print("=" * 60)
    for filename, display, descr in NOTEBOOKS:
        print(f"\n--- {display} ---")
        upload_or_update_notebook(str(CATALOG_NB / filename), display, description=descr)

    print("\n" + "=" * 60)
    print(f"Step 5: move items into folder '{FOLDER_NAME}'")
    print("=" * 60)
    folder_id = _get_or_create_folder(FOLDER_NAME)
    _move_into_folder(folder_id)

    print("\nDONE. Attach OraclesForge_Seed to OraclesForge_LH and run it first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
