# 🚀 Getting Started with Fabric Arcade

Welcome to Fabric Arcade! This guide will help you install your first game and start learning Microsoft Fabric through play.

---

## What is Fabric Arcade?

Fabric Arcade is a collection of **gamified learning experiences** for Microsoft Fabric. Instead of reading documentation, you learn by:

- 🏎️ Racing cars while streaming telemetry to Eventhouse
- 🚀 Monitoring astronaut vitals during a lunar mission
- ⚽ Predicting sports outcomes with ML models
- 🏰 Building data pipelines as fantasy quests

Each game automatically deploys real Fabric items (Eventhouses, Eventstreams, Notebooks, etc.) to your workspace.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Fabric Workspace** | Any workspace where you have Contributor access |
| **Fabric Capacity** | F2 or higher (Trial capacity works for most games!) |

That's it! No local installation needed.

---

## Quick Start (3 Steps)

### Step 1: Open a Fabric Notebook

Create a new notebook in your Fabric workspace or use an existing one.

### Step 2: Install the Package

Run this in the first cell:

```python
%pip install -q fabric-arcade
```

Wait for the installation to complete. The kernel will restart automatically.

### Step 3: Install a Game!

Run this in the next cell:

```python
from fabric_arcade import arcade

# See what's available
arcade.list()

# Install your first game
arcade.install("fabric-racing-game")
```

🎉 **That's it!** The game is now deployed to your workspace.

---

## What Happens When You Install a Game?

When you run `arcade.install("game-id")`, the following happens automatically:

1. ✅ **Eventhouse** is created (if the game uses Real-Time Intelligence)
2. ✅ **KQL Database** is created with proper schemas
3. ✅ **Tables** are created with correct column types
4. ✅ **Eventstream** is created for data ingestion
5. ✅ **Notebooks** are deployed with game code and dashboards

All items are created in your current workspace with proper naming and relationships.

---

## Available Commands

### `arcade.list()`

Display all available games with their difficulty and estimated time.

```python
arcade.list()
```

Output:
```
🎮 Fabric Arcade - Available Games
──────────────────────────────────
🏎️ Fabric Racing Game  ⭐⭐   RTI  30 min  ✅ Available
🚀 Mission Artemis 2   ⭐⭐⭐  RTI  45 min  ✅ Available
⚽ Sports Tracker      ⭐⭐   RTI  25 min  🔜 Coming Soon
```

### `arcade.info(game_id)`

Get detailed information about a specific game.

```python
arcade.info("fabric-racing-game")
```

### `arcade.install(game_id)`

Install a game in your current workspace.

```python
arcade.install("fabric-racing-game")
```

### `arcade.install(game_id, workspace_id="...")`

Install a game in a specific workspace (if different from current).

```python
arcade.install("fabric-racing-game", workspace_id="your-workspace-guid")
```

---

## After Installation

Once a game is installed:

1. **Refresh your workspace** - New items should appear
2. **Open the main notebook** - Usually named after the game
3. **Run all cells** - Follow the instructions in the notebook
4. **Have fun learning!** - Each game teaches specific Fabric concepts

---

## Choosing the Right Game

### For Beginners (< 20 min)

| Game | You'll Learn |
|------|--------------|
| 🎯 Target Practice | Eventstream → Eventhouse basics |

### For Intermediate Users (20-35 min)

| Game | You'll Learn |
|------|--------------|
| 🏎️ Fabric Racing Game | Custom Endpoints, JSON mapping, Real-Time dashboards |
| ⚽ Sports Tracker | ML predictions on streaming data |

### For Advanced Users (35+ min)

| Game | You'll Learn |
|------|--------------|
| 🚀 Mission Artemis 2 | Multi-table streaming, IoT telemetry, complex KQL |
| 🏰 Quest Data Pipeline | Medallion architecture, Data Factory pipelines |

---

## Troubleshooting

### "Package not found" error
Make sure you're running in a Fabric notebook (not local Python):
```python
%pip install -q fabric-arcade
```

### "Workspace not found" error
The arcade uses your current notebook's workspace. Make sure you have Contributor permissions.

### Items not appearing after install
- Wait 30-60 seconds for creation to complete
- Refresh your workspace view in the browser
- Check the notebook output for any error messages

### Game requires higher capacity
Some advanced games require F4+ capacity. Check the game requirements in the catalog.

---

## Getting Help

- 📚 **Documentation:** [Browse the Catalog](catalog/index.md)
- 🐛 **Issues:** [GitHub Issues](https://github.com/maenglar78/fabric-arcade/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/maenglar78/fabric-arcade/discussions)

---

## Next Steps

1. **[Browse the Game Catalog](catalog/index.md)** - Find a game that interests you
2. **[Fabric Racing Game](catalog/fabric-racing-game.md)** - Great first game for beginners
3. **[Mission Artemis 2](catalog/mission-artemis-2.md)** - Advanced multi-stream architecture

---

*Happy Learning! 🎮*

### Per Intermedi (15-30 min)
| Gioco | Impari |
|-------|--------|
| 🏎️ Race Analytics | RTI completo + Power BI |
| ⚽ Sports Tracker | RTI + Data Science/ML |
| 🧙 Wizard's Workshop | Data Science patterns |
| 🚂 Train Dispatch | Streaming optimization |

### Per Avanzati (30-60 min)
| Gioco | Impari |
|-------|--------|
| 🚀 Mission Artemis | RTI completo + anomaly detection |
| 🏰 Quest Pipeline | Medallion architecture |
| 🏙️ City Builder | Data Warehouse star schema |
| 🌊 Ocean Explorer | RTI + ML avanzato |

## 🏆 Sistema Achievement

Ogni gioco ha achievement che puoi sbloccare:

```python
# Vedi i tuoi achievement
arcade.achievements()

# Output:
# 🏆 Your Achievements
# ========================================
# 🚀 First Launch - Completed your first project
# ⏱️ Real-Time Rookie - Processed 10,000 events
#
# Progress: 2/10 games completed
# Total play time: 1h 15m
```

## ❓ FAQ

### Il gioco non si installa
Verifica di essere autenticato con Azure:
```bash
az account show
```

Se non sei autenticato:
```bash
az login
```

### Non ho abbastanza capacità
Alcuni giochi richiedono F4+ per Spark. Prova prima i giochi con tag `RTI` o `PBI` che funzionano con F2.

### Posso modificare i giochi?
Assolutamente! Dopo l'installazione, tutti gli item sono nel tuo workspace. Modifica, sperimenta, impara!

### Come contribuisco un nuovo gioco?
Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per le linee guida.

## 🔗 Risorse

- [Documentazione Fabric](https://learn.microsoft.com/fabric/)
- [GitHub Repository](https://github.com/fabricarcade/fabric-arcade)
- [Discord Community](https://discord.gg/fabricarcade)

---

**Pronto a giocare?** Inizia con `arcade.list()` e scegli la tua avventura! 🎮
