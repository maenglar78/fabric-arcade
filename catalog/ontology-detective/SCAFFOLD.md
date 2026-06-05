# 🕵️ Ontology Detective — Design Notes (v1.0)

> Released as a 5-case noir mystery. Player designs the ontology in DTB, queries evidence in KQL, judge validates the accusation.

## Architecture

| Item | Type | Role |
|---|---|---|
| `Datapolis_DetectiveEH` | Eventhouse + KQL DB | hosts evidence tables + DetectiveEvents telemetry |
| `DetectiveOntology` | Ontology (DTB) | empty at install — player adds entity types per case |
| `OntologyDetective_Seed` | Notebook | populates KQL DB with 5 noir datasets |
| `OntologyDetective_CaseFile` | Notebook | briefings, KQL helpers, `detective.accuse(...)` judge, badge |
| `OntologyDetective_Dashboard` | Notebook | reads DetectiveEvents → cases solved / accuracy / rank |

## Why Ontology + KQL together?

- **Ontology** = pedagogical exercise. Player designs `Person`, `Location`, `wasAt` in DTB UI so they internalize the conceptual model.
- **KQL** = execution substrate. We don't fight the data plane of the DTB ontology — we use familiar KQL tables for the actual evidence.
- The judge does not parse the player's DAX/KQL; it just checks the accused name against `CULPRITS[case_id]` and emits telemetry.

## Solutions

Plain-text in `SOLUTIONS.md` (no AES). The `CULPRITS` map inside `OntologyDetective_CaseFile` is also visible — the game rewards completion, not security through obscurity.

## Cases (final 5)

| # | id | Concept |
|---|---|---|
| 1 | `stolen-pie` | Entity types + properties (tutorial) |
| 2 | `museum` | 1-N + temporal filter |
| 3 | `phone-call` | N-N self-relationship + graph join |
| 4 | `stolen-identity` | sameAs / entity resolution |
| 5 | `final-heist` | Multi-domain (Bank+Police+Telecom) |

## Ranks

`Aspiring → Rookie → Investigator → Inspector → Senior Detective → 🏆 Commissioner of Datapolis` (1 case per tier).

## Badge

Same HMAC-SHA256 pattern as retro-arcade / city-builder. Skills declared: `["Fabric Ontology", "Digital Twin Builder", "KQL", "Knowledge Graph", "Entity Resolution"]`.
