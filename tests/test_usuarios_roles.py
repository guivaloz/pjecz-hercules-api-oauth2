"""
Unit Tests Usuarios-Roles
"""

import unittest

import requests

from tests import config, oauth2_token


class TestUsuariosRoles(unittest.TestCase):
    """Tests Usuarios-Roles class"""

    def test_get_usuario_rol(self):
        """Test get usuario_rol"""

        # Consultar el usuario_rol con ID 1
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/usuarios_roles/1",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
