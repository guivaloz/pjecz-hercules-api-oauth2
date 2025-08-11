"""
Usuarios, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Esquema que se entrega al hacer login"""

    access_token: str
    expires_in: int
    token_type: str
    username: str


class UsuarioOut(BaseModel):
    """Esquema para entregar usuarios"""

    email: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    puesto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    model_config = ConfigDict(from_attributes=True)


class OneUsuarioOut(BaseModel):
    """Esquema para entregar un usuario"""

    success: bool
    message: str
    data: UsuarioOut | None = None


class UsuarioInDB(UsuarioOut):
    """Usuario en base de datos"""

    username: str
    permissions: dict
    hashed_password: str
    disabled: bool
