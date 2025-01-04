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
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/materias",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)

    def test_get_materia_fam(self):
        """Test get materia FAM"""
        clave = "FAM"
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/materias/{clave}",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
