"""
Tests Init
"""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()


# Cargar las variables de entorno
config = {
    "autoridades_claves": os.getenv("AUTORIDADES_CLAVES", "TEST1,TEST2,TEST3").split(","),
    "api_base_url": os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
    "distritos_claves": os.getenv("DISTRITOS_CLAVES", "TEST1,TEST2,TEST3").split(","),
    "materias_claves": os.getenv("MATERIAS_CLAVES", "TEST1,TEST2,TEST3").split(","),
    "password": os.getenv("PASSWORD"),
    "timeout": int(os.getenv("TIMEOUT", "10")),
    "username": os.getenv("USERNAME"),
}

# Obtener el token para hacer el login a la API
payload = {
    "grant_type": "password",
    "username": config["username"],
    "password": config["password"],
}
try:
    response = requests.post(
        url=f"{config['api_base_url']}/token",
        data=payload,
    )
except requests.exceptions.RequestException as error:
    print(error)
    sys.exit(1)
oauth2_token = response.json()["access_token"]
