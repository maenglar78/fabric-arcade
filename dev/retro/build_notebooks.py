"""
Build the 3 Retro Arcade notebooks (.ipynb) from inline content and write
them into the catalog folder (no Fabric upload — installation happens via
the fabric_arcade installer like every other game).

Run:
    python dev/retro/build_notebooks.py
"""
from __future__ import annotations
import json
from pathlib import Path
from textwrap import dedent
import datetime as _dt

ROOT = Path(__file__).resolve().parents[2]
CATALOG_NB = ROOT / "catalog" / "retro-arcade" / "notebooks"
CATALOG_NB.mkdir(parents=True, exist_ok=True)

BUILD_STAMP = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Build stamp: {BUILD_STAMP}")


FABRIC_NB_METADATA = {
    "kernelspec": {
        "display_name": "Synapse PySpark",
        "language": "python",
        "name": "synapse_pyspark",
    },
    "language_info": {"name": "python"},
    "microsoft": {
        "language": "python",
        "language_group": "synapse_pyspark",
        "ms_spell_check": {"ms_spell_check_language": "en"},
    },
    "nteract": {"version": "nteract-front-end@1.0.0"},
    "spark_compute": {
        "compute_id": "/trident/default",
        "session_options": {"conf": {}},
    },
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
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": FABRIC_NB_METADATA,
        "cells": cells,
    }


def write_nb(name: str, cells: list[dict]) -> Path:
    p = CATALOG_NB / f"{name}.ipynb"
    p.write_text(json.dumps(_nb(cells), indent=1), encoding="utf-8")
    return p


# =====================================================================
# 01_Setup — Arcade Hall seed + Direct Lake semantic model
# =====================================================================

