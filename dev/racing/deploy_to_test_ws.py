"""
Deploy Fabric Racing Game to the "Fabric Arcade Test" workspace, inside a
dedicated folder, using the LOCAL (fixed) assets — NOT GitHub.

Items created (matching catalog/fabric-racing-game/manifest.json):
  1. Eventhouse  RacingEventhouse
  2. KQLDatabase RaceData (child of RacingEventhouse)
  3. Apply schemas/GameEvents.kql (table + JSON mapping) to RaceData
  4. Eventstream RacingStream (empty — user wires Custom Endpoint -> KQL manually)
  5. Notebooks: Racing_Championship (racing_game_v3.ipynb), Race_Dashboard, Race_Check
  6. Move every item into folder "Fabric Racing Game (test)"

Idempotent: re-running reuses existing items and updates notebook definitions.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GAME = ROOT / "catalog" / "fabric-racing-game"
NB_DIR = GAME / "notebooks"
KQL_SCHEMA = GAME / "schemas" / "GameEvents.kql"

# Reuse the proven Fabric Arcade Test helpers.
sys.path.insert(0, str(ROOT / "dev" / "cathedral"))
from upload_notebook import (  # noqa: E402
    WORKSPACE_ID, FABRIC_API, _headers, _wait_lro, find_item, _az_token,
    upload_or_update_notebook,
)

EVENTHOUSE = "RacingEventhouse"
KQLDB = "RaceData"
EVENTSTREAM = "RacingStream"
FOLDER_NAME = "Fabric Racing Game (test)"

NOTEBOOKS = [
    ("racing_game_v3.ipynb", "Racing_Championship",
     "Fabric Racing - Championship Edition. Cell 1 config, Cell 2 play (streams telemetry), Cell 3 verify."),
    ("race_dashboard.ipynb", "Race_Dashboard",
     "Fabric Racing - live KQL dashboard over RaceData."),
    ("race_check.ipynb", "Race_Check",
     "Fabric Racing - badge check: one completed race + working dashboard queries."),
]


def _create_item(item_type: str, name: str, description: str = "",
                 extra: dict | None = None) -> str:
    existing = find_item(name, item_type)
    if existing:
        print(f"[OK] {item_type} '{name}' already exists (id={existing['id']})")
        return existing["id"]
    print(f"[CREATE] {item_type} '{name}'...")
    body = {"displayName": name, "type": item_type}
    if description:
        body["description"] = description
    if extra:
        body.update(extra)
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


def _wait_query_uri(db_id: str, tries: int = 40) -> str:
    for _ in range(tries):
        r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/kqlDatabases/{db_id}",
                         headers=_headers())
        if r.status_code == 200:
            uri = r.json().get("properties", {}).get("queryServiceUri")
            if uri:
                return uri
        time.sleep(3)
    raise RuntimeError(f"no queryServiceUri for KQL DB {db_id}")


def _exec_kql(db_id: str, db_name: str, csl: str) -> None:
    uri = _wait_query_uri(db_id)
    token = _az_token("https://kusto.kusto.windows.net")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(f"{uri}/v1/rest/mgmt", headers=headers,
                      json={"csl": csl, "db": db_name})
    if r.status_code != 200:
        raise RuntimeError(f"KQL mgmt HTTP {r.status_code}: {r.text[:400]}")


def _kql_commands(text: str) -> list[str]:
    cmds = []
    for block in text.split("\n\n"):
        cmd = "\n".join(ln for ln in block.splitlines()
                        if not ln.strip().startswith("//")).strip()
        if cmd:
            cmds.append(cmd)
    return cmds


def _get_or_create_folder(name: str) -> str:
    r = requests.get(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/folders",
                     headers=_headers(), timeout=60)
    for f in (r.json().get("value", []) if r.status_code == 200 else []):
        if f.get("displayName") == name:
            print(f"[folder] reuse '{name}' -> {f['id']}")
            return f["id"]
    r = requests.post(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/folders",
                      headers=_headers(), json={"displayName": name}, timeout=60)
    r.raise_for_status()
    fid = r.json().get("id")
    print(f"[folder] created '{name}' -> {fid}")
    return fid


def _move(item_id: str, name: str, folder_id: str) -> None:
    r = requests.post(
        f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items/{item_id}/move",
        headers=_headers(), json={"targetFolderId": folder_id}, timeout=60)
    if r.status_code in (200, 202):
        print(f"[move]  {name:<22} OK")
    else:
        print(f"[move]  {name:<22} {r.status_code} {r.text[:200]}")


def main() -> int:
    ids: dict[str, str] = {}

    print("=" * 60)
    print("Step 1: Eventhouse", EVENTHOUSE)
    print("=" * 60)
    eh_id = _create_item("Eventhouse", EVENTHOUSE, "Fabric Racing - KQL analytics engine")
    ids[EVENTHOUSE] = eh_id

    print("\n" + "=" * 60)
    print("Step 2: KQLDatabase", KQLDB)
    print("=" * 60)
    db = find_item(KQLDB, "KQLDatabase")
    if db:
        db_id = db["id"]
        print(f"[OK] KQLDatabase '{KQLDB}' already exists (id={db_id})")
    else:
        db_id = _create_item("KQLDatabase", KQLDB, "Fabric Racing - GameEvents telemetry",
                             extra={"creationPayload": {
                                 "databaseType": "ReadWrite",
                                 "parentEventhouseItemId": eh_id}})
    ids[KQLDB] = db_id

    print("\n" + "=" * 60)
    print("Step 3: apply GameEvents.kql schema")
    print("=" * 60)
    for cmd in _kql_commands(KQL_SCHEMA.read_text(encoding="utf-8")):
        print(f"  exec: {cmd.splitlines()[0][:70]}...")
        _exec_kql(db_id, KQLDB, cmd)
    print("[OK] GameEvents table + mapping applied")

    print("\n" + "=" * 60)
    print("Step 4: Eventstream", EVENTSTREAM, "(empty - configure manually)")
    print("=" * 60)
    ids[EVENTSTREAM] = _create_item("Eventstream", EVENTSTREAM,
                                    "Fabric Racing - Custom Endpoint -> RaceData/GameEvents")

    print("\n" + "=" * 60)
    print("Step 5: notebooks")
    print("=" * 60)
    for filename, display, descr in NOTEBOOKS:
        print(f"\n--- {display} ---")
        ids[display] = upload_or_update_notebook(str(NB_DIR / filename), display, description=descr)

    print("\n" + "=" * 60)
    print(f"Step 6: move items into folder '{FOLDER_NAME}'")
    print("=" * 60)
    folder_id = _get_or_create_folder(FOLDER_NAME)
    for name, item_id in ids.items():
        _move(item_id, name, folder_id)

    print("\nDONE.")
    print("Next (manual, per README): open RacingStream -> add Custom Endpoint 'TelemetryInput'")
    print("-> add KQL destination RacingEventhouse/RaceData/GameEvents (Json) -> Publish.")
    print("Then copy the 4 SAS values into Racing_Championship Cell 1 and play.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
