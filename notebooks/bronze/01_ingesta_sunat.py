"""
Prueba real de ingesta — SUNAT
Descarga los cuadros oficiales de exportaciones (xlsx, sin login).
"""
import requests
import pandas as pd
import io

CUADROS = {
    "G6": "Exportación Definitiva por País de destino",
    "G9": "Exportaciones Definitivas, según sub-partida nacional",
}

BASE_URL = "https://www.sunat.gob.pe/estadisticasestudios/nota_tributaria/cdro_{codigo}.xlsx"

def descargar_cuadro_sunat(codigo: str) -> pd.DataFrame:
    url = BASE_URL.format(codigo=codigo)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return pd.read_excel(io.BytesIO(resp.content), sheet_name=0, header=None)

if __name__ == "__main__":
    for codigo, descripcion in CUADROS.items():
        print(f"\n--- {codigo}: {descripcion} ---")
        df = descargar_cuadro_sunat(codigo)
        print(f"Shape: {df.shape}")
        print(df.head(15))