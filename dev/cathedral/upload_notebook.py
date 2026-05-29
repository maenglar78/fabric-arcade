"""
Dev helper: create/update Fabric notebooks in Fabric Arcade Test workspace.
Reusable across all dev iterations on Calc Groups Cathedral.

Usage:
    python upload_notebook.py <local.ipynb> <DisplayName> [--description "..."]

Or as a module:
    from upload_notebook import upload_or_update_notebook
    upload_or_update_notebook("path.ipynb", "MyNotebook", description="...")
"""
from __future__ import annotations
import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

WORKSPACE_ID = "a5235927-0289-4a06-83d1-456be383b496"  # Fabric Arcade Test
FABRIC_API = "https://api.fabric.microsoft.com/v1"


def _az_token(resource: str) -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource", resource,
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True
    )
    return out.stdout.strip()


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_az_token('https://api.fabric.microsoft.com')}",
        "Content-Type": "application/json",
    }


def _wait_lro(location: str, timeout: int = 300) -> dict:
    h = _headers()
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = requests.get(location, headers=h)
        if r.status_code == 200:
            obj = r.json()
            status = (obj.get("status") or "").lower()
            if status == "succeeded":
                # try /result
                try:
                    rr = requests.get(location.rstrip("/") + "/result", headers=h)
                    if rr.status_code == 200:
                        return rr.json()
                except Exception:
                    pass
                return obj
            if status == "failed":
                raise RuntimeError(f"Operation failed: {obj}")
        time.sleep(3)
    raise TimeoutError(f"LRO did not complete: {location}")


def find_item(display_name: str, item_type: str) -> dict | None:
    r = requests.get(
        f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items?type={item_type}",
        headers=_headers(),
    )
    r.raise_for_status()
    for it in r.json().get("value", []):
        if it.get("displayName") == display_name:
            return it
    return None


def rename_notebook(old_name: str, new_name: str) -> bool:
    """Rename a notebook in-place. Returns True if renamed, False if not found
    (or already named new_name)."""
    h = _headers()
    if find_item(new_name, "Notebook"):
        return False  # new name already exists
    existing = find_item(old_name, "Notebook")
    if not existing:
        return False
    nb_id = existing["id"]
    url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items/{nb_id}"
    r = requests.patch(url, headers=h, json={"displayName": new_name})
    if r.status_code not in (200, 202):
        raise RuntimeError(f"rename HTTP {r.status_code}: {r.text}")
    print(f"  [RENAMED] {old_name} -> {new_name} (id={nb_id})")
    return True


def _ipynb_to_b64(path: Path) -> str:
    """Read .ipynb, ensure it's valid JSON, return base64."""
    content = path.read_text(encoding="utf-8")
    # Validate JSON
    json.loads(content)
    return base64.b64encode(content.encode("utf-8")).decode("ascii")


def upload_or_update_notebook(
    ipynb_path: str | Path,
    display_name: str,
    description: str = "",
) -> str:
    """Create or update a Fabric notebook. Returns item id."""
    path = Path(ipynb_path)
    if not path.exists():
        raise FileNotFoundError(path)
    payload_b64 = _ipynb_to_b64(path)
    existing = find_item(display_name, "Notebook")

    definition = {
        "format": "ipynb",
        "parts": [{
            "path": "notebook-content.ipynb",
            "payload": payload_b64,
            "payloadType": "InlineBase64",
        }]
    }

    h = _headers()
    if existing:
        nb_id = existing["id"]
        url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/notebooks/{nb_id}/updateDefinition"
        body = {"definition": definition}
        r = requests.post(url, headers=h, json=body)
        print(f"  updateDefinition HTTP {r.status_code}")
        if r.status_code == 202:
            loc = r.headers.get("Location")
            if not loc:
                raise RuntimeError(f"202 without Location header. Headers: {dict(r.headers)}")
            print(f"  LRO Location: {loc}")
            _wait_lro(loc)
        elif r.status_code not in (200, 201):
            raise RuntimeError(f"updateDefinition HTTP {r.status_code}: {r.text}")
        print(f"  [UPDATED] {display_name} id={nb_id}")
        return nb_id
    else:
        url = f"{FABRIC_API}/workspaces/{WORKSPACE_ID}/items"
        body = {
            "displayName": display_name,
            "type": "Notebook",
            "description": description,
            "definition": definition,
        }
        r = requests.post(url, headers=h, json=body)
        if r.status_code == 202:
            obj = _wait_lro(r.headers["Location"])
            nb_id = obj.get("id", "?")
        elif r.status_code == 201:
            nb_id = r.json()["id"]
        else:
            raise RuntimeError(f"create item HTTP {r.status_code}: {r.text}")
        print(f"  [CREATED] {display_name} id={nb_id}")
        return nb_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ipynb_path")
    ap.add_argument("display_name")
    ap.add_argument("--description", default="")
    args = ap.parse_args()
    upload_or_update_notebook(args.ipynb_path, args.display_name, args.description)


if __name__ == "__main__":
    main()
