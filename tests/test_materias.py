"""
Unit Tests Materias
"""

import unittest

import requests

from tests import config, oauth2_token


class TestMaterias(unittest.TestCase):
    """Tests Materias class"""

    def test_get_materias(self):
        """Test get materias"""

        # Consultar
        try:
            response = requests.get(
                url=f"{config['api_base_url']}/api/v5/materias",
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
            self.assertEqual("clave" in item, True)
            self.assertEqual("nombre" in item, True)
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("en_sentencias" in item, True)

    def test_get_materia_by_clave(self):
        """Test get materia by clave"""

        # Bucle por claves
        for clave in config["materias_claves"]:
            # Consultar
            try:
                response = requests.get(
                    f"{config['api_base_url']}/api/v5/materias/{clave}",
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
            self.assertEqual("nombre" in item, True)
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("en_sentencias" in item, True)


if __name__ == "__main__":
    unittest.main()
