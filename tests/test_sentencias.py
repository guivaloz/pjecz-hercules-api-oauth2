"""
Unit Tests Sentencias
"""

import unittest

import requests

from tests import config, oauth2_token


class TestSentencias(unittest.TestCase):
    """Tests Sentencias class"""

    def test_get_sentencias(self):
        """Test get sentencias"""
        try:
            response = requests.get(
                url=f"{config['base_url']}/api/v1/sentencias",
                headers={"Authorization": f"Bearer {oauth2_token}"},
                timeout=config["timeout"],
            )
        except requests.exceptions.RequestException as error:
            self.fail(error)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
