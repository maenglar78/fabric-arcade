"""
Build the 3 City Builder notebooks (.ipynb) into the catalog folder.

  - city_builder_seed.ipynb       (PHASE 1: fully implemented — PySpark seed)
  - city_builder_mayor.ipynb      (PHASE 2 stub for now)
  - city_builder_dashboard.ipynb  (PHASE 3 stub for now)

Run:
    python dev/city/build_notebooks.py
"""
from __future__ import annotations
import json
from pathlib import Path
from textwrap import dedent
import datetime as _dt

ROOT = Path(__file__).resolve().parents[2]
CATALOG_NB = ROOT / "catalog" / "city-builder" / "notebooks"
CATALOG_NB.mkdir(parents=True, exist_ok=True)

BUILD_STAMP = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Build stamp: {BUILD_STAMP}")


FABRIC_NB_METADATA = {
    "kernelspec": {"display_name": "Synapse PySpark", "language": "python", "name": "synapse_pyspark"},
    "language_info": {"name": "python"},
    "microsoft": {
        "language": "python",
        "language_group": "synapse_pyspark",
        "ms_spell_check": {"ms_spell_check_language": "en"},
    },
    "nteract": {"version": "nteract-front-end@1.0.0"},
    "spark_compute": {"compute_id": "/trident/default", "session_options": {"conf": {}}},
    "synapse_widget": {"state": {}, "version": "0.1"},
    "widgets": {},
}


def _md(text: str) -> dict:
    src = dedent(text).strip("\n") + "\n"
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def _code(text: str, hidden: bool = False) -> dict:
    src = dedent(text).strip("\n") + "\n"
    meta: dict = {}
    if hidden:
        meta["jupyter"] = {"source_hidden": True}
        meta["collapsed"] = True
    return {
        "cell_type": "code",
        "metadata": meta,
        "execution_count": None,
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }


def _nb(cells: list[dict]) -> dict:
    return {"nbformat": 4, "nbformat_minor": 5, "metadata": FABRIC_NB_METADATA, "cells": cells}


def write_nb(name: str, cells: list[dict]) -> Path:
    p = CATALOG_NB / f"{name}.ipynb"
    p.write_text(json.dumps(_nb(cells), indent=1), encoding="utf-8")
    return p


# =====================================================================
# city_builder_seed.ipynb — Datapolis raw + Blueprint generators
# =====================================================================

