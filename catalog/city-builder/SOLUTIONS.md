# 🔐 City Builder — Full Solutions (T-SQL + DAX)

> Spoiler file. Copy-paste each district's T-SQL into `Datapolis_DW` and the DAX
> measures into `Datapolis_Model`. Then run `mayor.validate("<district-id>")`.

Conventions:
- All T-SQL targets `Datapolis_DW`. Raw tables are read cross-database via
  `[Datapolis_LH].[dbo].[<raw>]`.
- Semantic model name **must be exactly** `Datapolis_Model`.
- Measure **names must match exactly** (the Mayor calls them by name).

Recommended order: **1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 (boss)**.
Districts 3, 4, 5 must be done before 8 (boss reuses their facts + conformed dims).

---

## 1️⃣ Town Hall — Phantom Census

### T-SQL
```sql
DROP TABLE IF EXISTS dbo.FactCensusEvent;
DROP TABLE IF EXISTS dbo.DimCitizen;

CREATE TABLE dbo.DimCitizen (
    CitizenKey   INT          NOT NULL,
    CitizenId    VARCHAR(20)  NOT NULL,
    FullName     VARCHAR(100) NULL,
    Profession   VARCHAR(50)  NULL,
    HomeDistrict VARCHAR(50)  NULL
);

INSERT INTO dbo.DimCitizen (CitizenKey, CitizenId, FullName, Profession, HomeDistrict)
SELECT
    ROW_NUMBER() OVER (ORDER BY citizen_id) AS CitizenKey,
    citizen_id,
    full_name,
    profession,
    home_district
FROM [Datapolis_LH].[dbo].[raw_phantom_census]
WHERE row_type = 'ATTR';

CREATE TABLE dbo.FactCensusEvent (
    CitizenKey INT         NOT NULL,
    EventType  VARCHAR(20) NOT NULL,
    EventDate  DATE        NOT NULL
);

INSERT INTO dbo.FactCensusEvent (CitizenKey, EventType, EventDate)
SELECT
    d.CitizenKey,
    e.event_type,
    e.event_date
FROM [Datapolis_LH].[dbo].[raw_phantom_census] AS e
JOIN dbo.DimCitizen AS d ON d.CitizenId = e.citizen_id
WHERE e.row_type = 'EVENT';
```

### DAX (in `Datapolis_Model`)
Relationship: `FactCensusEvent[CitizenKey]` → `DimCitizen[CitizenKey]` (many-to-one).
```DAX
Citizens             = DISTINCTCOUNT(DimCitizen[CitizenKey])
Birth Events         = CALCULATE(COUNTROWS(FactCensusEvent), FactCensusEvent[EventType]="Birth")
Death Events         = CALCULATE(COUNTROWS(FactCensusEvent), FactCensusEvent[EventType]="Death")
Net Population Change = [Birth Events] - [Death Events]
```

---

## 2️⃣ Neon District — Shifting Identities (SCD-1)

### T-SQL
```sql
DROP TABLE IF EXISTS dbo.DimResident;

CREATE TABLE dbo.DimResident (
    ResidentKey INT          NOT NULL,
    CitizenId   VARCHAR(20)  NOT NULL,
    FullName    VARCHAR(100) NULL,
    IsAugmented BIT          NOT NULL,
    District    VARCHAR(50)  NULL,
    Tier        VARCHAR(20)  NULL
);

WITH merged AS (
    SELECT citizen_id, full_name, is_augmented, district, tier, 0 AS priority
    FROM [Datapolis_LH].[dbo].[raw_neon_residents]
    UNION ALL
    SELECT citizen_id, full_name, is_augmented, district, tier, 1 AS priority
    FROM [Datapolis_LH].[dbo].[raw_neon_residents_updates]
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY citizen_id ORDER BY priority DESC) AS rn
    FROM merged
)
INSERT INTO dbo.DimResident (ResidentKey, CitizenId, FullName, IsAugmented, District, Tier)
SELECT
    ROW_NUMBER() OVER (ORDER BY citizen_id) AS ResidentKey,
    citizen_id, full_name,
    CAST(is_augmented AS BIT),
    district, tier
FROM ranked
WHERE rn = 1;
```

