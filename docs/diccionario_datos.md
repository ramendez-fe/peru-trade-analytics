# Diccionario de Datos — Capa Silver

Este documento describe la estructura, el tipado y el significado de los datos almacenados en las tablas de la capa Silver, tras el proceso de limpieza, desduplicación y conciliación de monedas.

## Tablas Principales: `silver.sunat_paises` y `silver.comtrade`

| Campo | Tipo | Unidad | Fuente | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `pais_destino` | string | — | SUNAT / Comtrade | País de destino de la exportación. En Comtrade, el código '0' se normalizó como 'MUNDO'. |
| `fecha` | date | — | SUNAT | Primer día del mes que representa el valor (ej. 2005-01-01 para enero). |
| `anio` | int | — | Comtrade | Año del periodo reportado en la extracción. |
| `valor_fob_usd` | double | USD | SUNAT / Comtrade | Valor FOB transaccional en dólares, estandarizado desde su escala original. |
| `valor_fob_pen` | double | PEN (Soles) | Calculado | Equivalente en Soles (`valor_fob_usd` × `tasa_cambio_rellena`). Exclusivo de la tabla SUNAT. |

---

## Tabla de Referencia: `silver.tipo_cambio`

| Campo | Tipo | Unidad | Fuente | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `fecha` | date | — | BCRP (Calendario) | Calendario maestro continuo de 365 días. |
| `tasa_cambio` | double | S/ por US$ | BCRP | Tipo de cambio venta bancario original. Es nulo en fines de semana y feriados. |
| `tasa_cambio_rellena` | double | S/ por US$ | Calculado | Tasa de cambio imputada mediante *forward-fill* (y *back-fill* de rescate) para garantizar 100% de cobertura. |