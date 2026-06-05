"""
Deploy Ontology Detective infrastructure to the Fabric Arcade Test workspace.

Steps:
  1. Rebuild notebooks (build_notebooks.py)
  2. Ensure Eventhouse `Datapolis_DetectiveEH` + default KQL DB
  3. Ensure Ontology `DetectiveOntology` (empty — player designs it in DTB UI)
  4. Apply DetectiveEvents.kql schema (telemetry + 8 evidence tables)
  5. Upload 3 notebooks: OntologyDetective_Seed / _CaseFile / _Dashboard
"""
from __future__ import annotations
import subprocess
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG_NB = ROOT / "catalog" / "ontology-detective" / "notebooks"
KQL_SCHEMA = ROOT / "catalog" / "ontology-detective" / "schemas" / "DetectiveEvents.kql"

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
    eh_id = _create_item("Eventhouse", name, "Ontology Detective evidence + telemetry")
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
    print("Step 2: ensure Eventhouse Datapolis_DetectiveEH")
    print("=" * 60)
    eh_id, db_id = _ensure_eventhouse("Datapolis_DetectiveEH")

    print()
    print("=" * 60)
    print("Step 3: ensure DetectiveOntology (Ontology item, empty)")
    print("=" * 60)
    _create_item("Ontology", "DetectiveOntology",
                 "Ontology Detective — player designs entities in Digital Twin Builder")

    print()
    print("=" * 60)
    print("Step 4: apply DetectiveEvents.kql schema")
    print("=" * 60)
    csl = KQL_SCHEMA.read_text(encoding="utf-8")
    for block in [b.strip() for b in csl.split("\n\n") if b.strip()]:
        cmd_lines = [ln for ln in block.splitlines() if not ln.strip().startswith("//")]
        cmd = "\n".join(cmd_lines).strip()
        if not cmd:
            continue
        print(f"  exec: {cmd.splitlines()[0][:80]}...")
        _exec_kql(db_id, "Datapolis_DetectiveEH", cmd)
    print("[OK] DetectiveEvents schema applied")

    print()
    print("=" * 60)
    print("Step 5: upload notebooks")
    print("=" * 60)
    notebooks = [
        ("ontology_detective_seed.ipynb",      "OntologyDetective_Seed",
         "Ontology Detective — seed Datapolis_DetectiveEH with the 5 case datasets"),
        ("ontology_detective_casefile.ipynb",  "OntologyDetective_CaseFile",
         "Ontology Detective — 5 noir cases + ontology-driven KQL gameplay"),
        ("ontology_detective_dashboard.ipynb", "OntologyDetective_Dashboard",
         "Ontology Detective — cases solved / accuracy / rank"),
    ]
    for filename, display, descr in notebooks:
        print(f"\n--- {display} ---")
        upload_or_update_notebook(
            str(CATALOG_NB / filename), display, description=descr
        )

    print()
    print("DONE. Run OntologyDetective_Seed first to populate Datapolis_DetectiveEH.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
