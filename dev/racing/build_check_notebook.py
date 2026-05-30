"""
Build catalog/fabric-racing-game/notebooks/race_check.ipynb

Cells:
  1. Markdown intro
  2. CONFIG (PLAYER_NAME, DASHBOARD_URL, KQL cluster & db)
  3. KQL helper (token + kql())
  4. Check 1: at least one completed race for PLAYER_NAME
  5. Check 2: three canonical KQL queries proving data is usable
  6. Self-attest dashboard URL (format validation)
  7. Compute rank + issue signed badge
"""
from __future__ import annotations
import json
from pathlib import Path
from textwrap import dedent

OUT = Path(__file__).resolve().parents[2] / "catalog" / "fabric-racing-game" / "notebooks" / "race_check.ipynb"

NB_META = {
    "kernelspec": {"display_name": "Synapse PySpark", "language": "python", "name": "synapse_pyspark"},
    "language_info": {"name": "python"},
    "microsoft": {"language": "python", "language_group": "synapse_pyspark"},
    "nteract": {"version": "nteract-front-end@1.0.0"},
    "spark_compute": {"compute_id": "/trident/default", "session_options": {"conf": {}}},
    "widgets": {},
}


def md(text: str) -> dict:
    src = dedent(text).strip("\n") + "\n"
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def code(text: str) -> dict:
    src = dedent(text).strip("\n") + "\n"
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }


