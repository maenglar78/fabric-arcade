# Contributing to Fabric Arcade 🎮

Thank you for wanting to contribute to Fabric Arcade! This document explains how to create new games for the catalog.

## 🎯 Types of Contributions

### 1. New Game
Create a new gamified project to learn Fabric.

### 2. Improve Existing Game
Add features, fix bugs, or improve documentation.

### 3. Translation
Translate games into other languages.

## 🎮 Creating a New Game

### Step 1: Choose the Type

| Type | Duration | Complexity | Ideal for |
|------|----------|------------|-----------|
| **Mission** | 30-60 min | Multi-workload | Complete end-to-end scenarios |
| **Challenge** | 15-30 min | Single workload | Focus on specific skills |
| **Arcade** | 5-15 min | Beginner | Quick and fun demos |

### Step 2: Define the Story

Every game must have:
- **Engaging theme**: Space, sports, fantasy, simulation...
- **Clear objective**: What does the user build?
- **Progression**: Chapters/levels with increasing difficulty
- **Achievements**: Badges to motivate completion

### Step 3: Folder Structure

```
catalog/
└── my-game-name/
    ├── manifest.json      # Required metadata
    ├── README.md          # Game documentation
    ├── architecture.svg   # Architecture diagram
    ├── notebooks/
    │   ├── 01_setup.py
    │   ├── 02_main.py
    │   └── 03_analysis.py
    ├── definitions/       # Fabric item definitions (optional)
    │   ├── eventhouse.json
    │   └── eventstream.json
    ├── data/
    │   └── sample_data.json
    └── assets/
        └── game_icon.png
```

### Step 4: Create the manifest.json

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

### Step 5: Write the Documentation

The README.md must include:

1. **Title and Badges** - Name, difficulty, duration, workload
2. **Story/Briefing** - The narrative context
3. **Learning Objectives** - What they will learn
4. **Prerequisites** - Technical requirements
5. **Quick Start** - How to install and launch
6. **Detailed Chapters** - Step-by-step guides with code
7. **Achievements** - Earnable badges
8. **Architecture** - ASCII or SVG diagram
9. **Resources** - Links to Fabric documentation

### Step 6: Create the Notebooks

Guidelines for notebooks:
- Use magic cells `%md` for explanations
- Include sample output where possible
- Add emojis to make it visually appealing
- Test on Fabric before committing

## 📋 Pre-Submit Checklist

- [ ] Valid manifest.json
- [ ] Complete README.md
- [ ] All notebooks tested on Fabric
- [ ] No hardcoded credentials
- [ ] Achievements defined
- [ ] Architecture diagram included

## 🔍 Code Review

Your PR will be reviewed for:
- Technical correctness
- Narrative quality
- Documentation completeness
- Functional tests

## 📜 License

By contributing you agree that your code will be released under the MIT license.

---

**Questions?** Open an Issue or contact us on Discord!

*"Every game makes Fabric more fun to learn!"* 🎮
