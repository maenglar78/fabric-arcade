# 🎮 Getting Started with Fabric Arcade

Benvenuto in Fabric Arcade! Questa guida ti aiuterà a iniziare in pochi minuti.

## 🚀 Installazione

### Opzione 1: pip install (consigliato)

```bash
pip install fabric-arcade
```

### Opzione 2: Da sorgente

```bash
git clone https://github.com/fabricarcade/fabric-arcade.git
cd fabric-arcade
pip install -e .
```

## 📋 Prerequisiti

1. **Microsoft Fabric workspace** con capacità F2+ (alcuni giochi richiedono F4+)
2. **Azure CLI** installato e autenticato:
   ```bash
   az login
   ```
3. **Python 3.9+**

## 🎯 Il Tuo Primo Gioco

### Step 1: Importa la libreria

```python
import fabric_arcade as arcade
```

### Step 2: Esplora il catalogo

```python
# Vedi tutti i giochi disponibili
arcade.list()

# Filtra per workload
from fabric_arcade.core import Workload
arcade.list(workload=Workload.RTI)  # Solo Real-Time Intelligence

# Filtra per difficoltà
from fabric_arcade.core import Difficulty
arcade.list(difficulty=Difficulty.BEGINNER)  # Solo per principianti
```

Output esempio:
```
🎮 FABRIC ARCADE - Game Catalog
================================================================================
Icon Game                           Type         Workloads       Diff   Time    
--------------------------------------------------------------------------------
🚀   Mission Artemis                mission      RTI+DE          ⭐⭐⭐   45 min
🏎️   Race Analytics                 mission      RTI+PBI         ⭐⭐    30 min
⚽   Sports Tracker                 challenge    RTI+DS          ⭐⭐    25 min
🏰   Quest Data Pipeline            mission      DE+DF           ⭐⭐⭐   40 min
🎰   Retro Arcade Dashboard         arcade       PBI             ⭐      10 min
...
--------------------------------------------------------------------------------
Total: 10 games available
```

### Step 3: Installa un gioco

```python
# Scegli un gioco adatto al tuo livello
# Per principianti: retro-arcade o target-practice
# Per intermedi: fabric-racing-game o sports-tracker
# Per avanzati: mission-artemis-2 o city-builder

arcade.install("fabric-racing-game")
```

Questo creerà automaticamente nel tuo workspace Fabric:
- Eventhouse e KQL Database
- Eventstream configurato
- Notebook con il simulatore
- Dashboard di base

### Step 4: Gioca!

```python
arcade.play("fabric-racing-game")
```

Questo aprirà il notebook principale con le istruzioni del gioco.

## 🗺️ Scegliere il Gioco Giusto

### Per Principianti (< 15 min)
| Gioco | Impari |
|-------|--------|
| 🎰 Retro Arcade | Power BI basics |
| 🎯 Target Practice | Eventstream + Eventhouse basics |

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
