
CREATE SCHEMA IF NOT EXISTS clean;

-- Viajes aptos para análisis ordinario
CREATE OR REPLACE TABLE clean.viajes AS
SELECT *
FROM staging.viajes
WHERE NOT excluir_clean
  AND tipo_importe = 'ORDINARIO';

-- Importes negativos para análisis separado
CREATE OR REPLACE TABLE clean.ajustes AS
SELECT *
FROM staging.viajes
WHERE tipo_importe = 'AJUSTE_POTENCIAL';
