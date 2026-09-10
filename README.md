# Comercio Exterior Peruano — Pipeline Analítico End-to-End

Proyecto de portafolio para Data Engineer (Azure) — un pipeline analítico completo (bronze → silver → gold) que responde una pregunta de negocio real sobre las exportaciones peruanas, cruzando tres fuentes oficiales: **SUNAT**, **UN Comtrade** y **BCRP**.

> 🚧 **Estado del proyecto:** en construcción activa. Este README se actualiza fase por fase — la sección [Estado actual](#estado-actual) siempre refleja el avance real, no el plan ideal.

---

## Resumen

¿Qué sectores de exportación peruana crecieron o se contrajeron más en términos reales (ajustados por tipo de cambio) en los últimos años, y cuán concentrada está esa exportación en pocos países de destino?

Este proyecto ingesta datos crudos de 3 fuentes públicas hacia una capa **bronze** en Delta Lake, los limpia y concilia en **silver** aplicando reglas de calidad versionadas, los modela dimensionalmente en **gold**, orquesta todo el proceso como jobs de Databricks, lo valida automáticamente con un pipeline de Jenkins en cada cambio, y lo expone en un dashboard de Power BI que responde la pregunta de negocio.

**KPIs que responde:**
1. Variación interanual del valor exportado por sector (USD constantes).
2. Top-5 países destino por sector y año.
3. Índice de concentración HHI por sector (`HHI = SUM(participacion_pais_% ^ 2)`).
4. Tipo de cambio promedio aplicado por año.

---

## Arquitectura

```
[SUNAT]     ─┐
[UN Comtrade]─┼──→  BRONZE  →  SILVER  →  GOLD  →  Power BI
[BCRP]       ─┘
```

| Capa | Qué vive ahí | Responsabilidad |
|---|---|---|
| **Bronze** | Datos crudos, formato original + metadatos de ingesta | Trazabilidad total, nunca se modifica |
| **Silver** | Datos limpios, tipados, deduplicados, conciliados | Lógica de negocio de "qué es un dato válido" |
| **Gold** | Modelo dimensional (hechos + dimensiones) | Listo para consumo analítico y Power BI |
| **Databricks Workflows** | Orquestación de los notebooks | Reemplaza la ejecución manual por un proceso repetible |
| **Jenkins** | CI/CD — lint + tests en cada push | Valida el código antes de considerarlo "listo" |
| **Power BI** | Dashboard conectado a gold | Storytelling de negocio |

Diagrama completo en [`docs/arquitectura.png`](docs/arquitectura.png) · Esquema estrella en [`docs/esquema_estrella.png`](docs/esquema_estrella.png).

---

## Fuentes de datos y por qué se eligieron

Las 3 fuentes fueron verificadas en vivo (no son datasets genéricos de práctica) antes de construir sobre ellas.

### SUNAT — Nota Tributaria y Aduanera
- **Portal:** https://www.sunat.gob.pe/estadisticasestudios/exportaciones.html
- **Cuadros usados:** `cdro_G6.xlsx` (exportación por país destino), `cdro_G9.xlsx` (por sub-partida nacional)
- **Por qué:** SUNAT es la entidad que registra cada declaración aduanera en el Perú — es la fuente primaria, no un agregador. Único origen con el detalle exacto de **partida arancelaria × país destino** que la pregunta de negocio necesita.
- **Limitación:** descarga `.xlsx` con filas de encabezado antes de la tabla real; requiere limpieza en silver.

### UN Comtrade — Base de datos de comercio internacional de la ONU
- **Endpoint gratuito (sin key):** https://comtradeapi.un.org/public/v1/preview/C/A/HS (tope 500 registros)
- **Registro para acceso completo:** https://comtradedeveloper.un.org/ (gratis, hasta 100 000 registros/llamada)
- **Reporter code de Perú:** `604` (código numérico UN M49)
- **Por qué:** permite comparar a Perú contra otros países (benchmarking) y conciliar cómo el país receptor reporta la misma transacción — ejercicio real de conciliación de datos.
- **Limitación:** el endpoint gratuito tiene tope de 500 registros; se necesita la key gratuita para el volumen real.

### BCRP — Banco Central de Reserva del Perú
- **API:** `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{serie}/json/{fecha_inicio}/{fecha_fin}`
- **Serie usada:** `PD04640PD` — Tipo de cambio Sistema Bancario SBS (S/ por US$), Venta, diario
- **Por qué:** fuente oficial del tipo de cambio peruano, gratuita y sin key — más defendible en una entrevista que un agregador externo. Serie diaria completa desde 1992.
- **Limitación:** fines de semana/feriados aparecen como `"n.d."`, requiere forward-fill en silver.

---

## Decisiones de diseño clave

- **Conversión de moneda con tasa histórica, no actual** — cada registro de comercio se normaliza a USD usando la tasa de cambio vigente en su fecha exacta (con forward-fill para fines de semana/feriados), no la tasa del día de hoy. Es el error más común en este tipo de proyecto y el que más se nota evitarlo.
- **Esquema estrella real** — una tabla de hechos (`hechos_comercio_exterior`) con grano `(fecha, país_destino, partida_arancelaria)` y 3 dimensiones propias (`dim_tiempo`, `dim_pais`, `dim_producto_sector`), en vez de una tabla plana renombrada como "gold".
- **Reglas de calidad explícitas y medibles** — cada regla de silver (valores no negativos, fechas en rango, país válido) genera un reporte cuantificado de cuántos registros pasaron y cuántos fallaron, no una limpieza "a ojo".
- **CI/CD real, no solo mencionado** — Jenkins ejecuta lint + pruebas automatizadas en cada push, con capturas de ejecuciones reales (exitosas y fallidas) como evidencia.

---

## Estructura del repositorio

```text
comercio-exterior-peru-de/
├── README.md
├── docs/
│   ├── 01_planteamiento.md
│   ├── diccionario_datos.md
│   ├── reporte_calidad.md
│   ├── arquitectura.png
│   └── esquema_estrella.png
├── notebooks/
│   ├── bronze/
│   │   ├── 01_ingesta_sunat.py
│   │   ├── 02_ingesta_comtrade.py
│   │   └── 03_ingesta_bcrp.py
│   ├── silver/
│   │   ├── 01_limpieza_conciliacion.py
│   │   └── 02_conversion_moneda.py
│   ├── gold/
│   │   ├── 01_dim_tiempo.py
│   │   ├── 02_dim_pais.py
│   │   ├── 03_dim_producto_sector.py
│   │   └── 04_hechos_comercio_exterior.py
│   └── kpis/
│       └── kpis.sql
├── jobs/
│   └── workflow_comercio_exterior.json
├── ci/
│   └── Jenkinsfile
├── tests/
│   ├── test_bronze_ingesta.py
│   ├── test_silver_calidad.py
│   └── test_gold_reconciliacion.py
└── powerbi/
    └── dashboard_comercio_exterior.pbix
```

---

## Cómo reproducirlo

1. **Bronze:** corre los 3 notebooks de `notebooks/bronze/` (requieren `requests`, `pandas`, `openpyxl`; en Databricks, PySpark ya viene incluido). Ninguno necesita credenciales para la prueba inicial — Comtrade solo pide key si superas 500 registros.
2. **Silver:** corre `notebooks/silver/01_limpieza_conciliacion.py` y luego `02_conversion_moneda.py` sobre las tablas bronze.
3. **Gold:** corre los 4 notebooks de `notebooks/gold/` en orden (`dim_tiempo` → `dim_pais` → `dim_producto_sector` → `hechos_comercio_exterior`).
4. **Orquestación:** importa `jobs/workflow_comercio_exterior.json` como Job de Databricks Workflows para encadenar todo automáticamente.
5. **Power BI:** conecta `powerbi/dashboard_comercio_exterior.pbix` al catálogo/esquema `gold` vía el conector de Azure Databricks.

---

## Estado actual

- [x] Fase 0 — Planteamiento y fuentes de datos verificadas
- [x] Fase 1 — Ingesta a Bronze (prueba real de las 3 fuentes sincronizadas al 2005)
- [x] Fase 2 — Limpieza y conciliación en Silver
- [ ] Fase 3 — Modelado dimensional en Gold
- [ ] Fase 4 — Orquestación en Databricks
- [ ] Fase 5 — Flujo de Git/GitHub (ramas, PRs, conflicto resuelto)
- [ ] Fase 6 — CI/CD con Jenkins
- [ ] Fase 7 — Pruebas automatizadas conectadas al CI/CD
- [ ] Fase 8 — Dashboard de Power BI
- [ ] Fase 9 — Documentación final revisada

---

## Limitaciones conocidas

- El endpoint gratuito de UN Comtrade limita a 500 registros por consulta — el volumen completo del proyecto requiere la key gratuita de `comtradedeveloper.un.org`.
- Los cuadros de SUNAT son archivos `.xlsx` pensados para lectura humana (no una API), por lo que cualquier cambio de formato en el portal puede romper el parseo — se documenta en `docs/diccionario_datos.md`.
- El alcance temporal y geográfico de esta primera versión es acotado (ver `docs/01_planteamiento.md`); no pretende ser un reporte oficial de comercio exterior.
- Escalabilidad del MVP: El proyecto actual se configuró como un MVP enfocado en el año 2005 y en el mercado del café. Gracias al diseño parametrizado en PySpark, el pipeline puede ser extrapolado a otros años (ej. 2015-2024) u otros sectores simplemente ajustando los parámetros de extracción en Bronze.

## Qué haría distinto en producción

- Orquestador gestionado con reintentos y alertas más robustas que un job manual de Databricks.
- Ingesta incremental real (solo registros nuevos desde la última corrida) en vez de recarga completa.
- Monitoreo de calidad de datos con alertas automáticas, no solo un reporte estático por corrida.
- Manejo de secretos con Azure Key Vault en vez de Jenkins Credentials Store únicamente.
- Particionamiento y volumen pensados para escala productiva, no para el tamaño de un proyecto de portafolio.

---

## Stack técnico

`PySpark` · `Delta Lake` · `Azure Databricks` · `SQL avanzado` · `Git/GitHub` · `Jenkins` · `Power BI` · `Python` (`requests`, `pandas`, `openpyxl`)