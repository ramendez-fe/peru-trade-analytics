"""
Prueba real de ingesta — UN Comtrade (endpoint "preview", sin API key)
"""
import requests

URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
PARAMS = {
    "flowCode": "X",
    "reporterCode": 604, # Código numérico UN M49 de Perú
    "period": 2023,
    "partnerCode": 0,
    "cmdCode": "TOTAL",
}

def probar_comtrade():
    resp = requests.get(URL, params=PARAMS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    registros = data.get("data", [])
    print(f"Registros obtenidos: {len(registros)}")
    
    if registros:
        print("\n--- Primer registro ---")
        print(registros[0])
    
    return registros

if __name__ == "__main__":
    probar_comtrade()