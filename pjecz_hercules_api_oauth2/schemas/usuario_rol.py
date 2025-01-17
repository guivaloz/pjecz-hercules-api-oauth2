"""
Usuarios-Roles, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class UsuarioRolOut(BaseModel):
    """Esquema para entregar usuarios-roles"""

    id: int | None = None
    rol_id: int | None = None
    rol_nombre: str | None = None
    usuario_id: int | None = None
    usuario_nombre: str | None = None
    descripcion: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneUsuarioRolOut(OneBaseOut):
    """Esquema para entregar un usuario-rol"""

    data: UsuarioRolOut | None = None
