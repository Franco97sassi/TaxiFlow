
WITH pagos AS (
    SELECT DISTINCT
        COALESCE(payment_type, -1) AS pago_id
    FROM {{ source('clean', 'viajes') }}
)

SELECT
    pago_id,
    CASE pago_id
        WHEN 1 THEN 'Credit card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No charge'
        WHEN 4 THEN 'Dispute'
        WHEN 5 THEN 'Unknown'
        WHEN 6 THEN 'Voided trip'
        WHEN -1 THEN 'Not reported'
        ELSE 'Other'
    END AS tipo_pago
FROM pagos