### DAX
```DAX
Residents           = DISTINCTCOUNT(DimResident[ResidentKey])
Augmented Residents = CALCULATE(COUNTROWS(DimResident), DimResident[IsAugmented]=TRUE())
Gold Tier Residents = CALCULATE(COUNTROWS(DimResident), DimResident[Tier]="Gold")
```

---

## 3️⃣ Skylane — Anti-Grav Couriers (additive fact + conformed dims)

### T-SQL
```sql
DROP TABLE IF EXISTS dbo.FactFlight;
DROP TABLE IF EXISTS dbo.DimSector;
DROP TABLE IF EXISTS dbo.DimDate;

-- DimDate: full calendar spanning Skylane + Bazaar (3 years from 2046-01-01).
CREATE TABLE dbo.DimDate (
    DateKey  INT  NOT NULL,
    FullDate DATE NOT NULL,
    Year     INT  NOT NULL,
    MonthNum INT  NOT NULL
);

-- Fabric Warehouse: no recursive CTEs, no OPTION (MAXRECURSION).
-- Build a tally with cross-joined VALUES (1461 days from 2046-01-01).
WITH
  n0(n) AS (SELECT 0 UNION ALL SELECT 0 UNION ALL SELECT 0 UNION ALL SELECT 0
            UNION ALL SELECT 0 UNION ALL SELECT 0 UNION ALL SELECT 0 UNION ALL SELECT 0
            UNION ALL SELECT 0 UNION ALL SELECT 0),                 -- 10
  n1(n) AS (SELECT a.n FROM n0 a CROSS JOIN n0 b),                  -- 100
  n2(n) AS (SELECT a.n FROM n1 a CROSS JOIN n1 b),                  -- 10 000
  nums(rn) AS (SELECT ROW_NUMBER() OVER (ORDER BY (SELECT 1)) - 1 FROM n2),
  cal(d) AS (
      SELECT DATEADD(day, rn, CAST('2046-01-01' AS DATE))
      FROM nums
      WHERE rn < DATEDIFF(day, '2046-01-01', '2050-01-01')          -- 1461
  )
INSERT INTO dbo.DimDate (DateKey, FullDate, Year, MonthNum)
SELECT
    YEAR(d)*10000 + MONTH(d)*100 + DAY(d),
    d, YEAR(d), MONTH(d)
FROM cal;

-- DimSector
CREATE TABLE dbo.DimSector (
    SectorKey  INT         NOT NULL,
    SectorName VARCHAR(50) NOT NULL
);

INSERT INTO dbo.DimSector (SectorKey, SectorName)
SELECT
    ROW_NUMBER() OVER (ORDER BY SectorName) AS SectorKey,
    SectorName
FROM (
    SELECT pickup_sector AS SectorName FROM [Datapolis_LH].[dbo].[raw_skylane_traffic] WHERE pickup_sector IS NOT NULL
    UNION
    SELECT drop_sector   AS SectorName FROM [Datapolis_LH].[dbo].[raw_skylane_traffic] WHERE drop_sector   IS NOT NULL
) s;

-- FactFlight (drop NULL pickup_sector rows)
CREATE TABLE dbo.FactFlight (
    FlightId        VARCHAR(20) NOT NULL,
    DateKey         INT         NOT NULL,
    PickupSectorKey INT         NOT NULL,
    DropSectorKey   INT         NOT NULL,
    DurationMin     INT         NOT NULL,
    DistanceKm      FLOAT       NOT NULL,
    Helium3Kg       FLOAT       NOT NULL
);

INSERT INTO dbo.FactFlight (FlightId, DateKey, PickupSectorKey, DropSectorKey, DurationMin, DistanceKm, Helium3Kg)
SELECT
    f.flight_id,
    YEAR(f.flight_date)*10000 + MONTH(f.flight_date)*100 + DAY(f.flight_date),
    sp.SectorKey,
    sd.SectorKey,
    f.duration_min, f.distance_km, f.helium3_kg
FROM [Datapolis_LH].[dbo].[raw_skylane_traffic] AS f
JOIN dbo.DimSector sp ON sp.SectorName = f.pickup_sector
JOIN dbo.DimSector sd ON sd.SectorName = f.drop_sector
WHERE f.pickup_sector IS NOT NULL;
```

