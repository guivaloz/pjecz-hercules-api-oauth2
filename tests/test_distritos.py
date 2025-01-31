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

        # Consultar
        try:
            response = requests.get(
                url=f"{config['api_base_url']}/api/v5/distritos",
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

        # Validar los datos
        self.assertEqual(type(contenido["data"]), list)
        for item in contenido["data"]:
            self.assertEqual("id" in item, True)
            self.assertEqual("clave" in item, True)
            self.assertEqual("es_distrito_judicial" in item, True)
            self.assertEqual("es_distrito" in item, True)
            self.assertEqual("es_jurisdiccional" in item, True)
            self.assertEqual("nombre_corto" in item, True)
            self.assertEqual("nombre" in item, True)

    def test_get_distrito_by_clave(self):
        """Test get distrito by clave"""

        # Bucle por claves
        for clave in config["distritos_claves"]:
            # Consultar
            try:
                response = requests.get(
                    f"{config['api_base_url']}/api/v5/distritos/{clave}",
                    headers={"Authorization": f"Bearer {oauth2_token}"},
                    timeout=config["timeout"],
                )
            except requests.exceptions.ConnectionError as error:
                self.fail(error)
            self.assertEqual(response.status_code, 200)

            # Validar el contenido de la respuesta
            contenido = response.json()
            self.assertEqual("success" in contenido, True)
            self.assertEqual("message" in contenido, True)
            self.assertEqual("data" in contenido, True)

            # Validar que se haya tenido éxito
            self.assertEqual(contenido["success"], True)

            # Validar los datos
            self.assertEqual(type(contenido["data"]), dict)
            item = contenido["data"]
            self.assertEqual("clave" in item, True)
            self.assertEqual(item["clave"] == clave, True)
            self.assertEqual("id" in item, True)
            self.assertEqual("es_distrito_judicial" in item, True)
            self.assertEqual("es_distrito" in item, True)
            self.assertEqual("es_jurisdiccional" in item, True)
            self.assertEqual("nombre_corto" in item, True)
            self.assertEqual("nombre" in item, True)


if __name__ == "__main__":
    unittest.main()