SETUP_CELLS = [
    _md(f"""
    # 🕹️ Retro Arcade — Setup

    > Build stamp: **{BUILD_STAMP}**

    Run this notebook **ONCE** to bootstrap the game. It populates the
    `Arcade_LH` Lakehouse with synthetic 80s-arcade tables (Scores, Games,
    Players, Cabinets, Date) and builds the `ArcadeHall_Model` Direct Lake
    semantic model that you will use to build your report.

    ## Requirements
    1. Attach **`Arcade_LH`** as the default Lakehouse (📚 icon → *Add* → Existing Lakehouse).
    2. Run all cells top → bottom.

    Total runtime: ~1–2 minutes.
    """),

    _code(r"""
    # === Setup ===
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade",
                    "--disable-pip-version-check", "PyJWT>=2.6.0"],
                   check=False, capture_output=True)

    import random, datetime as dt
    from pyspark.sql import functions as F, types as T

    SEED_VERSION = "v1"
    RNG_SEED = 1980
    YEARS    = [2023, 2024, 2025]
    random.seed(RNG_SEED)

    for t in ["date", "games", "players", "cabinets", "scores",
              "Date", "Games", "Players", "Cabinets", "Scores"]:
        try: spark.sql(f"DROP TABLE IF EXISTS {t}")
        except Exception: pass
    print("🧹 Clean slate.")
    """),

    _md("## Step 1 — Date dimension (3 years)"),
    _code(r"""
    start = dt.date(YEARS[0], 1, 1); end = dt.date(YEARS[-1], 12, 31)
    days  = (end - start).days + 1
    rows = []
    for i in range(days):
        d = start + dt.timedelta(days=i)
        rows.append((int(d.strftime("%Y%m%d")), d, d.year,
                     (d.month - 1) // 3 + 1, d.month, d.strftime("%B"),
                     d.day, d.strftime("%A"), d.isoweekday() in (6, 7)))
    schema = T.StructType([
        T.StructField("DateKey", T.IntegerType(), False),
        T.StructField("Date", T.DateType(), False),
        T.StructField("Year", T.IntegerType(), False),
        T.StructField("Quarter", T.IntegerType(), False),
        T.StructField("MonthNum", T.IntegerType(), False),
        T.StructField("MonthName", T.StringType(), False),
        T.StructField("DayOfMonth", T.IntegerType(), False),
        T.StructField("DayName", T.StringType(), False),
        T.StructField("IsWeekend", T.BooleanType(), False),
    ])
    date_df = spark.createDataFrame(rows, schema)
    (date_df.write.format("delta").mode("overwrite")
            .option("overwriteSchema", "true").saveAsTable("date"))
    print(f"✅ date rows={date_df.count():,}")
    """),

    _md("## Step 2 — Games dimension (12 arcade classics)"),
    _code(r"""
    GAMES = [
        (1,  "Pac-Man",        "Maze",     1980, "Namco"),
        (2,  "Donkey Kong",    "Platform", 1981, "Nintendo"),
        (3,  "Galaga",         "Shooter",  1981, "Namco"),
        (4,  "Frogger",        "Action",   1981, "Konami"),
        (5,  "Centipede",      "Shooter",  1981, "Atari"),
        (6,  "Asteroids",      "Shooter",  1979, "Atari"),
        (7,  "Q*bert",         "Puzzle",   1982, "Gottlieb"),
        (8,  "Defender",       "Shooter",  1981, "Williams"),
        (9,  "Dig Dug",        "Maze",     1982, "Namco"),
        (10, "Tempest",        "Shooter",  1981, "Atari"),
        (11, "Street Fighter II","Fighting",1991,"Capcom"),
        (12, "Tetris",         "Puzzle",   1984, "Atari Games"),
    ]
    games_df = spark.createDataFrame(GAMES,
        ["GameKey", "GameName", "Genre", "ReleaseYear", "Manufacturer"])
    (games_df.write.format("delta").mode("overwrite")
            .option("overwriteSchema", "true").saveAsTable("games"))
    print(f"✅ games rows={games_df.count():,}")
    """),

    _md("## Step 3 — Players dimension (40 handles)"),
    _code(r"""
    HANDLES = ["BLAZE","NEON","PIXEL","ROXY","ZARA","KIRO","MAXX","NOVA","JINX","RIPP",
               "VEGA","ECHO","FROST","HEX","ATOM","DUKE","SCAR","WOLF","BOLT","ASH",
               "ZERO","RAVN","FURY","NYX","TANK","KOBR","FLUX","JADE","ORC","KAI",
               "BANE","GHST","VYX","RUNE","ZED","PYRO","FAUN","ION","KARM","BYTE"]
    COUNTRIES = ["US","JP","IT","FR","DE","UK","ES","BR","CA","KR"]
    rng = random.Random(RNG_SEED + 1)
    rows = [(i+1, h, rng.choice(COUNTRIES), rng.randint(1979, 1995))
            for i, h in enumerate(HANDLES)]
    players_df = spark.createDataFrame(rows,
        ["PlayerKey", "Handle", "Country", "JoinYear"])
    (players_df.write.format("delta").mode("overwrite")
            .option("overwriteSchema", "true").saveAsTable("players"))
    print(f"✅ players rows={players_df.count():,}")
    """),

    _md("## Step 4 — Cabinets dimension (8 arcade locations)"),
    _code(r"""
    CABINETS = [
        (1, "Times Square Hall",  "Upright"),
        (2, "Tokyo Akihabara",    "Upright"),
        (3, "Milano Galleria",    "Cocktail"),
        (4, "Paris Pigalle",      "Upright"),
        (5, "London Soho",        "Cocktail"),
        (6, "Berlin Friedrich",   "Upright"),
        (7, "LA Venice Beach",    "Cabaret"),
        (8, "Madrid Gran Via",    "Upright"),
    ]
    cab_df = spark.createDataFrame(CABINETS, ["CabinetKey","Location","CabinetType"])
    (cab_df.write.format("delta").mode("overwrite")
            .option("overwriteSchema", "true").saveAsTable("cabinets"))
    print(f"✅ cabinets rows={cab_df.count():,}")
    """),

    _md("## Step 5 — Scores fact (~80k rows, with seasonality & player skill)"),
    _code(r"""
    date_pool = [(int(d.strftime('%Y%m%d')), d) for d in
                 (dt.date(YEARS[0], 1, 1) + dt.timedelta(days=i) for i in range(days))]
    rng = random.Random(RNG_SEED + 2)

    # Player skill 0.5..2.5 multiplier
    skill = {pk: rng.uniform(0.5, 2.5) for pk in range(1, len(HANDLES)+1)}
    # Game base score
    base  = {gk: rng.randint(2_000, 15_000) for gk in range(1, len(GAMES)+1)}
    # Weekend bonus
    def factor(d, pk, gk):
        f = 1.0
        if d.isoweekday() in (6,7): f *= 1.25
        if d.month in (7,8,12):     f *= 1.15  # summer & xmas peak
        return f * skill[pk]

    N_SCORES = 80_000
    rows = []
    for sk in range(1, N_SCORES + 1):
        dk, d  = rng.choice(date_pool)
        pk     = rng.randint(1, len(HANDLES))
        gk     = rng.randint(1, len(GAMES))
        cabk   = rng.randint(1, len(CABINETS))
        score  = int(base[gk] * rng.uniform(0.4, 1.6) * factor(d, pk, gk))
        dur    = rng.randint(30, 1800)              # seconds
        cred   = rng.randint(1, 5)
        onecc  = (cred == 1 and rng.random() < 0.05)  # 5% of single-credit runs are 1cc
        rows.append((sk, dk, pk, gk, cabk, score, dur, cred, onecc))

    schema = T.StructType([
        T.StructField("ScoreKey", T.IntegerType(), False),
        T.StructField("DateKey",  T.IntegerType(), False),
        T.StructField("PlayerKey",T.IntegerType(), False),
        T.StructField("GameKey",  T.IntegerType(), False),
        T.StructField("CabinetKey",T.IntegerType(),False),
        T.StructField("Score",    T.IntegerType(), False),
        T.StructField("DurationSeconds", T.IntegerType(), False),
        T.StructField("Credits",  T.IntegerType(), False),
        T.StructField("OneCC",    T.BooleanType(), False),
    ])
    scores_df = spark.createDataFrame(rows, schema)
    (scores_df.write.format("delta").mode("overwrite")
              .option("overwriteSchema", "true").saveAsTable("scores"))
    print(f"✅ scores rows={scores_df.count():,}")
    """),

    _md("## Step 6 — Summary"),
    _code(r"""
    for t in ["date","games","players","cabinets","scores"]:
        n = spark.table(t).count()
        print(f"  {t:<10} {n:>10,} rows")
    print("\n🕹️  Lakehouse Arcade_LH is ready.")
    """),

    _md(r"""
    ## Step 7 — Build the `ArcadeHall_Model` Direct Lake semantic model

    Creates the semantic model with relationships and 6 base measures so you can
    immediately start building visuals in your report.
    """),

    _code(r"""
    import subprocess, sys, importlib
    try:
        import sempy_labs as labs
        from sempy_labs import directlake as labs_dl
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "semantic-link-labs"],
                       check=True)
        importlib.invalidate_caches()
        import sempy_labs as labs
        from sempy_labs import directlake as labs_dl
    print(f"sempy-labs version: {getattr(labs, '__version__', '?')}")

    import sempy.fabric as fabric

    MODEL_NAME = "ArcadeHall_Model"
    LAKEHOUSE  = "Arcade_LH"
    TABLES = {
        "Date":     "date",
        "Games":    "games",
        "Players":  "players",
        "Cabinets": "cabinets",
        "Scores":   "scores",
    }

    try:
        df = fabric.list_datasets()
        name_col = next((c for c in df.columns
                         if c.lower() in ("dataset name","name","display name")), None)
        already = (df[name_col] == MODEL_NAME).any() if name_col else False
    except Exception as e:
        print(f"(could not list datasets: {e}); will try to create.")
        already = False

    if already:
        print(f"✅ Semantic model '{MODEL_NAME}' already exists — refreshing.")
        try:
            fabric.refresh_dataset(dataset=MODEL_NAME, refresh_type="full")
            print("✅ Refresh OK.")
        except Exception as e:
            print(f"⚠️  Refresh failed: {e}")
    else:
        print(f"🛠️  Creating Direct Lake model '{MODEL_NAME}'...")
        labs_dl.generate_direct_lake_semantic_model(
            dataset=MODEL_NAME,
            lakehouse=LAKEHOUSE,
            lakehouse_tables=list(TABLES.values()),
        )
        print("✅ Model created.")
    """),

    _md("## Step 8 — Add relationships and base measures"),
    _code(r"""
    from sempy_labs.tom import connect_semantic_model

    with connect_semantic_model(dataset=MODEL_NAME, readonly=False) as tom:
        # --- Rename physical tables to PascalCase ---
        wanted = {"date":"Date","games":"Games","players":"Players",
                  "cabinets":"Cabinets","scores":"Scores"}
        for t in list(tom.model.Tables):
            if t.Name in wanted and t.Name != wanted[t.Name]:
                t.Name = wanted[t.Name]

        # --- Mark Date table ---
        try:
            tom.mark_as_date_table(table_name="Date", column_name="Date")
        except Exception as e:
            print(f"(mark_as_date_table skipped: {e})")

        # --- Relationships (delete pre-existing autos, then create explicit) ---
        for r in list(tom.model.Relationships):
            tom.model.Relationships.Remove(r)

        rels = [
            ("Scores","DateKey","Date","DateKey"),
            ("Scores","GameKey","Games","GameKey"),
            ("Scores","PlayerKey","Players","PlayerKey"),
            ("Scores","CabinetKey","Cabinets","CabinetKey"),
        ]
        for ft, fk, dt, dk in rels:
            try:
                tom.add_relationship(
                    from_table=ft, from_column=fk,
                    to_table=dt,    to_column=dk,
                    from_cardinality="Many", to_cardinality="One",
                )
            except Exception as e:
                print(f"(relationship {ft}->{dt} skipped: {e})")

        # --- Base measures on Scores ---
        measures = [
            ("Total Score",       "SUM(Scores[Score])",               "#,0"),
            ("Total Plays",       "COUNTROWS(Scores)",                "#,0"),
            ("Total Credits",     "SUM(Scores[Credits])",             "#,0"),
            ("Active Players",    "DISTINCTCOUNT(Scores[PlayerKey])", "0"),
            ("Cabinets Used",     "DISTINCTCOUNT(Scores[CabinetKey])","0"),
            ("Avg Score",         "AVERAGE(Scores[Score])",           "#,0"),
            ("1cc Achievements",  "CALCULATE(COUNTROWS(Scores), Scores[OneCC] = TRUE)", "#,0"),
        ]
        existing = {m.Name for m in tom.all_measures()}
        for name, expr, fmt in measures:
            if name in existing: continue
            tom.add_measure(table_name="Scores", measure_name=name,
                            expression=expr, format_string=fmt,
                            description="Base measure provided by setup.")
        print("✅ Relationships + measures applied.")
    """),

    _md(r"""
    ## ✅ Done

    `ArcadeHall_Model` is live. Next:
    1. Open **`02_Quest`** for the 5-level brief.
    2. In the workspace, **+ New → Power BI report → Pick a published semantic model →
       `ArcadeHall_Model`** and name the report **`Arcade_Hall_Report`**.
    3. Build the report following the 5 levels.
    4. When done, open **`03_Check`** to validate and mint your badge.
    """),
]


