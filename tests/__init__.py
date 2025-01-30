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
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
    "base_url": os.getenv("BASE_URL", "http://127.0.0.1:8000"),
    "timeout": int(os.getenv("TIMEOUT", "10")),
}

# Obtener el token para hacer el login a la API
payload = {
    "grant_type": "password",
    "username": config["username"],
    "password": config["password"],
}
try:
    response = requests.post(
        url=f"{config['base_url']}/token",
        data=payload,
    )
except requests.exceptions.RequestException as error:
    print(error)
    sys.exit(1)
oauth2_token = response.json()["access_token"]
