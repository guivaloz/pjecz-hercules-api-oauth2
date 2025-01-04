"""
Usuarios-Roles v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from lib.fastapi_pagination_custom_page import CustomPage
from models.permiso import Permiso
from models.usuario_rol import UsuarioRol
from schemas.usuario import UsuarioInDB
from schemas.usuario_rol import OneUsuarioRolOut, UsuarioRolOut

usuarios_roles = APIRouter(prefix="/api/v1/usuarios_roles", tags=["sistema"])


def get_usuario_rol(database: Session, usuario_rol_id: int) -> UsuarioRol:
    """Consultar un usuario-rol por su ID"""
    usuario_rol = database.query(UsuarioRol).get(usuario_rol_id)
    if usuario_rol is None:
        raise MyNotExistsError("No existe ese usuario-rol")
    if usuario_rol.estatus != "A":
        raise MyIsDeletedError("No es activo ese usuario-rol, está eliminado")
    return usuario_rol


@usuarios_roles.get("/{usuario_rol_id}", response_model=OneUsuarioRolOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    usuario_rol_id: int,
):
    """Detalle de un usuario_rol a partir de su ID"""
    if current_user.permissions.get("USUARIOS ROLES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        usuario_rol = get_usuario_rol(database, usuario_rol_id)
    except MyAnyError as error:
        return OneUsuarioRolOut(success=False, message=str(error), errors=[str(error)], data=None)
    return OneUsuarioRolOut(
        success=True, message="Detalle de un usuario_rol", errors=[], data=UsuarioRolOut.model_validate(usuario_rol)
    )


@usuarios_roles.get("", response_model=CustomPage[UsuarioRolOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de usuarios_roles"""
    if current_user.permissions.get("USUARIOS ROLES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(UsuarioRol).filter(UsuarioRol.estatus == "A").order_by(UsuarioRol.id)
    return paginate(query)
