# Ontology Detective — Solutions (Spoilers!)

> **Stop. Read no further until you have tried each case yourself.**
> This file is plain text on purpose — the educational value is in the
> *modelling* and the *query*, not in keeping secrets.

For every case below:
1. **Ontology** — the entities & relationships you should have added to
   `DetectiveOntology` in the Digital Twin Builder UI before writing the query.
2. **KQL query** — one canonical solution. Many equivalents exist.
3. **Culprit** — the name to pass to `detective.accuse(...)`.

All queries assume you've run `OntologyDetective_Seed` and you're working
inside `OntologyDetective_CaseFile`.

---

## Case #1 — The Stolen Pie  🧁  `stolen-pie`

### Ontology
- **Person**
- **Room**
- **Visit** *(reified relationship: Person `wasIn` Room from `enteredAt` to `leftAt`)*

### KQL
```kql
Case1_Visits
| where RoomName == "Kitchen"
| where EnteredAt < datetime(2026-06-05 14:30:00)
  and LeftAt   > datetime(2026-06-05 14:00:00)
| where PersonName != "Mrs. Plum"
| project PersonName
```

### Culprit
**Bob Hollowstone**

```python
detective.accuse("stolen-pie", "Bob Hollowstone")
```

---

## Case #2 — Disappearance at the Museum  🏛️  `museum`

### Ontology
- **Person**
- **Location**
- **CameraEvent** *(Person `wasAt` Location at `seenAt`)*

### KQL
```kql
Case2_CameraEvents
| where Location == "Etruscan Hall"
| where SeenAt between (datetime(2026-06-04 21:14:00) .. datetime(2026-06-04 21:18:00))
| project GuestName
```

### Culprit
**Lady Marlowe**

```python
detective.accuse("museum", "Lady Marlowe")
```

---

## Case #3 — The Mysterious Phone Call  📞  `phone-call`

### Ontology
- **Person**
- **PhoneCall** *(Person `called` Person at `calledAt`)*  — self-relationship

### KQL
```kql
let toCarballo =
    Case3_PhoneCalls
    | where Callee == "Senator Carballo"
    | project Suspect=Caller, CarballoCallTime=CalledAt;
let toAconite =
    Case3_PhoneCalls
    | where Callee == "Dr. Aconite"
    | project Suspect=Caller, AconiteCallTime=CalledAt;
toCarballo
| join kind=inner toAconite on Suspect
| where abs(datetime_diff('minute', CarballoCallTime, AconiteCallTime)) <= 120
| project Suspect
```

### Culprit
**Vincenzo Lupara**

```python
detective.accuse("phone-call", "Vincenzo Lupara")
```

---

## Case #4 — Stolen Identity  🎭  `stolen-identity`

### Ontology
- **Person**
- **Alias** *(Alias `sameAs` Person)*
- **HotelCheckIn** *(Alias `checkedIn` Hotel at `checkedInAt`)*

### KQL
```kql
Case4_HotelCheckIns
| where HotelName == "Quantum"
| where CheckedInAt between (datetime(2026-06-01 22:00:00) .. datetime(2026-06-02 02:00:00))
| join kind=inner Case4_Aliases on $left.UsedName == $right.AliasName
| project RealName
```

### Culprit
**Ricardo Vega** *(the real name behind the alias `V. Rodriguez`)*

```python
detective.accuse("stolen-identity", "Ricardo Vega")
```

---

## Case #5 — The Final Heist (BOSS)  🌃  `final-heist`

### Ontology — three sub-namespaces under one shared `Person`
- **Bank.Account** *(Person `owns` Account, kind `RelayShell`)*
- **Police.Patrol** *(Person `seenIn` Zone, `onDutyRegister: bool`)*
- **Telecom.PhoneCall** *(Person `called` PhoneNumber)*

### KQL
```kql
let RelayAccountOwners =
    Case5_BankAccounts
    | where AccountKind == "RelayShell"
    | project PersonName;
let GhostsInZone =
    Case5_PolicePatrols
    | where PatrolZone == "Bank District" and OnDutyRegister == false
    | project PersonName;
let BurnerCallers =
    Case5_BurnerCalls
    | where Callee == "+39-X-USA-E-GETTA"
      and CalledAt between (datetime(2026-06-05 23:00:00) .. datetime(2026-06-05 23:10:00))
    | project PersonName=Caller;
RelayAccountOwners
| join kind=inner GhostsInZone on PersonName
| join kind=inner BurnerCallers  on PersonName
| project PersonName
```

### Culprit
**Madame Cinquedeo**

```python
detective.accuse("final-heist", "Madame Cinquedeo")
```

---

## Detective ranks

| Cases solved | Rank                              |
|-------------:|-----------------------------------|
| 0            | Aspiring Detective                |
| 1            | 🥉 Rookie                         |
| 2            | 🥈 Investigator                   |
| 3            | 🎯 Inspector                      |
| 4            | 🔍 Senior Detective               |
| 5            | 🏆 Commissioner of Datapolis      |

Solving all 5 and minting the badge in **Step 6** of `OntologyDetective_CaseFile`
gives you the **Commissioner of Datapolis** badge — shareable on LinkedIn.
