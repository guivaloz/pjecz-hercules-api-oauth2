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
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/distritos",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
