"""
Prueba real de ingesta — BCRP (tipo de cambio, sin API key)
"""
import requests

SERIE = "PD04640PD"
URL = f"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{SERIE}/json/2024-01-01/2024-01-31"

def probar_bcrp():
    resp = requests.get(URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    periodos = data.get("periods", [])
    print(f"Registros obtenidos: {len(periodos)}")
    
    for p in periodos[:5]:
        print(p["name"], "->", p["values"])
        
    return periodos

if __name__ == "__main__":
    probar_bcrp()