
# TaxiFlow — Data Engineering Architecture

## Overview

TaxiFlow is an end-to-end batch Data Engineering
project using NYC Yellow Taxi Trip Records.

## Technology Stack

- Python 3.13
- DuckDB
- SQL
- dbt Core
- GitHub Actions
- Streamlit
- Plotly
- Docker and Docker Compose

## Data Flow

NYC TLC Parquet Files
        |
        v
Python Batch Ingestion
        |
        v
RAW Data Layer
        |
        v
STAGING (DuckDB)
        |
        v
CLEAN (DuckDB)
        |
        v
dbt Data Warehouse
        |
        +-- dim_fecha
        +-- dim_zona
        +-- dim_pago
        +-- fct_viajes
        |
        v
SQL Analytical Queries
        |
        v
Streamlit Dashboard

## Data Quality

- Raw data validation
- Staging quality flags
- Clean trip records
- Separate adjustment records
- Warehouse reconciliation
- dbt data tests
- Python unit tests

## Orchestration

The Python orchestrator executes ingestion,
transformation, cleaning, dbt builds,
reconciliation and automated tests.

GitHub Actions provides:

- Continuous Integration
- Manual batch execution
- Scheduled monthly execution

## Containerization

Docker packages the Streamlit dashboard.

The DuckDB warehouse is mounted into the
container as a read-only volume.

The warehouse database and raw Parquet files
are excluded from Git.

## Current Limitations

- Batch processing uses fixed 2025 periods.
- No incremental ingestion yet.
- No persistent cloud data storage.
- Dashboard is intended for local execution.
- Scheduled runs recreate the warehouse
  inside an ephemeral GitHub runner.
