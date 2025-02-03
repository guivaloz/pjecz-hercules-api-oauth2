"""
Unit Tests Web Paginas
"""

import unittest

import requests

from tests import config, oauth2_token


class TestWebPaginas(unittest.TestCase):
    """Tests WebPaginas class"""

    def test_get_web_paginas(self):
        """Test get web_paginas"""

        # Consultar
        try:
            response = requests.get(
                url=f"{config['api_base_url']}/api/v5/web_paginas",
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
            self.assertEqual("contenido" in item, True)
            self.assertEqual("etiquetas" in item, True)
            self.assertEqual("estado" in item, True)
            self.assertEqual("fecha_modificacion" in item, True)
            self.assertEqual("responsable" in item, True)
            self.assertEqual("resumen" in item, True)
            self.assertEqual("ruta" in item, True)
            self.assertEqual("titulo" in item, True)
            self.assertEqual("vista_previa" in item, True)


if __name__ == "__main__":
    unittest.main()
