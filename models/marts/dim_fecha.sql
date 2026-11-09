
WITH fechas AS (
    SELECT DISTINCT
        CAST(tpep_pickup_datetime AS DATE) AS fecha
    FROM {{ source('clean', 'viajes') }}
)

SELECT
    CAST(strftime(fecha, '%Y%m%d') AS INTEGER)
        AS fecha_key,
    fecha,
    YEAR(fecha) AS anio,
    MONTH(fecha) AS mes,
    DAY(fecha) AS dia,
    DAYOFWEEK(fecha) AS dia_semana
FROM fechas
WHERE fecha IS NOT NULL
