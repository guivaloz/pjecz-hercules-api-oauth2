"""
Roles, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from lib.schemas_base import OneBaseOut


class RolOut(BaseModel):
    """Esquema para entregar roles"""

    id: int | None = None
    nombre: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneRolOut(OneBaseOut):
    """Esquema para entregar un rol"""

    data: RolOut | None = None