CELLS = [
    md("""
    # 🏎️ Fabric Racing — Badge Check

    Earn the **Fabric Racing** achievement badge by proving two things:

    1. ✅ You played **at least one full race** (a `LevelComplete` event landed in `GameEvents`).
    2. ✅ You built a **Real-Time Dashboard** on `RaceData` — and we sanity-check that the data
       behind it actually works (three canonical KQL queries must return rows).

    Then paste the URL of your dashboard, run the last cell, and your signed badge appears.

    > Run all cells top → bottom. No need to attach a Lakehouse.
    """),

    md("## ⚙️ Step 0 — Configuration"),

    code("""
    # --- EDIT THESE ---
    PLAYER_NAME = "Mauro"                 # must match the PlayerId you used while racing
    DASHBOARD_URL = "https://app.fabric.microsoft.com/groups/<workspace_id>/dashboards/<dashboard_id>"  # paste your KQL dashboard URL

    # Eventhouse query endpoint (copy from RacingEventhouse > 'Query URI' in Fabric)
    EH_CLUSTER  = "https://trd-XXXXXXXXXX.z6.kusto.fabric.microsoft.com"
    EH_DATABASE = "RaceData"
    EH_TABLE    = "GameEvents"
    # ------------------
    print(f"Player        : {PLAYER_NAME}")
    print(f"KQL cluster   : {EH_CLUSTER}")
    print(f"Database      : {EH_DATABASE}")
    print(f"Dashboard URL : {DASHBOARD_URL}")
    """),

    md("## 🔌 Step 1 — KQL helper (Bearer-token + REST)"),

    code("""
    import requests, pandas as pd

    def _kql_token():
        # Try Fabric notebookutils first, then mssparkutils as fallback.
        try:
            import notebookutils
            return notebookutils.credentials.getToken("kusto")
        except Exception:
            pass
        try:
            return mssparkutils.credentials.getToken("kusto")  # noqa: F821
        except Exception:
            pass
        return None

    def kql(query: str) -> pd.DataFrame:
        tok = _kql_token()
        if not tok:
            raise RuntimeError("Could not acquire Kusto token. Are you running inside Fabric?")
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

    print("✅ KQL helper ready.")
    """),

    md("""
    ## 🏁 Step 2 — Check 1: at least one completed race

    We look for the **`LevelComplete`** event for your `PlayerId` (= `PLAYER_NAME`).
    """),

    code("""
    Q1 = f'''
    {EH_TABLE}
    | where PlayerId =~ "{PLAYER_NAME}"
    | where EventType == "LevelComplete"
    | summarize Races = count(),
                BestScore = max(Score),
                LastPlay = max(Timestamp)
    '''
    df1 = kql(Q1)
    if df1.empty or int(df1.iloc[0]["Races"] or 0) < 1:
        check1_pass = False
        races, best_score, last_play = 0, 0, None
        print("❌ No completed races found for", PLAYER_NAME)
        print("   → Open the Racing_Championship notebook, finish at least one level, then re-run this.")
    else:
        races      = int(df1.iloc[0]["Races"])
        best_score = int(df1.iloc[0]["BestScore"] or 0)
        last_play  = df1.iloc[0]["LastPlay"]
        check1_pass = True
        print(f"✅ Races completed : {races}")
        print(f"🏆 Best score      : {best_score}")
        print(f"🕒 Last play       : {last_play}")
    """),

    md("""
    ## 📊 Step 3 — Check 2: dashboard data is real

    Three canonical KQL queries the dashboard *must* be able to answer. If any returns 0 rows,
    your dashboard is empty / wrong — fix it before claiming the badge.

    | # | Query |
    |---|-------|
    | A | Top 5 players by best score |
    | B | Score per level (your runs) |
    | C | Speed telemetry over time (last 24h, your runs) |
    """),

    code("""
    Q2A = f'''
    {EH_TABLE}
    | where EventType == "LevelComplete"
    | summarize BestScore = max(Score) by PlayerId
    | top 5 by BestScore desc
    '''
    Q2B = f'''
    {EH_TABLE}
    | where PlayerId =~ "{PLAYER_NAME}"
    | where EventType == "LevelComplete"
    | summarize BestScore = max(Score) by Level
    | order by Level asc
    '''
    Q2C = f'''
    {EH_TABLE}
    | where PlayerId =~ "{PLAYER_NAME}"
    | where Timestamp > ago(24h)
    | where EventType == "Telemetry"
    | summarize AvgSpeed = avg(Speed) by bin(Timestamp, 1m)
    | order by Timestamp asc
    '''

    results = {}
    for label, q in [("A · top5_players", Q2A), ("B · level_scores", Q2B), ("C · speed_timeline", Q2C)]:
        try:
            df = kql(q)
            results[label] = len(df)
        except Exception as e:
            results[label] = f"ERROR: {e}"

    check2_pass = all(isinstance(v, int) and v > 0 for v in results.values())
    for k, v in results.items():
        ok = isinstance(v, int) and v > 0
        print(f"{'✅' if ok else '❌'} {k:25s} → {v} rows")

    if not check2_pass:
        print("\\n⚠️ Some queries returned no rows. Likely causes:")
        print("   • You haven't completed any level yet (re-run after a race).")
        print("   • Eventstream is not publishing to GameEvents.")
        print("   • PLAYER_NAME differs from the PlayerId you used in the game.")
    """),

    md("""
    ## 🔗 Step 4 — Self-attest your dashboard

    The badge embeds a link to *your* dashboard so anyone can see it. We only check the URL
    looks like a Fabric dashboard URL — the actual link is your word.
    """),

    code("""
    import re
    dash_ok = bool(re.match(r"^https://app\\.fabric\\.microsoft\\.com/.+", DASHBOARD_URL or ""))
    if not dash_ok:
        print("❌ DASHBOARD_URL doesn't look like a Fabric dashboard URL.")
        print("   Paste the URL from your browser when viewing the KQL dashboard.")
    else:
        print(f"✅ Dashboard URL accepted: {DASHBOARD_URL}")
    """),

    md("""
    ## 🏅 Step 5 — Issue your signed badge

    All three gates must pass:
    - **Race completed** ✅
    - **Dashboard queries return data** ✅
    - **Dashboard URL provided** ✅

    Rank is computed from your best score:

    | Rank | Threshold (best score) |
    |---|---|
    | 🥉 Rookie Driver        | any race finished |
    | 🥈 Podium Finisher      | ≥ 1 500 |
    | 🥇 Pole Position        | ≥ 3 000 |
    | 🏆 Champion             | ≥ 5 000 (boss level cleared) |
    """),

    code("""
    def _rank(best: int) -> str:
        if best >= 5000: return "Champion"
        if best >= 3000: return "Pole Position"
        if best >= 1500: return "Podium Finisher"
        return "Rookie Driver"

    all_pass = check1_pass and check2_pass and dash_ok
    if not all_pass:
        print("🚫 Badge NOT issued — fix the failing checks above and re-run.")
    else:
        rank = _rank(best_score)
        try:
            from fabric_arcade import issue_badge
        except ImportError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "fabric-arcade"], check=False)
            from fabric_arcade import issue_badge

        badge = issue_badge(
            game_id="fabric-racing-game",
            player=PLAYER_NAME,
            rank=rank,
            score=best_score,
            base_url="https://maenglar78.github.io/fabric-arcade",
            skills=["Eventhouse", "KQL", "Real-Time Dashboard"],
        )
        print(f"🏆 Rank   : {rank}")
        print(f"🔗 Badge  : {badge.url}")
        print()
        print("Open the URL above to download the PNG / SVG and share on LinkedIn.")
        try:
            from IPython.display import Markdown, display
            display(Markdown(badge.share_block()))
        except Exception:
            pass
    """),
]


nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": NB_META, "cells": CELLS}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print(f"✅ Wrote {OUT}")
