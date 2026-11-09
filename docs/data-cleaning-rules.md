
# TaxiFlow — Data Cleaning Rules

## Objective

Define consistent, auditable rules for transforming
NYC Taxi trip records into analytical datasets.

## Architecture

RAW -> STAGING -> CLEAN

RAW preserves the original Parquet files.

STAGING adds derived fields, quality flags,
source periods and anomaly classifications.

CLEAN contains records suitable for ordinary
trip analytics under the agreed business rules.

## Cleaning Rules

| ID | Condition | Treatment |
|---|---|---|
| R01 | Required pickup/dropoff date is NULL | Exclude from CLEAN |
| R02 | Dropoff <= pickup | Exclude from CLEAN |
| R03 | Trip distance < 0 | Exclude from CLEAN |
| R04 | Trip distance = 0 | Flag for review |
| R05 | Trip distance > 100 miles | Flag as outlier |
| R06 | Total amount < 0 | Classify as potential adjustment |
| R07 | Total amount is NULL | Exclude from CLEAN |
| R08 | Pickup outside source month | Flag for review |
| R09 | Passenger count is NULL or zero | Flag for review |
| R10 | Trip duration > 24 hours | Flag as outlier |

## Data Quality Principles

1. Never modify RAW source files.
2. Preserve all records in STAGING.
3. Record quality flags for each anomaly.
4. Do not assume negative amounts are errors.
5. Document the criteria used for CLEAN.
6. Maintain source-month traceability.
7. Make transformations repeatable.

## Initial Findings — January 2025

Total records: 3,475,226

- Missing required fields: 0
- Negative distances: 0
- Distances over 100 miles: 162
- Negative total amounts: 63,037
- Inconsistent timestamps: 124
- Zero-duration trips: 1,927

Counts may overlap between quality rules.

## Next Step

Implement SQL transformations using DuckDB.