# =====================================================================
# 02_Quest — 5 levels brief
# =====================================================================

QUEST_CELLS = [
    _md(f"""
    # 🕹️ Retro Arcade — The Quest

    > Build stamp: **{BUILD_STAMP}**

    You inherit the keys to the **Arcade Hall**: a semantic model packed with
    decades of high-scores from 12 arcade classics, played by 40 handles across
    8 cabinets. Your mission: build a **report worthy of the kill screen**.

    Five levels, twenty points each. **Insert the coin and press START.**

    ---
    ## How to play
    1. In the workspace, click **+ New → Power BI report**.
    2. Choose **Pick a published semantic model** → `ArcadeHall_Model`.
    3. Save the report as **`Arcade_Hall_Report`** (exact name — the checker looks for it).
    4. Build the report following the 5 levels below.
    5. Open **`03_Check`** to validate and mint your signed badge.

    💡 *You can save & re-open many times. Each level is graded independently.*

    ---
    """),

    _md(r"""
    ## 🟢 Level 1 — Foundation · *The First Cabinet*

    Lay the groundwork. A report nobody can navigate is a report nobody reads.

    **Requirements**
    - At least **3 pages**
    - Each page has a meaningful **page title** (not "Page 1")
    - Each page has a **page background** color or image (not default white)

    **Suggested pages**
    - `Hall Overview` — high-level KPIs
    - `Player Spotlight` — drill into a single player
    - `Game Library` — game-level analysis

    **Score:** 20 pts (5 base + 5 per requirement met)
    """),

    _md(r"""
    ## 🟡 Level 2 — Visuals · *Pixel Perfect*

    A real arcade dashboard speaks in many shapes. Show off your variety.

    **Requirements**
    - Use **at least 5 different visual types** across the report
    - Mandatory: at least 1 **Card** and at least 1 **Slicer**
    - Recommended mix: Card, Bar, Line, Matrix, Map / Treemap / Donut

    **Score:** 20 pts (4 pts per unique visual type, capped at 20)
    """),

    _md(r"""
    ## 🟠 Level 3 — Interactivity · *Combo Move*

    Players should *play* with the data, not stare at it.

    **Requirements**
    - At least **2 Slicer visuals** (e.g., Game, Player, Year)
    - At least **1 sync slicer** shared across multiple pages
    - Configure at least **1 edit-interaction** override (you'll naturally hit this)

    **Score:** 20 pts (7 + 7 + 6)
    """),

    _md(r"""
    ## 🟣 Level 4 — Storytelling · *Bonus Stage*

    Bookmarks, tooltips, drill-throughs — the bonus stages of report design.

    **Requirements**
    - At least **1 Bookmark**
    - At least **1 Tooltip page** (set its page type to *Tooltip*)
    - At least **1 Drill-through page** (with a drill-through filter on a column)

    **Score:** 20 pts (7 + 7 + 6)
    """),

    _md(r"""
    ## 🔵 Level 5 — Polish · *High Score*

    Spit & polish. This is what separates a report from a *trophy*.

    **Requirements**
    - Apply a **custom theme** (not the default *Classic* / *City Park*)
    - Add **conditional formatting** on at least **1 visual** (data bars, color scales, or icons)
    - Provide a **Mobile layout** for at least **1 page**

    **Score:** 20 pts (7 + 7 + 6)

    ---

    ## 🏅 Ranks

    | Score | Rank |
    | -----:| ---- |
    |   20+ | 🥉 Newbie |
    |   40+ | 🪙 Quarter Muncher |
    |   60+ | 🎯 High Roller |
    |   80+ | 👾 Arcade Legend |
    |  100  | 🏆 Kill Screen Survivor |

    Run **`03_Check`** any time to see your live score. You don't have to finish
    all levels in one sitting.
    """),
]


