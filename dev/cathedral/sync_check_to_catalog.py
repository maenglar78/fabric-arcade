"""
Rebuild 03_Check.ipynb from build_and_upload_notebooks.CHECK_CELLS
and write it into the catalog (no Fabric upload).

Use this whenever you tweak the Cathedral check cells and need the
installable catalog copy refreshed.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

# Importing pulls in CHECK_CELLS and the _nb() helper.
import build_and_upload_notebooks as bld  # noqa: E402

CATALOG = HERE.parent.parent / "catalog" / "calc-groups-cathedral" / "notebooks" / "03_Check.ipynb"

nb = bld._nb(bld.CHECK_CELLS)
CATALOG.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print(f"OK wrote {CATALOG}")
