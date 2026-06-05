"""Build the 3 Ontology Detective notebooks from a single Python source.

Outputs:
  catalog/ontology-detective/notebooks/ontology_detective_seed.ipynb
  catalog/ontology-detective/notebooks/ontology_detective_casefile.ipynb
  catalog/ontology-detective/notebooks/ontology_detective_dashboard.ipynb

Notes
-----
* Seed populates the Datapolis_DetectiveEH KQL DB with 5 case datasets and the
  DetectiveEvents telemetry table.
* CaseFile contains 5 noir briefings + `detective.accuse(name)` judge + a
  retro-arcade-style HMAC badge cell.
* Dashboard reads DetectiveEvents to show cases solved / accuracy / rank.

Run via `python dev/detective/deploy_to_test_ws.py` (which calls this first).
"""
from __future__ import annotations
import datetime as dt
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT  = ROOT / "catalog" / "ontology-detective" / "notebooks"
OUT.mkdir(parents=True, exist_ok=True)

BUILD_STAMP = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------- cell helpers ---------------------------------
def _md(src: str) -> dict:
    body = textwrap.dedent(src).strip()
    return {"cell_type": "markdown", "metadata": {},
            "source": body.splitlines(keepends=True)}


def _code(src: str, hidden: bool = False) -> dict:
    md = {}
    if hidden:
        md = {"jupyter": {"source_hidden": True}}
    body = textwrap.dedent(src).strip()
    return {
        "cell_type": "code", "metadata": md, "execution_count": None,
        "outputs": [], "source": body.splitlines(keepends=True)
    }


def _notebook(cells: list[dict]) -> dict:
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"},
            "microsoft": {"language": "python", "language_group": "synapse_pyspark"}
        },
        "cells": cells
    }


def _write(name: str, cells: list[dict]) -> None:
    p = OUT / name
    p.write_text(json.dumps(_notebook(cells), indent=1), encoding="utf-8")
    print(f"📓 Wrote {p}")


# =====================================================================
# CASE DATA — single source of truth (used by Seed + by SOLUTIONS.md)
# =====================================================================
# Each row is rendered into an inline KQL .ingest command at seed time.

