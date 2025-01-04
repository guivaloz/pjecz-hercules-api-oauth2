"""
Unit Tests MateriasTiposJuicios
"""

import unittest

import requests

from tests import config, oauth2_token


class TestMateriasTiposJuicios(unittest.TestCase):
    """Tests MateriasTiposJuicios class"""

    def test_get_materias_tipos_juicios(self):
        """Test get materias_tipos_juicios"""
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/materias_tipos_juicios",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
