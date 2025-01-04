"""
Unit Tests Modulos
"""

import unittest

import requests

from tests import config, oauth2_token


class TestModulos(unittest.TestCase):
    """Tests Modulos class"""

    def test_get_modulo(self):
        """Test get modulo"""
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/modulos/1",  # Consultar el ID 1
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)

    def test_get_modulos(self):
        """Test get modulos"""
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/modulos",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
