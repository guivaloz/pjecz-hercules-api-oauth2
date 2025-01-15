"""
Usuarios, v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import get_current_user
from ..dependencies.database import Session, get_db
from ..dependencies.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError, MyNotValidParamError
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_email
from ..models.autoridad import Autoridad
from ..models.permiso import Permiso
from ..models.usuario import Usuario
from ..schemas.usuario import OneUsuarioOut, UsuarioInDB, UsuarioOut

usuarios = APIRouter(prefix="/api/v1/usuarios", tags=["sistema"])


def get_usuario_with_email(database: Session, email: str) -> Usuario:
    """Consultar una usuario por su email"""
    try:
        email = safe_email(email)
    except ValueError:
        raise MyNotValidParamError("No es válido el email del usuario")
    usuario = database.query(Usuario).filter(Usuario.email == email).first()
    if usuario is None:
        raise MyNotExistsError("No existe ese usuario")
    if usuario.estatus != "A":
        raise MyIsDeletedError("No es activo ese usuario, está eliminado")
    return usuario


@usuarios.get("/{email}", response_model=OneUsuarioOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    email: str,
):
    """Detalle de un usuario a partir de su e-mail"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        usuario = get_usuario_with_email(database, email)
    except MyAnyError as error:
        return OneUsuarioOut(success=False, message=str(error), errors=[str(error)], data=None)
    return OneUsuarioOut(success=True, message="Detalle de un usuario", errors=[], data=UsuarioOut.model_validate(usuario))


@usuarios.get("", response_model=CustomPage[UsuarioOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = None,
):
    """Paginado de usuarios"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Usuario)
    if autoridad_clave is not None:
        try:
            clave = safe_clave(autoridad_clave)
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
        query = query.join(Autoridad).filter(Autoridad.clave == clave).filter(Autoridad.estatus == "A")
    query = query.filter(Usuario.estatus == "A").order_by(Usuario.email)
    return paginate(query)
