-- ==============================================================================
-- KPIs Analíticos - Proyecto de Exportaciones (Capa Gold)
-- ==============================================================================

-- KPI 1: Variación Mensual del Valor FOB (USD) por Sector en 2005
-- Muestra cómo evolucionaron las exportaciones mes a mes usando la función LAG()
WITH exportaciones_mensuales AS (
    SELECT 
        ds.sector,
        dt.mes,
        dt.nombre_mes,
        SUM(h.valor_fob_usd) AS valor_exportado_usd
    FROM gold.hechos_exportaciones h
    JOIN gold.dim_tiempo dt ON h.id_tiempo = dt.id_tiempo
    JOIN gold.dim_producto_sector ds ON h.id_sector = ds.id_sector
    GROUP BY ds.sector, dt.mes, dt.nombre_mes
)
SELECT 
    sector, 
    mes,
    nombre_mes,
    valor_exportado_usd,
    -- Calculamos la diferencia con el mes anterior
    valor_exportado_usd - LAG(valor_exportado_usd) OVER (PARTITION BY sector ORDER BY mes) AS variacion_absoluta_usd
FROM exportaciones_mensuales
ORDER BY sector, mes;


-- KPI 2: Top 5 Países Destino Históricos por Sector (Basado en total USD)
-- Demuestra el uso de RANK() para obtener los mercados más importantes
WITH ranking_paises AS (
    SELECT 
        ds.sector,
        dp.pais_destino,
        SUM(h.valor_fob_usd) AS total_exportado_usd,
        RANK() OVER (PARTITION BY ds.sector ORDER BY SUM(h.valor_fob_usd) DESC) as ranking
    FROM gold.hechos_exportaciones h
    JOIN gold.dim_pais dp ON h.id_pais = dp.id_pais
    JOIN gold.dim_producto_sector ds ON h.id_sector = ds.id_sector
    GROUP BY ds.sector, dp.pais_destino
)
SELECT * 
FROM ranking_paises 
WHERE ranking <= 5
ORDER BY sector, ranking;