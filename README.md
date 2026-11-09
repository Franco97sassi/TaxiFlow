
# TaxiFlow — Data Engineering Pipeline

End-to-end Data Engineering project using real NYC Yellow Taxi trip data.

## Overview

TaxiFlow is a data engineering pipeline designed to ingest,
validate, transform and analyze NYC Taxi trip records.

## Tech Stack

- Python 3.13
- DuckDB
- SQL
- Requests
- Pandas
- NumPy
- Apache Parquet
- Git & GitHub

## Architecture

NYC Taxi Dataset
    |
    v
Python Data Ingestion
    |
    v
Raw Data (Parquet)
    |
    v
Data Profiling
    |
    v
Data Quality Validation

Future stages: ETL/ELT, Data Warehouse, dbt,
GitHub Actions, Streamlit and Docker.

## Project Structure

TaxiFlow/
├── src/
│   ├── ingesta.py
│   ├── perfilado.py
│   └── validacion.py
├── data/
│   ├── raw/
│   └── warehouse/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md

## Installation

Create a virtual environment:

    py -m venv .venv

Activate it on Windows:

    .\.venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install -r requirements.txt

## Usage

Download January 2025:

    python src/ingesta.py --anio 2025 --mes 1

Download February 2025:

    python src/ingesta.py --anio 2025 --mes 2

Profile January data:

    python src/perfilado.py

Validate January data:

    python src/validacion.py

## Data Quality Findings

January 2025:
- Total records: 3,475,226
- Missing required values: 0
- Negative distances: 0
- Distances over 100 miles: 162
- Negative total amounts: 63,037
- Inconsistent timestamps: 124
- Zero-duration trips: 1,927

Anomalies are preserved in the raw dataset.

## Data Source

NYC Taxi & Limousine Commission:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Roadmap

- [x] Environment setup
- [x] Batch data ingestion
- [x] Data profiling
- [x] Data quality validation
- [x] Parameterized and idempotent ingestion
- [ ] ETL/ELT and data cleaning
- [ ] Data warehouse and dbt
- [ ] Pipeline automation
- [ ] Analytics dashboard
- [ ] Docker, testing and final documentation



## Data Warehouse & Dimensional Modeling

TaxiFlow implements a star schema using DuckDB and dbt.

### Fact Table

- analytics.fct_viajes

### Dimension Tables

- analytics.dim_fecha
- analytics.dim_zona
- analytics.dim_pago

### Data Warehouse Results

- Source records: 7,052,769
- Clean trips: 6,927,342
- Fact table records: 6,927,342
- dbt models: 4
- dbt tests passed: 11

### Execute the Warehouse

Configure TAXIFLOW_DB_PATH with the absolute
path to the local DuckDB database.

Run transformations and tests:

    dbt build --profiles-dir .

Generate documentation:

    dbt docs generate --profiles-dir .

Serve documentation:

    dbt docs serve --profiles-dir .

### Data Quality

- Dimension keys validated for uniqueness
- Mandatory keys validated for nulls
- Fact-to-dimension relationships validated
- CLEAN and FACT record counts reconciled