CASE_DATA = {
    # Case 1: The Stolen Pie. CULPRIT: Bob Hollowstone (only one in Kitchen 14:00–14:30)
    "Case1_Visits": [
        # PersonName, RoomName, EnteredAt, LeftAt
        ("Mrs. Plum",        "Kitchen",     "2026-06-05T13:30:00Z", "2026-06-05T14:00:00Z"),
        ("Mrs. Plum",        "Living Room", "2026-06-05T14:00:00Z", "2026-06-05T14:35:00Z"),
        ("Mrs. Plum",        "Kitchen",     "2026-06-05T14:35:00Z", "2026-06-05T15:00:00Z"),
        ("Bob Hollowstone",  "Living Room", "2026-06-05T13:55:00Z", "2026-06-05T14:05:00Z"),
        ("Bob Hollowstone",  "Kitchen",     "2026-06-05T14:05:00Z", "2026-06-05T14:20:00Z"),
        ("Bob Hollowstone",  "Living Room", "2026-06-05T14:20:00Z", "2026-06-05T14:40:00Z"),
        ("Alice Greengrass", "Living Room", "2026-06-05T13:50:00Z", "2026-06-05T14:30:00Z"),
        ("Alice Greengrass", "Garden",      "2026-06-05T14:30:00Z", "2026-06-05T14:50:00Z"),
        ("Mortimer Quill",   "Garden",      "2026-06-05T13:55:00Z", "2026-06-05T14:25:00Z"),
        ("Mortimer Quill",   "Living Room", "2026-06-05T14:25:00Z", "2026-06-05T14:40:00Z"),
    ],

    # Case 2: Museum. CULPRIT: Lady Marlowe (only one at Etruscan Hall 21:14–21:18)
    "Case2_CameraEvents": [
        # GuestName, Location, SeenAt
        ("Lady Marlowe",     "Ballroom",       "2026-06-04T21:00:00Z"),
        ("Lady Marlowe",     "Etruscan Hall",  "2026-06-04T21:15:00Z"),
        ("Lady Marlowe",     "Garden Terrace", "2026-06-04T21:25:00Z"),
        ("Lord Pembroke",    "Foyer",          "2026-06-04T21:00:00Z"),
        ("Lord Pembroke",    "Ballroom",       "2026-06-04T21:10:00Z"),
        ("Lord Pembroke",    "Egyptian Wing",  "2026-06-04T21:20:00Z"),
        ("Dr. Faraday",      "Egyptian Wing",  "2026-06-04T21:05:00Z"),
        ("Dr. Faraday",      "Etruscan Hall",  "2026-06-04T21:25:00Z"),
        ("Count Volturino",  "Foyer",          "2026-06-04T21:00:00Z"),
        ("Count Volturino",  "Ballroom",       "2026-06-04T21:15:00Z"),
        ("Count Volturino",  "Garden Terrace", "2026-06-04T21:30:00Z"),
        ("Miss Crispin",     "Egyptian Wing",  "2026-06-04T21:00:00Z"),
        ("Miss Crispin",     "Foyer",          "2026-06-04T21:15:00Z"),
        ("Miss Crispin",     "Ballroom",       "2026-06-04T21:20:00Z"),
        ("Professor Bell",   "Etruscan Hall",  "2026-06-04T21:00:00Z"),
        ("Professor Bell",   "Ballroom",       "2026-06-04T21:13:00Z"),
        ("Professor Bell",   "Foyer",          "2026-06-04T21:22:00Z"),
        ("Madame Volga",     "Garden Terrace", "2026-06-04T21:00:00Z"),
        ("Madame Volga",     "Etruscan Hall",  "2026-06-04T21:30:00Z"),
        ("Sir Hamilton",     "Egyptian Wing",  "2026-06-04T21:00:00Z"),
        ("Sir Hamilton",     "Garden Terrace", "2026-06-04T21:15:00Z"),
        ("Sir Hamilton",     "Ballroom",       "2026-06-04T21:25:00Z"),
    ],

    # Case 3: Phone Call. CULPRIT: Vincenzo Lupara
    # (only one who called BOTH Senator Carballo AND Dr. Aconite within 2 hours of each other)
    "Case3_PhoneCalls": [
        # Caller, Callee, CalledAt
        ("Vincenzo Lupara", "Senator Carballo", "2026-06-03T18:30:00Z"),
        ("Vincenzo Lupara", "Dr. Aconite",      "2026-06-03T20:00:00Z"),
        ("Maria Rossi",     "Senator Carballo", "2026-06-03T18:00:00Z"),
        ("Maria Rossi",     "Bank of Datapolis","2026-06-03T19:30:00Z"),
        ("Antonio Bruno",   "Dr. Aconite",      "2026-06-03T18:15:00Z"),
        ("Antonio Bruno",   "Maria Rossi",      "2026-06-03T19:45:00Z"),
        ("Elena Verdi",     "Senator Carballo", "2026-06-03T17:00:00Z"),
        ("Elena Verdi",     "Dr. Aconite",      "2026-06-03T23:30:00Z"),  # >2h apart
        ("Giuseppe Neri",   "Senator Carballo", "2026-06-03T16:00:00Z"),
        ("Giuseppe Neri",   "Vincenzo Lupara",  "2026-06-03T20:30:00Z"),
        ("Carla Bianchi",   "Dr. Aconite",      "2026-06-03T15:00:00Z"),
        ("Carla Bianchi",   "Maria Rossi",      "2026-06-03T22:00:00Z"),
        ("Senator Carballo","Bank of Datapolis","2026-06-03T17:45:00Z"),
        ("Dr. Aconite",     "Pharmacy 7",       "2026-06-03T19:00:00Z"),
    ],

    # Case 4: Stolen Identity. CULPRIT: Ricardo Vega (real name behind alias 'V. Rodriguez')
    "Case4_Aliases": [
        # AliasName, RealName
        ("V. Rodriguez",  "Ricardo Vega"),
        ("Mister V",      "Ricardo Vega"),
        ("Vega R.",       "Roberto Vega Junior"),
        ("R. Roberts",    "Roberto Vega Junior"),
        ("R. Vega III",   "Rafael Vega"),
        ("Rafa V.",       "Rafael Vega"),
    ],
    "Case4_HotelCheckIns": [
        # UsedName, HotelName, CheckedInAt
        ("V. Rodriguez",  "Quantum",   "2026-06-01T22:30:00Z"),  # ← culprit (within window)
        ("Vega R.",       "Plaza",     "2026-06-01T19:00:00Z"),
        ("R. Roberts",    "Quantum",   "2026-05-30T20:00:00Z"),  # wrong night
        ("R. Vega III",   "Continental","2026-06-01T23:00:00Z"),
        ("Rafa V.",       "Quantum",   "2026-06-02T03:00:00Z"),  # past window
        ("Mister V",      "Plaza",     "2026-06-01T18:00:00Z"),
        ("Vega R.",       "Quantum",   "2026-05-29T21:00:00Z"),  # wrong night
    ],

    # Case 5: Final Heist (BOSS). CULPRIT: Madame Cinquedeo
    # (only person in all three sets:
    #   opened RelayShell account + in Bank District NOT on register + called burner 23:00–23:10)
    "Case5_BankAccounts": [
        # PersonName, AccountKind, OpenedAt
        ("Madame Cinquedeo", "RelayShell", "2026-05-15T10:00:00Z"),
        ("Hugo Pellegrini",  "RelayShell", "2026-05-20T11:00:00Z"),
        ("Sven Halberd",     "RelayShell", "2026-05-22T14:30:00Z"),
        ("Iris Velvetan",    "Standard",   "2026-05-25T09:15:00Z"),
        ("Tomas Krall",      "RelayShell", "2026-05-28T16:00:00Z"),
        ("Madame Cinquedeo", "Standard",   "2024-01-10T10:00:00Z"),
    ],
    "Case5_PolicePatrols": [
        # PersonName, PatrolZone, SeenAt, OnDutyRegister
        ("Madame Cinquedeo", "Bank District",   "2026-06-05T22:55:00Z", False),
        ("Hugo Pellegrini",  "Bank District",   "2026-06-05T22:30:00Z", True),
        ("Sven Halberd",     "Harbor",          "2026-06-05T22:50:00Z", False),
        ("Tomas Krall",      "Bank District",   "2026-06-05T23:00:00Z", True),
        ("Iris Velvetan",    "Bank District",   "2026-06-05T22:45:00Z", False),
        ("Carla Drago",      "Bank District",   "2026-06-05T22:40:00Z", False),
    ],
    "Case5_BurnerCalls": [
        # Caller, Callee, CalledAt
        ("Madame Cinquedeo", "+39-X-USA-E-GETTA", "2026-06-05T23:04:00Z"),
        ("Hugo Pellegrini",  "+39-X-USA-E-GETTA", "2026-06-05T22:00:00Z"),  # outside window
        ("Iris Velvetan",    "+39-X-USA-E-GETTA", "2026-06-05T23:30:00Z"),  # outside window
        ("Tomas Krall",      "Iris Velvetan",     "2026-06-05T23:05:00Z"),  # not the burner
        ("Sven Halberd",     "+39-X-USA-E-GETTA", "2026-06-05T23:07:00Z"),  # in window but no RelayShell
        ("Carla Drago",      "+39-X-USA-E-GETTA", "2026-06-05T23:08:00Z"),  # no RelayShell account
    ],
}