# =====================================================================
# 03_Check — Validate report via sempy + mint badge
# =====================================================================

CHECK_CELLS = [
    _md(f"""
    # 🕹️ Retro Arcade — Check & Score

    > Build stamp: **{BUILD_STAMP}**

    Reads the **PBIR definition** of your report via `sempy.fabric.get_report_definition`,
    grades each of the 5 levels, assigns a rank, and mints your signed badge.

    Re-run any time — the report is fetched fresh every run.
    """),

    _md("## Step 0 — Configure"),
    _code(r"""
    # ============================================================
    # 👇 Edit these two values before running
    # ============================================================
    PLAYER_NAME  = "Your Name Here"           # name shown on the badge
    REPORT_NAME  = "Arcade_Hall_Report"       # name you gave your report
    # WORKSPACE is auto-detected (current workspace)
    # ============================================================
    """),

    _md("## Step 1 — Install / import dependencies"),
    _code(r"""
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade",
                    "--disable-pip-version-check", "PyJWT>=2.6.0"],
                   check=False, capture_output=True)
    try:
        import sempy.fabric as fabric
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "semantic-link"],
                       check=True)
        import sempy.fabric as fabric
    import json, base64
    from collections import Counter
    """),

    _md("## Step 2 — Fetch the report definition (PBIR)"),
    _code(r"""
    # get_report_definition returns the PBIR parts as a DataFrame with columns
    # ['path', 'payload', 'payloadType'] (payload base64-encoded).
    print(f"📥 Fetching '{REPORT_NAME}'...")
    df_def = fabric.get_report_definition(report=REPORT_NAME)

    # Normalize into dict {path: text}
    parts = {}
    for _, row in df_def.iterrows():
        p = row["path"]
        payload = row["payload"]
        ptype   = (row.get("payloadType") or "").lower() if hasattr(row, "get") else ""
        try:
            if ptype == "inlinebase64" or (payload and len(payload) % 4 == 0):
                raw = base64.b64decode(payload).decode("utf-8", errors="replace")
            else:
                raw = str(payload)
        except Exception:
            raw = str(payload)
        parts[p] = raw

    print(f"✅ Got {len(parts)} PBIR parts.")
    print("Sample paths:")
    for p in list(parts.keys())[:10]:
        print(" ", p)
    """),

    _md("## Step 3 — Parse pages, visuals, theme, mobile layout"),
    _code(r"""
    def _json(path):
        if path in parts:
            try: return json.loads(parts[path])
            except Exception: return None
        return None

    # ---- Pages list ----
    pages_index = _json("definition/pages/pages.json") or {}
    page_names  = []
    if isinstance(pages_index.get("pageOrder"), list):
        page_names = list(pages_index["pageOrder"])
    else:
        # fallback: scan folders
        for p in parts:
            if p.startswith("definition/pages/") and p.endswith("/page.json"):
                page_names.append(p.split("/")[2])
        page_names = sorted(set(page_names))

    print(f"📄 Pages found: {len(page_names)}")
    for pn in page_names: print("  ", pn)

    pages_data = []
    for pn in page_names:
        pjson = _json(f"definition/pages/{pn}/page.json") or {}
        # gather visuals
        visuals = []
        for p in parts:
            prefix = f"definition/pages/{pn}/visuals/"
            if p.startswith(prefix) and p.endswith("/visual.json"):
                vj = _json(p) or {}
                visuals.append(vj)
        pages_data.append({"name": pn, "json": pjson, "visuals": visuals})

    # ---- Report-level (theme, mobile) ----
    report_json = _json("definition/report.json") or {}
    theme_paths = [p for p in parts if p.startswith("StaticResources/RegisteredResources/")
                                       and p.endswith(".json")]
    has_custom_theme = bool(theme_paths)
    """),

    _md("## Step 4 — Grade the 5 levels"),
    _code(r"""
    SLICER_KEYS = ("slicer", "advancedSlicerVisual")

    def visual_type(v):
        # PBIR shape varies; check common fields
        return (v.get("visual", {}).get("visualType")
                or v.get("visualContainerObjects", {}).get("visualType")
                or v.get("singleVisual", {}).get("visualType")
                or v.get("visualType")
                or "")

    def page_display_title(pj):
        # PBIR shape: pj['displayName'] is the page title shown in the tab
        return pj.get("displayName") or ""

    def page_has_background(pj):
        # check pj['objects']['background'] presence (color or image)
        objs = pj.get("objects") or {}
        bg   = objs.get("background")
        return bool(bg)

    def page_kind(pj):
        # Tooltip / Drillthrough markers
        # pageBindings shape varies, but tooltips usually have 'pageBindings':{'visualName':...} or 'type':'tooltip'
        opt = pj.get("type") or pj.get("pageType") or ""
        if str(opt).lower() == "tooltip": return "tooltip"
        if str(opt).lower() == "drillthrough" or pj.get("filterConfig", {}).get("filters"):
            # presence of drillthrough filter
            for f in (pj.get("filterConfig", {}).get("filters") or []):
                if str(f.get("type", "")).lower() == "drillthrough":
                    return "drillthrough"
        # mobile layout?
        return "regular"

    def page_has_mobile(pj):
        # PBIR mobile layout is a separate JSON: definition/pages/<page>/mobile.json
        return any(p.startswith(f"definition/pages/{pj.get('name','')}/mobile") for p in parts)

    # ---------------- Level 1 ---------------- #
    n_pages = len(pages_data)
    titled  = sum(1 for pd in pages_data if page_display_title(pd["json"]).strip()
                  and not page_display_title(pd["json"]).strip().lower().startswith("page "))
    bg      = sum(1 for pd in pages_data if page_has_background(pd["json"]))
    L1 = 0
    L1 += 10 if n_pages >= 3 else (5 if n_pages == 2 else 0)
    L1 += 5  if titled >= max(3, n_pages) else (3 if titled >= 2 else 0)
    L1 += 5  if bg >= max(3, n_pages) else (3 if bg >= 1 else 0)
    L1 = min(20, L1)
    print(f"🟢 L1 Foundation:      pages={n_pages}  titled={titled}  bg={bg}  →  {L1}/20")

    # ---------------- Level 2 ---------------- #
    all_visuals = [v for pd in pages_data for v in pd["visuals"]]
    types = Counter(visual_type(v) for v in all_visuals if visual_type(v))
    n_unique = sum(1 for t,c in types.items() if c >= 1)
    has_card   = any(t in ("card","cardVisual","multiRowCard") for t in types)
    has_slicer = any(t in SLICER_KEYS for t in types)
    L2 = min(20, n_unique * 4)
    if not has_card:   L2 = min(L2, 16)
    if not has_slicer: L2 = min(L2, 16)
    print(f"🟡 L2 Visuals:         types_seen={dict(types)}  unique={n_unique}  card={has_card}  slicer={has_slicer}  →  {L2}/20")

    # ---------------- Level 3 ---------------- #
    n_slicers = sum(c for t,c in types.items() if t in SLICER_KEYS)
    # sync slicer: a slicer with syncSlicers configured (very approximate)
    sync_count = 0
    for v in all_visuals:
        if visual_type(v) in SLICER_KEYS:
            s = json.dumps(v)
            if '"syncGroup"' in s or '"syncSlicers"' in s:
                sync_count += 1
    # edit-interactions: presence of "interactions" overrides at page level
    interactions = sum(1 for pd in pages_data
                       if '"filters"' in json.dumps(pd["json"]) and '"hidden"' in json.dumps(pd["json"]))
    L3 = 0
    L3 += 7 if n_slicers >= 2 else (4 if n_slicers == 1 else 0)
    L3 += 7 if sync_count >= 1 else 0
    L3 += 6 if interactions >= 1 else 0
    L3 = min(20, L3)
    print(f"🟠 L3 Interactivity:   slicers={n_slicers}  sync={sync_count}  interactions={interactions}  →  {L3}/20")

    # ---------------- Level 4 ---------------- #
    bookmarks_json = _json("definition/bookmarks/bookmarks.json")
    n_bookmarks = 0
    if isinstance(bookmarks_json, dict):
        n_bookmarks = len(bookmarks_json.get("items", []))
    else:
        # scan folder
        n_bookmarks = sum(1 for p in parts if p.startswith("definition/bookmarks/") and p.endswith("/bookmark.json"))
    n_tooltips      = sum(1 for pd in pages_data if page_kind(pd["json"]) == "tooltip")
    n_drillthrough  = sum(1 for pd in pages_data if page_kind(pd["json"]) == "drillthrough")
    L4 = 0
    L4 += 7 if n_bookmarks >= 1 else 0
    L4 += 7 if n_tooltips >= 1 else 0
    L4 += 6 if n_drillthrough >= 1 else 0
    L4 = min(20, L4)
    print(f"🟣 L4 Storytelling:    bookmarks={n_bookmarks}  tooltips={n_tooltips}  drillthrough={n_drillthrough}  →  {L4}/20")

    # ---------------- Level 5 ---------------- #
    # conditional formatting: look for "objects" with "dataBars" / "background" / "fontColor" with "fillRule"/"gradient"
    cond_fmt = 0
    for v in all_visuals:
        s = json.dumps(v)
        if any(k in s for k in ('"dataBars"', '"colorScale"', '"fillRule"', '"gradient"')):
            cond_fmt += 1
    n_mobile = sum(1 for pd in pages_data if page_has_mobile(pd["json"]))
    L5 = 0
    L5 += 7 if has_custom_theme else 0
    L5 += 7 if cond_fmt >= 1 else 0
    L5 += 6 if n_mobile >= 1 else 0
    L5 = min(20, L5)
    print(f"🔵 L5 Polish:          theme={has_custom_theme}  condFmt={cond_fmt}  mobile={n_mobile}  →  {L5}/20")

    TOTAL = L1 + L2 + L3 + L4 + L5
    print()
    print("=" * 60)
    print(f"  TOTAL SCORE: {TOTAL}/100")
    print("=" * 60)

    if   TOTAL >= 100: RANK = "Kill Screen Survivor"
    elif TOTAL >=  80: RANK = "Arcade Legend"
    elif TOTAL >=  60: RANK = "High Roller"
    elif TOTAL >=  40: RANK = "Quarter Muncher"
    elif TOTAL >=  20: RANK = "Newbie"
    else:              RANK = "Spectator"

    FINAL_SCORE = TOTAL
    FINAL_RANK  = RANK
    print(f"  RANK: {RANK}")
    """),

    _md("## Step 5 — 🏅 Mint your shareable badge"),
    _code(r"""
    # ============================================================
    # Retro Arcade — Badge issuance
    # HMAC-signed URL for the GitHub Pages badge viewer
    # ============================================================
    import json, time, hmac, hashlib, base64
    from IPython.display import display, Markdown, HTML

    _BADGE_SECRET = b"fabric-arcade-badge-v1-7K9mP3xQ"
    _BASE_URL     = "https://maenglar78.github.io/fabric-arcade"
    _GAME_ID      = "retro-arcade"

    def _b64u(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

    def _issue(game_id, player, rank, score):
        payload = {"v": 1, "g": game_id, "p": str(player),
                   "r": str(rank), "s": int(score), "t": int(time.time())}
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        sig  = hmac.new(_BADGE_SECRET, body, hashlib.sha256).digest()
        return f"{_BASE_URL}/badge.html?t={_b64u(body)}.{_b64u(sig)}"

    score = globals().get("FINAL_SCORE", 0)
    rank  = globals().get("FINAL_RANK", "Spectator")

    if score < 20:
        display(Markdown(
            f"### 🚧 Not yet eligible (score {score}/100)\n\n"
            f"Reach **at least 20 points** to earn the Newbie badge. "
            f"Re-open `02_Quest` for the level checklist."
        ))
    elif PLAYER_NAME.strip() in ("", "Your Name Here"):
        display(Markdown(
            "### ✍️ Set your name first\n\n"
            "Edit `PLAYER_NAME` in **Step 0** and re-run the notebook."
        ))
    else:
        url = _issue(_GAME_ID, PLAYER_NAME, rank, score)
        display(Markdown(
            f"### 🏅 Badge minted\n\n"
            f"**{PLAYER_NAME}** — *{rank}* · score **{score}/100**\n\n"
            f"🔗 **[Open your badge]({url})**\n\n"
            f"Click *Download PNG* / *Share on LinkedIn* on the badge page."
        ))
        display(HTML(f'<a href="{url}" target="_blank" '
                     f'style="display:inline-block;padding:10px 20px;border-radius:8px;'
                     f'background:linear-gradient(135deg,#ff006e,#8338ec);color:white;'
                     f'text-decoration:none;font-weight:600">🏅 Open my badge page</a>'))
    """),
]


def main():
    for name, cells in [
        ("01_Setup", SETUP_CELLS),
        ("02_Quest", QUEST_CELLS),
        ("03_Check", CHECK_CELLS),
    ]:
        p = write_nb(name, cells)
        print(f"📓 Wrote {p}")


if __name__ == "__main__":
    main()
