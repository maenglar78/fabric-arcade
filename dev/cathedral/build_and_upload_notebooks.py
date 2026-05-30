"""
Build the 3 Cathedral notebooks (.ipynb) from inline content,
then upload them to the Fabric Arcade Test workspace.

Re-run anytime to refresh notebooks in Fabric.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).parent))
from upload_notebook import upload_or_update_notebook  # noqa: E402

OUT_DIR = Path(__file__).parent / "notebooks_built"
OUT_DIR.mkdir(exist_ok=True)

import datetime as _dt
BUILD_STAMP = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"🏗️  Build stamp: {BUILD_STAMP}")


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
        # Fabric / Jupyter: collapse the source so the student sees only the output.
        meta["jupyter"] = {"source_hidden": True}
        meta["collapsed"] = True
    return {
        "cell_type": "code",
        "metadata": meta,
        "execution_count": None,
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }


def _code_hidden(text: str) -> dict:
    return _code(text, hidden=True)


def _nb(cells: list[dict]) -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": FABRIC_NB_METADATA,
        "cells": cells,
    }


def write_nb(name: str, nb: dict) -> Path:
    p = OUT_DIR / f"{name}.ipynb"
    p.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    return p


# =====================================================================
# 1) SEED NOTEBOOK — generates synthetic Sales/Date/Customer/Budget
#    into the attached Lakehouse, then creates Cathedral_Model
#    (Direct Lake semantic model) on top of those tables.
# =====================================================================

SEED_CELLS = [
    _md(f"""
    # 🧮 Calc Groups Cathedral — Seed Notebook

    > 🏗️ Build: **{BUILD_STAMP}** &nbsp;·&nbsp; if you don't see this stamp after re-upload, close the notebook tab and reopen it.

    > **Run this notebook ONCE to bootstrap the game.**
    > It populates the `Cathedral_LH` Lakehouse with synthetic Sales / Date / Customer / Budget tables (3 years),
    > then creates the `Cathedral_Model` Direct Lake semantic model on top of them.

    ## Requirements
    1. Attach **`Cathedral_LH`** as the default Lakehouse on this notebook (📚 icon in the left rail → *Add* → Existing Lakehouse).
    2. Run all cells top → bottom.

    Total runtime: ~1–2 minutes.
    """),

    _code(r"""
    # === Imports & constants ===
    # Upgrade PyJWT silently to avoid sempy-labs dependency conflict warning later on.
    # NOTE: stderr is captured so the cosmetic 'pip's dependency resolver' warning is hidden.
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade",
                    "--disable-pip-version-check", "PyJWT>=2.6.0"],
                   check=False, capture_output=True)

    import random, datetime as dt
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    SEED_VERSION = "v1"          # bump if you change generators
    RNG_SEED = 42                # deterministic
    YEARS = [2023, 2024, 2025]
    N_CUSTOMERS = 50
    N_SALES = 100_000

    random.seed(RNG_SEED)

    # Best-effort: detect attached Lakehouse (don't hard-fail, just warn).
    lh_name = ""
    for key in ["trident.lakehouse.name", "trident.activeworkspace.lakehouseName",
                "trident.workspace.lakehouseName"]:
        try:
            v = spark.conf.get(key)
            if v: lh_name = v; break
        except Exception:
            pass
    print(f"Default Lakehouse: {lh_name or '(not detected)'}")

    # Drop stale tables from prior runs (idempotent).
    for t in ["date", "customer", "sales", "budget",
              "Date", "Customer", "Sales", "Budget"]:
        try:
            spark.sql(f"DROP TABLE IF EXISTS {t}")
        except Exception:
            pass
    print("🧹 Clean slate.")
    """),

    _md("## Step 1 — Date dimension (3 years, daily grain)"),

    _code(r"""
    start = dt.date(YEARS[0], 1, 1)
    end   = dt.date(YEARS[-1], 12, 31)
    days  = (end - start).days + 1

    rows = []
    for i in range(days):
        d = start + dt.timedelta(days=i)
        rows.append((
            int(d.strftime("%Y%m%d")),               # DateKey
            d,                                       # Date
            d.year,                                  # Year
            (d.month - 1) // 3 + 1,                  # Quarter
            d.month,                                 # MonthNum
            d.strftime("%B"),                        # MonthName
            d.day,                                   # DayOfMonth
            d.strftime("%A"),                        # DayName
            d.isoweekday() in (6, 7),                # IsWeekend
        ))

    schema = T.StructType([
        T.StructField("DateKey",     T.IntegerType(),   False),
        T.StructField("Date",        T.DateType(),      False),
        T.StructField("Year",        T.IntegerType(),   False),
        T.StructField("Quarter",     T.IntegerType(),   False),
        T.StructField("MonthNum",    T.IntegerType(),   False),
        T.StructField("MonthName",   T.StringType(),    False),
        T.StructField("DayOfMonth",  T.IntegerType(),   False),
        T.StructField("DayName",     T.StringType(),    False),
        T.StructField("IsWeekend",   T.BooleanType(),   False),
    ])

    date_df = spark.createDataFrame(rows, schema)
    (date_df.write.format("delta").mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable("date"))
    print(f"✅ date  rows={date_df.count():,}")
    """),

    _md("## Step 2 — Customer dimension"),

    _code(r"""
    REGIONS  = ["EU-North", "EU-South", "US-East", "US-West", "APAC"]
    SEGMENTS = ["Enterprise", "SMB", "Consumer"]

    rng = random.Random(RNG_SEED + 1)
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        rows.append((
            i,
            f"Customer {i:03d}",
            rng.choice(REGIONS),
            rng.choice(SEGMENTS),
        ))

    cust_df = spark.createDataFrame(rows, ["CustomerKey", "CustomerName", "Region", "Segment"])
    (cust_df.write.format("delta").mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable("customer"))
    print(f"✅ customer  rows={cust_df.count():,}")
    """),

    _md("## Step 3 — Sales fact (~100k rows, deterministic, with seasonality)"),

    _code(r"""
    # Build a date list once (Python side) for fast sampling
    date_pool = [(int(d.strftime('%Y%m%d')), d) for d in
                 (dt.date(YEARS[0], 1, 1) + dt.timedelta(days=i) for i in range(days))]

    rng = random.Random(RNG_SEED + 2)

    # Mild seasonality: Q4 +30%, Q1 -10%
    def season_factor(month):
        if month in (10, 11, 12): return 1.30
        if month in (1, 2):       return 0.90
        return 1.0

    # YoY growth: 2023 base, 2024 +12%, 2025 +18%
    year_growth = {2023: 1.00, 2024: 1.12, 2025: 1.18}

    rows = []
    for sales_key in range(1, N_SALES + 1):
        date_key, d = rng.choice(date_pool)
        cust_key = rng.randint(1, N_CUSTOMERS)
        qty = rng.randint(1, 20)
        unit_price = round(rng.uniform(10.0, 500.0), 2)
        raw_amount = qty * unit_price
        amount = round(raw_amount * season_factor(d.month) * year_growth[d.year], 2)
        rows.append((sales_key, date_key, cust_key, qty, unit_price, amount))

    schema = T.StructType([
        T.StructField("SalesKey",   T.IntegerType(),   False),
        T.StructField("DateKey",    T.IntegerType(),   False),
        T.StructField("CustomerKey", T.IntegerType(),  False),
        T.StructField("Quantity",   T.IntegerType(),   False),
        T.StructField("UnitPrice",  T.DoubleType(),    False),
        T.StructField("Amount",     T.DoubleType(),    False),
    ])

    sales_df = spark.createDataFrame(rows, schema)
    (sales_df.write.format("delta").mode("overwrite")
             .option("overwriteSchema", "true")
             .saveAsTable("sales"))
    print(f"✅ sales  rows={sales_df.count():,}")
    """),

    _md("## Step 4 — Budget (monthly per region, planned ≈ 95% of actuals)"),

    _code(r"""
    # Budget needs Year/MonthNum/Region — join back to date+customer
    actuals = (sales_df
        .join(date_df, "DateKey")
        .join(cust_df, "CustomerKey")
        .groupBy("Year", "MonthNum", "Region")
        .agg(F.round(F.sum("Amount"), 2).alias("Actual")))

    budget_df = actuals.withColumn("Budget", F.round(F.col("Actual") * 0.95, 2)).select(
        "Year", "MonthNum", "Region", "Budget"
    )

    (budget_df.write.format("delta").mode("overwrite")
              .option("overwriteSchema", "true")
              .saveAsTable("budget"))
    print(f"✅ budget  rows={budget_df.count():,}")
    """),

    _md("## Step 5 — Summary"),

    _code(r"""
    for t in ["date", "customer", "sales", "budget"]:
        n = spark.table(t).count()
        print(f"  {t:<10} {n:>10,} rows")
    print("\n🏛️  Lakehouse Cathedral_LH is ready.")
    """),

    _md(r"""
    ## Step 6 — Create the `Cathedral_Model` semantic model (Direct Lake)

    Uses `sempy-labs` to build a Direct Lake semantic model on top of the 4 tables.
    Idempotent: if the model already exists, it's left alone (delete it first if you want a fresh one).
    """),

    _code(r"""
    # Install / import sempy-labs (Fabric runtime ships sempy but not labs by default)
    import subprocess, sys, importlib
    try:
        import sempy_labs as labs
        from sempy_labs import directlake as labs_dl  # explicit submodule import
    except ImportError:
        print("Installing semantic-link-labs...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "semantic-link-labs"],
                       check=True)
        importlib.invalidate_caches()
        import sempy_labs as labs
        from sempy_labs import directlake as labs_dl
    print(f"sempy-labs version: {getattr(labs, '__version__', '?')}")

    import sempy.fabric as fabric

    MODEL_NAME = "Cathedral_Model"
    LAKEHOUSE  = "Cathedral_LH"
    # Physical tables in OneLake are lowercase (Spark's saveAsTable behavior).
    # Dict maps semantic-model table name (Pascal) → physical Delta folder name (lowercase).
    # Logical name (Pascal, used in DAX) -> physical Delta folder (lowercase, Spark default).
    TABLES = {
        "Date":     "date",
        "Customer": "customer",
        "Sales":    "sales",
        "Budget":   "budget",
    }

    # Check existence via sempy.fabric.list_datasets()
    try:
        df = fabric.list_datasets()
        # Column name varies across versions: 'Dataset Name', 'name', etc.
        name_col = next((c for c in df.columns if c.lower() in ("dataset name", "name", "display name")), None)
        already = (df[name_col] == MODEL_NAME).any() if name_col else False
    except Exception as e:
        print(f"(could not list datasets: {e}); will try to create...")
        already = False

    if already:
        print(f"✅ Semantic model '{MODEL_NAME}' already exists — attempting refresh only.")
        import time
        last_err = None
        for attempt in range(1, 6):
            try:
                fabric.refresh_dataset(dataset=MODEL_NAME, refresh_type="full")
                print(f"✅ Refresh succeeded on attempt {attempt}.")
                last_err = None
                break
            except Exception as e:
                last_err = e
                print(f"   attempt {attempt} failed: {e}")
                time.sleep(20)
        if last_err is not None:
            print("⚠️  Refresh still failing. Delete the model in Fabric UI and re-run this cell to recreate from scratch.")
            print(f"   Last error: {last_err}")
    else:
        # Warm up SQL endpoint metadata for the freshly-written tables.
        # Without this wait, refresh fails with "tables don't exist or access denied".
        import time
        print("⏳ Waiting 45s for SQL endpoint metadata sync of newly-written tables...")
        time.sleep(45)

        print(f"⏳ Creating Direct Lake semantic model '{MODEL_NAME}' from Lakehouse '{LAKEHOUSE}' (without refresh)...")
        labs_dl.generate_direct_lake_semantic_model(
            dataset=MODEL_NAME,
            tables=TABLES,
            source=LAKEHOUSE,
            source_type="Lakehouse",
            refresh=False,
        )
        print(f"✅ Created '{MODEL_NAME}' (unrefreshed).")

        # Refresh separately with retries; first refresh on a brand new Direct Lake model
        # can flake while the SQL endpoint catches up.
        print("⏳ Refreshing model (with retries)...")
        last_err = None
        for attempt in range(1, 6):
            try:
                fabric.refresh_dataset(dataset=MODEL_NAME, refresh_type="full")
                print(f"✅ Refresh succeeded on attempt {attempt}.")
                last_err = None
                break
            except Exception as e:
                last_err = e
                print(f"   attempt {attempt} failed: {e}")
                time.sleep(20)
        if last_err is not None:
            print("⚠️  Refresh still failing — model exists, you can retry refresh manually from Fabric UI.")
            print(f"   Last error: {last_err}")
    """),

    _md(r"""
    ## Step 7 — Add relationships + seed measure

    The judge needs at minimum:
    - relationship `Sales[DateKey]   ↔ Date[DateKey]`
    - relationship `Sales[CustomerKey] ↔ Customer[CustomerKey]`
    - one seed measure `Sales Amount Seed := SUM(Sales[Amount])` (excluded from your elegance score)
    """),

    _code(r"""
    # Ensure sempy-labs is available (re-import is cheap if Step 6 already installed it)
    import subprocess, sys, importlib
    try:
        import sempy_labs as labs
        from sempy_labs import tom as labs_tom  # EXPLICIT submodule import
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "semantic-link-labs"],
                       check=True)
        importlib.invalidate_caches()
        import sempy_labs as labs
        from sempy_labs import tom as labs_tom
    import traceback

    MODEL_NAME = "Cathedral_Model"
    SEED_MEASURE = "Sales Amount Seed"

    def _safe(label, fn):
        try:
            fn()
            print(f"  ✅ {label}")
        except Exception as e:
            print(f"  ❌ {label}: {type(e).__name__}: {e}")
            traceback.print_exc()

    print(f"🔌 Connecting to semantic model {MODEL_NAME!r}...")
    try:
        ctx = labs_tom.connect_semantic_model(dataset=MODEL_NAME, readonly=False)
    except Exception:
        print("❌ connect_semantic_model failed")
        traceback.print_exc()
        raise

    with ctx as tom:

        # --- Inventory check (each piece isolated) ---
        try:
            tnames = [t.Name for t in tom.model.Tables]
            print("📋 Tables in model:", tnames)
        except Exception:
            print("❌ enumerate Tables failed")
            traceback.print_exc()
            tnames = []

        for tname in ("Date", "Customer", "Sales", "Budget"):
            try:
                cols = [c.Name for c in tom.model.Tables[tname].Columns]
                print(f"   {tname}: {cols}")
            except Exception as e:
                print(f"   ❌ Table {tname!r} not found: {e}")

        # --- relationships ---
        def has_rel(from_tbl, from_col, to_tbl, to_col):
            for r in tom.model.Relationships:
                try:
                    if (r.FromTable.Name == from_tbl and r.FromColumn.Name == from_col
                        and r.ToTable.Name == to_tbl and r.ToColumn.Name == to_col):
                        return True
                except Exception:
                    pass
            return False

        def _add_rel_date():
            if has_rel("Sales", "DateKey", "Date", "DateKey"):
                print("  = rel Sales->Date already exists"); return
            tom.add_relationship(
                from_table="Sales", from_column="DateKey",
                to_table="Date",  to_column="DateKey",
                from_cardinality="Many", to_cardinality="One",
                cross_filtering_behavior="OneDirection",
            )

        def _add_rel_cust():
            if has_rel("Sales", "CustomerKey", "Customer", "CustomerKey"):
                print("  = rel Sales->Customer already exists"); return
            tom.add_relationship(
                from_table="Sales", from_column="CustomerKey",
                to_table="Customer", to_column="CustomerKey",
                from_cardinality="Many", to_cardinality="One",
                cross_filtering_behavior="OneDirection",
            )

        def _mark_date():
            tom.mark_as_date_table(table_name="Date", column_name="Date")

        def _add_seed_measure():
            if any(m.Name == SEED_MEASURE for m in tom.model.Tables["Sales"].Measures):
                print(f"  = measure {SEED_MEASURE} already exists"); return
            tom.add_measure(
                table_name="Sales",
                measure_name=SEED_MEASURE,
                expression="SUM(Sales[Amount])",
                format_string="#,##0.00",
                description="Seed measure — excluded from elegance score.",
            )

        _safe("relationship Sales[DateKey] -> Date[DateKey]", _add_rel_date)
        _safe("relationship Sales[CustomerKey] -> Customer[CustomerKey]", _add_rel_cust)
        _safe("mark Date as date table (column 'Date')", _mark_date)
        _safe(f"add measure {SEED_MEASURE}", _add_seed_measure)

    print("✅ Model committed.")
    print()
    print("🎉 Setup complete. Open the `CalcGroups_Cathedral` notebook to start playing!")
    """),
]

# =====================================================================
# 2) CATHEDRAL NOTEBOOK — the actual game (Phase C)
# =====================================================================

CATHEDRAL_CELLS = [
    _md(f"""
    # 🏛️ Calc Groups Cathedral — Quest Brief

    > 🏗️ Build: **{BUILD_STAMP}** &nbsp;·&nbsp; if you don't see this stamp after re-upload, close the notebook tab and reopen it.

    > _An apprentice writes a measure for every KPI variation._
    > _A master architect carves them all from **one stone**._

    ---

    ## 📜 Your mission

    The CFO just asked for a **complete sales dashboard**. They want **12 KPIs** — each a
    variation of the same `Sales Amount` base measure: this year, last year, YoY, YTD,
    rolling 12 months, % of year, distinct customers… the full Time Intelligence catalogue.

    Your job: open the **`Cathedral_Model`** semantic model in the workspace and **carve
    12 DAX measures**, one per pillar. The names, the data, the test contexts — they're
    all locked down. You just write the DAX.

    When you're done, open the **`CalcGroups_Check`** notebook → run it → it grades each
    measure, scores your DAX for **elegance**, and assigns you an **Architect rank**.

    ---

    ## 🛠️ How to add measures in the web modeler

    1. In the workspace, open **`Cathedral_Model`** (semantic model).
    2. Click **`Open data model`** → you'll see the diagram (Date, Customer, Sales, Budget).
    3. Right-click on the **`Sales`** table → **`New measure`**.
    4. Type the measure name on the left of `:=` and the DAX on the right, e.g.
       ```dax
       M_05_YTD := CALCULATE([Sales Amount Seed], DATESYTD('Date'[Date]))
       ```
    5. Click ✅ to commit. Repeat for all 12 pillars.
    6. **All measures must live on the `Sales` table** — the checker looks for them there.

    > 💡 Tip: the seed measure **`[Sales Amount Seed] = SUM(Sales[Amount])`** is already there.
    > Build every pillar by wrapping it in `CALCULATE(...)`.

    ---
    """),

    _md("## Step 1 — Connect to Cathedral_Model and sanity-check the data"),
    _code(r"""
    # Imports + bootstrap
    import subprocess, sys, importlib
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade",
                    "--disable-pip-version-check", "PyJWT>=2.6.0"],
                   check=False, capture_output=True)
    try:
        import sempy_labs as labs
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "--disable-pip-version-check", "semantic-link-labs"],
                       check=True, capture_output=True)
        importlib.invalidate_caches()
        import sempy_labs as labs
    import sempy.fabric as fabric

    MODEL_NAME = "Cathedral_Model"
    LAKEHOUSE  = "Cathedral_LH"

    try:
        WORKSPACE_ID = fabric.get_notebook_workspace_id()
    except Exception:
        WORKSPACE_ID = None
    print(f"🏢 Workspace : {WORKSPACE_ID}")

    # Sync the Lakehouse SQL endpoint (required after the Seed notebook ran).
    try:
        from sempy_labs import refresh_sql_endpoint_metadata
        try:
            refresh_sql_endpoint_metadata(item=LAKEHOUSE, workspace=WORKSPACE_ID, type="Lakehouse")
        except TypeError:
            refresh_sql_endpoint_metadata(item=LAKEHOUSE, workspace=WORKSPACE_ID)
        print("✅ SQL endpoint synced")
    except Exception as e:
        print(f"⚠️ SQL endpoint sync: {type(e).__name__}: {str(e)[:200]}")

    # Force a Direct Lake reframe so the columns are queryable.
    try:
        fabric.refresh_dataset(dataset=MODEL_NAME, workspace=WORKSPACE_ID, refresh_type="full")
        print("✅ Cathedral_Model refreshed")
    except Exception as e:
        print(f"⚠️ refresh: {type(e).__name__}: {str(e)[:200]}")

    # Smoke test: the base measure should return a positive number.
    df = fabric.evaluate_dax(dataset=MODEL_NAME, workspace=WORKSPACE_ID,
                             dax_string="EVALUATE { [Sales Amount Seed] }")
    print(f"📊 Sales Amount Seed = {df.iloc[0,0]:,.2f}")
    print()
    print("🟢 You are connected. Read the next section, then go build your 12 measures.")
    """),

    _md(r"""
    ## Step 2 — Read carefully: the 12 Pillars

    For each pillar below, **create a measure in the `Sales` table** of `Cathedral_Model`
    with the **exact name** shown (the checker is case-sensitive). The base measure
    `[Sales Amount Seed] = SUM(Sales[Amount])` is already there — wrap it.

    The checker will evaluate your measure in **3 filter contexts** and compare it to
    the canonical result. The DAX you write also gets an **elegance score**: shorter +
    less nesting = more points.

    ---

    ### 🪨 Pillar #1 — `M_01_Current` — Current Sales
    Sum of sales in the current filter context. The warm-up.
    - **Hint**: simply reference `[Sales Amount Seed]`.
    - **Test contexts**: `'Date'[Year]=2024`  •  `'Date'[Year]=2025 & 'Date'[MonthNum]=6`  •  `'Date'[Year]=2024 & Customer[Region]="EU-North"`

    ### 🪨 Pillar #2 — `M_02_LastYear` — Sales Last Year
    Same period one year before. Hint: `SAMEPERIODLASTYEAR('Date'[Date])`.

    ### 🪨 Pillar #3 — `M_03_YoY` — Sales YoY (absolute)
    Current sales minus same period last year.

    ### 🪨 Pillar #4 — `M_04_YoYPct` — Sales YoY %
    Percentage growth vs. last year. Hint: `DIVIDE`.

    ### 🪨 Pillar #5 — `M_05_YTD` — Sales Year-to-Date
    Hint: `DATESYTD('Date'[Date])`.

    ### 🪨 Pillar #6 — `M_06_MTD` — Sales Month-to-Date
    Hint: `DATESMTD('Date'[Date])`.

    ### 🪨 Pillar #7 — `M_07_QTD` — Sales Quarter-to-Date
    Hint: `DATESQTD('Date'[Date])`.

    ### 🪨 Pillar #8 — `M_08_Rolling12` — Rolling 12-month Sales
    Trailing 12 months. Hint: `DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -12, MONTH)`.

    ### 🪨 Pillar #9 — `M_09_BestMonth` — Best Month Value
    Highest monthly total inside the current filter. Hint: `MAXX(VALUES('Date'[MonthNum]), [Sales Amount Seed])`.

    ### 🪨 Pillar #10 — `M_10_PctOfYear` — % of Year
    Share of the yearly total taken by the current month. Hint: `DIVIDE` with `ALL` over the date columns.

    ### 🪨 Pillar #11 — `M_11_AvgDailySales` — Average Daily Sales
    Mean across visible days. Hint: `AVERAGEX(VALUES('Date'[Date]), [Sales Amount Seed])`.

    ### 🪨 Pillar #12 — `M_12_DistinctCustomers` — Distinct Customers
    How many unique customers bought something. Hint: `DISTINCTCOUNT(Sales[CustomerKey])`.

    ---
    """),

    _md(r"""
    ## Step 3 — Build the measures in the web modeler

    1. Switch to the workspace tab → open **`Cathedral_Model`** → **`Open data model`**.
    2. Right-click the **`Sales`** table → **`New measure`**.
    3. Use the **exact** measure name (e.g. `M_05_YTD`), enter the DAX, hit ✅.
    4. Repeat for all 12.

    > 🔁 **Reminder**: every measure must live on the **`Sales`** table.

    ## Step 4 — Grade your work

    Open the **`CalcGroups_Check`** notebook in the workspace and run it.
    It will:
    - Verify each measure exists with the expected name.
    - Run it in the 3 test contexts and compare to the canonical answer.
    - Compute an **elegance score** (shorter + less nesting = better).
    - Assign your **Architect rank** (Stonemason → Cathedral Builder).
    - Log every attempt to `Cathedral_EH.CathedralEvents` (telemetry).

    When all 12 pillars are 🟢, the Check notebook will unlock the **final challenge**.

    🍀 *Good luck, architect.*
    """),
]

# =====================================================================
# 3) CHECK NOTEBOOK — grades the 12 measures + unlocks the calc group challenge
# =====================================================================

CHECK_CELLS = [
    _md(f"""
    # ✅ Calc Groups Cathedral — Check & Grade

    > 🏗️ Build: **{BUILD_STAMP}** &nbsp;·&nbsp; if you don't see this stamp after re-upload, close the notebook tab and reopen it.

    ## How to use this notebook

    1. Click **▶️ Run all** in the toolbar.
    2. Wait ~30 seconds — the model is refreshed and your 12 measures are graded.
    3. Read the **grading panel** that appears below each step.

    > 🕵️ The code is hidden on purpose: you don't need to read it, just run it.
    > (If you're curious, click the `…` next to any cell → **Show input**.)

    The checker will:
    - Verify each of the 12 measures (`M_01_Current` … `M_12_DistinctCustomers`) exists on the `Sales` table.
    - Evaluate each one in 3 filter contexts and compare to the canonical answer.
    - Score **correctness** + **elegance** (shorter DAX, less nesting → more points).
    - Log every check to `Cathedral_EH.CathedralEvents`.
    - If all 12 pass → unlock the **final challenge**.
    """),

    _md("## Step 1 — Setup"),
    _code_hidden(r"""
    import subprocess, sys, importlib, json, uuid, math, re, time, getpass
    import datetime as dt
    import pandas as pd

    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade",
                    "--disable-pip-version-check", "PyJWT>=2.6.0"],
                   check=False, capture_output=True)
    try:
        import sempy_labs as labs
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "--disable-pip-version-check", "semantic-link-labs"],
                       check=True, capture_output=True)
        importlib.invalidate_caches()
        import sempy_labs as labs
    import sempy.fabric as fabric

    # --- Silence sempy / .NET chatter so the grading panel stays readable ---
    import logging, warnings
    warnings.filterwarnings("ignore")
    for name in ("sempy", "sempy.fabric", "sempy_labs", "Microsoft", "py4j"):
        logging.getLogger(name).setLevel(logging.ERROR)
    # sempy prints the "'[V]'... serialized as string" line via the root logger.
    logging.getLogger().setLevel(logging.ERROR)

    MODEL_NAME  = "Cathedral_Model"
    LAKEHOUSE   = "Cathedral_LH"
    EH_CLUSTER  = "https://trd-z9b3f5xvzm87f8c2kd.z6.kusto.fabric.microsoft.com"
    EH_DATABASE = "Cathedral_EH"
    EH_TABLE    = "CathedralEvents"
    HOST_TABLE  = "Sales"   # measures expected on this table

    try:
        WORKSPACE_ID = fabric.get_notebook_workspace_id()
    except Exception:
        WORKSPACE_ID = None

    SESSION_ID = str(uuid.uuid4())
    try:    PLAYER_ID = getpass.getuser()
    except: PLAYER_ID = "anonymous"

    print(f"🏢 Workspace : {WORKSPACE_ID}")
    print(f"🎮 Session   : {SESSION_ID}")
    print(f"🧑 Player    : {PLAYER_ID}")

    # Refresh Direct Lake before grading (idempotent).
    try:
        fabric.refresh_dataset(dataset=MODEL_NAME, workspace=WORKSPACE_ID, refresh_type="full")
        print("✅ Model refreshed")
    except Exception as e:
        print(f"⚠️ refresh: {type(e).__name__}: {str(e)[:200]}")
    """),

    _md("## Step 2 — Helpers (DAX runner, elegance scorer, KQL logger)"),
    _code_hidden(r"""
    def _norm_dax(expr: str) -> str:
        return re.sub(r"\s+", " ", expr.strip())

    import os, contextlib, io
    @contextlib.contextmanager
    def _muted():
        '''Silence stdout+stderr at the OS level — needed to swallow the
        .NET '[V]' serialization warnings that bypass Python logging.'''
        try:
            so_fd = os.dup(1); se_fd = os.dup(2)
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, 1); os.dup2(devnull, 2)
            os.close(devnull)
            yield
        finally:
            try: os.dup2(so_fd, 1); os.close(so_fd)
            except Exception: pass
            try: os.dup2(se_fd, 2); os.close(se_fd)
            except Exception: pass

    def run_dax_scalar(expr: str, ctx_filters):
        '''Wrap a scalar expression in EVALUATE ROW(CALCULATE(...)). Returns float or None.'''
        flt = ", " + ", ".join(ctx_filters) if ctx_filters else ""
        q   = f"EVALUATE ROW(\"V\", CALCULATE({expr}{flt}))"
        try:
            with _muted():
                df = fabric.evaluate_dax(dataset=MODEL_NAME, workspace=WORKSPACE_ID, dax_string=q)
            if df.empty: return None
            v = df.iloc[0, 0]
            return None if v is None else float(v)
        except Exception as e:
            return None

    def elegance_score(dax: str) -> float:
        s = _norm_dax(dax)
        char_pen = max(0, len(s) - 60) * 0.4
        calc = len(re.findall(r"\bCALCULATE\b", s, re.IGNORECASE))
        filt = len(re.findall(r"\bFILTER\b",    s, re.IGNORECASE))
        sumx = len(re.findall(r"\bSUMX\b",      s, re.IGNORECASE))
        nest_pen = max(0, calc - 1) * 8 + filt * 6 + sumx * 4
        return max(0.0, round(100 - char_pen - nest_pen, 1))

    def values_close(a, b, rel=1e-4, abs_tol=1e-2) -> bool:
        if a is None or b is None: return False
        return math.isclose(a, b, rel_tol=rel, abs_tol=abs_tol)

    def get_measure_expression(measure_name: str) -> str | None:
        '''Read the user's DAX expression for a measure (from INFO.MEASURES()).'''
        q = (
            "EVALUATE SELECTCOLUMNS(INFO.MEASURES(), \"Name\", [Name], \"Expr\", [Expression])"
        )
        try:
            with _muted():
                df = fabric.evaluate_dax(dataset=MODEL_NAME, workspace=WORKSPACE_ID, dax_string=q)
            for _, r in df.iterrows():
                if str(r.iloc[0]) == measure_name:
                    return str(r.iloc[1])
        except Exception:
            pass
        return None

    def _kql_token():
        try:
            import notebookutils
            return notebookutils.credentials.getToken("kusto")
        except Exception:
            pass
        try:
            import mssparkutils
            return mssparkutils.credentials.getToken("kusto")
        except Exception:
            pass
        return None

    def log_event(event_type, pillar_id, pillar_key, pass_fail, elegance, rank, duration_s, dax_len):
        import requests
        ts  = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        eid = str(uuid.uuid4())
        # Schema (15 cols): EventId, Timestamp, SessionId, PlayerId, EventType,
        # PillarId, PillarKey, SubmittedValue, ExpectedValue, PassFail,
        # MeasureCount, CalcGroupCount, EleganceScore, Rank, DurationSeconds
        row = (f'"{eid}","{ts}","{SESSION_ID}","{PLAYER_ID}","{event_type}",'
               f'{pillar_id},"{pillar_key}",0,0,"{pass_fail}",'
               f'{dax_len},0,{elegance},"{rank}",{duration_s:.3f}')
        csl = f".ingest inline into table {EH_TABLE} <|\n{row}"
        try:
            tok = _kql_token()
            if not tok: return
            requests.post(f"{EH_CLUSTER}/v1/rest/mgmt",
                          headers={"Authorization": f"Bearer {tok}",
                                   "Content-Type": "application/json"},
                          json={"db": EH_DATABASE, "csl": csl}, timeout=10)
        except Exception:
            pass

    print("✅ Helpers loaded.")
    """),

    _md("## Step 3 — Pillar definitions (canonical answers)"),
    _code_hidden(r"""
    from dataclasses import dataclass, field
    from typing import List, Tuple

    BASE = "[Sales Amount Seed]"

    CTX_2024_FULL = ("'Date'[Year]=2024",)
    CTX_2025_JUN  = ("'Date'[Year]=2025", "'Date'[MonthNum]=6")
    CTX_2024_EUN  = ("'Date'[Year]=2024", "Customer[Region]=\"EU-North\"")
    CTX_2025_FULL = ("'Date'[Year]=2025",)
    CTX_2024_DEC  = ("'Date'[Year]=2024", "'Date'[MonthNum]=12")
    CTX_2024_JAN  = ("'Date'[Year]=2024", "'Date'[MonthNum]=1")

    @dataclass
    class Pillar:
        id: int
        key: str
        measure_name: str
        title: str
        canonical_dax: str
        contexts: List[Tuple[str, ...]]
        unit: str = "number"

    PILLARS = [
        Pillar(1,  "Current",          "M_01_Current",          "Current Sales",
               BASE, [CTX_2024_FULL, CTX_2025_JUN, CTX_2024_EUN]),
        Pillar(2,  "LastYear",         "M_02_LastYear",         "Sales LY",
               f"CALCULATE({BASE}, SAMEPERIODLASTYEAR('Date'[Date]))",
               [CTX_2024_FULL, CTX_2025_JUN, CTX_2024_EUN]),
        Pillar(3,  "YoY",              "M_03_YoY",              "Sales YoY (abs)",
               f"{BASE} - CALCULATE({BASE}, SAMEPERIODLASTYEAR('Date'[Date]))",
               [CTX_2024_FULL, CTX_2025_JUN, CTX_2024_EUN]),
        Pillar(4,  "YoYPct",           "M_04_YoYPct",           "Sales YoY %",
               f"DIVIDE({BASE} - CALCULATE({BASE}, SAMEPERIODLASTYEAR('Date'[Date])), "
               f"CALCULATE({BASE}, SAMEPERIODLASTYEAR('Date'[Date])))",
               [CTX_2024_FULL, CTX_2025_JUN, CTX_2024_EUN], unit="percent"),
        Pillar(5,  "YTD",              "M_05_YTD",              "Sales YTD",
               f"CALCULATE({BASE}, DATESYTD('Date'[Date]))",
               [CTX_2024_FULL, CTX_2025_JUN, CTX_2024_EUN]),
        Pillar(6,  "MTD",              "M_06_MTD",              "Sales MTD",
               f"CALCULATE({BASE}, DATESMTD('Date'[Date]))",
               [CTX_2025_JUN, CTX_2024_FULL, CTX_2024_EUN]),
        Pillar(7,  "QTD",              "M_07_QTD",              "Sales QTD",
               f"CALCULATE({BASE}, DATESQTD('Date'[Date]))",
               [CTX_2025_JUN, CTX_2024_FULL, CTX_2024_EUN]),
        Pillar(8,  "Rolling12",        "M_08_Rolling12",        "Rolling 12-month",
               f"CALCULATE({BASE}, DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -12, MONTH))",
               [CTX_2024_FULL, CTX_2025_JUN, CTX_2025_FULL]),
        Pillar(9,  "BestMonth",        "M_09_BestMonth",        "Best Month Value",
               f"MAXX(VALUES('Date'[MonthNum]), {BASE})",
               [CTX_2024_FULL, CTX_2025_FULL, CTX_2024_EUN]),
        Pillar(10, "PctOfYear",        "M_10_PctOfYear",        "% of Year",
               f"DIVIDE({BASE}, CALCULATE({BASE}, ALL('Date'[MonthNum], 'Date'[MonthName], "
               f"'Date'[DayOfMonth], 'Date'[DayName], 'Date'[Date], 'Date'[DateKey], "
               f"'Date'[IsWeekend], 'Date'[Quarter])))",
               [CTX_2025_JUN, CTX_2024_DEC, CTX_2024_JAN], unit="percent"),
        Pillar(11, "AvgDailySales",    "M_11_AvgDailySales",    "Average Daily Sales",
               f"AVERAGEX(VALUES('Date'[Date]), {BASE})",
               [CTX_2024_FULL, CTX_2025_JUN, CTX_2024_EUN]),
        Pillar(12, "DistinctCustomers", "M_12_DistinctCustomers", "Distinct Customers",
               "DISTINCTCOUNT(Sales[CustomerKey])",
               [CTX_2024_FULL, CTX_2025_JUN, CTX_2024_EUN], unit="integer"),
    ]
    PILLAR_BY_ID = {p.id: p for p in PILLARS}

    RANKS = [(0, "Stonemason"), (300, "Apprentice"), (700, "Journeyman"),
             (1100, "Architect"), (1500, "Master Architect"), (1800, "Cathedral Builder")]

    def rank_for(total: float) -> str:
        r = "Stonemason"
        for thr, name in RANKS:
            if total >= thr: r = name
        return r

    print(f"📜 {len(PILLARS)} pillars loaded.")
    """),

    _md("## Step 4 — Grade all 12 measures"),
    _code_hidden(r"""
    def check_all():
        print("┌─ 🏛️  Cathedral Check ─────────────────────────────────────────────")
        results = []
        total_score = 0.0
        for p in PILLARS:
            t0 = time.time()
            user_expr = get_measure_expression(p.measure_name)
            if not user_expr:
                print(f"│ ⬜ #{p.id:2d} {p.measure_name:<26s}  MISSING")
                results.append({"pillar": p.id, "status": "MISSING", "score": 0})
                log_event("check", p.id, p.key, "MISSING", 0, rank_for(total_score), time.time()-t0, 0)
                continue

            # Evaluate canonical vs user measure in each context.
            all_pass = True
            for ctx in p.contexts:
                exp = run_dax_scalar(p.canonical_dax, list(ctx))
                got = run_dax_scalar(f"[{p.measure_name}]", list(ctx))
                if not values_close(got, exp):
                    all_pass = False
                    break

            if all_pass:
                eleg  = elegance_score(user_expr)
                score = 50 + eleg * 0.5
                total_score += score
                print(f"│ 🟢 #{p.id:2d} {p.measure_name:<26s}  score={score:5.1f}  elegance={eleg:5.1f}")
                results.append({"pillar": p.id, "status": "PASS", "score": score, "elegance": eleg})
                log_event("check", p.id, p.key, "PASS", eleg, rank_for(total_score), time.time()-t0, len(user_expr))
            else:
                print(f"│ 🔴 #{p.id:2d} {p.measure_name:<26s}  WRONG result")
                results.append({"pillar": p.id, "status": "FAIL", "score": 0})
                log_event("check", p.id, p.key, "FAIL", 0, rank_for(total_score), time.time()-t0, len(user_expr))

        rank = rank_for(total_score)
        passed = sum(1 for r in results if r["status"] == "PASS")
        print("├──────────────────────────────────────────────────────────────────")
        print(f"│  Passed       : {passed} / {len(PILLARS)}")
        print(f"│  Total score  : {total_score:.1f}")
        print(f"│  Architect    : {rank}")
        print("└──────────────────────────────────────────────────────────────────")

        if passed == len(PILLARS):
            print()
            print("🎉🎉🎉  ALL 12 PILLARS PASSED  🎉🎉🎉")
            print("       Scroll down to unlock the FINAL CHALLENGE 👇")
        else:
            missing = [r["pillar"] for r in results if r["status"] != "PASS"]
            print()
            print(f"📌 Pillars still to complete: {missing}")
            print("   Go back to Cathedral_Model and fix/add the measures, then re-run check_all().")

        return results

    results = check_all()
    """),

    _md(r"""
    ---
    ## 🏆 Final Challenge — The Calculation Group

    > _Read this section **only** after all 12 pillars are 🟢._

    You just wrote **12 measures**. Look at them: most of them (11 out of 12) are just
    `CALCULATE([Sales Amount Seed], <time-intel function>)`. Different wrappers — **same
    base measure**. That repetition is a smell, and the cure has a name: **Calculation Groups**.

    A calculation group is a single table that **applies a transformation to any measure
    you reference inside it**. Instead of 11 time-intel measures, you write **one base
    measure + 11 calculation items**. (`M_12_DistinctCustomers` stays standalone —
    it's a different aggregation, not a time-intel transformation.) The dashboard then uses something like:

    ```dax
    CALCULATE([Sales Amount Seed], 'Time Intelligence'[Calc] = "YTD")
    ```

    …and the calc item rewrites the measure on the fly.

    ### 📚 Reference
    - **DAX Patterns – Calculation groups** (Marco Russo / Alberto Ferrari):
      <https://www.daxpatterns.com/calculation-groups/>
    - **Microsoft Learn – Calculation groups**:
      <https://learn.microsoft.com/power-bi/transform-model/calculation-groups>

    ### 🛠️ Build it in the web modeler

    1. Open **`Cathedral_Model`** → **Open data model**.
    2. In the ribbon: **Calculation group** (📐 icon in the Calculations group).
    3. Name the calc group **`Time Intelligence`** and the column **`Calc`**.
    4. Add **11 calculation items** with these **exact** names and expressions:

    | Item name           | Expression                                                                  |
    |---------------------|-----------------------------------------------------------------------------|
    | `Current`           | `SELECTEDMEASURE()`                                                         |
    | `LastYear`          | `CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Date'[Date]))`            |
    | `YoY`               | `SELECTEDMEASURE() - CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Date'[Date]))` |
    | `YoYPct`            | `DIVIDE(SELECTEDMEASURE() - CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Date'[Date])), CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Date'[Date])))` |
    | `YTD`               | `CALCULATE(SELECTEDMEASURE(), DATESYTD('Date'[Date]))`                      |
    | `MTD`               | `CALCULATE(SELECTEDMEASURE(), DATESMTD('Date'[Date]))`                      |
    | `QTD`               | `CALCULATE(SELECTEDMEASURE(), DATESQTD('Date'[Date]))`                      |
    | `Rolling12`         | `CALCULATE(SELECTEDMEASURE(), DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -12, MONTH))` |
    | `BestMonth`         | `MAXX(VALUES('Date'[MonthNum]), SELECTEDMEASURE())`                         |
    | `PctOfYear`         | `DIVIDE(SELECTEDMEASURE(), CALCULATE(SELECTEDMEASURE(), ALL('Date')))`      |
    | `AvgDailySales`     | `AVERAGEX(VALUES('Date'[Date]), SELECTEDMEASURE())`                         |

    > ⚠️ **Note**: `M_12_DistinctCustomers` is **not** a time-intelligence transformation —
    > it's a different aggregation on a different column. It stays as a standalone
    > measure on `Sales`. The calc group has **11 items**.

    > 💡 Notice `SELECTEDMEASURE()` — this is the magic. The calc item operates on
    > whatever measure you wrap with `CALCULATE([...], 'Time Intelligence'[Calc] = "...")`.
    > Look at `PctOfYear` — what was 200+ characters with explicit `ALL(...)` columns
    > becomes one tidy `ALL('Date')`. That's the point.

    When you're done, run the cell below.
    """),

    _md("## Step 5 — Verify the Calculation Group"),
    _code_hidden(r"""
    # M_12_DistinctCustomers is NOT a time-intelligence transformation,
    # it stays as a standalone measure. The calc group has 11 items.
    CG_PILLARS = [p for p in PILLARS if p.key != "DistinctCustomers"]
    EXPECTED_ITEMS = [p.key for p in CG_PILLARS]
    CG_TABLE = "Time Intelligence"
    CG_COL   = "Calc"

    def check_calc_group():
        print(f"┌─ 🏆 Calculation Group Check — '{CG_TABLE}'[{CG_COL}] ──────────────")
        # 1) Discover items present
        q = f"EVALUATE VALUES('{CG_TABLE}'[{CG_COL}])"
        try:
            df = fabric.evaluate_dax(dataset=MODEL_NAME, workspace=WORKSPACE_ID, dax_string=q)
        except Exception as e:
            print(f"│ ❌ Calc group not found: {type(e).__name__}: {str(e)[:200]}")
            print(f"│    Make sure the table is named exactly '{CG_TABLE}' with column '{CG_COL}'.")
            print("└─────────────────────────────────────────────────────────────────")
            return

        present = set(df.iloc[:, 0].astype(str).tolist())
        missing = [n for n in EXPECTED_ITEMS if n not in present]
        if missing:
            print(f"│ ⬜ Missing calc items: {missing}")

        # 2) Evaluate each calc item via SELECTEDMEASURE and compare to canonical.
        total_score = 0.0
        passed = 0
        for p in CG_PILLARS:
            if p.key not in present:
                print(f"│ ⬜ #{p.id:2d} {p.key:<22s}  ITEM MISSING")
                continue
            expr = f"CALCULATE({BASE}, '{CG_TABLE}'[{CG_COL}] = \"{p.key}\")"
            all_pass = True
            for ctx in p.contexts:
                exp = run_dax_scalar(p.canonical_dax, list(ctx))
                got = run_dax_scalar(expr, list(ctx))
                if not values_close(got, exp):
                    all_pass = False
                    break
            if all_pass:
                passed += 1
                eleg  = elegance_score(expr)
                score = 50 + eleg * 0.5
                total_score += score
                print(f"│ 🟢 #{p.id:2d} {p.key:<22s}  score={score:5.1f}  elegance={eleg:5.1f}")
                log_event("calcgroup", p.id, p.key, "PASS", eleg, rank_for(total_score), 0.0, len(expr))
            else:
                print(f"│ 🔴 #{p.id:2d} {p.key:<22s}  WRONG result")
                log_event("calcgroup", p.id, p.key, "FAIL", 0, rank_for(total_score), 0.0, len(expr))

        rank = rank_for(total_score)
        print("├──────────────────────────────────────────────────────────────────")
        print(f"│  Passed       : {passed} / {len(CG_PILLARS)}")
        print(f"│  Total score  : {total_score:.1f}  (the elegance kicker!)")
        print(f"│  Architect    : {rank}")
        print("└──────────────────────────────────────────────────────────────────")
        if passed == len(CG_PILLARS):
            print()
            print("🏛️🏛️🏛️  CATHEDRAL BUILT  🏛️🏛️🏛️")
            print(f"       You are now a {rank}.")
            print("       One base measure × one calculation group = 12 KPIs.")
            print("       Welcome to the master path.")

        # Export final state for the badge cell.
        globals()["FINAL_SCORE"]  = int(round(total_score))
        globals()["FINAL_RANK"]   = rank
        globals()["FINAL_PASSED"] = passed
        globals()["FINAL_TOTAL"]  = len(CG_PILLARS)

    check_calc_group()
    """),
    _md("""
    ## 🏅 Step 6 — Claim your shareable badge

    If you built the full Cathedral (all 11 calc items pass), you can mint a
    **signed badge** with your name, rank, and score, and download/share it
    on LinkedIn or Twitter.

    Set your display name in the cell below and run it.
    """),
    _code(r'''
    # ============================================================
    # Cathedral — Badge issuance
    # ------------------------------------------------------------
    # Generates a HMAC-signed URL for maenglar78.github.io/fabric-arcade/badge.html
    # so anyone who opens the link sees the signed badge and can verify it.
    # The page builds the medal SVG dynamically from the token payload.
    # ============================================================

    PLAYER_NAME = "Your Name Here"   # 👈 change me before running

    import json, time, hmac, hashlib, base64
    from IPython.display import display, Markdown, HTML

    # Keep in sync with fabric_arcade/badge.py and website/badge.html
    _BADGE_SECRET = b"fabric-arcade-badge-v1-7K9mP3xQ"
    _BASE_URL     = "https://maenglar78.github.io/fabric-arcade"
    _GAME_ID      = "calc-groups-cathedral"
    _SKILLS       = ["DAX", "Calculation Groups", "Semantic Model"]

    def _b64u(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

    def _issue(game_id, player, rank, score):
        payload = {"v": 1, "g": game_id, "p": str(player),
                   "r": str(rank), "s": int(score), "t": int(time.time()),
                   "k": _SKILLS}
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        sig  = hmac.new(_BADGE_SECRET, body, hashlib.sha256).digest()
        return f"{_BASE_URL}/badge.html?t={_b64u(body)}.{_b64u(sig)}"

    passed = globals().get("FINAL_PASSED", 0)
    total  = globals().get("FINAL_TOTAL", 11)
    score  = globals().get("FINAL_SCORE", 0)
    rank   = globals().get("FINAL_RANK", "Stonemason")

    if passed < total:
        display(Markdown(
            f"### 🚧 Not yet eligible\n\n"
            f"You passed **{passed}/{total}** calc items. "
            f"Finish the Final Challenge (run **Step 5** above) to unlock your badge."
        ))
    elif PLAYER_NAME.strip() in ("", "Your Name Here"):
        display(Markdown(
            "### ✍️ Set your name first\n\n"
            "Edit `PLAYER_NAME` at the top of this cell to the name you want "
            "on the badge (real name, handle, anything you like) and re-run."
        ))
    else:
        url = _issue(_GAME_ID, PLAYER_NAME, rank, score)
        display(Markdown(
            f"### 🏅 Badge minted\n\n"
            f"**{PLAYER_NAME}** — *{rank}* · score **{score}**\n\n"
            f"🔗 **[Open your badge]({url})**\n\n"
            f"Open the link, click *Download PNG* / *Share on LinkedIn*. "
            f"Anyone who opens the URL will see the medal with your name on it "
            f"and the page will verify the signature in their browser."
        ))
        display(HTML(f'<a href="{url}" target="_blank" '
                     f'style="display:inline-block;padding:10px 20px;border-radius:8px;'
                     f'background:linear-gradient(135deg,#6c5ce7,#a29bfe);color:white;'
                     f'text-decoration:none;font-weight:600">🏅 Open my badge page</a>'))
    '''),
]

# =====================================================================
# 4) DASHBOARD NOTEBOOK — minimal placeholder (real implementation in Phase D)
# =====================================================================

DASHBOARD_CELLS = [
    _md(f"""
    # 📊 Cathedral — Personal Journey Dashboard

    > 🏗️ Build: **{BUILD_STAMP}**

    Every time you ran the **Check** notebook, an event was logged to
    `Cathedral_EH.CathedralEvents`. This dashboard reads that history and shows
    **how** you got to the cathedral — not just the final score.

    Click **▶️ Run all** in the toolbar and read the tiles below.
    """),

    _md("## Step 1 — Connect to the telemetry table"),
    _code_hidden(r"""
    import subprocess, sys, importlib
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--upgrade",
                    "--disable-pip-version-check", "PyJWT>=2.6.0", "plotly>=5.18.0"],
                   check=False, capture_output=True)
    import requests, json
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    EH_CLUSTER  = "https://trd-z9b3f5xvzm87f8c2kd.z6.kusto.fabric.microsoft.com"
    EH_DATABASE = "Cathedral_EH"
    EH_TABLE    = "CathedralEvents"

    def _kql_token():
        try:
            import notebookutils
            return notebookutils.credentials.getToken("kusto")
        except Exception:
            pass
        try:
            import mssparkutils
            return mssparkutils.credentials.getToken("kusto")
        except Exception:
            pass
        return None

    def kql(query: str) -> pd.DataFrame:
        tok = _kql_token()
        if not tok:
            raise RuntimeError("Could not acquire Kusto token.")
        r = requests.post(
            f"{EH_CLUSTER}/v2/rest/query",
            headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
            json={"db": EH_DATABASE, "csl": query},
            timeout=30,
        )
        if r.status_code != 200:
            raise RuntimeError(f"KQL HTTP {r.status_code}: {r.text[:600]}")
        for frame in r.json():
            if frame.get("FrameType") == "DataTable" and frame.get("TableKind") == "PrimaryResult":
                cols = [c["ColumnName"] for c in frame["Columns"]]
                return pd.DataFrame(frame["Rows"], columns=cols)
        return pd.DataFrame()

    # Project to friendly snake_case names so the rest of the notebook is readable.
    Q = f'''
    {EH_TABLE}
    | project
        ts          = Timestamp,
        session_id  = SessionId,
        player_id   = PlayerId,
        event_type  = EventType,
        pillar_id   = PillarId,
        pillar_key  = PillarKey,
        pass_fail   = PassFail,
        elegance    = EleganceScore,
        rank        = Rank,
        duration_s  = DurationSeconds
    | order by ts asc
    '''
    df_all = kql(Q)
    if df_all.empty:
        print("⚠️ No telemetry yet. Run the Check notebook first.")
    else:
        df_all["ts"] = pd.to_datetime(df_all["ts"])
        df_all["elegance"] = pd.to_numeric(df_all["elegance"], errors="coerce")
        df_all["pillar_id"] = pd.to_numeric(df_all["pillar_id"], errors="coerce").astype("Int64")
        print(f"✅ Loaded {len(df_all)} events across {df_all['session_id'].nunique()} session(s).")
    """),

    _md("## Step 2 — Where you are now (latest attempt per pillar)"),
    _code_hidden(r"""
    if df_all.empty:
        print("No data.")
    else:
        # For each pillar take the LAST event of type 'check' (the user's most recent grading).
        last_check = (
            df_all[df_all["event_type"] == "check"]
            .sort_values("ts")
            .groupby("pillar_id", as_index=False)
            .tail(1)
            .sort_values("pillar_id")
        )

        passed = (last_check["pass_fail"] == "PASS").sum()
        total  = 12
        rank   = last_check.iloc[-1]["rank"] if not last_check.empty else "Stonemason"

        print(f"🏛️  Pillars passed   : {passed} / {total}")
        print(f"📜  Current rank      : {rank}")
        print(f"🎯  Avg elegance      : {last_check[last_check['pass_fail']=='PASS']['elegance'].mean():.1f}")
        print()

        status_color = {"PASS": "#3CB371", "FAIL": "#E5736A", "MISSING": "#BBBBBB"}
        fig = px.bar(
            last_check,
            x="pillar_id", y="elegance",
            color="pass_fail",
            color_discrete_map=status_color,
            hover_data=["pillar_key", "pass_fail", "elegance"],
            title="Elegance per pillar (latest attempt) — taller = leaner DAX",
            labels={"pillar_id": "Pillar #", "elegance": "Elegance (0-100)"},
        )
        fig.update_yaxes(range=[0, 105])
        fig.update_layout(height=380, showlegend=True, legend_title_text="status")
        fig.show()
    """),

    _md("## Step 3 — Timeline (every attempt, in order)"),
    _code_hidden(r"""
    if df_all.empty:
        print("No data.")
    else:
        df_tl = df_all.copy()
        df_tl["status"] = df_tl["pass_fail"]
        status_color = {"PASS": "#3CB371", "FAIL": "#E5736A", "MISSING": "#BBBBBB"}

        fig = px.scatter(
            df_tl,
            x="ts", y="pillar_id",
            color="status",
            color_discrete_map=status_color,
            symbol="event_type",
            symbol_map={"check": "circle", "calcgroup": "diamond"},
            hover_data=["pillar_key", "elegance", "rank"],
            title="Your attempts over time — circle = measure check, diamond = calc-group check",
            labels={"ts": "Time", "pillar_id": "Pillar #"},
        )
        fig.update_yaxes(dtick=1, range=[0.5, 12.5])
        fig.update_layout(height=420)
        fig.show()

        attempts_per_pillar = (
            df_all[df_all["event_type"] == "check"]
            .groupby("pillar_id").size().rename("attempts").reset_index()
        )
        if (attempts_per_pillar["attempts"] > 1).any():
            grinders = attempts_per_pillar[attempts_per_pillar["attempts"] > 1]
            print("🔁 Pillars you re-tried (= where DAX is hard):")
            for _, row in grinders.iterrows():
                print(f"   #{int(row['pillar_id']):2d}  {int(row['attempts'])} attempts")
    """),

    _md("## Step 4 — The point of the lesson: Measures vs Calculation Group"),
    _code_hidden(r"""
    if df_all.empty:
        print("No data.")
    else:
        last_check_pass = (
            df_all[(df_all["event_type"] == "check") & (df_all["pass_fail"] == "PASS")]
            .sort_values("ts").groupby("pillar_id", as_index=False).tail(1)
            [["pillar_id", "pillar_key", "elegance"]]
            .rename(columns={"elegance": "Measures"})
        )
        last_cg = (
            df_all[(df_all["event_type"] == "calcgroup") & (df_all["pass_fail"] == "PASS")]
            .sort_values("ts").groupby("pillar_id", as_index=False).tail(1)
            [["pillar_id", "elegance"]]
            .rename(columns={"elegance": "CalcGroup"})
        )

        cmp = last_check_pass.merge(last_cg, on="pillar_id", how="left")
        if cmp["CalcGroup"].isna().all():
            print("ℹ️  The Calc Group challenge hasn't been completed yet.")
            print("    Build the 'Time Intelligence' calc group, run check_calc_group(),")
            print("    then re-run this notebook to see the elegance gain.")
        else:
            cmp_long = cmp.melt(
                id_vars=["pillar_id", "pillar_key"],
                value_vars=["Measures", "CalcGroup"],
                var_name="approach", value_name="elegance",
            ).dropna()

            fig = px.bar(
                cmp_long,
                x="pillar_id", y="elegance",
                color="approach", barmode="group",
                color_discrete_map={"Measures": "#7F8FA6", "CalcGroup": "#F6B93B"},
                title="Elegance gain — same KPI, two implementations",
                labels={"pillar_id": "Pillar #", "elegance": "Elegance"},
            )
            fig.update_yaxes(range=[0, 105])
            fig.update_layout(height=380)
            fig.show()

            gain = (cmp["CalcGroup"] - cmp["Measures"]).dropna()
            if len(gain):
                print(f"📈 Average elegance gain : +{gain.mean():.1f} points")
                print(f"🏆 Biggest single gain   : +{gain.max():.1f} points  "
                      f"(pillar #{int(cmp.loc[gain.idxmax(),'pillar_id'])} — "
                      f"{cmp.loc[gain.idxmax(),'pillar_key']})")
    """),

    _md("## Step 5 — Session recap"),
    _code_hidden(r"""
    if df_all.empty:
        print("No data.")
    else:
        last_sid = df_all.sort_values("ts").iloc[-1]["session_id"]
        sdf = df_all[df_all["session_id"] == last_sid].sort_values("ts")
        t0, t1 = sdf["ts"].min(), sdf["ts"].max()
        dur = (t1 - t0).total_seconds()

        print(f"🎮 Session ID     : {last_sid}")
        print(f"🧑 Player         : {sdf.iloc[0]['player_id']}")
        print(f"⏱️  Duration       : {dur/60:.1f} min")
        print(f"📊 Events         : {len(sdf)}  "
              f"(check={ (sdf['event_type']=='check').sum() }, "
              f"calcgroup={ (sdf['event_type']=='calcgroup').sum() })")
        print(f"🏛️  Final rank     : {sdf.iloc[-1]['rank']}")
        print()
        print("Per-pillar recap (latest event of this session):")
        recap = sdf.sort_values("ts").groupby("pillar_id").tail(1)[
            ["pillar_id", "pillar_key", "event_type", "pass_fail", "elegance"]
        ].sort_values("pillar_id").reset_index(drop=True)
        print(recap.to_string(index=False))
    """),
]


def main():
    # One-shot rename of legacy notebooks (in-place, preserves IDs and history).
    from upload_notebook import rename_notebook
    legacy_renames = {
        "CalcGroups_Seed":      "01_Setup",
        "CalcGroups_Cathedral": "02_Quest",
        "CalcGroups_Check":     "03_Check",
        "CalcGroups_Dashboard": "04_Dashboard",
    }
    for old, new in legacy_renames.items():
        try:
            rename_notebook(old, new)
        except Exception as e:
            print(f"  rename skip {old}: {type(e).__name__}: {str(e)[:120]}")

    notebooks = [
        ("01_Setup",      _nb(SEED_CELLS),       "Cathedral — synthetic data + Direct Lake model"),
        ("02_Quest",      _nb(CATHEDRAL_CELLS),  "Cathedral — quest brief (12 pillars)"),
        ("03_Check",      _nb(CHECK_CELLS),      "Cathedral — check & grade + final challenge"),
        ("04_Dashboard",  _nb(DASHBOARD_CELLS),  "Cathedral — personal journey dashboard"),
    ]
    for name, nb, desc in notebooks:
        path = write_nb(name, nb)
        print(f"📓 Built {path}")
        upload_or_update_notebook(path, name, description=desc)


if __name__ == "__main__":
    main()