CULPRITS = {
    "stolen-pie":       "Bob Hollowstone",
    "museum":           "Lady Marlowe",
    "phone-call":       "Vincenzo Lupara",
    "stolen-identity":  "Ricardo Vega",
    "final-heist":      "Madame Cinquedeo",
}

ONTOLOGY_HINTS = {
    "stolen-pie":      ["Person", "Room", "Visit (Person wasIn Room @ time)"],
    "museum":          ["Person", "Location", "CameraEvent (Person wasAt Location @ time)"],
    "phone-call":      ["Person", "PhoneCall (Person called Person @ time)"],
    "stolen-identity": ["Person", "Alias (sameAs Person)", "HotelCheckIn (Alias usedAt Hotel @ time)"],
    "final-heist":     ["Person", "BankAccount (owned by Person)",
                        "Patrol (Person seenIn Zone @ time)",
                        "PhoneCall (Person called PhoneNumber @ time)"],
}


def _kql_value(v):
    """Render a Python value as a KQL inline literal."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        # KQL datetime literal vs string
        if v.endswith("Z") and "T" in v and len(v) >= 19:
            return f"datetime({v})"
        return v   # plain string; quoted via inline ingest CSV semantics
    return str(v)


def _kql_ingest_inline(table: str, rows: list[tuple]) -> str:
    """Build a `.ingest inline into table T <| ... ` command (CSV).

    Booleans are rendered as the literal lowercase `true`/`false`.
    Datetimes are accepted directly as ISO strings (KQL CSV parses them).
    """
    csv_lines = []
    for row in rows:
        parts = []
        for v in row:
            if isinstance(v, bool):
                parts.append("true" if v else "false")
            else:
                parts.append(str(v))
        csv_lines.append(",".join(parts))
    body = "\n".join(csv_lines)
    return f".ingest inline into table {table} <|\n{body}"


# =====================================================================
# ontology_detective_seed.ipynb
# =====================================================================
SEED_CELLS: list[dict] = [
    _md(f"""
    # 🕵️ Ontology Detective — Seed

    > Build stamp: **{BUILD_STAMP}**

    Populates the **Datapolis_DetectiveEH** KQL database with the 5 noir case
    datasets and (re-)creates the `DetectiveEvents` telemetry table.

    **Run all cells once after `arcade.install(\"ontology-detective\")`**.
    """),

    _md("## Step 1 — Resolve KQL endpoint"),
    _code(r"""
    import os, json, uuid, requests
    from IPython.display import Markdown, display

    EH_NAME = "Datapolis_DetectiveEH"
    DB_NAME = "Datapolis_DetectiveEH"

    try:
        import notebookutils
        WORKSPACE_ID = notebookutils.runtime.context.get("currentWorkspaceId")
        _gettoken    = notebookutils.credentials.getToken
    except Exception:
        import mssparkutils
        WORKSPACE_ID = mssparkutils.runtime.context.get("currentWorkspaceId")
        _gettoken    = mssparkutils.credentials.getToken

    FAB = "https://api.fabric.microsoft.com/v1"
    def _fab(url):
        r = requests.get(url, headers={"Authorization": f"Bearer {_gettoken('pbi')}"}, timeout=60)
        r.raise_for_status(); return r.json()

    dbs = _fab(f"{FAB}/workspaces/{WORKSPACE_ID}/items?type=KQLDatabase").get("value", [])
    target = next((d for d in dbs if d["displayName"] == DB_NAME), None)
    if not target:
        raise RuntimeError(f"KQL DB '{DB_NAME}' not found — was arcade.install run?")
    DB_ID = target["id"]
    info = _fab(f"{FAB}/workspaces/{WORKSPACE_ID}/kqlDatabases/{DB_ID}")
    KQL_URI = info["properties"]["queryServiceUri"]
    print("Workspace :", WORKSPACE_ID)
    print("KQL DB    :", DB_NAME, "id=", DB_ID)
    print("Endpoint  :", KQL_URI)
    """),

    _md("## Step 2 — Helpers (KQL management + query)"),
    _code(r"""
    def _kql_mgmt(csl: str):
        tok = _gettoken("kusto")
        r = requests.post(f"{KQL_URI}/v1/rest/mgmt",
                          headers={"Authorization": f"Bearer {tok}",
                                   "Content-Type": "application/json"},
                          json={"csl": csl, "db": DB_NAME}, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"KQL mgmt {r.status_code}: {r.text[:500]}")
        return r.json()

    def _kql_query(csl: str):
        tok = _gettoken("kusto")
        r = requests.post(f"{KQL_URI}/v2/rest/query",
                          headers={"Authorization": f"Bearer {tok}",
                                   "Content-Type": "application/json"},
                          json={"csl": csl, "db": DB_NAME}, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"KQL query {r.status_code}: {r.text[:500]}")
        return r.json()
    """),

    _md("## Step 3 — Apply schema (idempotent `.create-merge`)"),
    _code(rf"""
    SCHEMA = r'''
    .create-merge table DetectiveEvents (
        EventId: string, Timestamp: datetime, SessionId: string, PlayerId: string,
        EventType: string, CaseId: string, AccusedPerson: string,
        ValidationResult: string, DurationSeconds: long, Rank: string
    )

    .alter-merge table DetectiveEvents policy retention softdelete = 90d

    .create-merge table Case1_Visits (
        PersonName: string, RoomName: string, EnteredAt: datetime, LeftAt: datetime
    )

    .create-merge table Case2_CameraEvents (
        GuestName: string, Location: string, SeenAt: datetime
    )

    .create-merge table Case3_PhoneCalls (
        Caller: string, Callee: string, CalledAt: datetime
    )

    .create-merge table Case4_Aliases (
        AliasName: string, RealName: string
    )

    .create-merge table Case4_HotelCheckIns (
        UsedName: string, HotelName: string, CheckedInAt: datetime
    )

    .create-merge table Case5_BankAccounts (
        PersonName: string, AccountKind: string, OpenedAt: datetime
    )

    .create-merge table Case5_PolicePatrols (
        PersonName: string, PatrolZone: string, SeenAt: datetime, OnDutyRegister: bool
    )

    .create-merge table Case5_BurnerCalls (
        Caller: string, Callee: string, CalledAt: datetime
    )
    '''
    for block in [b.strip() for b in SCHEMA.split("\n\n") if b.strip()]:
        _kql_mgmt(block)
        print("  ✓", block.splitlines()[0][:80])
    print("Schema applied.")
    """),

    _md(
        "## Step 4 — Load evidence (idempotent: clears each evidence table first)\n\n"
        "Each evidence row is sent as inline CSV via `.ingest inline into table T <| ...`."
    ),
    _code(_render_seed_evidence_cell()) if False else _code(  # placeholder, real code below
        r"""# placeholder — overwritten in build script"""),
]

