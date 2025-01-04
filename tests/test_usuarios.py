"""
Unit Tests Usuarios
"""

import unittest

import requests

from tests import config, oauth2_token


class TestUsuarios(unittest.TestCase):
    """Tests Usuarios class"""

    def test_get_usuario(self):
        """Test get usuario"""
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/usuarios/1",  # Consultar el ID 1
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)

    def test_get_usuario_username(self):
        """Test get usuario username"""
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/usuarios/{config['username']}",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