SEED_CELLS = [
    _md(f"""
    # 🏙️ City Builder — Seed Datapolis_LH

    > Build stamp: **{BUILD_STAMP}**

    Run this notebook **ONCE** to populate **Datapolis_LH** with the raw
    "dirty" datasets and the blueprint answer keys the Mayor will use to
    validate your warehouse build.

    ## Requirements
    1. Attach **`Datapolis_LH`** as the default Lakehouse (📚 icon → *Add* → Existing Lakehouse).
    2. Run all cells top → bottom.

    Runtime: ~2–3 minutes.

    ## What gets created (all Delta tables)

    | District | Raw tables | Blueprint table |
    |---|---|---|
    | 1 Town Hall | `raw_phantom_census` | `blueprint_town_hall` |
    | 2 Neon District | `raw_neon_residents`, `raw_neon_residents_updates` | `blueprint_neon_district` |
    | 3 Skylane | `raw_skylane_traffic` | `blueprint_skylane` |
    | 4 Plasma Core | `raw_plasma_readings` | `blueprint_plasma_core` |
    | 5 Bazaar 9 | `raw_bazaar_sales` | `blueprint_bazaar_9` |
    | 6 Cryo Hospital | `raw_cryo_admissions` | `blueprint_cryo_hospital` |
    | 7 Holo-Stage | `raw_holo_shows`, `raw_holo_artists`, `raw_holo_lineup` | `blueprint_holo_stage` |
    | 8 Grid Overlook (BOSS) | — (reuses 3, 4, 5) | `blueprint_grid_overlook` |

    Blueprint tables follow shape `(MeasureName STRING, ExpectedValue DOUBLE)` and are
    used by the Mayor's DAX-vs-blueprint validation.
    """),

    _md("## Step 1 — Setup"),
    _code(r"""
    import random
    from datetime import date, datetime, timedelta
    from pyspark.sql import functions as F, types as T, Row

    # Deterministic seed so Blueprint values are reproducible across runs.
    random.seed(2049)

    SCALE_SKYLANE = 80_000   # flights (district 3)
    SCALE_PLASMA  = 26_280   # hourly readings = 3 years
    SCALE_BAZAAR  = 30_000   # sales        (district 5)
    SCALE_CRYO    =  8_000   # admissions   (district 6)

    print("Datapolis seed parameters loaded.")
    """, hidden=True),

    # ----------------------- District 1 -----------------------
    _md("## Step 2 — District 1: Town Hall (Phantom Census)"),
    _code(r"""
    # Single dump tape: each row is EITHER a citizen attribute row OR a life event row,
    # but they live in the same table with mixed columns and NULLs. Player must split.
    EVENT_TYPES = ["Birth", "Death", "Move_In", "Move_Out"]
    DISTRICTS   = ["Town Hall", "Neon", "Skylane Hub", "Plasma Core", "Bazaar 9",
                   "Cryo Hospital", "Fabricator", "Holo-Stage"]
    PROFESSIONS = ["Tech-Smith", "Bio-Hacker", "Drone Pilot", "Cryo Nurse",
                   "Plasma Tuner", "Net Runner", "Cartographer", "Vendor"]

    NUM_CITIZENS = 1_500
    NUM_EVENTS   = 6_000
    base_date = date(2046, 1, 1)

    rows = []
    # Attribute rows: one per citizen
    for cid in range(1, NUM_CITIZENS + 1):
        rows.append(Row(
            row_type="ATTR",
            citizen_id=f"CT-{cid:05d}",
            full_name=f"Resident_{cid:04d}",
            profession=random.choice(PROFESSIONS),
            home_district=random.choice(DISTRICTS),
            event_type=None,
            event_date=None,
        ))
    # Event rows: many per citizen
    for _ in range(NUM_EVENTS):
        cid = random.randint(1, NUM_CITIZENS)
        rows.append(Row(
            row_type="EVENT",
            citizen_id=f"CT-{cid:05d}",
            full_name=None,
            profession=None,
            home_district=None,
            event_type=random.choices(EVENT_TYPES, weights=[3, 1, 4, 2])[0],
            event_date=base_date + timedelta(days=random.randint(0, 365 * 3)),
        ))
    random.shuffle(rows)
    df = spark.createDataFrame(rows)
    df.write.mode("overwrite").format("delta").saveAsTable("raw_phantom_census")
    print(f"  raw_phantom_census: {df.count():,} rows (mixed attr + event)")

    # Blueprint
    births = sum(1 for r in rows if r.row_type == "EVENT" and r.event_type == "Birth")
    deaths = sum(1 for r in rows if r.row_type == "EVENT" and r.event_type == "Death")
    blueprint = spark.createDataFrame([
        ("Citizens",              float(NUM_CITIZENS)),
        ("Birth Events",          float(births)),
        ("Death Events",          float(deaths)),
        ("Net Population Change", float(births - deaths)),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_town_hall")
    print(f"  blueprint_town_hall: {blueprint.count()} measures")
    """),

    # ----------------------- District 2 -----------------------
    _md("## Step 3 — District 2: Neon District (Shifting Identities)"),
    _code(r"""
    # Two raw files: original residents + a later "updates" file that overwrites
    # full_name and is_augmented for some citizens. SCD Type 1 territory.
    NUM_RES = 600
    AUGMENT_RATE = 0.30
    UPDATE_RATE  = 0.20

    original = []
    for i in range(1, NUM_RES + 1):
        original.append(Row(
            citizen_id=f"CT-{i:05d}",
            full_name=f"Resident_{i:04d}",
            is_augmented=False,
            district="Neon",
            tier=random.choice(["Bronze", "Silver", "Gold"]),
        ))
    df1 = spark.createDataFrame(original)
    df1.write.mode("overwrite").format("delta").saveAsTable("raw_neon_residents")

    upd_rows = []
    n_updates = int(NUM_RES * UPDATE_RATE)
    for i in random.sample(range(1, NUM_RES + 1), n_updates):
        upd_rows.append(Row(
            citizen_id=f"CT-{i:05d}",
            full_name=f"Aug_{i:04d}_v2",   # new name after augmentation
            is_augmented=True,
            district="Neon",
            tier="Gold",
        ))
    df2 = spark.createDataFrame(upd_rows)
    df2.write.mode("overwrite").format("delta").saveAsTable("raw_neon_residents_updates")

    # Blueprint: final state after SCD-1 merge — N residents, n_updates of them augmented.
    blueprint = spark.createDataFrame([
        ("Residents",            float(NUM_RES)),
        ("Augmented Residents",  float(n_updates)),
        ("Gold Tier Residents",  float(
            sum(1 for r in original if r.tier == "Gold") + n_updates - sum(
                1 for r in original if r.tier == "Gold" and r.citizen_id in {u.citizen_id for u in upd_rows}
            )
        )),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_neon_district")
    print(f"  raw_neon_residents: {NUM_RES} | updates: {n_updates} | Blueprint saved")
    """),

    # ----------------------- District 3 -----------------------
    _md("## Step 3 — District 3: Skylane (Anti-Grav Couriers)"),
    _code(r"""
    SECTORS = ["Alpha-Cargo", "Beta-Medical", "Gamma-Civilian", "Delta-Military",
               "Epsilon-Pleasure", "Zeta-Industrial"]
    base_date = date(2046, 1, 1)
    rows = []
    for fid in range(1, SCALE_SKYLANE + 1):
        d = base_date + timedelta(days=random.randint(0, 365 * 3))
        dur = random.randint(8, 90)             # minutes
        dist_km = round(random.uniform(2.0, 60.0), 2)
        fuel = round(dist_km * random.uniform(0.4, 0.9), 3)   # He-3 kg
        # 2% NULL pickup sector to simulate dirty data
        psec = None if random.random() < 0.02 else random.choice(SECTORS)
        dsec = random.choice(SECTORS)
        rows.append(Row(
            flight_id=f"FL-{fid:06d}",
            flight_date=d,
            pickup_sector=psec,
            drop_sector=dsec,
            duration_min=dur,
            distance_km=float(dist_km),
            helium3_kg=float(fuel),
        ))
    df = spark.createDataFrame(rows)
    df.write.mode("overwrite").format("delta").saveAsTable("raw_skylane_traffic")

    # Blueprint uses CLEAN values (after dropping NULL pickup_sector for the count).
    clean = df.dropna(subset=["pickup_sector"])
    n_flights = clean.count()
    total_he3 = clean.agg(F.sum("helium3_kg")).first()[0]
    avg_dur   = clean.agg(F.avg("duration_min")).first()[0]
    blueprint = spark.createDataFrame([
        ("Flights",                float(n_flights)),
        ("Total Helium-3 Burned",  float(total_he3)),
        ("Avg Flight Duration",    float(avg_dur)),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_skylane")
    print(f"  raw_skylane_traffic: {df.count():,} flights ({df.count()-n_flights} with NULL pickup) | Blueprint saved")
    """),

    # ----------------------- District 4 -----------------------
    _md("## Step 4 — District 4: Plasma Core (Reactor Readings)"),
    _code(r"""
    # 3 years × 365 × 24 = 26,280 hourly snapshots.
    base_dt = datetime(2046, 1, 1, 0, 0, 0)
    pressure_base = 4.2     # MPa
    temp_base     = 1450.0  # K
    mw_base       = 320.0   # output

    THRESHOLD = 5.0  # critical pressure
    rows = []
    total_critical = 0
    p_sum = 0.0
    p_n   = 0
    mw_max = 0.0
    for h in range(SCALE_PLASMA):
        ts = base_dt + timedelta(hours=h)
        # Slight diurnal + noise
        wave = 0.4 * (((h % 24) - 12) / 12)
        p = pressure_base + wave + random.gauss(0, 0.25)
        t = temp_base + 50 * wave + random.gauss(0, 12)
        mw = mw_base + 20 * wave + random.gauss(0, 8)
        rows.append(Row(
            reading_ts=ts,
            pressure_mpa=float(p),
            temperature_k=float(t),
            output_mw=float(mw),
        ))
        p_sum += p; p_n += 1
        if p > THRESHOLD: total_critical += 1
        if mw > mw_max: mw_max = mw

    df = spark.createDataFrame(rows)
    df.write.mode("overwrite").format("delta").saveAsTable("raw_plasma_readings")

    blueprint = spark.createDataFrame([
        ("Avg Pressure",    float(p_sum / p_n)),
        ("Max Output MW",   float(mw_max)),
        ("Critical Hours",  float(total_critical)),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_plasma_core")
    print(f"  raw_plasma_readings: {df.count():,} hourly | avg P={p_sum/p_n:.3f} | critical hours={total_critical}")
    """),

    # ----------------------- District 5 -----------------------
    _md("## Step 5 — District 5: Bazaar 9 (Quantum Market)"),
    _code(r"""
    base_date = date(2046, 1, 1)
    rows = []
    precog_count = 0
    total_amount = 0.0
    delivery_total = 0.0
    for sid in range(1, SCALE_BAZAAR + 1):
        od = base_date + timedelta(days=random.randint(0, 365 * 3))
        # 8% of sales are pre-cog (delivered BEFORE ordered)
        offset = random.randint(-3, 7)
        is_precog = offset < 0
        if is_precog: precog_count += 1
        dd = od + timedelta(days=offset)
        amt = round(random.uniform(8.0, 1200.0), 2)
        total_amount += amt
        delivery_total += amt
        rows.append(Row(
            sale_id=f"SL-{sid:07d}",
            order_date=od,
            delivery_date=dd,
            customer_id=f"C-{random.randint(1, 4000):05d}",
            amount_credits=float(amt),
            is_pre_cog=bool(is_precog),
        ))
    df = spark.createDataFrame(rows)
    df.write.mode("overwrite").format("delta").saveAsTable("raw_bazaar_sales")

    blueprint = spark.createDataFrame([
        ("Sales by Order Date",     float(total_amount)),
        ("Sales by Delivery Date",  float(delivery_total)),
        ("Pre-Cog Deliveries",      float(precog_count)),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_bazaar_9")
    print(f"  raw_bazaar_sales: {df.count():,} sales | pre-cog: {precog_count} ({precog_count/SCALE_BAZAAR:.1%})")
    """),

    # ----------------------- District 6 -----------------------
    _md("## Step 6 — District 6: Cryo Hospital (Admission Tags)"),
    _code(r"""
    base_date = date(2046, 1, 1)
    rows = []
    vip_emergency = 0
    sum_dur = 0
    for aid in range(1, SCALE_CRYO + 1):
        ad = base_date + timedelta(days=random.randint(0, 365 * 3))
        is_emerg = random.random() < 0.20
        has_ins  = random.random() < 0.65
        is_aug   = random.random() < 0.40
        is_vip   = random.random() < 0.05
        if is_emerg and is_vip: vip_emergency += 1
        dur = random.randint(1, 1095)  # days in cryo
        sum_dur += dur
        rows.append(Row(
            cryo_ticket=f"CRYO-{aid:07d}",
            admission_date=ad,
            duration_days=int(dur),
            is_emergency=bool(is_emerg),
            has_insurance=bool(has_ins),
            is_augmented=bool(is_aug),
            is_vip=bool(is_vip),
        ))
    df = spark.createDataFrame(rows)
    df.write.mode("overwrite").format("delta").saveAsTable("raw_cryo_admissions")

    blueprint = spark.createDataFrame([
        ("Admissions",                 float(SCALE_CRYO)),
        ("VIP Emergency Admissions",   float(vip_emergency)),
        ("Avg Cryo Duration",          float(sum_dur / SCALE_CRYO)),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_cryo_hospital")
    print(f"  raw_cryo_admissions: {df.count():,} | VIP-Emerg: {vip_emergency} | avg dur={sum_dur/SCALE_CRYO:.1f}d")
    """),

    # ----------------------- District 7 -----------------------
    _md("## Step 7 — District 7: Holo-Stage (M:N Bridge)"),
    _code(r"""
    NUM_ARTISTS = 80
    NUM_SHOWS   = 1_200
    base_date = date(2046, 1, 1)
    GENRES   = ["Synth-Opera", "Glitch-Comedy", "Holo-Drama", "Neon-Jazz", "Cyber-Mime"]
    REGIONS  = ["Alpha", "Beta", "Gamma", "Delta"]

    artists = []
    for i in range(1, NUM_ARTISTS + 1):
        artists.append(Row(
            artist_id=f"A-{i:03d}",
            artist_name=f"DJ_{i:03d}",
            region=random.choice(REGIONS),
            base_cachet=round(random.uniform(500, 5000), 2),
        ))
    spark.createDataFrame(artists).write.mode("overwrite").format("delta").saveAsTable("raw_holo_artists")

    shows = []
    sold_total = 0.0
    show_attend = 0
    for s in range(1, NUM_SHOWS + 1):
        sd = base_date + timedelta(days=random.randint(0, 365 * 3))
        attend = random.randint(50, 800)
        rev = round(attend * random.uniform(12.0, 28.0), 2)
        show_attend += attend
        sold_total  += rev
        shows.append(Row(
            show_id=f"SH-{s:05d}",
            show_date=sd,
            genre=random.choice(GENRES),
            attendance=int(attend),
            revenue_credits=float(rev),
        ))
    spark.createDataFrame(shows).write.mode("overwrite").format("delta").saveAsTable("raw_holo_shows")

    # Lineup: M:N — each show has 2-6 artists.
    lineup = []
    artist_ids = [a.artist_id for a in artists]
    show_ids   = [s.show_id   for s in shows]
    cachet_by_show: dict[str, float] = {}
    for sid in show_ids:
        k = random.randint(2, 6)
        picks = random.sample(artist_ids, k)
        show_cachet = 0.0
        for aid in picks:
            cachet = next(a.base_cachet for a in artists if a.artist_id == aid)
            lineup.append(Row(show_id=sid, artist_id=aid, cachet=float(cachet)))
            show_cachet += cachet
        cachet_by_show[sid] = show_cachet
    spark.createDataFrame(lineup).write.mode("overwrite").format("delta").saveAsTable("raw_holo_lineup")

    total_cachet = sum(cachet_by_show.values())
    blueprint = spark.createDataFrame([
        ("Shows",                float(NUM_SHOWS)),
        ("Total Cachet",         float(total_cachet)),
        ("Avg Cachet per Show",  float(total_cachet / NUM_SHOWS)),
        ("Total Attendance",     float(show_attend)),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_holo_stage")
    print(f"  raw_holo_artists: {NUM_ARTISTS} | raw_holo_shows: {NUM_SHOWS} | lineup rows: {len(lineup):,}")
    """),

    # ----------------------- District 8 (BOSS Blueprint) -----------------------
    _md("## Step 8 — District 8: Grid Overlook (BOSS Blueprint)"),
    _code(r"""
    # Boss reuses raw data from D3 (Skylane) + D4 (Plasma) + D5 (Bazaar).
    # The Grid Stress Index is a normalized blend computed from already-clean facts.
    # We pre-compute the global value as the boss Blueprint; the Mayor will sample
    # multiple slices when validating perf + correctness.

    flights = spark.table("raw_skylane_traffic").dropna(subset=["pickup_sector"]).count()
    he3     = spark.table("raw_skylane_traffic").dropna(subset=["pickup_sector"]) \
                  .agg(F.sum("helium3_kg")).first()[0]
    avg_p   = spark.table("raw_plasma_readings").agg(F.avg("pressure_mpa")).first()[0]
    sales   = spark.table("raw_bazaar_sales").agg(F.sum("amount_credits")).first()[0]

    # Stress index = 0.4 * (avg_p / 5.0) + 0.3 * (he3 / 50000) + 0.3 * (sales / 1e7)
    stress = 0.4 * (avg_p / 5.0) + 0.3 * (he3 / 50000.0) + 0.3 * (sales / 1.0e7)

    blueprint = spark.createDataFrame([
        ("Total Flights (clean)",    float(flights)),
        ("Total Helium-3",            float(he3)),
        ("Avg Reactor Pressure",      float(avg_p)),
        ("Total Sales",               float(sales)),
        ("Grid Stress Index",         float(stress)),
    ], "MeasureName STRING, ExpectedValue DOUBLE")
    blueprint.write.mode("overwrite").format("delta").saveAsTable("blueprint_grid_overlook")
    print(f"  blueprint_grid_overlook: Grid Stress Index = {stress:.4f}")
    """),

    # ----------------------- Summary -----------------------
    _md("## ✅ Seed complete"),
    _code(r"""
    tables = [t.name for t in spark.catalog.listTables() if t.name.startswith(("raw_", "blueprint_"))]
    print(f"Datapolis_LH now has {len(tables)} seed tables:")
    for t in sorted(tables):
        n = spark.table(t).count()
        print(f"  - {t:<35} {n:>10,} rows")
    print("\n🏛️ Mayor: 'The tapes are restored. Open CityBuilder_Mayor and begin with District 1 — Town Hall.'")
    """),
]


