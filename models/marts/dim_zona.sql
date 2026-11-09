
WITH zonas AS (
    SELECT
        COALESCE(PULocationID, -1) AS zona_id
    FROM {{ source('clean', 'viajes') }}

    UNION

    SELECT
        COALESCE(DOLocationID, -1) AS zona_id
    FROM {{ source('clean', 'viajes') }}
)

SELECT zona_id
FROM zonas
