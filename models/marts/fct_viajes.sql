
SELECT
    CAST(
        strftime(
            CAST(tpep_pickup_datetime AS DATE),
            '%Y%m%d'
        ) AS INTEGER
    ) AS fecha_key,

    COALESCE(PULocationID, -1)
        AS zona_origen_id,

    COALESCE(DOLocationID, -1)
        AS zona_destino_id,

    COALESCE(payment_type, -1)
        AS pago_id,

    tpep_pickup_datetime AS fecha_inicio,
    tpep_dropoff_datetime AS fecha_fin,

    trip_distance,
    duracion_minutos,
    fare_amount,
    tip_amount,
    total_amount,

    periodo_origen,
    requiere_revision

FROM {{ source('clean', 'viajes') }}
