"""
Unit Tests Usuarios
"""

import unittest

import requests

from tests import config, oauth2_token


class TestUsuarios(unittest.TestCase):
    """Tests Usuarios class"""

    def test_get_usuarios(self):
        """Test GET method for usuarios"""

        # Consultar
        try:
            response = requests.get(
                f"{config['api_base_url']}/api/v5/usuarios",
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
            self.assertEqual("email" in item, True)
            self.assertEqual("nombres" in item, True)
            self.assertEqual("apellido_paterno" in item, True)
            self.assertEqual("apellido_materno" in item, True)
            self.assertEqual("puesto" in item, True)

    def test_get_usuario_by_email(self):
        """Test get usuario by e-mail"""

        # Consultar
        try:
            response = requests.get(
                url=f"{config['api_base_url']}/api/v5/usuarios/{config['username']}",
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
        self.assertEqual(type(contenido["data"]), dict)
        item = contenido["data"]
        self.assertEqual("email" in item, True)
        self.assertEqual(item["email"] == config["username"], True)
        self.assertEqual("apellido_paterno" in item, True)
        self.assertEqual("apellido_materno" in item, True)
        self.assertEqual("autoridad_clave" in item, True)
        self.assertEqual("autoridad_descripcion_corta" in item, True)
        self.assertEqual("distrito_clave" in item, True)
        self.assertEqual("distrito_nombre_corto" in item, True)
        self.assertEqual("nombres" in item, True)
        self.assertEqual("puesto" in item, True)


if __name__ == "__main__":
    unittest.main()