### DAX
Relationships:
- `FactFlight[DateKey]`         → `DimDate[DateKey]`
- `FactFlight[PickupSectorKey]` → `DimSector[SectorKey]` (active)
- `FactFlight[DropSectorKey]`   → `DimSector[SectorKey]` (inactive — role-play)

```DAX
Flights               = COUNTROWS(FactFlight)
Total Helium-3 Burned = SUM(FactFlight[Helium3Kg])
Avg Flight Duration   = AVERAGE(FactFlight[DurationMin])
```

---

## 4️⃣ Plasma Core — Reactor Readings (semi-additive)

### T-SQL
```sql
DROP TABLE IF EXISTS dbo.FactReactorReading;

CREATE TABLE dbo.FactReactorReading (
    ReadingTs    DATETIME2(6) NOT NULL,
    PressureMPa  FLOAT        NOT NULL,
    TemperatureK FLOAT        NOT NULL,
    OutputMW     FLOAT        NOT NULL
);

INSERT INTO dbo.FactReactorReading (ReadingTs, PressureMPa, TemperatureK, OutputMW)
SELECT reading_ts, pressure_mpa, temperature_k, output_mw
FROM [Datapolis_LH].[dbo].[raw_plasma_readings];
```

### DAX
No relationship needed (standalone fact).
```DAX
Avg Pressure   = AVERAGE(FactReactorReading[PressureMPa])
Max Output MW  = MAX(FactReactorReading[OutputMW])
Critical Hours = CALCULATE(COUNTROWS(FactReactorReading), FactReactorReading[PressureMPa] > 5.0)
```

---

## 5️⃣ Bazaar 9 — Quantum Market (role-playing dim)

### T-SQL
> Requires `DimDate` from District 3 (calendar covers 2046–2049).

```sql
DROP TABLE IF EXISTS dbo.FactSale;

CREATE TABLE dbo.FactSale (
    SaleId          VARCHAR(20) NOT NULL,
    OrderDateKey    INT         NOT NULL,
    DeliveryDateKey INT         NOT NULL,
    CustomerId      VARCHAR(20) NOT NULL,
    AmountCredits   FLOAT       NOT NULL,
    IsPreCog        BIT         NOT NULL
);

INSERT INTO dbo.FactSale (SaleId, OrderDateKey, DeliveryDateKey, CustomerId, AmountCredits, IsPreCog)
SELECT
    sale_id,
    YEAR(order_date)*10000    + MONTH(order_date)*100    + DAY(order_date),
    YEAR(delivery_date)*10000 + MONTH(delivery_date)*100 + DAY(delivery_date),
    customer_id,
    amount_credits,
    CAST(is_pre_cog AS BIT)
FROM [Datapolis_LH].[dbo].[raw_bazaar_sales];
```

### DAX
Relationships:
- `FactSale[OrderDateKey]`    → `DimDate[DateKey]` **active**
- `FactSale[DeliveryDateKey]` → `DimDate[DateKey]` **inactive**

