"""
Deploy City Builder Phase 1 infrastructure to the Fabric Arcade Test workspace.

Steps:
  1. Rebuild notebooks (build_notebooks.py)
  2. Ensure Lakehouse `Datapolis_LH`
  3. Ensure Warehouse `Datapolis_DW`
  4. Ensure Eventhouse `Datapolis_EH` + default KQL DB
  5. Create CityEvents KQL table (idempotent .create-merge)
  6. Upload 3 notebooks: CityBuilder_Seed / _Mayor / _Dashboard
"""
from __future__ import annotations
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG_NB = ROOT / "catalog" / "city-builder" / "notebooks"
KQL_SCHEMA = ROOT / "catalog" / "city-builder" / "schemas" / "CityEvents.kql"

# Reuse Cathedral upload helper (same workspace, same token logic).
sys.path.insert(0, str(ROOT / "dev" / "cathedral"))
from upload_notebook import (  # noqa: E402
    WORKSPACE_ID, FABRIC_API, _headers, _wait_lro, find_item, _az_token,
    upload_or_update_notebook,
)


def _create_item(item_type: str, name: str, description: str = "") -> str:
    existing = find_item(name, item_type)
    if existing:
        print(f"[OK] {item_type} '{name}' already exists (id={existing['id']})")
        return existing["id"]
    print(f"[CREATE] {item_type} '{name}'...")
    h = _headers()
    body = {"displayName": name, "type": item_type}
    if description:
        body["description"] = description
    r = requests.post(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items",
                      headers=h, json=body)
    if r.status_code == 202:
        obj = _wait_lro(r.headers["Location"])
        item_id = obj.get("id", "?")
    elif r.status_code in (200, 201):
        item_id = r.json()["id"]
    else:
        raise RuntimeError(f"create {item_type} HTTP {r.status_code}: {r.text}")
    print(f"[CREATED] {item_type} '{name}' id={item_id}")
    return item_id


def _ensure_eventhouse(name: str) -> tuple[str, str]:
    eh_id = _create_item("Eventhouse", name, "City Builder telemetry")
    # The default KQL DB is auto-provisioned with the same displayName as the EH.
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
    # Pull queryServiceUri from /kqlDatabases/{id}
    h = _headers()
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/kqlDatabases/{db_id}",
                     headers=h)
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


def main() -> int:
    print("=" * 60)
    print("Step 1: rebuild notebooks from build_notebooks.py")
    print("=" * 60)
    subprocess.run([sys.executable, str(HERE / "build_notebooks.py")], check=True)

    print()
    print("=" * 60)
    print("Step 2-4: ensure Fabric items")
    print("=" * 60)
    _create_item("Lakehouse", "Datapolis_LH", "City Builder raw + oracle datasets")
    _create_item("Warehouse", "Datapolis_DW", "City Builder — player builds Fact/Dim tables here")
    eh_id, db_id = _ensure_eventhouse("Datapolis_EH")

    print()
    print("=" * 60)
    print("Step 5: deploy CityEvents KQL table")
    print("=" * 60)
    csl = KQL_SCHEMA.read_text(encoding="utf-8")
    # Split on blank lines between commands.
    for block in [b.strip() for b in csl.split("\n\n") if b.strip()]:
        # Drop comment-only lines from the block.
        cmd_lines = [ln for ln in block.splitlines() if not ln.strip().startswith("//")]
        cmd = "\n".join(cmd_lines).strip()
        if not cmd:
            continue
        print(f"  exec: {cmd.splitlines()[0][:80]}...")
        _exec_kql(db_id, "Datapolis_EH", cmd)
    print("[OK] CityEvents schema applied")

    print()
    print("=" * 60)
    print("Step 6: upload notebooks")
    print("=" * 60)
    notebooks = [
        ("city_builder_seed.ipynb",      "CityBuilder_Seed",
         "City Builder — seed Datapolis_LH with raw + oracle datasets"),
        ("city_builder_mayor.ipynb",     "CityBuilder_Mayor",
         "City Builder — Mayor briefings and validation (Phase 2)"),
        ("city_builder_dashboard.ipynb", "CityBuilder_Dashboard",
         "City Builder — Datapolis dashboard (Phase 3)"),
    ]
    for filename, display, descr in notebooks:
        print(f"\n--- {display} ---")
        upload_or_update_notebook(
            str(CATALOG_NB / filename), display, description=descr
        )

    print()
    print("DONE. Run CityBuilder_Seed first to populate Datapolis_LH.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
