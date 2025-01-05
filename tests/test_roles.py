"""
Unit Tests Roles
"""

import unittest

import requests

from tests import config, oauth2_token


class TestRoles(unittest.TestCase):
    """Tests Roles class"""

    def test_get_roles(self):
        """Test get roles"""
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/roles",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
