"""
Usuarios-Roles v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from models.usuario_rol import UsuarioRol
from schemas.usuario_rol import OneUsuarioRolOut

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
async def detalle_usuario_rol(
    database: Annotated[Session, Depends(get_db)],
    usuario_rol_id: int,
):
    """Detalle de un usuario-rol a partir de su ID"""
    try:
        usuario_rol = get_usuario_rol(database, usuario_rol_id)
    except MyAnyError as error:
        return OneUsuarioRolOut(success=False, message=str(error))
    return OneUsuarioRolOut.model_validate(usuario_rol)
