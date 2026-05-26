# 🏙️ City Builder Analytics

> **Design and analyze a virtual city with data warehousing**

![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red)
![Duration](https://img.shields.io/badge/Duration-60%20min-blue)
![Workloads](https://img.shields.io/badge/Workloads-DE%20%2B%20DW-green)

## 🎯 City Briefing

Congratulations, Mayor! You've been elected to lead **New Data City**. Your mission: build a thriving metropolis by making data-driven decisions about population, resources, traffic, and citizen happiness.

This game teaches **Data Warehouse** patterns through urban planning simulation!

## 🏗️ What You'll Build

- Population growth analytics
- Resource consumption tracking (water, electricity, waste)
- Traffic flow analysis
- Citizen satisfaction surveys
- City budget optimization

## 🛠️ What You'll Learn

| Skill | Fabric Workload | Level |
|-------|-----------------|-------|
| Star schema design | Data Warehouse | ⭐⭐⭐ |
| T-SQL analytics | SQL Endpoint | ⭐⭐ |
| Slowly changing dimensions | DW Patterns | ⭐⭐⭐ |
| Data visualization | Power BI | ⭐⭐ |

## 📋 Prerequisites

- Microsoft Fabric workspace with F4+ capacity
- T-SQL knowledge
- Understanding of dimensional modeling

## 🏙️ Quick Start

```python
import fabric_arcade as arcade

arcade.install("city-builder")
arcade.play("city-builder")
```

## 📖 City Chapters

### Chapter 1: City Planning 🗺️
**Objective**: Design the data warehouse schema

Create the Warehouse `city-analytics` with a star schema:

**Dimension Tables:**
```sql
-- District dimension (where things happen)
CREATE TABLE dim_district (
    district_key INT PRIMARY KEY,
    district_id VARCHAR(10),
    district_name VARCHAR(100),
    zone_type VARCHAR(50),  -- Residential, Commercial, Industrial
    area_sqkm DECIMAL(10,2),
    population_capacity INT,
    established_date DATE
);

-- Time dimension
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    day_of_week VARCHAR(10),
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BIT,
    is_holiday BIT
);

-- Service dimension
CREATE TABLE dim_service (
    service_key INT PRIMARY KEY,
    service_id VARCHAR(10),
    service_name VARCHAR(100),
    service_category VARCHAR(50),  -- Utilities, Transport, Emergency
    cost_per_unit DECIMAL(10,2)
);

-- Citizen dimension (SCD Type 2)
CREATE TABLE dim_citizen (
    citizen_key INT PRIMARY KEY,
    citizen_id VARCHAR(20),
    age_group VARCHAR(20),
    income_bracket VARCHAR(20),
    district_key INT,
    employment_status VARCHAR(20),
    effective_date DATE,
    expiry_date DATE,
    is_current BIT
);
```

**Fact Tables:**
```sql
-- Resource consumption facts
CREATE TABLE fact_resource_consumption (
    consumption_id BIGINT IDENTITY PRIMARY KEY,
    date_key INT,
    district_key INT,
    service_key INT,
    consumption_amount DECIMAL(15,2),
    cost DECIMAL(15,2),
    peak_hour_usage DECIMAL(10,2)
);

-- Traffic facts
CREATE TABLE fact_traffic (
    traffic_id BIGINT IDENTITY PRIMARY KEY,
    date_key INT,
    district_key INT,
    hour_of_day INT,
    vehicle_count INT,
    avg_speed_kmh DECIMAL(5,2),
    congestion_index DECIMAL(3,2)
);

-- Citizen satisfaction facts
CREATE TABLE fact_satisfaction_survey (
    survey_id BIGINT IDENTITY PRIMARY KEY,
    date_key INT,
    citizen_key INT,
    district_key INT,
    overall_score INT,  -- 1-10
    safety_score INT,
    cleanliness_score INT,
    transport_score INT,
    services_score INT
);
```

### Chapter 2: Population Growth 👥
**Objective**: Analyze population trends and forecast growth

```sql
-- Population by district over time
WITH population_trend AS (
    SELECT 
        d.district_name,
        dt.year,
        dt.quarter,
        COUNT(DISTINCT c.citizen_key) as population
    FROM dim_citizen c
    JOIN dim_district d ON c.district_key = d.district_key
    JOIN dim_date dt ON c.effective_date <= dt.full_date 
        AND (c.expiry_date > dt.full_date OR c.is_current = 1)
    GROUP BY d.district_name, dt.year, dt.quarter
)
SELECT 
    district_name,
    year,
    quarter,
    population,
    LAG(population) OVER (PARTITION BY district_name ORDER BY year, quarter) as prev_quarter,
    CAST((population - LAG(population) OVER (PARTITION BY district_name ORDER BY year, quarter)) 
        AS FLOAT) / NULLIF(LAG(population) OVER (PARTITION BY district_name ORDER BY year, quarter), 0) * 100 
        as growth_rate_pct
FROM population_trend
ORDER BY district_name, year, quarter;
```

### Chapter 3: Resource Management 💡
**Objective**: Optimize city resource allocation

```sql
-- Resource consumption by district and service
SELECT 
    d.district_name,
    d.zone_type,
    s.service_category,
    SUM(f.consumption_amount) as total_consumption,
    SUM(f.cost) as total_cost,
    AVG(f.peak_hour_usage) as avg_peak_usage,
    SUM(f.consumption_amount) / d.population_capacity as consumption_per_capita
FROM fact_resource_consumption f
JOIN dim_district d ON f.district_key = d.district_key
JOIN dim_service s ON f.service_key = s.service_key
JOIN dim_date dt ON f.date_key = dt.date_key
WHERE dt.year = YEAR(GETDATE())
GROUP BY d.district_name, d.zone_type, s.service_category, d.population_capacity
ORDER BY total_cost DESC;

-- Identify districts exceeding resource capacity
SELECT 
    d.district_name,
    s.service_name,
    SUM(f.consumption_amount) as monthly_consumption,
    d.population_capacity * s.cost_per_unit as expected_max,
    CASE 
        WHEN SUM(f.consumption_amount) > d.population_capacity * s.cost_per_unit * 1.2 
        THEN '🚨 CRITICAL'
        WHEN SUM(f.consumption_amount) > d.population_capacity * s.cost_per_unit 
        THEN '⚠️ WARNING'
        ELSE '✅ NORMAL'
    END as status
FROM fact_resource_consumption f
JOIN dim_district d ON f.district_key = d.district_key
JOIN dim_service s ON f.service_key = s.service_key
JOIN dim_date dt ON f.date_key = dt.date_key
WHERE dt.full_date >= DATEADD(month, -1, GETDATE())
GROUP BY d.district_name, s.service_name, d.population_capacity, s.cost_per_unit;
```

### Chapter 4: Traffic Control 🚗
**Objective**: Reduce congestion with data-driven decisions

```sql
-- Hourly traffic patterns by district
SELECT 
    d.district_name,
    f.hour_of_day,
    AVG(f.vehicle_count) as avg_vehicles,
    AVG(f.avg_speed_kmh) as avg_speed,
    AVG(f.congestion_index) as avg_congestion,
    CASE 
        WHEN AVG(f.congestion_index) > 0.8 THEN '🔴 Gridlock'
        WHEN AVG(f.congestion_index) > 0.5 THEN '🟡 Heavy'
        WHEN AVG(f.congestion_index) > 0.3 THEN '🟢 Moderate'
        ELSE '⚪ Light'
    END as traffic_status
FROM fact_traffic f
JOIN dim_district d ON f.district_key = d.district_key
GROUP BY d.district_name, f.hour_of_day
ORDER BY d.district_name, f.hour_of_day;

-- Identify bottleneck hours for each district
WITH ranked_hours AS (
    SELECT 
        d.district_name,
        f.hour_of_day,
        AVG(f.congestion_index) as avg_congestion,
        RANK() OVER (PARTITION BY d.district_name ORDER BY AVG(f.congestion_index) DESC) as congestion_rank
    FROM fact_traffic f
    JOIN dim_district d ON f.district_key = d.district_key
    GROUP BY d.district_name, f.hour_of_day
)
SELECT * FROM ranked_hours WHERE congestion_rank <= 3;
```

### Chapter 5: Citizen Happiness 😊
**Objective**: Maximize citizen satisfaction scores

```sql
-- Overall city happiness dashboard
SELECT 
    d.district_name,
    COUNT(*) as survey_count,
    AVG(CAST(f.overall_score AS FLOAT)) as avg_overall,
    AVG(CAST(f.safety_score AS FLOAT)) as avg_safety,
    AVG(CAST(f.cleanliness_score AS FLOAT)) as avg_cleanliness,
    AVG(CAST(f.transport_score AS FLOAT)) as avg_transport,
    AVG(CAST(f.services_score AS FLOAT)) as avg_services,
    CASE 
        WHEN AVG(CAST(f.overall_score AS FLOAT)) >= 8 THEN '🌟 Excellent'
        WHEN AVG(CAST(f.overall_score AS FLOAT)) >= 6 THEN '😊 Good'
        WHEN AVG(CAST(f.overall_score AS FLOAT)) >= 4 THEN '😐 Fair'
        ELSE '😟 Needs Work'
    END as district_rating
FROM fact_satisfaction_survey f
JOIN dim_district d ON f.district_key = d.district_key
JOIN dim_date dt ON f.date_key = dt.date_key
WHERE dt.full_date >= DATEADD(month, -3, GETDATE())
GROUP BY d.district_name
ORDER BY avg_overall DESC;

-- Correlation: Does resource availability affect happiness?
SELECT 
    d.district_name,
    AVG(CAST(sat.overall_score AS FLOAT)) as happiness_score,
    SUM(res.consumption_amount) / COUNT(DISTINCT sat.citizen_key) as resources_per_citizen,
    CORR(sat.overall_score, res.consumption_amount) as correlation
FROM fact_satisfaction_survey sat
JOIN dim_district d ON sat.district_key = d.district_key
JOIN fact_resource_consumption res ON sat.district_key = res.district_key 
    AND sat.date_key = res.date_key
GROUP BY d.district_name;
```

## 🏅 Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| City Founder | Create all tables | 🏗️ |
| Population Expert | Analyze growth trends | 👥 |
| Resource Manager | Optimize consumption | 💡 |
| Traffic Controller | Reduce congestion | 🚗 |
| Happiness Mayor | Achieve 8+ satisfaction | 😊 |
| Metropolis Master | Complete all chapters | 🏆 |

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEW DATA CITY HALL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Lakehouse   │  │ Lakehouse   │  │ Data        │             │
│  │ Bronze City │─▶│ Silver City │─▶│ Warehouse   │             │
│  │ (Raw)       │  │ (Clean)     │  │ city-       │             │
│  └─────────────┘  └─────────────┘  │ analytics   │             │
│                                     └──────┬──────┘             │
│                                            │                    │
│                    ┌───────────────────────┼───────────────┐   │
│                    │                       │               │   │
│                    ▼                       ▼               ▼   │
│             ┌───────────┐           ┌───────────┐   ┌─────────┐│
│             │ dim_      │           │ fact_     │   │ Power   ││
│             │ tables    │           │ tables    │   │ BI      ││
│             │ ⭐ Star   │           │           │   │ Report  ││
│             │   Schema  │           │           │   │         ││
│             └───────────┘           └───────────┘   └─────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔗 Resources

- [Fabric Data Warehouse](https://learn.microsoft.com/fabric/data-warehouse/)
- [Star Schema Design](https://learn.microsoft.com/power-bi/guidance/star-schema)
- [T-SQL Reference](https://learn.microsoft.com/sql/t-sql/language-reference)

## 🎮 Related Games

- 🏰 **Quest Pipeline** - Medallion architecture fundamentals
- 🚂 **Train Dispatch** - Real-time operations
- 🌊 **Ocean Explorer** - Combine with ML analytics

---

*"Build the city, govern with data!"* 🏙️
