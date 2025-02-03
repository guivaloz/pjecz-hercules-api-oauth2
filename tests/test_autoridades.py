"""
Unit Tests Autoridades
"""

import unittest

import requests

from tests import config, oauth2_token


class TestAutoridades(unittest.TestCase):
    """Tests Autoridades class"""

    def test_get_autoridades(self):
        """Test get autoridades"""

        # Consultar
        try:
            response = requests.get(
                url=f"{config['api_base_url']}/api/v5/autoridades",
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
            self.assertEqual("distrito_clave" in item, True)
            self.assertEqual("distrito_nombre_corto" in item, True)
            self.assertEqual("materia_clave" in item, True)
            self.assertEqual("materia_nombre" in item, True)
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("descripcion_corta" in item, True)
            self.assertEqual("directorio_edictos" in item, True)
            self.assertEqual("directorio_glosas" in item, True)
            self.assertEqual("directorio_listas_de_acuerdos" in item, True)
            self.assertEqual("directorio_sentencias" in item, True)
            self.assertEqual("es_extinto" in item, True)
            self.assertEqual("es_cemasc" in item, True)
            self.assertEqual("es_defensoria" in item, True)
            self.assertEqual("es_jurisdiccional" in item, True)
            self.assertEqual("es_notaria" in item, True)
            self.assertEqual("es_organo_especializado" in item, True)
            self.assertEqual("organo_jurisdiccional" in item, True)

    def test_get_autoridad_by_clave(self):
        """Test get autoridad by clave"""

        # Bucle por claves
        for clave in config["autoridades_claves"]:
            # Consultar
            try:
                response = requests.get(
                    f"{config['api_base_url']}/api/v5/autoridades/{clave}",
                    headers={"Authorization": f"Bearer {oauth2_token}"},
                    timeout=config["timeout"],
                )
            except requests.exceptions.ConnectionError as error:
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
            self.assertEqual("clave" in item, True)
            self.assertEqual(item["clave"] == clave, True)
            self.assertEqual("descripcion" in item, True)
            self.assertEqual("descripcion_corta" in item, True)
            self.assertEqual("distrito_clave" in item, True)
            self.assertEqual("distrito_nombre_corto" in item, True)
            self.assertEqual("directorio_edictos" in item, True)
            self.assertEqual("directorio_glosas" in item, True)
            self.assertEqual("directorio_listas_de_acuerdos" in item, True)
            self.assertEqual("directorio_sentencias" in item, True)
            self.assertEqual("es_extinto" in item, True)
            self.assertEqual("es_cemasc" in item, True)
            self.assertEqual("es_defensoria" in item, True)
            self.assertEqual("es_jurisdiccional" in item, True)
            self.assertEqual("es_notaria" in item, True)
            self.assertEqual("es_organo_especializado" in item, True)
            self.assertEqual("organo_jurisdiccional" in item, True)


if __name__ == "__main__":
    unittest.main()
