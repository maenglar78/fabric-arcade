# 🎮 Fabric Arcade

> **Learn Microsoft Fabric by Playing** - A gamified catalog of projects to learn Real-Time Intelligence, Data Engineering, Power BI and Data Science through fun experiences.

[![PyPI version](https://img.shields.io/pypi/v/fabric-arcade?color=blue)](https://pypi.org/project/fabric-arcade/)
[![Python](https://img.shields.io/pypi/pyversions/fabric-arcade)](https://pypi.org/project/fabric-arcade/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start (Fabric Notebook)

**Just 3 lines of code** to install a complete learning environment in your Fabric workspace!

```python
# Cell 1 - Install the package
%pip install -q fabric-arcade
```

```python
# Cell 2 - Import and explore
from fabric_arcade import arcade

# List all available games
arcade.list()
```

```python
# Cell 3 - Install a game in your current workspace!
arcade.install("fabric-racing-game")
```

That's it! The game assets (Eventhouse, KQL Database, tables, notebooks) are automatically created in your workspace.

---

## 🎯 What You Learn

Instead of boring technical tutorials, you learn by building:

| Game | You Learn | Workloads |
|------|-----------|-----------|
| 🏎️ **Fabric Racing Game** | Custom Endpoints, JSON mapping, streaming dashboards | RTI |
| 🏛️ **Calc Groups Cathedral** | Calculation Groups on Direct Lake semantic models | PBI |
| 🏙️ **City Builder** | Warehouse modeling & medallion analytics | DW, DE |
| 🕵️ **Ontology Detective** | Digital Twin Builder ontologies & relationships | RTI |
| 🧙‍♂️ **Monster Breach** | Pipelines, Dataflows & real-time defense | DE, DF, RTI |

---

## 📋 Requirements

| Requirement | Detail |
|-------------|--------|
| **Fabric Capacity** | F2 or higher (trial works!) |
| **Workspace** | Any workspace where you have Contributor access |

No local installation needed - everything runs inside Fabric notebooks!

---

## 🎮 API Reference

### `arcade.list()`
Display all available games with their difficulty and duration.

### `arcade.info(game_id)`
Show detailed information about a specific game.

```python
arcade.info("fabric-racing-game")
```

### `arcade.install(game_id, workspace_id=None)`
Install a game in a workspace. If `workspace_id` is not provided, uses the current notebook's workspace.

```python
# Install in current workspace
arcade.install("fabric-racing-game")

# Install in a specific workspace
arcade.install("fabric-racing-game", workspace_id="your-workspace-guid")
```

---

## 🎲 Game Catalog

| Game | Type | Difficulty | Duration | Status |
|------|------|------------|----------|--------|
| 🏎️ Fabric Racing Game | Mission | ⭐⭐ | 30 min | ✅ Available |
| 🏛️ Calc Groups Cathedral | Puzzle | ⭐⭐⭐ | 60 min | ✅ Available |
| 🏙️ City Builder | Mission | ⭐⭐⭐ | 50 min | ✅ Available |
| 🕵️ Ontology Detective | Mission | ⭐⭐⭐ | 45 min | ✅ Available |
| 🧙‍♂️ Monster Breach | Quest | ⭐⭐⭐ | 60 min | ✅ Available |
| 🕹️ Retro Arcade | Arcade | ⭐⭐ | 45 min | ✅ Available |
| 🔮 Oracle's Forge | Mission | ⭐⭐⭐⭐ | 75 min | 🔜 Coming Soon |
| 🛡️ Sentinel Grid | Mission | ⭐⭐⭐ | — | 🔜 Coming Soon |
| 🧪 Purity Protocol | Challenge | ⭐⭐⭐ | — | 🔜 Coming Soon |
| 🌀 Portal Nexus | Mission | ⭐⭐⭐ | — | 🔜 Coming Soon |
| 🔐 Vault Keeper | Mission | ⭐⭐⭐ | 45 min | 🔜 Coming Soon |
| 🦁 The Sphinx | Challenge | ⭐⭐⭐ | 40 min | 🔜 Coming Soon |

**Workload Legend:**
- **RTI** = Real-Time Intelligence (Eventstream, Eventhouse, KQL)
- **DE** = Data Engineering (Spark, Lakehouse, Notebooks)
- **DS** = Data Science (ML Models, Predictions)
- **DF** = Data Factory (Pipelines, Dataflows)
- **PBI** = Power BI (Reports, Dashboards)

---

## 🛠️ Local Development (CLI)

For contributors or local testing:

```bash
# Clone and install
git clone https://github.com/maenglar78/fabric-arcade.git
cd fabric-arcade
pip install -e .

# Login to Azure
az login

# Use CLI
arcade list
arcade install fabric-racing-game -w "My Workspace"
```

---

## 🤝 Contributing

Want to create a new game? See [CONTRIBUTING.md](CONTRIBUTING.md).

### Project Structure
```
catalog/
└── my-new-game/
    ├── manifest.json       # Game metadata
    ├── notebooks/          # Fabric notebooks
    ├── schemas/            # KQL table schemas
    └── eventstream/        # Eventstream definitions
```

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Made with ❤️ for the Fabric Community**

*"Data is more fun when you're playing with it!"*