# We rebuild Step 4 as a real cell with inlined data
def _render_seed_evidence_cell() -> str:
    blocks = []
    for table, rows in CASE_DATA.items():
        ingest = _kql_ingest_inline(table, rows)
        # KQL .clear table then re-ingest (idempotent for replay)
        blocks.append(f".clear table {table} data")
        blocks.append(ingest)
    joined = "\n\n".join(blocks)
    return (
        "EVIDENCE = r'''\n" + joined + "\n'''\n"
        "for block in [b.strip() for b in EVIDENCE.split('\\n\\n') if b.strip()]:\n"
        "    _kql_mgmt(block)\n"
        "    head = block.splitlines()[0][:90]\n"
        "    print('  ✓', head)\n"
        "print('Evidence loaded for all 5 cases.')"
    )

SEED_CELLS[-1] = _code(_render_seed_evidence_cell())

SEED_CELLS += [
    _md("## Step 5 — Sanity check (row counts per evidence table)"),
    _code(r"""
    counts_kql = r'''
    union withsource=Table
        Case1_Visits, Case2_CameraEvents, Case3_PhoneCalls,
        Case4_Aliases, Case4_HotelCheckIns,
        Case5_BankAccounts, Case5_PolicePatrols, Case5_BurnerCalls
    | summarize Rows=count() by Table
    | order by Table asc
    '''
    res = _kql_query(counts_kql)
    rows = res["Tables"][0]["Rows"]
    md_lines = ["| Table | Rows |", "|-------|-----:|"] + [f"| `{r[0]}` | {r[1]} |" for r in rows]
    display(Markdown("\n".join(md_lines)))
    print("✅ Seeded successfully. Open OntologyDetective_CaseFile next.")
    """),
]


# =====================================================================
# ontology_detective_casefile.ipynb
# =====================================================================
def _briefing_md(case_no: int, case_id: str, icon: str, title: str, body: str) -> str:
    """Render a noir briefing markdown block."""
    return f"""## {icon} Case #{case_no} — {title}\n\n*Case ID: `{case_id}`*\n\n{body}"""


