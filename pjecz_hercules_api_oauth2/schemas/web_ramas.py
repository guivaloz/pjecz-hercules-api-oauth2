"""
Web Ramas, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class WebRamaOut(BaseModel):
    """Esquema para entregar WebRama"""

    clave: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class OneWebRamaOut(OneBaseOut):
    """Esquema para entregar una WebRama"""

    data: WebRamaOut | None = None
