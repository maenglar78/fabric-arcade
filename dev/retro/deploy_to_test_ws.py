"""
Deploy Retro Arcade to the Fabric Arcade Test workspace for live testing.

Steps:
1. Ensure `Arcade_LH` Lakehouse exists (create if missing).
2. Build + upload the 3 notebooks: Retro_01_Setup, Retro_02_Quest, Retro_03_Check
   (prefixed so they don't collide with Cathedral notebooks of similar name).

Run:
    python dev/retro/deploy_to_test_ws.py
"""
from __future__ import annotations
import subprocess
import sys
import time
import requests
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG_NB = ROOT / "catalog" / "retro-arcade" / "notebooks"

# Reuse Cathedral upload helper (same workspace, same token logic).
sys.path.insert(0, str(ROOT / "dev" / "cathedral"))
from upload_notebook import (  # noqa: E402
    WORKSPACE_ID, FABRIC_API, _headers, _wait_lro, find_item,
    upload_or_update_notebook,
)

LAKEHOUSE_NAME = "Arcade_LH"


def ensure_lakehouse(name: str) -> str:
    existing = find_item(name, "Lakehouse")
    if existing:
        print(f"[OK] Lakehouse '{name}' already exists (id={existing['id']})")
        return existing["id"]
    print(f"[CREATE] Lakehouse '{name}'...")
    h = _headers()
    body = {"displayName": name, "type": "Lakehouse"}
    r = requests.post(f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items",
                      headers=h, json=body)
    if r.status_code == 202:
        obj = _wait_lro(r.headers["Location"])
        lh_id = obj.get("id", "?")
    elif r.status_code == 201:
        lh_id = r.json()["id"]
    else:
        raise RuntimeError(f"create Lakehouse HTTP {r.status_code}: {r.text}")
    print(f"[CREATED] Lakehouse '{name}' id={lh_id}")
    return lh_id


def main():
    # Step 1: rebuild notebooks from source (safety net).
    print("=" * 60)
    print("Step 1: rebuild notebooks from build_notebooks.py")
    print("=" * 60)
    subprocess.run([sys.executable, str(HERE / "build_notebooks.py")],
                   check=True)

    # Step 2: ensure Lakehouse exists.
    print()
    print("=" * 60)
    print("Step 2: ensure Lakehouse")
    print("=" * 60)
    ensure_lakehouse(LAKEHOUSE_NAME)

    # Step 3: upload notebooks (prefixed to avoid collision with Cathedral's 01_Setup etc.).
    print()
    print("=" * 60)
    print("Step 3: upload notebooks")
    print("=" * 60)
    notebooks = [
        ("01_Setup.ipynb", "Retro_01_Setup",
         "Retro Arcade - seed Arcade_LH + build ArcadeHall_Model"),
        ("02_Quest.ipynb", "Retro_02_Quest",
         "Retro Arcade - 5 levels brief for the Power BI report"),
        ("03_Check.ipynb", "Retro_03_Check",
         "Retro Arcade - check report via sempy and mint badge"),
    ]
    for fname, display, desc in notebooks:
        p = CATALOG_NB / fname
        print()
        print(f"--- {display} ---")
        upload_or_update_notebook(p, display, description=desc)

    print()
    print("DONE. Open the workspace and run Retro_01_Setup first.")


if __name__ == "__main__":
    main()