BRIEFINGS = {
    "stolen-pie": ("🧁", "The Stolen Pie", """
> *Rain on the windows. The phone rings before I've finished my second coffee. Mrs. Plum,
> bless her, has lost her championship blueberry pie. Cooling on the kitchen counter, 14:00.
> Back from the garden at 14:30 — gone. Three neighbours dropped by that afternoon. One of
> them left with a warm pie and a guilty smile.*

**The scene** — Mrs. Plum's kitchen, **14:00 to 14:30**, Datapolis suburbs.

**Suspects** — Bob Hollowstone · Alice Greengrass · Mortimer Quill *(plus Mrs. Plum herself)*.

**Evidence** — every entry into a room of the house was logged by Mrs. Plum's smart-home
camera. The table `Case1_Visits` has columns `PersonName`, `RoomName`, `EnteredAt`, `LeftAt`.

**Your job** — build an ontology with at minimum `Person`, `Room`, and a `Visit` relation,
then write a KQL query that returns the **single person, not Mrs. Plum, who was in the
Kitchen during the theft window**. Call `detective.accuse("<their name>")`.
"""),

    "museum": ("🏛️", "Disappearance at the Museum", """
> *Two million credits walked out of the Datapolis Museum last night. The Vector Vase —
> Etruscan, fourth century BC, behind glass that should've held. The gala was packed.
> Eight VIPs, two hundred lesser guests, and every camera in the house humming. The
> alarm tripped at **21:14**. The vase was already gone by **21:18**.*

**The scene** — Etruscan Hall, theft window **21:14 → 21:18**, gala evening 2026-06-04.

**Evidence** — `Case2_CameraEvents` (`GuestName`, `Location`, `SeenAt`). The cameras
sampled each guest as they entered a new room.

**Your job** — extend the ontology with `Location` and a temporal `CameraEvent`. Find the
**one guest** captured at the Etruscan Hall **between 21:14 and 21:18 inclusive**. Accuse
them.
"""),

    "phone-call": ("📞", "The Mysterious Phone Call", """
> *Senator Carballo dropped at dinner last night. Coroner says aconitine — a poison so
> rare in Datapolis only one chemist still keeps it: Doc Aconite. We pulled the phone
> records. The killer didn't poison Carballo himself — he had the dose delivered. Means
> he called Carballo to know when, and called Doc Aconite to get the stuff. Within a
> two-hour window.*

**The scene** — phone records for 2026-06-03, `Case3_PhoneCalls` (`Caller`, `Callee`,
`CalledAt`).

**Your job** — model `Person` with a self-relationship `called`. Find the **one person
who placed a call to BOTH `Senator Carballo` AND `Dr. Aconite`, with the two calls less
than 2 hours apart**. Hint: `datetime_diff('minute', t1, t2)`. Accuse them.
"""),

    "stolen-identity": ("🎭", "Stolen Identity", """
> *Three men in Datapolis answer to "Mr. Vega." One's a real estate broker. One's a
> teenage influencer. One's a forger working out of a back room in Quantum Hall. A
> stolen-card report from Hotel Quantum, night of June 1st: someone checked in under a
> Vega alias and ran up 12k in charges before vanishing. The receipt's signed in a name
> that isn't on any ID. But every Vega has aliases.*

**The scene** — Hotel Quantum, check-in window **22:00 on 2026-06-01 → 02:00 on 2026-06-02**.

**Evidence** — `Case4_Aliases` (`AliasName`, `RealName`) maps every known alias to the
real Vega. `Case4_HotelCheckIns` (`UsedName`, `HotelName`, `CheckedInAt`) is the
front-desk register.

**Your job** — model `Person` + an `Alias` with a `sameAs` link. **Resolve** the alias of
the check-in at Hotel Quantum in the window, then accuse the **real Vega** behind it.
"""),

    "final-heist": ("🌃", "The Final Heist (BOSS)", """
> *Fifty million crypto-bonds out of the Central Bank vault at exactly 23:05 last night.
> Whoever pulled this off needed three things lined up: a clean shell account to land the
> bonds in, a way into the Bank District without showing up on the patrol register, and a
> burner-line call placed in the ten-minute window of the heist. Three agencies — Bank,
> Police, Telecom — each gave us a partial list. One name is on all three.*

**The scene** — 2026-06-05, heist window **23:00 → 23:10**, Bank District.

**Evidence (3 sources)**
- `Case5_BankAccounts` — who opened an `AccountKind == "RelayShell"`
- `Case5_PolicePatrols` — who was seen in `PatrolZone == "Bank District"` with
  `OnDutyRegister == false`
- `Case5_BurnerCalls` — who called `Callee == "+39-X-USA-E-GETTA"` in the heist window

**Your job** — federate three sub-namespaces (`Bank.Account`, `Police.Patrol`,
`Telecom.PhoneCall`) under one shared `Person`. Compute the **intersection**. Accuse the
single name that appears in all three. *(Note: this case is on you to solve. The whole
city is watching.)*
"""),
}


