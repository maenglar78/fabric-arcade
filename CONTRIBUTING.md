# Contributing to Fabric Arcade 🎮

Grazie per voler contribuire a Fabric Arcade! Questo documento spiega come creare nuovi giochi per il catalogo.

## 🎯 Tipi di Contributi

### 1. Nuovo Gioco
Crea un nuovo progetto gamificato per imparare Fabric.

### 2. Miglioramento Gioco Esistente
Aggiungi feature, correggi bug, o migliora la documentazione.

### 3. Traduzione
Traduci i giochi in altre lingue.

## 🎮 Creare un Nuovo Gioco

### Step 1: Scegli il Tipo

| Tipo | Durata | Complessità | Ideale per |
|------|--------|-------------|------------|
| **Mission** | 30-60 min | Multi-workload | Scenari completi end-to-end |
| **Challenge** | 15-30 min | Singolo workload | Focus su skill specifiche |
| **Arcade** | 5-15 min | Beginner | Demo rapide e divertenti |

### Step 2: Definisci la Storia

Ogni gioco deve avere:
- **Tema accattivante**: Spazio, sport, fantasy, simulazione...
- **Obiettivo chiaro**: Cosa costruisce l'utente?
- **Progressione**: Capitoli/livelli con difficoltà crescente
- **Achievement**: Badge per motivare il completamento

### Step 3: Struttura Cartelle

```
catalog/
└── my-game-name/
    ├── manifest.json      # Metadata obbligatorio
    ├── README.md          # Documentazione gioco
    ├── architecture.svg   # Diagramma architettura
    ├── notebooks/
    │   ├── 01_setup.py
    │   ├── 02_main.py
    │   └── 03_analysis.py
    ├── definitions/       # Fabric item definitions (opzionale)
    │   ├── eventhouse.json
    │   └── eventstream.json
    ├── data/
    │   └── sample_data.json
    └── assets/
        └── game_icon.png
```

### Step 4: Crea il manifest.json

```json
{
    "$schema": "https://arcade.fabric.example.com/schemas/game-manifest-v1.json",
    "id": "my-game-name",
    "name": "My Game Name",
    "version": "1.0.0",
    "description": "Brief description of what players will learn and build",
    "type": "mission|challenge|arcade",
    "workloads": ["RTI", "DE", "PBI", "DS", "DF", "DW"],
    "difficulty": 1-3,
    "duration_minutes": 15-60,
    "icon": "🎮",
    "tags": ["tag1", "tag2"],
    "prerequisites": {
        "fabric_capacity": "F2",
        "python_packages": [],
        "skills": []
    },
    "learning_objectives": [
        "Objective 1",
        "Objective 2"
    ],
    "achievements": [
        {
            "id": "achievement-id",
            "name": "Achievement Name",
            "description": "How to earn it",
            "icon": "🏆"
        }
    ],
    "items": [
        {
            "type": "Eventhouse|Eventstream|Notebook|etc",
            "name": "item-name",
            "description": "What this item does"
        }
    ],
    "story": {
        "intro": "The narrative hook",
        "chapters": [
            {
                "title": "Chapter 1",
                "description": "What happens in this chapter"
            }
        ]
    }
}
```

### Step 5: Scrivi la Documentazione

Il README.md deve includere:

1. **Titolo e Badge** - Nome, difficoltà, durata, workload
2. **Storia/Briefing** - Il contesto narrativo
3. **Learning Objectives** - Cosa impareranno
4. **Prerequisites** - Requisiti tecnici
5. **Quick Start** - Come installare e avviare
6. **Capitoli Dettagliati** - Guide step-by-step con codice
7. **Achievement** - Badge guadagnabili
8. **Architettura** - Diagramma ASCII o SVG
9. **Risorse** - Link a documentazione Fabric

### Step 6: Crea i Notebook

Linee guida per i notebook:
- Usa celle magic `%md` per spiegazioni
- Includi output di esempio dove possibile
- Aggiungi emoji per rendere visivamente accattivante
- Testa su Fabric prima di committare

## 📋 Checklist Pre-Submit

- [ ] manifest.json valido
- [ ] README.md completo
- [ ] Tutti i notebook testati su Fabric
- [ ] Nessuna credenziale hardcoded
- [ ] Achievement definiti
- [ ] Diagramma architettura incluso

## 🔍 Code Review

Il tuo PR sarà revisionato per:
- Correttezza tecnica
- Qualità della narrazione
- Completezza della documentazione
- Test funzionali

## 📜 Licenza

Contribuendo accetti che il tuo codice sia rilasciato sotto licenza MIT.

---

**Domande?** Apri una Issue o contattaci su Discord!

*"Every game makes Fabric more fun to learn!"* 🎮