# =====================================================================
# city_builder_mayor.ipynb  (PHASE 2 — vertical slice: District 1)
# =====================================================================

MAYOR_CELLS = [
    _md(f"""
    # 🏛️ City Builder — The Mayor's Office

    > Build stamp: **{BUILD_STAMP}** · *Phase 2 — District 1 ready*

    You are the newly elected **Mayor of Datapolis**. Your predecessor sabotaged the
    municipal Data Warehouse. Rebuild it district by district.

    ## How to play
    1. **Attach** `Datapolis_LH` as the default Lakehouse on this notebook.
    2. **Run cells 1–2** below to wake the Mayor up.
    3. Call `mayor.help()` to see the district roster.
    4. For each district:
       - `mayor.briefing("<district_id>")` → reads the case file (story + schema + DAX hints)
       - You go to **`Datapolis_DW`** and write T-SQL to build `Dim*` / `Fact*` tables
         using the `raw_*` data from the Lakehouse SQL endpoint (3-part name).
       - You create / refresh a Power BI **`Datapolis_Model`** on top of `Datapolis_DW`
         and add the requested DAX measures.
       - `mayor.inspect("<district_id>")` → schema audit (tables + columns + nullability)
       - `mayor.validate("<district_id>")` → DAX checks vs the blueprint, partial scoring,
         and emits an event to the `CityEvents` Eventhouse table.
    5. `mayor.score()` → cumulative reputation + current rank.

    ## Required model name
    The semantic model **must** be called `Datapolis_Model` (the Mayor only inspects that one).
    """),

    _md("## ⚙️ Step 0 — Player"),
    _code(r"""
    # --- EDIT THIS ---
    PLAYER_NAME = "Your Name Here"   # shown on your shareable badge at the end
    # -----------------
    print(f"Player: {PLAYER_NAME}")
    """),

    _md("## Step 1 — Setup"),
    _code(r"""
    # Identity, names, endpoints.
    import os, uuid, json, time, struct, math, datetime as dt, requests
    from typing import Any
    from IPython.display import display, Markdown

    WORKSPACE_ID  = mssparkutils.runtime.context.get("currentWorkspaceId") \
                    if "mssparkutils" in dir() else None
    try:
        import notebookutils
        WORKSPACE_ID = notebookutils.runtime.context.get("currentWorkspaceId") or WORKSPACE_ID
    except Exception:
        pass

    LH_NAME    = "Datapolis_LH"
    DW_NAME    = "Datapolis_DW"
    EH_NAME    = "Datapolis_EH"
    MODEL_NAME = "Datapolis_Model"
    EH_TABLE   = "CityEvents"

    SESSION_ID = str(uuid.uuid4())
    PLAYER_ID  = os.environ.get("USER", "mayor")

    print(f"Workspace:  {WORKSPACE_ID}")
    print(f"Session:    {SESSION_ID}")
    print(f"Player:     {PLAYER_ID}")
    """, hidden=True),

    _md("## Step 2 — Helpers (DW, DAX, Eventhouse)"),
    _code(r"""
    # --- Token helpers ------------------------------------------------
    def _token(resource: str) -> str:
        try:
            import notebookutils
            return notebookutils.credentials.getToken(resource)
        except Exception:
            import mssparkutils
            return mssparkutils.credentials.getToken(resource)

    def _fabric_get(url: str) -> dict:
        tok = _token("pbi")
        r = requests.get(url, headers={"Authorization": f"Bearer {tok}"}, timeout=60)
        r.raise_for_status()
        return r.json()

    # --- Warehouse (pyodbc + AAD access token) ------------------------
    _DW_CONN_STR = {"v": None}

    def _dw_endpoint() -> str:
        if _DW_CONN_STR["v"]:
            return _DW_CONN_STR["v"]
        items = _fabric_get(f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/items?type=Warehouse").get("value", [])
        target = next((i for i in items if i["displayName"] == DW_NAME), None)
        if not target:
            raise RuntimeError(f"Warehouse '{DW_NAME}' not found in workspace.")
        info = _fabric_get(f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/warehouses/{target['id']}")
        srv = info.get("properties", {}).get("connectionString")
        if not srv:
            raise RuntimeError(f"No connectionString for warehouse '{DW_NAME}'.")
        _DW_CONN_STR["v"] = srv
        return srv

    def dw_query(sql: str):
        '''Run T-SQL on Datapolis_DW. Returns list[dict].'''
        import pyodbc
        srv = _dw_endpoint()
        tok = _token("https://database.windows.net/.default").encode("utf-16-le")
        attrs = {1256: bytes(struct.pack("=i", len(tok)) + tok)}  # SQL_COPT_SS_ACCESS_TOKEN
        cs = f"Driver={{ODBC Driver 18 for SQL Server}};Server={srv};Database={DW_NAME};Encrypt=yes;TrustServerCertificate=no"
        with pyodbc.connect(cs, attrs_before=attrs, timeout=30) as cn:
            cur = cn.cursor(); cur.execute(sql)
            cols = [c[0] for c in cur.description] if cur.description else []
            return [dict(zip(cols, r)) for r in cur.fetchall()] if cols else []

    # --- DAX via sempy.fabric -----------------------------------------
    def dax_scalar(expr: str) -> float | None:
        '''EVALUATE ROW("V", <scalar expr>) on Datapolis_Model. Returns float or None.'''
        import sempy.fabric as fabric
        q = f'EVALUATE ROW("V", {expr})'
        try:
            df = fabric.evaluate_dax(dataset=MODEL_NAME, workspace=WORKSPACE_ID, dax_string=q)
            if df.empty: return None
            v = df.iloc[0, 0]
            return None if v is None else float(v)
        except Exception as e:
            print(f"  ⚠️ DAX error: {e}")
            return None

    def model_exists() -> bool:
        try:
            items = _fabric_get(f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/items?type=SemanticModel").get("value", [])
            return any(i["displayName"] == MODEL_NAME for i in items)
        except Exception:
            return False

    # --- Blueprint readers (from Lakehouse) ---------------------------
    def blueprint(district_id: str) -> dict[str, float]:
        '''Read blueprint_<id> table from default Lakehouse, return MeasureName -> ExpectedValue.'''
        tbl = "blueprint_" + district_id.replace("-", "_")
        rows = spark.table(tbl).collect()
        return {r["MeasureName"]: float(r["ExpectedValue"]) for r in rows}

    # --- Eventhouse telemetry -----------------------------------------
    _EH_QSI = {"v": None}
    def _eh_query_uri() -> str:
        if _EH_QSI["v"]: return _EH_QSI["v"]
        dbs = _fabric_get(f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/kqlDatabases").get("value", [])
        target = next((d for d in dbs if d["displayName"] == EH_NAME), None)
        if not target:
            raise RuntimeError(f"KQL DB '{EH_NAME}' not found.")
        info = _fabric_get(f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/kqlDatabases/{target['id']}")
        uri = info.get("properties", {}).get("queryServiceUri")
        if not uri:
            raise RuntimeError("No queryServiceUri for Datapolis_EH.")
        _EH_QSI["v"] = uri
        return uri

    def log_event(event_type: str, district_id: str, concept: str,
                  reputation: float, rows_validated: int,
                  measure_name: str = "", expected: float = 0.0,
                  actual: float = 0.0, validation_result: str = "INFO") -> None:
        ts = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        eid = str(uuid.uuid4())
        # Schema: EventId,Timestamp,SessionId,PlayerId,EventType,District,Concept,
        #         Reputation,RowsValidated,MeasureName,ExpectedValue,ActualValue,ValidationResult
        row = (f'"{eid}","{ts}","{SESSION_ID}","{PLAYER_ID}","{event_type}",'
               f'"{district_id}","{concept}",{reputation},{rows_validated},'
               f'"{measure_name}",{expected},{actual},"{validation_result}"')
        csl = f".ingest inline into table {EH_TABLE} <|\n{row}"
        try:
            tok = _token("kusto")
            requests.post(f"{_eh_query_uri()}/v1/rest/mgmt",
                          headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                          json={"db": EH_NAME, "csl": csl}, timeout=15)
        except Exception as e:
            print(f"  ⚠️ telemetry failed: {e}")

    def query_kql(kql: str):
        tok = _token("kusto")
        r = requests.post(f"{_eh_query_uri()}/v1/rest/query",
                          headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                          json={"db": EH_NAME, "csl": kql}, timeout=30)
        r.raise_for_status()
        tbl = r.json()["Tables"][0]
        cols = [c["ColumnName"] for c in tbl["Columns"]]
        return [dict(zip(cols, row)) for row in tbl["Rows"]]

    print("✅ Helpers loaded — dw_query, dax_scalar, blueprint, log_event, query_kql.")
    """),

    _md("## Step 3 — District spec (Town Hall fully briefed; others stubbed)"),
    _code(r"""
    # Each district has: concept, points, expected tables w/ columns+types,
    # DAX measure names + canonical formula hints + blueprint key mapping.
    DISTRICTS = {
        "town-hall": {
            "n": 1, "name": "🏛️ Town Hall — Phantom Census",
            "concept": "Fact vs Dimension, grain",
            "points": 100,
            "narrative": (
                "After the '99 archive fire, only ONE corrupted tape survived. "
                "It dumps citizen attributes and life events into a single table "
                "(`raw_phantom_census`, 7,500 rows). Some rows carry person info, "
                "others carry event info. Same `citizen_id`, different shape. "
                "Your job: split the tape into a **dimension** and a **fact**."
            ),
            "raw_tables": ["raw_phantom_census"],
            "expected_tables": {
                "DimCitizen": [
                    ("CitizenKey",   "INT",            False),  # surrogate (PK)
                    ("CitizenId",    "VARCHAR(20)",    False),  # business key
                    ("FullName",     "VARCHAR(100)",   True),
                    ("Profession",   "VARCHAR(50)",    True),
                    ("HomeDistrict", "VARCHAR(50)",    True),
                ],
                "FactCensusEvent": [
                    ("CitizenKey", "INT",       False),  # FK to DimCitizen
                    ("EventType",  "VARCHAR(20)", False),
                    ("EventDate",  "DATE",        False),
                ],
            },
            "measures": [
                # (measure_name, dax_hint, blueprint_key)
                ("Citizens",
                 "DISTINCTCOUNT(DimCitizen[CitizenKey])",
                 "Citizens"),
                ("Birth Events",
                 'CALCULATE(COUNTROWS(FactCensusEvent), FactCensusEvent[EventType]="Birth")',
                 "Birth Events"),
                ("Death Events",
                 'CALCULATE(COUNTROWS(FactCensusEvent), FactCensusEvent[EventType]="Death")',
                 "Death Events"),
                ("Net Population Change",
                 '[Birth Events] - [Death Events]',
                 "Net Population Change"),
            ],
            "starter_sql": '''-- ============================================================
-- District 1 — Town Hall: split the Phantom Census tape
-- ============================================================
-- The Lakehouse table `[Datapolis_LH].[dbo].[raw_phantom_census]`
-- mixes citizen attributes (row_type='ATTR') and life events
-- (row_type='EVENT') in the SAME rows. Split them in two tables.

-- 1) DIMENSION ------------------------------------------------
DROP TABLE IF EXISTS dbo.DimCitizen;

CREATE TABLE dbo.DimCitizen (
    CitizenKey    INT             NOT NULL,   -- surrogate (PK)
    CitizenId     VARCHAR(20)     NOT NULL,   -- business key (from raw)
    FullName      VARCHAR(100)    NULL,
    Profession    VARCHAR(50)     NULL,
    HomeDistrict  VARCHAR(50)     NULL
);

INSERT INTO dbo.DimCitizen (CitizenKey, CitizenId, FullName, Profession, HomeDistrict)
SELECT
    -- TODO: generate a surrogate key (hint: ROW_NUMBER() OVER (ORDER BY ...))
    NULL                                             AS CitizenKey,
    citizen_id,
    full_name,
    profession,
    home_district
FROM [Datapolis_LH].[dbo].[raw_phantom_census]
WHERE 1=0; -- TODO: keep only the ATTR rows

-- 2) FACT -----------------------------------------------------
DROP TABLE IF EXISTS dbo.FactCensusEvent;

CREATE TABLE dbo.FactCensusEvent (
    CitizenKey  INT          NOT NULL,   -- FK → DimCitizen.CitizenKey
    EventType   VARCHAR(20)  NOT NULL,
    EventDate   DATE         NOT NULL
);

INSERT INTO dbo.FactCensusEvent (CitizenKey, EventType, EventDate)
SELECT
    -- TODO: look up the surrogate key by joining DimCitizen on CitizenId
    NULL          AS CitizenKey,
    e.event_type,
    e.event_date
FROM [Datapolis_LH].[dbo].[raw_phantom_census] AS e
-- TODO: JOIN dbo.DimCitizen AS d ON ...
WHERE 1=0; -- TODO: keep only the EVENT rows

-- Sanity check (expected: 1500 / 6000)
SELECT COUNT(*) AS dim_rows  FROM dbo.DimCitizen;
SELECT COUNT(*) AS fact_rows FROM dbo.FactCensusEvent;
''',
        },
        # ============================================================
        # District 2 — Neon District (SCD Type 1)
        # ============================================================
        "neon-district": {
            "n": 2,
            "name": "🏘️ Neon District — Shifting Identities",
            "concept": "Surrogate keys + SCD Type 1 (overwrite)",
            "points": 100,
            "narrative": (
                "Citizens legally rename themselves after augmentation. The source overwrites "
                "names with **no history kept** — that is the definition of **SCD Type 1**. "
                "Merge `raw_neon_residents` with `raw_neon_residents_updates`, generate a "
                "surrogate key, and let the new values overwrite the old."
            ),
            "raw_tables": ["raw_neon_residents", "raw_neon_residents_updates"],
            "expected_tables": {
                "DimResident": [
                    ("ResidentKey",   "INT",          False),  # surrogate
                    ("CitizenId",     "VARCHAR(20)",  False),  # business key
                    ("FullName",      "VARCHAR(100)", True),
                    ("IsAugmented",   "BIT",          False),
                    ("District",      "VARCHAR(50)",  True),
                    ("Tier",          "VARCHAR(20)",  True),
                ],
            },
            "measures": [
                ("Residents",
                 "DISTINCTCOUNT(DimResident[ResidentKey])",
                 "Residents"),
                ("Augmented Residents",
                 "CALCULATE(COUNTROWS(DimResident), DimResident[IsAugmented]=TRUE())",
                 "Augmented Residents"),
                ("Gold Tier Residents",
                 'CALCULATE(COUNTROWS(DimResident), DimResident[Tier]="Gold")',
                 "Gold Tier Residents"),
            ],
            "starter_sql": '''-- ============================================================
-- District 2 — Neon District: SCD Type 1 merge
-- ============================================================
-- Source: residents file + later updates file (renames, tier upgrades).
-- Goal: ONE DimResident row per CitizenId, latest values win.

DROP TABLE IF EXISTS dbo.DimResident;

CREATE TABLE dbo.DimResident (
    ResidentKey  INT           NOT NULL,   -- surrogate (PK)
    CitizenId    VARCHAR(20)   NOT NULL,   -- business key
    FullName     VARCHAR(100)  NULL,
    IsAugmented  BIT           NOT NULL,
    District     VARCHAR(50)   NULL,
    Tier         VARCHAR(20)   NULL
);

-- Strategy hint (one of many): build a CTE that UNIONs original + updates,
-- then for each CitizenId keep the LATEST row using ROW_NUMBER().
INSERT INTO dbo.DimResident (ResidentKey, CitizenId, FullName, IsAugmented, District, Tier)
SELECT
    -- TODO: ROW_NUMBER() OVER (ORDER BY CitizenId) AS ResidentKey,
    NULL                                              AS ResidentKey,
    CitizenId,
    FullName,
    IsAugmented,
    District,
    Tier
FROM (
    -- TODO: UNION ALL the two raw tables (mark each with a priority column,
    --       e.g. 0=original, 1=update) then keep priority=MAX per CitizenId.
    SELECT TOP 0
        CAST(NULL AS VARCHAR(20))  AS CitizenId,
        CAST(NULL AS VARCHAR(100)) AS FullName,
        CAST(NULL AS BIT)          AS IsAugmented,
        CAST(NULL AS VARCHAR(50))  AS District,
        CAST(NULL AS VARCHAR(20))  AS Tier
) AS latest;

-- Sanity (expected: 600)
SELECT COUNT(*) AS residents FROM dbo.DimResident;
''',
        },

        # ============================================================
        # District 3 — Skylane (Additive fact + conformed dimensions)
        # ============================================================
        "skylane": {
            "n": 3,
            "name": "🚁 Skylane — Anti-Grav Couriers",
            "concept": "Additive fact + conformed dimensions",
            "points": 100,
            "narrative": (
                "Anti-grav couriers run cargo and medevac flights across the city sectors. "
                "Build a clean additive **FactFlight** plus two **conformed dimensions** "
                "(`DimDate`, `DimSector`) that you will reuse in later districts. "
                "Note: ~2% of source rows have NULL `pickup_sector` — drop them."
            ),
            "raw_tables": ["raw_skylane_traffic"],
            "expected_tables": {
                "DimDate": [
                    ("DateKey",   "INT",   False),   # yyyymmdd
                    ("FullDate",  "DATE",  False),
                    ("Year",      "INT",   False),
                    ("MonthNum",  "INT",   False),
                ],
                "DimSector": [
                    ("SectorKey",   "INT",          False),
                    ("SectorName",  "VARCHAR(50)",  False),
                ],
                "FactFlight": [
                    ("FlightId",         "VARCHAR(20)",  False),
                    ("DateKey",          "INT",          False),
                    ("PickupSectorKey",  "INT",          False),
                    ("DropSectorKey",    "INT",          False),
                    ("DurationMin",      "INT",          False),
                    ("DistanceKm",       "FLOAT",        False),
                    ("Helium3Kg",        "FLOAT",        False),
                ],
            },
            "measures": [
                ("Flights",
                 "COUNTROWS(FactFlight)",
                 "Flights"),
                ("Total Helium-3 Burned",
                 "SUM(FactFlight[Helium3Kg])",
                 "Total Helium-3 Burned"),
                ("Avg Flight Duration",
                 "AVERAGE(FactFlight[DurationMin])",
                 "Avg Flight Duration"),
            ],
            "starter_sql": '''-- ============================================================
-- District 3 — Skylane: additive fact + conformed dimensions
-- ============================================================

-- 1) DimDate (one row per distinct flight date, but you usually want a full calendar)
DROP TABLE IF EXISTS dbo.DimDate;
CREATE TABLE dbo.DimDate (
    DateKey  INT  NOT NULL,    -- yyyymmdd
    FullDate DATE NOT NULL,
    Year     INT  NOT NULL,
    MonthNum INT  NOT NULL
);
INSERT INTO dbo.DimDate (DateKey, FullDate, Year, MonthNum)
SELECT DISTINCT
    -- TODO: build YYYYMMDD as INT, e.g. YEAR(d)*10000 + MONTH(d)*100 + DAY(d)
    NULL                AS DateKey,
    flight_date         AS FullDate,
    YEAR(flight_date),
    MONTH(flight_date)
FROM [Datapolis_LH].[dbo].[raw_skylane_traffic]
WHERE flight_date IS NOT NULL;

-- 2) DimSector (DISTINCT of pickup_sector + drop_sector, NULLs excluded)
DROP TABLE IF EXISTS dbo.DimSector;
CREATE TABLE dbo.DimSector (
    SectorKey  INT          NOT NULL,
    SectorName VARCHAR(50)  NOT NULL
);
INSERT INTO dbo.DimSector (SectorKey, SectorName)
SELECT
    -- TODO: ROW_NUMBER() OVER (ORDER BY SectorName)
    NULL          AS SectorKey,
    SectorName
FROM (
    SELECT pickup_sector AS SectorName FROM [Datapolis_LH].[dbo].[raw_skylane_traffic] WHERE pickup_sector IS NOT NULL
    UNION
    SELECT drop_sector   AS SectorName FROM [Datapolis_LH].[dbo].[raw_skylane_traffic] WHERE drop_sector   IS NOT NULL
) s;

-- 3) FactFlight (drop the NULL-pickup rows; join twice to DimSector for the two keys)
DROP TABLE IF EXISTS dbo.FactFlight;
CREATE TABLE dbo.FactFlight (
    FlightId         VARCHAR(20)  NOT NULL,
    DateKey          INT          NOT NULL,
    PickupSectorKey  INT          NOT NULL,
    DropSectorKey    INT          NOT NULL,
    DurationMin      INT          NOT NULL,
    DistanceKm       FLOAT        NOT NULL,
    Helium3Kg        FLOAT        NOT NULL
);
INSERT INTO dbo.FactFlight (FlightId, DateKey, PickupSectorKey, DropSectorKey, DurationMin, DistanceKm, Helium3Kg)
SELECT
    f.flight_id,
    -- TODO: lookup DateKey from DimDate
    NULL  AS DateKey,
    -- TODO: lookup pickup SectorKey from DimSector
    NULL  AS PickupSectorKey,
    -- TODO: lookup drop SectorKey from DimSector
    NULL  AS DropSectorKey,
    f.duration_min, f.distance_km, f.helium3_kg
FROM [Datapolis_LH].[dbo].[raw_skylane_traffic] AS f
WHERE f.pickup_sector IS NOT NULL;   -- dirty-data filter
''',
        },

        # ============================================================
        # District 4 — Plasma Core (Semi-additive snapshot fact)
        # ============================================================
        "plasma-core": {
            "n": 4,
            "name": "⚡ Plasma Core — Reactor Readings",
            "concept": "Semi-additive fact (periodic snapshot)",
            "points": 100,
            "narrative": (
                "Hourly reactor snapshots over 3 years. Pressure / temperature / output are "
                "**semi-additive** — summing pressure across hours is meaningless. Average it "
                "instead. Critical Hours = count of snapshots where pressure > 5.0 MPa."
            ),
            "raw_tables": ["raw_plasma_readings"],
            "expected_tables": {
                "FactReactorReading": [
                    ("ReadingTs",     "DATETIME2",  False),
                    ("PressureMPa",   "FLOAT",      False),
                    ("TemperatureK",  "FLOAT",      False),
                    ("OutputMW",      "FLOAT",      False),
                ],
            },
            "measures": [
                ("Avg Pressure",
                 "AVERAGE(FactReactorReading[PressureMPa])",
                 "Avg Pressure"),
                ("Max Output MW",
                 "MAX(FactReactorReading[OutputMW])",
                 "Max Output MW"),
                ("Critical Hours",
                 "CALCULATE(COUNTROWS(FactReactorReading), FactReactorReading[PressureMPa] > 5.0)",
                 "Critical Hours"),
            ],
            "starter_sql": '''-- ============================================================
-- District 4 — Plasma Core: semi-additive snapshot fact
-- ============================================================
-- No dimension to build — the grain is one row per (reactor, hour) and we
-- only have one reactor. A timestamp + 3 measures is enough.

DROP TABLE IF EXISTS dbo.FactReactorReading;

CREATE TABLE dbo.FactReactorReading (
    ReadingTs    DATETIME2 NOT NULL,
    PressureMPa  FLOAT     NOT NULL,
    TemperatureK FLOAT     NOT NULL,
    OutputMW     FLOAT     NOT NULL
);

INSERT INTO dbo.FactReactorReading (ReadingTs, PressureMPa, TemperatureK, OutputMW)
SELECT
    reading_ts,
    pressure_mpa,
    temperature_k,
    output_mw
FROM [Datapolis_LH].[dbo].[raw_plasma_readings];

-- Sanity (expected ~26,280 rows = 3 * 365 * 24)
SELECT COUNT(*) AS hourly_rows FROM dbo.FactReactorReading;
''',
        },

        # ============================================================
        # District 5 — Bazaar 9 (Role-playing dimension)
        # ============================================================
        "bazaar-9": {
            "n": 5,
            "name": "🛒 Bazaar 9 — The Quantum Market",
            "concept": "Role-playing dimension + USERELATIONSHIP",
            "points": 100,
            "narrative": (
                "Each sale has TWO dates: `OrderDate` and `DeliveryDate` (sometimes earlier "
                "for pre-cog VIPs!). In the model you'll wire `FactSale` to `DimDate` **twice** "
                "— one active relationship (OrderDate) and one inactive — then use "
                "**USERELATIONSHIP** in DAX to switch contexts."
            ),
            "raw_tables": ["raw_bazaar_sales"],
            "expected_tables": {
                "FactSale": [
                    ("SaleId",        "VARCHAR(20)",  False),
                    ("OrderDateKey",  "INT",          False),
                    ("DeliveryDateKey", "INT",        False),
                    ("CustomerId",    "VARCHAR(20)",  False),
                    ("AmountCredits", "FLOAT",        False),
                    ("IsPreCog",      "BIT",          False),
                ],
            },
            "measures": [
                ("Sales by Order Date",
                 "SUM(FactSale[AmountCredits])",
                 "Sales by Order Date"),
                ("Sales by Delivery Date",
                 "CALCULATE(SUM(FactSale[AmountCredits]), "
                 "USERELATIONSHIP(FactSale[DeliveryDateKey], DimDate[DateKey]))",
                 "Sales by Delivery Date"),
                ("Pre-Cog Deliveries",
                 "CALCULATE(COUNTROWS(FactSale), FactSale[IsPreCog]=TRUE())",
                 "Pre-Cog Deliveries"),
            ],
            "starter_sql": '''-- ============================================================
-- District 5 — Bazaar 9: role-playing date dimension
-- ============================================================
-- Reuses DimDate from District 3. If you skipped District 3, extend
-- DimDate first so it covers every order_date AND delivery_date here.

DROP TABLE IF EXISTS dbo.FactSale;

CREATE TABLE dbo.FactSale (
    SaleId          VARCHAR(20)  NOT NULL,
    OrderDateKey    INT          NOT NULL,
    DeliveryDateKey INT          NOT NULL,
    CustomerId      VARCHAR(20)  NOT NULL,
    AmountCredits   FLOAT        NOT NULL,
    IsPreCog        BIT          NOT NULL
);

INSERT INTO dbo.FactSale (SaleId, OrderDateKey, DeliveryDateKey, CustomerId, AmountCredits, IsPreCog)
SELECT
    sale_id,
    -- TODO: build INT DateKey from order_date (YYYYMMDD)
    NULL  AS OrderDateKey,
    -- TODO: build INT DateKey from delivery_date
    NULL  AS DeliveryDateKey,
    customer_id,
    amount_credits,
    CAST(is_pre_cog AS BIT)
FROM [Datapolis_LH].[dbo].[raw_bazaar_sales];

-- In the semantic model:
--   * Create relationship FactSale[OrderDateKey]    -> DimDate[DateKey]  ACTIVE
--   * Create relationship FactSale[DeliveryDateKey] -> DimDate[DateKey]  INACTIVE
--   * Use USERELATIONSHIP(...) in the "Sales by Delivery Date" measure.
''',
        },

        # ============================================================
        # District 6 — Cryo Hospital (Junk + degenerate dimensions)
        # ============================================================
        "cryo-hospital": {
            "n": 6,
            "name": "🏥 Cryo Hospital — Admission Tags",
            "concept": "Junk dimension + degenerate dimension",
            "points": 100,
            "narrative": (
                "Four boolean flags (`is_emergency`, `has_insurance`, `is_augmented`, `is_vip`) "
                "would bloat the fact with low-cardinality columns. Collapse them into a "
                "**junk dimension** `DimAdmissionType` with 16 rows. `CryoTicketNumber` is a "
                "**degenerate dimension** — keep it on the fact, no separate table."
            ),
            "raw_tables": ["raw_cryo_admissions"],
            "expected_tables": {
                "DimAdmissionType": [
                    ("AdmissionTypeKey", "INT",  False),
                    ("IsEmergency",     "BIT",  False),
                    ("HasInsurance",    "BIT",  False),
                    ("IsAugmented",     "BIT",  False),
                    ("IsVip",           "BIT",  False),
                ],
                "FactCryoAdmission": [
                    ("CryoTicket",       "VARCHAR(20)", False),  # degenerate dim
                    ("AdmissionDateKey", "INT",         False),
                    ("AdmissionTypeKey", "INT",         False),
                    ("DurationDays",     "INT",         False),
                ],
            },
            "measures": [
                ("Admissions",
                 "COUNTROWS(FactCryoAdmission)",
                 "Admissions"),
                ("VIP Emergency Admissions",
                 "CALCULATE(COUNTROWS(FactCryoAdmission), "
                 "DimAdmissionType[IsVip]=TRUE(), DimAdmissionType[IsEmergency]=TRUE())",
                 "VIP Emergency Admissions"),
                ("Avg Cryo Duration",
                 "AVERAGE(FactCryoAdmission[DurationDays])",
                 "Avg Cryo Duration"),
            ],
            "starter_sql": '''-- ============================================================
-- District 6 — Cryo Hospital: junk + degenerate dims
-- ============================================================

-- 1) Junk dim: cross-join all 4 flags = 2^4 = 16 rows.
DROP TABLE IF EXISTS dbo.DimAdmissionType;
CREATE TABLE dbo.DimAdmissionType (
    AdmissionTypeKey INT NOT NULL,
    IsEmergency      BIT NOT NULL,
    HasInsurance     BIT NOT NULL,
    IsAugmented      BIT NOT NULL,
    IsVip            BIT NOT NULL
);
INSERT INTO dbo.DimAdmissionType (AdmissionTypeKey, IsEmergency, HasInsurance, IsAugmented, IsVip)
SELECT
    -- TODO: ROW_NUMBER() OVER (ORDER BY a.b, b.b, c.b, d.b) AS AdmissionTypeKey
    NULL AS AdmissionTypeKey,
    CAST(a.b AS BIT), CAST(b.b AS BIT), CAST(c.b AS BIT), CAST(d.b AS BIT)
FROM (VALUES (0),(1)) a(b)
CROSS JOIN (VALUES (0),(1)) b(b)
CROSS JOIN (VALUES (0),(1)) c(b)
CROSS JOIN (VALUES (0),(1)) d(b);

-- 2) Fact, with degenerate CryoTicket sitting right on the row.
DROP TABLE IF EXISTS dbo.FactCryoAdmission;
CREATE TABLE dbo.FactCryoAdmission (
    CryoTicket       VARCHAR(20) NOT NULL,
    AdmissionDateKey INT         NOT NULL,
    AdmissionTypeKey INT         NOT NULL,
    DurationDays     INT         NOT NULL
);
INSERT INTO dbo.FactCryoAdmission (CryoTicket, AdmissionDateKey, AdmissionTypeKey, DurationDays)
SELECT
    r.cryo_ticket,
    -- TODO: build INT date key from admission_date
    NULL AS AdmissionDateKey,
    -- TODO: lookup AdmissionTypeKey by joining DimAdmissionType on the 4 BIT columns
    NULL AS AdmissionTypeKey,
    r.duration_days
FROM [Datapolis_LH].[dbo].[raw_cryo_admissions] r;
''',
        },

        # ============================================================
        # District 7 — Holo-Stage (Many-to-many bridge)
        # ============================================================
        "holo-stage": {
            "n": 7,
            "name": "🎭 Holo-Stage — Multiverse Performers",
            "concept": "Many-to-many via bridge table",
            "points": 100,
            "narrative": (
                "Each show features 2–6 artists; each artist plays many shows. Build "
                "`DimArtist`, `DimShow`, `FactShow` (one row per show, additive) and a "
                "**BridgeShowArtist** that resolves the M:N. Beware of fan-out: COUNTROWS on "
                "the fact must NOT inflate when filtered by artist."
            ),
            "raw_tables": ["raw_holo_shows", "raw_holo_artists", "raw_holo_lineup"],
            "expected_tables": {
                "DimArtist": [
                    ("ArtistKey",  "INT",          False),
                    ("ArtistId",   "VARCHAR(10)",  False),
                    ("ArtistName", "VARCHAR(50)",  False),
                    ("Region",     "VARCHAR(20)",  True),
                    ("BaseCachet", "FLOAT",        True),
                ],
                "DimShow": [
                    ("ShowKey",  "INT",          False),
                    ("ShowId",   "VARCHAR(10)",  False),
                    ("ShowDate", "DATE",         False),
                    ("Genre",    "VARCHAR(30)",  True),
                ],
                "FactShow": [
                    ("ShowKey",        "INT",   False),
                    ("Attendance",     "INT",   False),
                    ("RevenueCredits", "FLOAT", False),
                ],
                "BridgeShowArtist": [
                    ("ShowKey",   "INT",   False),
                    ("ArtistKey", "INT",   False),
                    ("Cachet",    "FLOAT", False),
                ],
            },
            "measures": [
                ("Shows",
                 "DISTINCTCOUNT(DimShow[ShowKey])",
                 "Shows"),
                ("Total Cachet",
                 "SUM(BridgeShowArtist[Cachet])",
                 "Total Cachet"),
                ("Avg Cachet per Show",
                 "DIVIDE(SUM(BridgeShowArtist[Cachet]), DISTINCTCOUNT(DimShow[ShowKey]))",
                 "Avg Cachet per Show"),
                ("Total Attendance",
                 "SUM(FactShow[Attendance])",
                 "Total Attendance"),
            ],
            "starter_sql": '''-- ============================================================
-- District 7 — Holo-Stage: M:N with a bridge table
-- ============================================================

-- 1) Dimensions
DROP TABLE IF EXISTS dbo.DimArtist;
CREATE TABLE dbo.DimArtist (
    ArtistKey  INT          NOT NULL,
    ArtistId   VARCHAR(10)  NOT NULL,
    ArtistName VARCHAR(50)  NOT NULL,
    Region     VARCHAR(20)  NULL,
    BaseCachet FLOAT        NULL
);
INSERT INTO dbo.DimArtist (ArtistKey, ArtistId, ArtistName, Region, BaseCachet)
SELECT
    -- TODO: ROW_NUMBER() OVER (ORDER BY artist_id)
    NULL, artist_id, artist_name, region, base_cachet
FROM [Datapolis_LH].[dbo].[raw_holo_artists];

DROP TABLE IF EXISTS dbo.DimShow;
CREATE TABLE dbo.DimShow (
    ShowKey  INT          NOT NULL,
    ShowId   VARCHAR(10)  NOT NULL,
    ShowDate DATE         NOT NULL,
    Genre    VARCHAR(30)  NULL
);
INSERT INTO dbo.DimShow (ShowKey, ShowId, ShowDate, Genre)
SELECT
    -- TODO: ROW_NUMBER() OVER (ORDER BY show_id)
    NULL, show_id, show_date, genre
FROM [Datapolis_LH].[dbo].[raw_holo_shows];

-- 2) Fact at show grain (NOT inflated by artists)
DROP TABLE IF EXISTS dbo.FactShow;
CREATE TABLE dbo.FactShow (
    ShowKey        INT   NOT NULL,
    Attendance     INT   NOT NULL,
    RevenueCredits FLOAT NOT NULL
);
INSERT INTO dbo.FactShow (ShowKey, Attendance, RevenueCredits)
SELECT
    -- TODO: lookup ShowKey from DimShow by show_id
    NULL, attendance, revenue_credits
FROM [Datapolis_LH].[dbo].[raw_holo_shows];

-- 3) Bridge (one row per show-artist pairing) carries Cachet as a fact-like measure
DROP TABLE IF EXISTS dbo.BridgeShowArtist;
CREATE TABLE dbo.BridgeShowArtist (
    ShowKey   INT   NOT NULL,
    ArtistKey INT   NOT NULL,
    Cachet    FLOAT NOT NULL
);
INSERT INTO dbo.BridgeShowArtist (ShowKey, ArtistKey, Cachet)
SELECT
    -- TODO: lookup ShowKey from DimShow + ArtistKey from DimArtist
    NULL, NULL, l.cachet
FROM [Datapolis_LH].[dbo].[raw_holo_lineup] l;

-- In the semantic model:
--   DimShow   1 ---* BridgeShowArtist *--- 1 DimArtist     (bridge resolves M:N)
--   DimShow   1 ---* FactShow         (one-to-one on ShowKey)
''',
        },

        # ============================================================
        # District 8 — Grid Overlook (BOSS: galaxy schema + DAX perf)
        # ============================================================
        "grid-overlook": {
            "n": 8,
            "name": "🌃 The Grid Overlook — BOSS: The Anomaly",
            "concept": "Galaxy schema + DAX performance (Grid Stress Index < 2s)",
            "points": 200,
            "narrative": (
                "A gravitational anomaly is destabilizing The Grid. The director needs ONE "
                "dashboard blending **FactFlight + FactReactorReading + FactSale** through "
                "the conformed `DimDate` and `DimSector`. Build the **Grid Stress Index** as a "
                "single DAX measure that runs in under 2 seconds:\n\n"
                "`StressIndex = 0.4 * (AvgPressure / 5.0) + 0.3 * (TotalHe3 / 50000) + "
                "0.3 * (TotalSales / 1e7)`"
            ),
            "raw_tables": [],
            "expected_tables": {
                # Just verify the conformed dims and the three facts exist.
                "DimDate":            [("DateKey",   "INT",          False)],
                "DimSector":          [("SectorKey", "INT",          False)],
                "FactFlight":         [("FlightId",  "VARCHAR(20)",  False)],
                "FactReactorReading": [("ReadingTs", "DATETIME2",    False)],
                "FactSale":           [("SaleId",    "VARCHAR(20)",  False)],
            },
            "measures": [
                ("Total Flights (clean)",
                 "COUNTROWS(FactFlight)",
                 "Total Flights (clean)"),
                ("Total Helium-3",
                 "SUM(FactFlight[Helium3Kg])",
                 "Total Helium-3"),
                ("Avg Reactor Pressure",
                 "AVERAGE(FactReactorReading[PressureMPa])",
                 "Avg Reactor Pressure"),
                ("Total Sales",
                 "SUM(FactSale[AmountCredits])",
                 "Total Sales"),
                ("Grid Stress Index",
                 "0.4 * DIVIDE([Avg Reactor Pressure], 5.0) "
                 "+ 0.3 * DIVIDE([Total Helium-3], 50000) "
                 "+ 0.3 * DIVIDE([Total Sales], 10000000)",
                 "Grid Stress Index"),
            ],
            "starter_sql": '''-- ============================================================
-- District 8 — BOSS: nothing new to build in T-SQL!
-- ============================================================
-- The galaxy schema = Districts 3 + 4 + 5 already in Datapolis_DW:
--    DimDate, DimSector   (conformed dimensions)
--    FactFlight           (District 3)
--    FactReactorReading   (District 4)
--    FactSale             (District 5)
--
-- If any of those is missing, finish that district first. Then in the
-- Datapolis_Model semantic model:
--   1. Verify the conformed dims connect to ALL three facts.
--   2. Add the 5 measures listed above (Grid Stress Index references the others).
--   3. Aim for < 2s response time on a full-table evaluation.
''',
        },
    }

    RANKS = [
        (0,   "Suspicious Citizen"),
        (100, "Ward Councilor"),
        (250, "Urban Planning Officer"),
        (500, "Mayor of Datapolis"),
        (800, "Chief Grid Architect"),
        (900, "🏆 Grid Keeper"),
    ]
    def rank_for(total: float) -> str:
        r = RANKS[0][1]
        for thr, name in RANKS:
            if total >= thr: r = name
        return r

    print(f"🗂️  {len(DISTRICTS)} districts registered "
          f"({sum(1 for v in DISTRICTS.values() if not v.get('stub'))} fully briefed).")
    """, hidden=True),

    _md("## Step 4 — The `Mayor` class"),
    _code(r"""
    class Mayor:
        TOL_REL = 1e-4
        TOL_ABS = 1e-2
        PASS_THRESHOLD = 0.80  # >=80% measures correct = full points (else proportional)

        # ------------------------------------------------------------
        def help(self):
            md = ["### 🏛️ Mayor's roster\n",
                  "| # | District | Status | Concept |",
                  "|---|----------|--------|---------|"]
            for did, d in DISTRICTS.items():
                if d.get("stub"):
                    md.append(f"| – | {d['name']} | 🚧 *coming soon* | – |")
                else:
                    md.append(f"| {d['n']} | `{did}` — {d['name']} | ✅ ready | {d['concept']} |")
            md.append("\n**Commands:** `mayor.briefing(\"town-hall\")`, "
                      "`mayor.inspect(\"town-hall\")`, `mayor.validate(\"town-hall\")`, "
                      "`mayor.score()`")
            display(Markdown("\n".join(md)))

        # ------------------------------------------------------------
        def briefing(self, district_id: str):
            d = DISTRICTS.get(district_id)
            if not d:
                print(f"❓ unknown district '{district_id}'"); return
            if d.get("stub"):
                display(Markdown(f"### {d['name']}\n🚧 *Not yet briefed by the Mayor's office.*"))
                return
            bp = blueprint(district_id)
            md = [f"## {d['name']}",
                  f"**Concept:** {d['concept']}  ·  **Reward:** {d['points']} reputation",
                  "",
                  f"### 📜 Case file", d['narrative'], "",
                  f"### 📥 Source tables (in `{LH_NAME}` lakehouse)"]
            for t in d['raw_tables']:
                md.append(f"- `{t}`  →  reachable from `Datapolis_DW` as "
                          f"`[{LH_NAME}].[dbo].[{t}]` via cross-database query.")
            md += ["", "### 🏗️ Required tables in `Datapolis_DW`"]
            for tname, cols in d['expected_tables'].items():
                md.append(f"\n**`dbo.{tname}`**\n")
                md.append("| Column | Type | Nullable |")
                md.append("|--------|------|----------|")
                for c, ty, nul in cols:
                    md.append(f"| `{c}` | `{ty}` | {'YES' if nul else 'NO'} |")
            md += ["", "### � How to build it", "",
                   f"**1. Open the Warehouse.** In the workspace, open the **City Builder** folder and click on **`{DW_NAME}`**. "
                   "In the top toolbar choose **`+ New SQL query`** → a blank T-SQL editor opens.",
                   "",
                   f"**2. Cross-database read.** The raw data lives in the Lakehouse, but the Warehouse can query it "
                   f"with a **3-part name**: `[{LH_NAME}].[dbo].[<raw_table>]`.",
                   "",
                   "**3. Starter T-SQL.** Paste the skeleton below and fill the `-- TODO:` parts. Run it with **▶ Run**. "
                   "You can iterate: `DROP TABLE IF EXISTS` is already there so re-running is safe.",
                   ""]
            if d.get("starter_sql"):
                md.append("```sql")
                md.append(d["starter_sql"].rstrip())
                md.append("```")
                md.append("")
            md += ["### 📊 Build the semantic model + DAX measures", "",
                   f"**4. Create the model.** After the tables exist in `{DW_NAME}`, open the warehouse, go to the **Model** "
                   f"view (left side bar) → **`+ New semantic model`** → select your `Dim*` and `Fact*` tables → set "
                   f"**Name = `{MODEL_NAME}`** (the Mayor only validates that exact name). Confirm relationships are 1:* "
                   "from the dimension key to the fact key.",
                   "",
                   f"**5. Add the measures.** In the model, **`+ New measure`** and write each of the DAX expressions below. "
                   "The measure **names** must match exactly (the Mayor calls them by name). The *expressions* are hints — "
                   "any DAX that returns the expected value earns credit.",
                   "",
                   "| Measure name | DAX hint | Expected value |",
                   "|--------------|----------|---------------:|"]
            for mname, dax_hint, bp_key in d['measures']:
                exp = bp.get(bp_key, "?")
                exp_str = f"{exp:,.0f}" if isinstance(exp, (int, float)) else str(exp)
                md.append(f"| `{mname}` | `{dax_hint}` | `{exp_str}` |")
            md += ["",
                   "### ✅ When you are done",
                   f"Back in this notebook, run:",
                   "",
                   f"```python",
                   f'mayor.inspect("{district_id}")    # schema audit on Datapolis_DW',
                   f'mayor.validate("{district_id}")   # DAX vs blueprint → +reputation',
                   f"```",
                   "",
                   "> Get **≥80%** of the measures right to claim full reputation; otherwise partial credit."]
            display(Markdown("\n".join(md)))

        # ------------------------------------------------------------
        def inspect(self, district_id: str):
            d = DISTRICTS.get(district_id)
            if not d or d.get("stub"):
                print(f"❓ no inspection plan for '{district_id}'"); return
            print(f"🔎 Inspecting `{DW_NAME}` for District {d['n']} — {d['name']}\n")
            try:
                got = dw_query(
                    "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE "
                    "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo'"
                )
            except Exception as e:
                print(f"❌ cannot reach Datapolis_DW: {e}"); return

            present = {}
            for r in got:
                present.setdefault(r["TABLE_NAME"], {})[r["COLUMN_NAME"]] = (
                    r["DATA_TYPE"].lower(), r["IS_NULLABLE"]
                )

            ok = True
            for tname, cols in d['expected_tables'].items():
                if tname not in present:
                    print(f"  ❌ table `{tname}` MISSING"); ok = False; continue
                print(f"  ✅ table `{tname}` exists")
                for cname, ctype, nullable in cols:
                    p = present[tname].get(cname)
                    if not p:
                        print(f"      ❌ column `{cname}` missing"); ok = False; continue
                    base_type = ctype.split("(")[0].lower()
                    if base_type not in p[0]:
                        print(f"      ⚠️  column `{cname}` type is `{p[0]}`, expected `{ctype}`")
                    else:
                        print(f"      ✅ `{cname}` ({p[0]})")
            log_event("INSPECT", district_id, d['concept'], 0, len(got),
                      validation_result="OK" if ok else "FAIL")
            print("\n🏛️ Schema inspection complete.")

        # ------------------------------------------------------------
        def validate(self, district_id: str):
            d = DISTRICTS.get(district_id)
            if not d or d.get("stub"):
                print(f"❓ no validation plan for '{district_id}'"); return
            if not model_exists():
                print(f"❌ Semantic model `{MODEL_NAME}` not found in this workspace.\n"
                      f"   Create it (Power BI Desktop or web) on top of `{DW_NAME}` and try again.")
                return
            bp = blueprint(district_id)
            print(f"📊 Validating District {d['n']} — {d['name']}\n")
            passed = 0
            total  = len(d['measures'])
            for mname, dax_hint, bp_key in d['measures']:
                expected = bp.get(bp_key)
                actual   = dax_scalar(f"[{mname}]")
                if actual is None:
                    print(f"  ❌ `{mname}` — not found in model or DAX error")
                    log_event("VALIDATE", district_id, d['concept'], 0, 0,
                              mname, expected or 0, 0, "MISSING")
                    continue
                ok = math.isclose(actual, expected, rel_tol=self.TOL_REL, abs_tol=self.TOL_ABS)
                tick = "✅" if ok else "❌"
                print(f"  {tick} `{mname}`  expected={expected:,.4f}  actual={actual:,.4f}")
                log_event("VALIDATE", district_id, d['concept'], 0, 0,
                          mname, expected, actual, "PASS" if ok else "FAIL")
                if ok: passed += 1

            ratio = passed / total if total else 0
            if ratio >= self.PASS_THRESHOLD:
                pts = d['points']
                verdict = f"🏅 FULL CREDIT  ·  +{pts} reputation"
            else:
                pts = round(d['points'] * ratio)
                verdict = f"📉 PARTIAL CREDIT  ·  +{pts} reputation ({passed}/{total} measures)"
            print(f"\n{verdict}")
            log_event("SCORE", district_id, d['concept'], pts, 0,
                      validation_result="PASS" if ratio >= self.PASS_THRESHOLD else "PARTIAL")
            return pts

        # ------------------------------------------------------------
        def score(self):
            try:
                rows = query_kql(
                    f"{EH_TABLE} | where SessionId == '{SESSION_ID}' and EventType == 'SCORE' "
                    f"| summarize Reputation = sum(Reputation) by District "
                    f"| order by District asc"
                )
            except Exception as e:
                print(f"❌ cannot query Eventhouse: {e}"); return
            total = sum(r["Reputation"] for r in rows)
            md = ["### 🏛️ Mayor's scoreboard (this session)",
                  "| District | Reputation |",
                  "|----------|-----------:|"]
            for r in rows:
                md.append(f"| `{r['District']}` | {int(r['Reputation'])} |")
            md.append(f"| **Total** | **{int(total)}** |")
            md.append(f"\n**Rank:** {rank_for(total)}")
            md.append(f"\n> Run the next cell (**Step 6**) to mint your shareable badge.")
            display(Markdown("\n".join(md)))
            # Export for the badge-issuance cell (same pattern as retro-arcade)
            globals()["FINAL_SCORE"] = int(total)
            globals()["FINAL_RANK"]  = rank_for(total)
            return total

    mayor = Mayor()
    log_event("SESSION_START", "datapolis", "init", 0, 0, validation_result="OK")
    print("🏛️ The Mayor is in office. Try: mayor.help()")
    """),

    _md("## Step 5 — Play"),
    _code(r"""
    mayor.help()
    """),
    _code(r"""
    # mayor.briefing("town-hall")
    """),
    _code(r"""
    # mayor.inspect("town-hall")
    """),
    _code(r"""
    # mayor.validate("town-hall")
    """),
    _code(r"""
    # mayor.score()
    """),

    _md("## Step 6 — Run all districts & compute final score\n\n"
        "Once you've added the T-SQL tables in `Datapolis_DW` and the DAX measures in\n"
        "`Datapolis_Model` for every district, run this cell to inspect + validate them\n"
        "all in one go and get your cumulative reputation."),
    _code(r"""
    for d in ["town-hall","neon-district","skylane","plasma-core",
              "bazaar-9","cryo-hospital","holo-stage","grid-overlook"]:
        mayor.inspect(d)
        mayor.validate(d)
    mayor.score()
    """),

    _md("## Step 7 — 🏅 Mint your shareable badge"),
    _code(r"""
    # ============================================================
    # City Builder — Badge issuance
    # HMAC-signed URL for the GitHub Pages badge viewer
    # ============================================================
    import json, time, hmac, hashlib, base64
    from IPython.display import display, Markdown, HTML

    _BADGE_SECRET = b"fabric-arcade-badge-v1-7K9mP3xQ"
    _BASE_URL     = "https://maenglar78.github.io/fabric-arcade"
    _GAME_ID      = "city-builder"
    _SKILLS       = ["Data Warehouse", "T-SQL", "Power BI", "DAX", "Star Schema"]

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
    rank  = globals().get("FINAL_RANK", "Suspicious Citizen")

    if score < 100:
        display(Markdown(
            f"### 🚧 Not yet eligible (score {score}/900)\n\n"
            f"Reach **at least 100 reputation** to earn the Ward Councilor badge. "
            f"Run `mayor.validate(\"<district-id>\")` on any district you skipped, "
            f"then re-run `mayor.score()` and this cell."
        ))
    elif PLAYER_NAME.strip() in ("", "Your Name Here"):
        display(Markdown(
            "### ✍️ Set your name first\n\n"
            "Edit `PLAYER_NAME` in **Step 0** and re-run `mayor.score()` + this cell."
        ))
    else:
        url = _issue(_GAME_ID, PLAYER_NAME, rank, score)
        display(Markdown(
            f"### 🏅 Badge minted\n\n"
            f"**{PLAYER_NAME}** — *{rank}* · reputation **{score}/900**\n\n"
            f"🔗 **[Open your badge]({url})**\n\n"
            f"Click *Download PNG* / *Share on LinkedIn* on the badge page."
        ))
        display(HTML(f'<a href="{url}" target="_blank" '
                     f'style="display:inline-block;padding:10px 20px;border-radius:8px;'
                     f'background:linear-gradient(135deg,#00d4ff,#8338ec);color:white;'
                     f'text-decoration:none;font-weight:600">🏅 Open my badge page</a>'))
        log_event("BADGE", "grid-overlook", rank, int(score), 0,
                  measure_name=url, validation_result="ISSUED")
    """),
]



# =====================================================================
# city_builder_dashboard.ipynb  (PHASE 3 stub)
# =====================================================================

DASH_CELLS = [
    _md(f"""
    # 🏙️ City Builder — Datapolis Dashboard

    > Build stamp: **{BUILD_STAMP}** · *Phase 3 implementation in progress*

    Will read the `CityEvents` KQL table from `Datapolis_EH` and render:
    - **City map** of Datapolis (Plotly): districts light up as built / fail red
    - **Mayor reputation** gauge
    - **DAX scoreboard** (measure-by-measure expected vs actual)
    - **Rank progression**: Suspicious Citizen → Grid Keeper
    """),
    _code(r"""
    print("🚧 Phase 3 — implementation coming after the Mayor is finished.")
    """),
]


if __name__ == "__main__":
    p1 = write_nb("city_builder_seed",       SEED_CELLS)
    p2 = write_nb("city_builder_mayor",      MAYOR_CELLS)
    p3 = write_nb("city_builder_dashboard",  DASH_CELLS)
    print(f"📓 Wrote {p1}")
    print(f"📓 Wrote {p2}")
    print(f"📓 Wrote {p3}")
