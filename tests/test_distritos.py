"""
Unit Tests Distritos
"""

import unittest

import requests

from tests import config, oauth2_token


class TestDistritos(unittest.TestCase):
    """Tests Distritos class"""

    def test_get_distritos(self):
        """Test get distritos"""

        # Consultar los distritos
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v5/distritos",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)

        # Validar el contenido de la respuesta
        contenido = response.json()
        self.assertEqual("success" in contenido, True)
        self.assertEqual("message" in contenido, True)
        self.assertEqual("data" in contenido, True)

        # Validar que se haya tenido éxito
        self.assertEqual(contenido["success"], True)

        # Validar que en los datos haya el listado de autoridades
        self.assertEqual(type(contenido["data"]), list)

    def test_get_distrito_dtrc(self):
        """Test get distrito DTRC"""
        clave = "dtrc"
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v5/distritos/{clave}",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