CASEFILE_CELLS: list[dict] = [
    _md(f"""
    # 🕵️ Ontology Detective — Case File

    > Build stamp: **{BUILD_STAMP}** · *Datapolis P.I.*

    Five cases. One ontology. Your reputation on the line.

    **Loop for every case**
    1. Read the **briefing**.
    2. Open **`DetectiveOntology`** in Fabric **Digital Twin Builder** UI; add the entity
       types and relationships the briefing calls for.
    3. Write a **KQL query** against the case tables until it returns a single suspect.
    4. Call `detective.accuse(case_id, "Name")`.

    Solve all five to be promoted **Commissioner of Datapolis** and mint your badge.
    """),

    _md("## ⚙️ Step 0 — Player"),
    _code(r"""
    # --- EDIT THIS ---
    PLAYER_NAME = "Your Name Here"   # shown on your shareable badge
    # -----------------
    print(f"Player: {PLAYER_NAME}")
    """),

    _md("## Step 1 — Endpoints, helpers, judge"),
    _code(r"""
    import os, uuid, json, time, datetime as dt, requests
    from IPython.display import Markdown, display, HTML

    EH_NAME = "Datapolis_DetectiveEH"
    DB_NAME = "Datapolis_DetectiveEH"

    try:
        import notebookutils
        WORKSPACE_ID = notebookutils.runtime.context.get("currentWorkspaceId")
        _gettoken    = notebookutils.credentials.getToken
    except Exception:
        import mssparkutils
        WORKSPACE_ID = mssparkutils.runtime.context.get("currentWorkspaceId")
        _gettoken    = mssparkutils.credentials.getToken

    FAB = "https://api.fabric.microsoft.com/v1"
    SESSION_ID = str(uuid.uuid4())
    PLAYER_ID  = os.environ.get("USER", "detective")

    def _fab(url):
        r = requests.get(url, headers={"Authorization": f"Bearer {_gettoken('pbi')}"}, timeout=60)
        r.raise_for_status(); return r.json()

    dbs = _fab(f"{FAB}/workspaces/{WORKSPACE_ID}/items?type=KQLDatabase").get("value", [])
    target = next((d for d in dbs if d["displayName"] == DB_NAME), None)
    if not target: raise RuntimeError(f"KQL DB '{DB_NAME}' not found")
    DB_ID = target["id"]
    KQL_URI = _fab(f"{FAB}/workspaces/{WORKSPACE_ID}/kqlDatabases/{DB_ID}")["properties"]["queryServiceUri"]
    print("Player    :", PLAYER_NAME)
    print("Session   :", SESSION_ID)
    print("Endpoint  :", KQL_URI)
    """),

    _code(r"""
    def query_kql(csl: str):
        '''Run a KQL query against Datapolis_DetectiveEH. Returns list[dict].'''
        tok = _gettoken("kusto")
        r = requests.post(f"{KQL_URI}/v2/rest/query",
                          headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                          json={"csl": csl, "db": DB_NAME}, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"KQL query {r.status_code}: {r.text[:500]}")
        # v2 response: locate the PrimaryResult frame
        for frame in r.json():
            if frame.get("FrameType") == "DataTable" and frame.get("TableKind") == "PrimaryResult":
                cols = [c["ColumnName"] for c in frame["Columns"]]
                return [dict(zip(cols, row)) for row in frame["Rows"]]
        return []

    def _mgmt(csl: str):
        tok = _gettoken("kusto")
        r = requests.post(f"{KQL_URI}/v1/rest/mgmt",
                          headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                          json={"csl": csl, "db": DB_NAME}, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"KQL mgmt {r.status_code}: {r.text[:500]}")

    def _q(v):
        s = str(v).replace("'", "\\'")
        return f"'{s}'"

    def log_event(event_type: str, case_id: str = "", accused: str = "",
                  result: str = "INFO", duration_s: int = 0, rank: str = ""):
        cmd = (
            f".ingest inline into table DetectiveEvents <|\n"
            f"{uuid.uuid4()},{dt.datetime.utcnow().isoformat()}Z,{SESSION_ID},{PLAYER_ID},"
            f"{event_type},{case_id},{accused},{result},{duration_s},{rank}"
        )
        try: _mgmt(cmd)
        except Exception as e: print(f"(telemetry suppressed: {e})")
    """),

    _md("## Step 2 — Detective class & ranks"),
    _code(r"""
    # The truth (no encryption — fair game; the goal is learning, not security theatre).
    CULPRITS = {
        "stolen-pie":      "Bob Hollowstone",
        "museum":          "Lady Marlowe",
        "phone-call":      "Vincenzo Lupara",
        "stolen-identity": "Ricardo Vega",
        "final-heist":     "Madame Cinquedeo",
    }

    CASES = [
        ("stolen-pie",      "🧁 The Stolen Pie"),
        ("museum",          "🏛️ Disappearance at the Museum"),
        ("phone-call",      "📞 The Mysterious Phone Call"),
        ("stolen-identity", "🎭 Stolen Identity"),
        ("final-heist",     "🌃 The Final Heist (BOSS)"),
    ]

    RANKS = [
        (0, "Aspiring Detective"),
        (1, "🥉 Rookie"),
        (2, "🥈 Investigator"),
        (3, "🎯 Inspector"),
        (4, "🔍 Senior Detective"),
        (5, "🏆 Commissioner of Datapolis"),
    ]
    def rank_for(solved: int) -> str:
        out = RANKS[0][1]
        for n, r in RANKS:
            if solved >= n: out = r
        return out

    class Detective:
        def help(self):
            md = ["### 🕵️ Detective Sherlock Graph — Datapolis P.I.\n",
                  "Methods:",
                  "- `detective.briefing(case_id)` — re-print a case briefing",
                  "- `detective.case_list()` — show all 5 cases + status",
                  "- `detective.accuse(case_id, \"Name\")` — submit your accusation",
                  "- `detective.scoreboard()` — cases solved, rank, accuracy"]
            display(Markdown("\n".join(md)))

        def case_list(self):
            solved = self._solved_set()
            rows = ["| # | Case | Status |", "|---|------|--------|"]
            for i, (cid, name) in enumerate(CASES, start=1):
                tag = "✅ Solved" if cid in solved else "🔓 Open"
                rows.append(f"| {i} | {name} | {tag} |")
            display(Markdown("\n".join(rows)))

        def briefing(self, case_id: str):
            md = BRIEFINGS_MD.get(case_id)
            if not md:
                print(f"❌ Unknown case: {case_id}. Try one of: {list(BRIEFINGS_MD)}")
                return
            log_event("CaseOpened", case_id=case_id, result="INFO")
            display(Markdown(md))

        def _solved_set(self) -> set:
            try:
                rows = query_kql(
                    f"DetectiveEvents | where SessionId == '{SESSION_ID}' "
                    f"and EventType == 'CaseSolved' | summarize by CaseId"
                )
                return {r["CaseId"] for r in rows if r.get("CaseId")}
            except Exception:
                return set()

        def accuse(self, case_id: str, accused: str):
            if case_id not in CULPRITS:
                print(f"❌ Unknown case: {case_id}"); return
            expected = CULPRITS[case_id]
            log_event("AccusationMade", case_id=case_id, accused=accused, result="INFO")
            if accused.strip().lower() == expected.lower():
                log_event("CaseSolved", case_id=case_id, accused=accused, result="CORRECT")
                display(Markdown(
                    f"### ✅ Case `{case_id}` — solved\n\n"
                    f"**{accused}** is in the holding cell. Datapolis sleeps easier."
                ))
            else:
                log_event("WrongAccusation", case_id=case_id, accused=accused, result="WRONG")
                display(Markdown(
                    f"### ❌ Wrong accusation\n\n"
                    f"**{accused}** has been released with apologies. Re-read the briefing, "
                    f"rework your KQL, and try again with `detective.accuse(\"{case_id}\", ...)`."
                ))
            self.scoreboard()

        def scoreboard(self):
            try:
                acc = query_kql(
                    f"DetectiveEvents | where SessionId == '{SESSION_ID}' "
                    f"and EventType in ('CaseSolved','WrongAccusation') "
                    f"| summarize Solved=countif(EventType=='CaseSolved'), "
                    f"Wrong=countif(EventType=='WrongAccusation')"
                )
            except Exception as e:
                print(f"(scoreboard unavailable: {e})"); return
            row = acc[0] if acc else {"Solved": 0, "Wrong": 0}
            solved = int(row.get("Solved", 0) or 0)
            wrong  = int(row.get("Wrong",  0) or 0)
            rank   = rank_for(solved)
            display(Markdown(
                f"### 🏛️ Detective scoreboard (this session)\n\n"
                f"- Cases solved : **{solved}/5**\n"
                f"- Wrong calls  : **{wrong}**\n"
                f"- Rank         : **{rank}**\n\n"
                f"> Solve all 5 cases, then run the badge cell at the bottom of this notebook."
            ))
            globals()["FINAL_SCORE"] = solved
            globals()["FINAL_RANK"]  = rank

    detective = Detective()
    log_event("DetectiveOnDuty", result="INFO")
    print("🕵️ Detective on duty. Try: detective.help()")
    """),

    _md("## Step 3 — Briefings (markdown)"),
    _code(r"""
    BRIEFINGS_MD = """ + repr({k: _briefing_md(i+1, k, *v[:1], v[1], v[2])
                                 for i, (k, v) in enumerate(BRIEFINGS.items())}) + r"""
    """),

    _md("## Step 4 — Play"),
    _code(r"""
    detective.help()
    """),
    _code(r"""
    # detective.case_list()
    """),
    _code(r"""
    # detective.briefing("stolen-pie")
    """),
    _code(r"""
    # --- Example KQL workspace (run any case query here) ---
    # rows = query_kql('''
    # Case1_Visits
    # | where RoomName == "Kitchen"
    # | where EnteredAt < datetime(2026-06-05 14:30:00)
    #   and LeftAt   > datetime(2026-06-05 14:00:00)
    # | where PersonName != "Mrs. Plum"
    # | project PersonName
    # ''')
    # rows
    """),
    _code(r"""
    # detective.accuse("stolen-pie", "Bob Hollowstone")
    """),

    _md(
        "## Step 5 — Show all briefings + scoreboard\n\n"
        "Run this after you've worked each case. It re-prints the 5 briefings (handy as a "
        "quick recap) and shows your current scoreboard / rank. Then move on to the badge cell."
    ),
    _code(r"""
    for cid, _name in CASES:
        detective.briefing(cid)
    detective.scoreboard()
    """),

    _md("## Step 6 — 🏅 Mint your shareable badge"),
    _code(r"""
    # ============================================================
    # Ontology Detective — Badge issuance (same pattern as retro-arcade / city-builder)
    # ============================================================
    import json, time, hmac, hashlib, base64
    from IPython.display import display, Markdown, HTML

    _BADGE_SECRET = b"fabric-arcade-badge-v1-7K9mP3xQ"
    _BASE_URL     = "https://maenglar78.github.io/fabric-arcade"
    _GAME_ID      = "ontology-detective"
    _SKILLS       = ["Fabric Ontology", "Digital Twin Builder", "KQL",
                     "Knowledge Graph", "Entity Resolution"]

    def _b64u(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

    def _issue(game_id, player, rank, score):
        payload = {"v": 1, "g": game_id, "p": str(player),
                   "r": str(rank), "s": int(score), "t": int(time.time()),
                   "k": _SKILLS}
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        sig  = hmac.new(_BADGE_SECRET, body, hashlib.sha256).digest()
        return f"{_BASE_URL}/badge.html?t={_b64u(body)}.{_b64u(sig)}"

    score = globals().get("FINAL_SCORE", 0)
    rank  = globals().get("FINAL_RANK", "Aspiring Detective")

    if score < 1:
        display(Markdown(
            f"### 🚧 Not yet eligible (cases solved {score}/5)\n\n"
            f"Solve **at least 1 case** to earn the Rookie badge. "
            f"Run `detective.accuse(...)` on any open case, then re-run "
            f"`detective.scoreboard()` and this cell."
        ))
    elif PLAYER_NAME.strip() in ("", "Your Name Here"):
        display(Markdown(
            "### ✍️ Set your name first\n\n"
            "Edit `PLAYER_NAME` in **Step 0** and re-run `detective.scoreboard()` + this cell."
        ))
    else:
        url = _issue(_GAME_ID, PLAYER_NAME, rank, score)
        display(Markdown(
            f"### 🏅 Badge minted\n\n"
            f"**{PLAYER_NAME}** — *{rank}* · cases solved **{score}/5**\n\n"
            f"🔗 **[Open your badge]({url})**\n\n"
            f"Click *Download PNG* / *Share on LinkedIn* on the badge page."
        ))
        display(HTML(f'<a href="{url}" target="_blank" '
                     f'style="display:inline-block;padding:10px 20px;border-radius:8px;'
                     f'background:linear-gradient(135deg,#00d4ff,#8338ec);color:white;'
                     f'text-decoration:none;font-weight:600">🏅 Open my badge page</a>'))
        log_event("BadgeIssued", case_id="all", accused=url, result="ISSUED", rank=rank)
    """),
]


