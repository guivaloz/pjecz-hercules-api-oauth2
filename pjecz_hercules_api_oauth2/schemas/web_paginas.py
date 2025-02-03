"""
Web Páginas, esquemas de pydantic
"""

from datetime import date

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class WebPaginaOut(BaseModel):
    """Esquema para items de WebPagina"""

    clave: str
    contenido: str
    etiquetas: str | None = None
    estado: str
    fecha_modificacion: date
    responsable: str | None = None
    resumen: str | None = None
    ruta: str
    titulo: str
    vista_previa: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneWebPaginaOut(OneBaseOut):
    """Esquema para entregar una WebPagina"""

    data: WebPaginaOut | None = None
