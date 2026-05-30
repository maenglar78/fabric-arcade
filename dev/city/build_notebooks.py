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
# city_builder_mayor.ipynb  (PHASE 2 stub)
# =====================================================================

MAYOR_CELLS = [
    _md(f"""
    # 🏛️ City Builder — The Mayor's Office

    > Build stamp: **{BUILD_STAMP}** · *Phase 2 implementation in progress*

    This notebook will hold:
    - District briefings (markdown — what to build in `Datapolis_DW` + DAX expected)
    - The `Mayor` class: `mayor.briefing("town-hall")`, `mayor.inspect_district("town-hall")`
    - INFORMATION_SCHEMA validators on `Datapolis_DW`
    - DAX validators via XMLA against `Datapolis_Model` (player creates)
    - Telemetry emitter to `CityEvents` in `Datapolis_EH`

    Run `CityBuilder_Seed` first to populate `Datapolis_LH` with raw + Blueprint data.
    """),
    _code(r"""
    # 🚧 Phase 2 — implementation coming next iteration.
    # For now: verify the seed worked by listing Blueprint tables in your default Lakehouse.
    blueprint_tables = [t.name for t in spark.catalog.listTables() if t.name.startswith("blueprint_")]
    print(f"Blueprint tables ready: {len(blueprint_tables)}")
    for t in sorted(blueprint_tables):
        spark.table(t).show(truncate=False)
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