# =====================================================================
# ontology_detective_dashboard.ipynb
# =====================================================================
DASH_CELLS: list[dict] = [
    _md(f"""
    # 🕵️ Ontology Detective — Dashboard

    > Build stamp: **{BUILD_STAMP}**

    Reads `DetectiveEvents` from **Datapolis_DetectiveEH** and shows cases solved,
    accuracy, and detective rank across all sessions.
    """),

    _code(r"""
    import os, requests
    from IPython.display import Markdown, display

    EH_NAME = "Datapolis_DetectiveEH"
    DB_NAME = "Datapolis_DetectiveEH"
    try:
        import notebookutils
        WORKSPACE_ID = notebookutils.runtime.context.get("currentWorkspaceId")
        _gettoken    = notebookutils.credentials.getToken
    except Exception:
        import mssparkutils
        WORKSPACE_ID = mssparkutils.runtime.context.get("currentWorkspaceId")
        _gettoken    = mssparkutils.credentials.getToken
    FAB = "https://api.fabric.microsoft.com/v1"
    def _fab(url):
        r = requests.get(url, headers={"Authorization": f"Bearer {_gettoken('pbi')}"}, timeout=60)
        r.raise_for_status(); return r.json()
    dbs = _fab(f"{FAB}/workspaces/{WORKSPACE_ID}/items?type=KQLDatabase").get("value", [])
    DB_ID = next(d for d in dbs if d["displayName"] == DB_NAME)["id"]
    KQL_URI = _fab(f"{FAB}/workspaces/{WORKSPACE_ID}/kqlDatabases/{DB_ID}")["properties"]["queryServiceUri"]

    def query_kql(csl):
        tok = _gettoken("kusto")
        r = requests.post(f"{KQL_URI}/v2/rest/query",
                          headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                          json={"csl": csl, "db": DB_NAME}, timeout=120)
        r.raise_for_status()
        for f in r.json():
            if f.get("FrameType") == "DataTable" and f.get("TableKind") == "PrimaryResult":
                cols = [c["ColumnName"] for c in f["Columns"]]
                return [dict(zip(cols, row)) for row in f["Rows"]]
        return []
    """),

    _md("## Cases solved per player"),
    _code(r"""
    rows = query_kql('''
    DetectiveEvents
    | where EventType in ('CaseSolved','WrongAccusation','BadgeIssued')
    | summarize Solved=dcountif(CaseId, EventType=='CaseSolved'),
                Wrong=countif(EventType=='WrongAccusation'),
                Badges=countif(EventType=='BadgeIssued')
      by PlayerId
    | order by Solved desc, Wrong asc
    ''')
    if not rows:
        display(Markdown("_No detective activity yet._"))
    else:
        md = ["| Player | Solved | Wrong calls | Badges |", "|--------|-------:|------------:|-------:|"]
        for r in rows:
            md.append(f"| `{r['PlayerId']}` | {r['Solved']} | {r['Wrong']} | {r['Badges']} |")
        display(Markdown("\n".join(md)))
    """),

    _md("## Recent events (last 25)"),
    _code(r"""
    rows = query_kql('''
    DetectiveEvents
    | order by Timestamp desc
    | take 25
    | project Timestamp, PlayerId, EventType, CaseId, AccusedPerson, ValidationResult
    ''')
    if not rows:
        display(Markdown("_No events._"))
    else:
        md = ["| When | Player | Event | Case | Accused | Result |",
              "|------|--------|-------|------|---------|--------|"]
        for r in rows:
            md.append(f"| {r['Timestamp']} | `{r['PlayerId']}` | {r['EventType']} | "
                      f"{r['CaseId']} | {r['AccusedPerson']} | {r['ValidationResult']} |")
        display(Markdown("\n".join(md)))
    """),
]


def main() -> int:
    print(f"Build stamp: {BUILD_STAMP}")
    _write("ontology_detective_seed.ipynb",      SEED_CELLS)
    _write("ontology_detective_casefile.ipynb",  CASEFILE_CELLS)
    _write("ontology_detective_dashboard.ipynb", DASH_CELLS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
