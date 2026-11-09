
CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.viajes AS

WITH base AS (
    SELECT
        * EXCLUDE (filename),

        date_diff(
            'second',
            tpep_pickup_datetime,
            tpep_dropoff_datetime
        ) / 60.0 AS duracion_minutos,

        regexp_extract(
            filename,
            'yellow_tripdata_([0-9]{4}-[0-9]{2})[.]parquet$',
            1
        ) AS periodo_origen

    FROM read_parquet(?, filename = true)
),

validaciones AS (
    SELECT
        *,

        (tpep_pickup_datetime IS NULL
         OR tpep_dropoff_datetime IS NULL) AS r01,

        (tpep_dropoff_datetime <=
         tpep_pickup_datetime) AS r02,

        (trip_distance < 0) AS r03,

        (trip_distance = 0) AS r04,

        (trip_distance > 100) AS r05,

        (total_amount < 0) AS r06,

        (total_amount IS NULL) AS r07,

        (
            strftime(
                tpep_pickup_datetime,
                '%Y-%m'
            ) IS DISTINCT FROM periodo_origen
        ) AS r08,

        (passenger_count IS NULL
         OR passenger_count = 0) AS r09,

        (duracion_minutos > 1440) AS r10

    FROM base
)

SELECT
    *,

    (
        COALESCE(r01, FALSE) OR
        COALESCE(r02, FALSE) OR
        COALESCE(r03, FALSE) OR
        COALESCE(r07, FALSE)
    ) AS excluir_clean,

    (
        COALESCE(r04, FALSE) OR
        COALESCE(r05, FALSE) OR
        COALESCE(r08, FALSE) OR
        COALESCE(r09, FALSE) OR
        COALESCE(r10, FALSE)
    ) AS requiere_revision,

    CASE
        WHEN COALESCE(r06, FALSE)
        THEN 'AJUSTE_POTENCIAL'
        ELSE 'ORDINARIO'
    END AS tipo_importe

FROM validaciones;