```DAX
Sales by Order Date    = SUM(FactSale[AmountCredits])
Sales by Delivery Date =
    CALCULATE(
        SUM(FactSale[AmountCredits]),
        USERELATIONSHIP(FactSale[DeliveryDateKey], DimDate[DateKey])
    )
Pre-Cog Deliveries     = CALCULATE(COUNTROWS(FactSale), FactSale[IsPreCog]=TRUE())
```

---

## 6️⃣ Cryo Hospital — Admission Tags (junk + degenerate dims)

### T-SQL
```sql
DROP TABLE IF EXISTS dbo.FactCryoAdmission;
DROP TABLE IF EXISTS dbo.DimAdmissionType;

CREATE TABLE dbo.DimAdmissionType (
    AdmissionTypeKey INT NOT NULL,
    IsEmergency      BIT NOT NULL,
    HasInsurance     BIT NOT NULL,
    IsAugmented      BIT NOT NULL,
    IsVip            BIT NOT NULL
);

INSERT INTO dbo.DimAdmissionType (AdmissionTypeKey, IsEmergency, HasInsurance, IsAugmented, IsVip)
SELECT
    ROW_NUMBER() OVER (ORDER BY a.b, b.b, c.b, d.b),
    CAST(a.b AS BIT), CAST(b.b AS BIT), CAST(c.b AS BIT), CAST(d.b AS BIT)
FROM (VALUES (0),(1)) a(b)
CROSS JOIN (VALUES (0),(1)) b(b)
CROSS JOIN (VALUES (0),(1)) c(b)
CROSS JOIN (VALUES (0),(1)) d(b);

CREATE TABLE dbo.FactCryoAdmission (
    CryoTicket       VARCHAR(20) NOT NULL,
    AdmissionDateKey INT         NOT NULL,
    AdmissionTypeKey INT         NOT NULL,
    DurationDays     INT         NOT NULL
);

INSERT INTO dbo.FactCryoAdmission (CryoTicket, AdmissionDateKey, AdmissionTypeKey, DurationDays)
SELECT
    r.cryo_ticket,
    YEAR(r.admission_date)*10000 + MONTH(r.admission_date)*100 + DAY(r.admission_date),
    j.AdmissionTypeKey,
    r.duration_days
FROM [Datapolis_LH].[dbo].[raw_cryo_admissions] r
JOIN dbo.DimAdmissionType j
  ON j.IsEmergency  = CAST(r.is_emergency  AS BIT)
 AND j.HasInsurance = CAST(r.has_insurance AS BIT)
 AND j.IsAugmented  = CAST(r.is_augmented  AS BIT)
 AND j.IsVip        = CAST(r.is_vip        AS BIT);
```

### DAX
Relationship: `FactCryoAdmission[AdmissionTypeKey]` → `DimAdmissionType[AdmissionTypeKey]`.
```DAX
Admissions               = COUNTROWS(FactCryoAdmission)
VIP Emergency Admissions =
    CALCULATE(
        COUNTROWS(FactCryoAdmission),
        DimAdmissionType[IsVip]=TRUE(),
        DimAdmissionType[IsEmergency]=TRUE()
    )
Avg Cryo Duration        = AVERAGE(FactCryoAdmission[DurationDays])
```

---

## 7️⃣ Holo-Stage — Multiverse Performers (M:N bridge)

