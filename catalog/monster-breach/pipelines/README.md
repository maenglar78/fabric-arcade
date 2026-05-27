# Empty Pipeline Definitions

This folder will hold the 9 empty pipeline definitions (JSON) that `arcade.install("monster-breach")` deploys to the workspace.

Pipelines are **intentionally empty** — the player builds them in the Fabric UI as part of the gameplay.

## TODO

Generate one `{pipelineName}.json` per item below, using Fabric Data Pipeline definition format. Each must:

- Have a unique name (matches `manifest.json` `items[].name`)
- Be syntactically valid (deployable via Fabric REST API `POST /workspaces/{ws}/dataPipelines`)
- Contain **no activities** (or a single noop activity if the API requires one)
- Include a description tag indicating which level it belongs to

## Pipelines

- Lvl01_CopyQuest
- Lvl02_FilterFortress
- Lvl03_SchemaShrine
- Lvl04_TriggerTower
- Lvl05_ForEachField
- Lvl06_IfMimicLair
- Lvl07_SwitchHydraDen
- Lvl08_RetryReef
- BossBattle_CorruptionKing
