"""
Usuarios, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from lib.schemas_base import OneBaseOut


class Token(BaseModel):
    """Token"""

    access_token: str
    expires_in: int
    token_type: str
    username: str


class UsuarioOut(BaseModel):
    """Esquema para entregar usuarios"""

    id: int | None = None
    email: str | None = None
    nombres: str | None = None
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    puesto: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneUsuarioOut(UsuarioOut, OneBaseOut):
    """Esquema para entregar un usuario"""


class UsuarioInDB(UsuarioOut):
    """Usuario en base de datos"""

    username: str
    permissions: dict
    hashed_password: str
    disabled: bool
