"""
Unit Tests Autoridades
"""

import unittest

import requests

from tests import config, oauth2_token


class TestAutoridades(unittest.TestCase):
    """Tests Autoridades class"""

    def test_get_autoridades(self):
        """Test get autoridades"""

        # Consultar las autoridades
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v5/autoridades",
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
        for item in contenido["data"]:
            self.assertEqual("clave" in item, True)

    def test_get_autoridad_trc_j1_fam(self):
        """Test get autoridad TRC-J1-FAM"""
        clave = "TRC-J1-FAM"
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v5/autoridades/{clave}",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
