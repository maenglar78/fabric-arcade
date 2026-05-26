# 🎮 Fabric Arcade

> **Learn Microsoft Fabric by Playing** - Un catalogo di progetti gamificati per imparare Real-Time Intelligence, Data Engineering, Power BI e Data Science in modo divertente.

<!-- Badges -->
[![CI](https://github.com/fabricarcade/fabric-arcade/actions/workflows/ci.yml/badge.svg)](https://github.com/fabricarcade/fabric-arcade/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/fabric-arcade?color=blue)](https://pypi.org/project/fabric-arcade/)
[![Python](https://img.shields.io/pypi/pyversions/fabric-arcade)](https://pypi.org/project/fabric-arcade/)
[![Downloads](https://img.shields.io/pypi/dm/fabric-arcade)](https://pypi.org/project/fabric-arcade/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

<p align="center">
  <a href="https://fabricarcade.github.io/fabric-arcade/">🌐 Website</a> •
  <a href="https://fabricarcade.github.io/fabric-arcade/docs/">📚 Docs</a> •
  <a href="#-quick-start">🚀 Quick Start</a> •
  <a href="#-game-catalog">🎮 Games</a> •
  <a href="CONTRIBUTING.md">🤝 Contribute</a>
</p>

---

## 🎯 La nostra missione

Trasformare l'apprendimento di Microsoft Fabric in un'esperienza **coinvolgente e divertente**. Invece di noiosi tutorial tecnici, impari costruendo:

- 🚀 **Missioni spaziali** con telemetria real-time e video sincronizzato
- 🏎️ **Gare automobilistiche** HTML5 multiplayer con streaming di dati
- ⚽ **Analytics sportive** in tempo reale con ML predictions
- 🏰 **Avventure fantasy** con Medallion Architecture
- 🎰 **Giochi arcade** con dashboard interattive

## 🕹️ Quick Start

```bash
# Install
pip install fabric-arcade

# Login to Azure (required for Fabric API)
az login
```

```python
import fabric_arcade as arcade

# Sfoglia i giochi disponibili
arcade.list_games()

# Installa un gioco nel tuo workspace
arcade.install("mission-artemis-2")

# Inizia a giocare!
arcade.play("mission-artemis-2")
```

## 📋 Requirements

| Requisito | Dettaglio |
|-----------|-----------|
| Python | 3.9+ |
| Fabric Capacity | F2 o superiore |
| Azure CLI | Loggato (`az login`) |

## 📚 Tipi di Esperienze

### 🚀 Missioni (Mission)
Progetti completi end-to-end che simulano scenari reali attraverso metafore gaming.
- **Durata**: 30-60 minuti
- **Complessità**: Intermedio/Avanzato
- **Esempio**: Mission Artemis 2 - Missione lunare con 4 astronauti e video sincronizzato

### 🏁 Sfide (Challenge)
Mini-progetti focalizzati su un singolo workload o pattern.
- **Durata**: 15-30 minuti
- **Complessità**: Beginner/Intermedio
- **Esempio**: Sports Tracker - Analytics sportive con ML predictions

### 🎮 Demo (Arcade)
Esperienze leggere e veloci per mostrare capacità specifiche.
- **Durata**: 5-15 minuti
- **Complessità**: Beginner
- **Esempio**: Retro Dashboard - Dashboard in stile anni '80 con dati streaming

## 🎲 Catalogo Giochi

| Gioco | Tipo | Workload | Difficoltà | Tempo |
|-------|------|----------|------------|-------|
| 🚀 [Mission Artemis 2](catalog/mission-artemis/) | Mission | RTI + DE | ⭐⭐⭐ | 45 min |
| 🏎️ [Fabric Racing Game](catalog/race-analytics/) | Mission | RTI | ⭐⭐ | 30 min |
| ⚽ [Sports Tracker](catalog/sports-tracker/) | Challenge | RTI + DS | ⭐⭐ | 25 min |
| 🏰 [Quest Data Pipeline](catalog/quest-pipeline/) | Mission | DE + DF | ⭐⭐⭐ | 40 min |
| 🎰 [Retro Arcade Dashboard](catalog/retro-arcade/) | Arcade | PBI | ⭐ | 10 min |
| 🌊 [Ocean Explorer](catalog/ocean-explorer/) | Mission | DS + RTI | ⭐⭐⭐ | 50 min |
| 🎯 [Target Practice](catalog/target-practice/) | Challenge | RTI | ⭐ | 15 min |
| 🏙️ [City Builder Analytics](catalog/city-builder/) | Mission | DE + DW | ⭐⭐⭐ | 60 min |
| 🧙 [Wizard's Workshop](catalog/wizard-workshop/) | Challenge | DS | ⭐⭐ | 20 min |
| 🚂 [Train Dispatch](catalog/train-dispatch/) | Arcade | RTI | ⭐⭐ | 15 min |

**Legenda Workload:**
- **RTI** = Real-Time Intelligence (Eventstream, Eventhouse, Real-Time Dashboard)
- **DE** = Data Engineering (Spark, Lakehouse, Notebooks)
- **PBI** = Power BI (Reports, Semantic Models)
- **DS** = Data Science (ML Models, Experiments)
- **DF** = Data Factory (Pipelines, Dataflows)
- **DW** = Data Warehouse

## 🏆 Gamification Features

### 🎖️ Achievement System
Guadagna badge completando obiettivi:
- **First Launch** 🚀 - Completa il tuo primo progetto
- **Speed Demon** ⚡ - Completa una challenge in meno di 10 minuti
- **Data Wizard** 🧙 - Usa tutti i workload Fabric
- **Real-Time Master** ⏱️ - Processa 1 milione di eventi
- **Pipeline Architect** 🏗️ - Costruisci una pipeline medallion completa

### 📊 Leaderboard
Competi con la community su:
- Tempo di completamento
- Efficienza delle query
- Creatività delle soluzioni

### 🎯 Daily Challenges
Ogni giorno una nuova micro-sfida per mantenere le skill affilate.

## 🛠️ Per Contributor

Vuoi creare un nuovo gioco? Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per le linee guida.

### Template Progetto
```
catalog/
└── my-new-game/
    ├── README.md           # Descrizione e obiettivi
    ├── architecture.svg    # Diagramma architettura
    ├── manifest.json       # Metadata progetto
    ├── notebooks/          # Notebook Fabric
    ├── pipelines/          # Pipeline definitions
    ├── data/               # Sample data generators
    └── assets/             # Immagini, icone, etc.
```

## 📖 Documentazione

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
- [Game Design Guide](docs/game-design-guide.md)
- [Contributing](CONTRIBUTING.md)

## 🤝 Community

- [Discord](https://discord.gg/fabricarcade)
- [GitHub Discussions](https://github.com/fabricarcade/discussions)
- [Twitter @FabricArcade](https://twitter.com/FabricArcade)

## 📜 License

MIT License - vedi [LICENSE](LICENSE) per dettagli.

---

**Made with ❤️ by the Fabric Gaming Community**

*"Data is more fun when you're playing with it!"*
