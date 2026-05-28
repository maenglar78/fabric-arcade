# 🕵️ Ontology Detective — Scaffold (Locked Design)

> **Status:** 🚧 Scaffold only. Notebooks contain placeholder cells. Ontology is pre-created empty (intentional — the Detective builds it case by case).

## 🎮 Game design

You are **Detective Sherlock Graph** at **Datapolis P.I.** Tone is **noir** — rainy streets, hard-boiled monologues, smoky offices. Each of 10 cases is solved by:

1. Designing the right **entity types + relationships** in the Fabric Ontology
2. Ingesting case evidence into ontology instances (ready-cell)
3. Writing a **KQL semantic query** that uniquely identifies the culprit
4. Calling `detective.accuse(name)` — judge decrypts the case solution and validates

### Locked design decisions

| Question | Decision |
|---|---|
| Ingestion of case files | **Ready-to-run cell** — player doesn't write ETL, focus is on reasoning |
| Query language | **KQL** over the ontology event store |
| Case solutions | **Encrypted** `solution.json.enc` per case (key = `SHA256(player_id || case_id || workspace_id)`) |
| Boss federation model | **Single ontology** with 3 sub-namespaces (Bank/Police/Telecom) — not 3 separate ontologies |
| Tone | **Noir** — gritty detective fiction |

## 📦 What `arcade.install("ontology-detective")` deploys

- **Lakehouse `Datapolis_DetectiveLH`** — 10 case folders with CSVs + `solution.json.enc`
- **Ontology `DetectiveOntology`** — **empty**, player builds it
- **Eventhouse `Datapolis_DetectiveEH`** + KQL DB `DetectiveData` + table `DetectiveEvents`
- **3 Notebooks**: `OntologyDetective_Seed`, `OntologyDetective_CaseFile`, `OntologyDetective_Dashboard`

## 🗺️ 10 cases → ontology concepts

| # | Case | Concept |
|---|---|---|
| 1 | 🧁 The Stolen Pie | Entity types + properties + 1 instance per type (tutorial) |
| 2 | 🏛️ Disappearance at the Museum | 1-N relationship (`Suspect wasAt Location`) |
| 3 | 🔪 Murder in the Library | Temporal event filtering + alibis |
| 4 | 💎 The Datapolis Diamond Heist | Inheritance (`Guard extends Employee extends Person`) |
| 5 | 📞 The Mysterious Phone Call | N-N relationship (`Person called Person`) |
| 6 | 🚗 Hit & Run on Vector Avenue | Multi-source events on one `Vehicle` |
| 7 | 💌 The Anonymous Blackmail | Reasoning: deduce missing property via transitive relations |
| 8 | 🎭 Stolen Identity | Aliases / `sameAs` links between instances |
| 9 | 🏦 Conspiracy at the Senate | Cycle detection in the graph (`bribes` loop) |
| 10 | 🌃 The Final Heist (BOSS) | Multi-domain in 1 ontology with 3 sub-namespaces |

## 🤖 What `detective.accuse()` (judge) verifies

- ✅ **Correct culprit** — decrypts `solution.json.enc` with the per-player/per-case key, matches the accused name
- ✅ **Supporting query** — re-executes the player's saved KQL query and confirms it actually returns the accused
- ✅ **Ontology minimalism** — `entity_types_used_in_query / entity_types_created` close to 1.0 (penalty if you created classes you never used)
- ✅ **Accuracy tracking** — count of prior `WrongAccusation` events affects Rank
- 🏆 **Rank promotion** — Rookie (0–3 solved) → Inspector (4–7) → Commissioner (8–10, low wrong-accusation rate)

## 🔨 TODO (development phase)

- [ ] Implement `ontology_detective_seed.ipynb` — generate 10 synthetic noir case bundles (CSVs + encrypted solutions) into `Datapolis_DetectiveLH`
- [ ] Implement `Detective` class in `ontology_detective_casefile.ipynb`:
  - `briefing(case_id)` — prints noir briefing
  - `ingest_evidence(case_id)` — checks ontology has required types, loads CSVs as instances (raises if missing types — first validation gate)
  - `accuse(person_name)` — decrypts solution, re-executes saved `SOLUTION_QUERY`, scores minimalism, emits telemetry
  - `rank()` — current detective rank
- [ ] Implement dashboard (cases solved, accuracy, minimalism, rank)
- [ ] Write 10 noir briefings (markdown cells in casefile notebook)
- [ ] Wire `arcade.install("ontology-detective")` in `FabricArcade/fabric_arcade/fabric_api.py`
  - **Tricky parts**: creating an empty Ontology item via Fabric REST API; binding ontology event store to KQL queries

## Constraints

- Do NOT alter racing game (frozen at tag `racing-v3-stable`)
- Notebooks must use minimal deps (`requests` + Python `cryptography` only — needed for `solution.json.enc` decryption)
- Solutions never appear in plain text in the repo