### T-SQL
```sql
DROP TABLE IF EXISTS dbo.BridgeShowArtist;
DROP TABLE IF EXISTS dbo.FactShow;
DROP TABLE IF EXISTS dbo.DimShow;
DROP TABLE IF EXISTS dbo.DimArtist;

CREATE TABLE dbo.DimArtist (
    ArtistKey  INT          NOT NULL,
    ArtistId   VARCHAR(10)  NOT NULL,
    ArtistName VARCHAR(50)  NOT NULL,
    Region     VARCHAR(20)  NULL,
    BaseCachet FLOAT        NULL
);
INSERT INTO dbo.DimArtist (ArtistKey, ArtistId, ArtistName, Region, BaseCachet)
SELECT
    ROW_NUMBER() OVER (ORDER BY artist_id),
    artist_id, artist_name, region, base_cachet
FROM [Datapolis_LH].[dbo].[raw_holo_artists];

CREATE TABLE dbo.DimShow (
    ShowKey  INT          NOT NULL,
    ShowId   VARCHAR(10)  NOT NULL,
    ShowDate DATE         NOT NULL,
    Genre    VARCHAR(30)  NULL
);
INSERT INTO dbo.DimShow (ShowKey, ShowId, ShowDate, Genre)
SELECT
    ROW_NUMBER() OVER (ORDER BY show_id),
    show_id, show_date, genre
FROM [Datapolis_LH].[dbo].[raw_holo_shows];

CREATE TABLE dbo.FactShow (
    ShowKey        INT   NOT NULL,
    Attendance     INT   NOT NULL,
    RevenueCredits FLOAT NOT NULL
);
INSERT INTO dbo.FactShow (ShowKey, Attendance, RevenueCredits)
SELECT s.ShowKey, r.attendance, r.revenue_credits
FROM [Datapolis_LH].[dbo].[raw_holo_shows] r
JOIN dbo.DimShow s ON s.ShowId = r.show_id;

CREATE TABLE dbo.BridgeShowArtist (
    ShowKey   INT   NOT NULL,
    ArtistKey INT   NOT NULL,
    Cachet    FLOAT NOT NULL
);
INSERT INTO dbo.BridgeShowArtist (ShowKey, ArtistKey, Cachet)
SELECT s.ShowKey, a.ArtistKey, l.cachet
FROM [Datapolis_LH].[dbo].[raw_holo_lineup] l
JOIN dbo.DimShow   s ON s.ShowId   = l.show_id
JOIN dbo.DimArtist a ON a.ArtistId = l.artist_id;
```

### DAX
Relationships:
- `DimShow[ShowKey]`   ↔ `FactShow[ShowKey]`         (1:1, bidirectional — Power BI enforces this for 1:1)
- `DimShow[ShowKey]`   → `BridgeShowArtist[ShowKey]`   (1:*, single direction)
- `DimArtist[ArtistKey]` → `BridgeShowArtist[ArtistKey]` (1:*, single direction)

```DAX
Shows               = DISTINCTCOUNT(DimShow[ShowKey])
Total Cachet        = SUM(BridgeShowArtist[Cachet])
Avg Cachet per Show = DIVIDE(SUM(BridgeShowArtist[Cachet]), DISTINCTCOUNT(DimShow[ShowKey]))
Total Attendance    = SUM(FactShow[Attendance])
```

---

## 8️⃣ Grid Overlook — BOSS (galaxy schema + DAX perf)

### T-SQL
Nothing new — the galaxy schema is the union of Districts 3 + 4 + 5
(`DimDate`, `DimSector`, `FactFlight`, `FactReactorReading`, `FactSale`).
If any is missing, finish that district first.

### DAX
In `Datapolis_Model`, ensure relationships exist for all three facts, then add:
```DAX
Total Flights (clean) = COUNTROWS(FactFlight)
Total Helium-3        = SUM(FactFlight[Helium3Kg])
Avg Reactor Pressure  = AVERAGE(FactReactorReading[PressureMPa])
Total Sales           = SUM(FactSale[AmountCredits])
Grid Stress Index =
      0.4 * DIVIDE([Avg Reactor Pressure], 5.0)
    + 0.3 * DIVIDE([Total Helium-3], 50000)
    + 0.3 * DIVIDE([Total Sales],    10000000)
```
Performance target: full-table evaluation < 2s.

---

## ✅ Validation cheat-sheet

```python
for d in ["town-hall","neon-district","skylane","plasma-core",
          "bazaar-9","cryo-hospital","holo-stage","grid-overlook"]:
    mayor.inspect(d)
    mayor.validate(d)
mayor.score()
```
