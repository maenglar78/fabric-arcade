"""
Restore the 'like before' flow for Fabric Racing:
  1. DROP the pre-created GameEvents table (+ mapping) in RaceData, so the
     Eventstream can create it itself in event-processing mode (auto-mapped).
  2. (Re)create RacingStream with ONLY the CustomEndpoint source (shipped ready),
     in the game folder. The user just adds the Eventhouse destination
     (event-processing -> Create new table GameEvents) and publishes.
"""
from __future__ import annotations
import base64, json, sys, time, uuid
from pathlib import Path
import requests

sys.path.insert(0, str(Path("dev/cathedral")))
import upload_notebook as u

WS = u.WORKSPACE_ID
EVENTHOUSE, KQLDB = "RacingEventhouse", "RaceData"
EVENTSTREAM = "RacingStream"
FOLDER_NAME = "Fabric Racing Game (test)"
SOURCE_NAME = "TelemetryInput"


def _find(name, item_type):
    r = requests.get(f"{u.FABRIC_API}/workspaces/{WS}/items?type={item_type}", headers=u._headers())
    r.raise_for_status()
    return next((it for it in r.json().get("value", []) if it["displayName"] == name), None)


def _folder_id(name):
    r = requests.get(f"{u.FABRIC_API}/workspaces/{WS}/folders", headers=u._headers())
    for f in (r.json().get("value", []) if r.status_code == 200 else []):
        if f["displayName"] == name:
            return f["id"]
    return None


def _b64(obj):
    text = obj if isinstance(obj, str) else json.dumps(obj, indent=2)
    return base64.b64encode(text.encode()).decode()


def drop_table():
    db = _find(KQLDB, "KQLDatabase")
    uri = requests.get(f"{u.FABRIC_API}/workspaces/{WS}/kqlDatabases/{db['id']}",
                       headers=u._headers()).json()["properties"]["queryServiceUri"]
    tok = u._az_token("https://kusto.kusto.windows.net")
    r = requests.post(f"{uri}/v1/rest/mgmt",
                      headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                      json={"csl": ".drop table GameEvents ifexists", "db": KQLDB})
    print("drop table GameEvents ->", r.status_code, "(table now absent; eventstream will create it)")


def recreate_source_only():
    fid = _folder_id(FOLDER_NAME)
    old = _find(EVENTSTREAM, "Eventstream")
    if old:
        d = requests.delete(f"{u.FABRIC_API}/workspaces/{WS}/items/{old['id']}", headers=u._headers())
        print("delete old eventstream ->", d.status_code)
        time.sleep(3)

    topology = {
        "sources": [{"name": SOURCE_NAME, "type": "CustomEndpoint", "properties": {}}],
        "destinations": [],
        "streams": [{
            "name": f"{EVENTSTREAM}-stream", "type": "DefaultStream", "properties": {},
            "inputNodes": [{"name": SOURCE_NAME}],
        }],
        "operators": [], "compatibilityLevel": "1.1",
    }
    platform = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Eventstream", "displayName": EVENTSTREAM},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    }
    body = {
        "displayName": EVENTSTREAM, "type": "Eventstream",
        "description": "Fabric Racing - Custom Endpoint ready; add Eventhouse destination (event-processing, create table GameEvents)",
        "definition": {"parts": [
            {"path": "eventstream.json", "payload": _b64(topology), "payloadType": "InlineBase64"},
            {"path": ".platform", "payload": _b64(platform), "payloadType": "InlineBase64"},
        ]},
    }
    if fid:
        body["folderId"] = fid

    for attempt in range(12):
        r = requests.post(f"{u.FABRIC_API}/workspaces/{WS}/items", headers=u._headers(), json=body)
        print(f"create attempt {attempt+1} ->", r.status_code)
        if r.status_code == 202:
            esid = u._wait_lro(r.headers["Location"]).get("id"); break
        if r.status_code == 201:
            esid = r.json()["id"]; break
        if r.status_code == 409 and "NotAvailableYet" in r.text:
            print("  name not free yet, waiting 30s..."); time.sleep(30); continue
        raise RuntimeError(f"{r.status_code}: {r.text[:400]}")
    else:
        raise RuntimeError("create failed")
    print("New Eventstream (source only) id:", esid)
    # confirm source running
    for i in range(10):
        time.sleep(5)
        t = requests.get(f"{u.FABRIC_API}/workspaces/{WS}/eventstreams/{esid}/topology", headers=u._headers())
        if t.status_code == 200 and t.json()["sources"]:
            print(f"  source status: {t.json()['sources'][0].get('status')}")
            if t.json()["sources"][0].get("status") == "Running":
                break


if __name__ == "__main__":
    drop_table()
    recreate_source_only()
    print("\nDONE. Next: open RacingStream -> TelemetryInput -> copy SAS -> run game ->")
    print("add Eventhouse destination (event-processing, Create new table GameEvents, Json) -> Publish.")
