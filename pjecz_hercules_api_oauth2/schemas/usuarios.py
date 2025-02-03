"""
Usuarios, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict

from ..dependencies.schemas_base import OneBaseOut


class Token(BaseModel):
    """Esquema que se entrega al hacer login"""

    access_token: str
    expires_in: int
    token_type: str
    username: str


class UsuarioOut(BaseModel):
    """Esquema para entregar usuarios"""

    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    autoridad_clave: str | None = None
    autoridad_descripcion_corta: str | None = None
    distrito_clave: str | None = None
    distrito_nombre_corto: str | None = None
    email: str | None = None
    nombres: str | None = None
    puesto: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneUsuarioOut(OneBaseOut):
    """Esquema para entregar un usuario"""

    data: UsuarioOut | None = None


class UsuarioInDB(UsuarioOut):
    """Usuario en base de datos"""

    username: str
    permissions: dict
    hashed_password: str
    disabled: bool
