# ⚽ Sports Tracker

> **Track live sports statistics and predict match outcomes with ML**

![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-orange)
![Duration](https://img.shields.io/badge/Duration-25%20min-blue)
![Workloads](https://img.shields.io/badge/Workloads-RTI%20%2B%20DS-green)

## 🎯 Match Briefing

The World Cup final is about to kick off! **22 players, 90 minutes, endless data**. Your mission: build a real-time sports analytics system that tracks player performance and predicts the winner.

You'll create:
- Live player statistics tracking (passes, shots, distance)
- Real-time match event stream (goals, fouls, substitutions)
- ML model for outcome prediction
- Interactive match dashboard

## 🛠️ What You'll Learn

| Skill | Fabric Workload | Level |
|-------|-----------------|-------|
| Event streaming | Eventstream | ⭐⭐ |
| Time-series queries | KQL | ⭐⭐ |
| ML model training | Data Science | ⭐⭐ |
| Feature engineering | Notebook | ⭐⭐ |

## 📋 Prerequisites

- Microsoft Fabric workspace with F2+ capacity
- Basic Python and ML concepts

## ⚽ Quick Start

```python
import fabric_arcade as arcade

arcade.install("sports-tracker")
arcade.play("sports-tracker")
```

## 📖 Match Chapters

### First Half: Setup 🏟️
**Objective**: Build the event collection infrastructure

1. Create Eventhouse `sports-events` with tables:

```kql
.create table MatchEvents (
    Timestamp: datetime,
    MatchId: string,
    EventType: string,
    PlayerId: string,
    PlayerName: string,
    Team: string,
    Minute: int,
    X: real,
    Y: real,
    Details: dynamic
)

.create table PlayerStats (
    Timestamp: datetime,
    MatchId: string,
    PlayerId: string,
    Passes: int,
    PassAccuracy: real,
    Shots: int,
    ShotsOnTarget: int,
    Distance: real,
    Sprints: int
)
```

2. Configure Eventstream for match data ingestion
3. Run the match simulator

### Half-Time: Analytics 📊
**Objective**: Build real-time match insights

**Query 1: Live Score**
```kql
MatchEvents
| where EventType == "goal"
| summarize Goals = count() by Team
| render piechart
```

**Query 2: Possession Heatmap**
```kql
MatchEvents
| where EventType == "pass"
| summarize PassCount = count() by Team, bin(X, 10), bin(Y, 10)
| render heatmap
```

**Query 3: Top Performers**
```kql
PlayerStats
| summarize arg_max(Timestamp, *) by PlayerId
| top 5 by Passes + Shots desc
| project PlayerName, Team, Passes, Shots, Distance
```

### Second Half: Prediction 🤖
**Objective**: Train an ML model to predict the winner

1. Extract features from match events:
   - Possession percentage
   - Shot accuracy
   - Pass completion rate
   - Dangerous attacks

2. Train a simple classifier:

```python
from sklearn.ensemble import RandomForestClassifier

features = ['possession', 'shots_on_target', 'pass_accuracy', 'corners']
X = match_data[features]
y = match_data['winner']

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predict current match outcome
current_match_features = get_live_features()
prediction = model.predict_proba(current_match_features)
print(f"Home Win: {prediction[0][0]:.1%}")
print(f"Draw: {prediction[0][1]:.1%}")  
print(f"Away Win: {prediction[0][2]:.1%}")
```

### Final Whistle: Dashboard 🏆
**Objective**: Build the match summary dashboard

Create a Real-Time Dashboard with:
- Live score and match clock
- Player statistics leaderboard
- Possession and shots comparison
- ML prediction gauge
- Event timeline

## 🏅 Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| Kickoff | Deploy and start streaming | ⚽ |
| Stat Master | Query all player statistics | 📊 |
| Prediction Ace | Achieve 70% prediction accuracy | 🎯 |
| Full Time | Complete all chapters | 🏆 |

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPORTS ANALYTICS CENTER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Notebook   │    │  Eventstream │    │  Eventhouse  │      │
│  │    Match     │───▶│   match-     │───▶│   sports-    │      │
│  │  Simulator   │    │   stream     │    │   events     │      │
│  └──────────────┘    └──────────────┘    └──────┬───────┘      │
│                                                  │               │
│                              ┌───────────────────┴───────┐      │
│                              │                           │      │
│                              ▼                           ▼      │
│                       ┌──────────────┐          ┌─────────────┐ │
│                       │   ML Model   │          │ RT Dashboard│ │
│                       │   Predictor  │          │   Match     │ │
│                       │              │─────────▶│   Center    │ │
│                       └──────────────┘          └─────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔗 Resources

- [Fabric Data Science](https://learn.microsoft.com/fabric/data-science/)
- [ML Model Training](https://learn.microsoft.com/fabric/data-science/train-models)
- [Real-Time Dashboard](https://learn.microsoft.com/fabric/real-time-intelligence/)

## 🎮 Related Games

- 🏎️ **Race Analytics** - Apply streaming to motorsport
- 🚀 **Mission Artemis** - More complex RTI patterns
- 🧙 **Wizard's Workshop** - Deep dive into ML

---

*"GOOOOOAL! The data doesn't lie!"* ⚽
