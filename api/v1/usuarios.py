"""
Usuarios v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from models.permiso import Permiso
from models.usuario import Usuario
from schemas.usuario import OneUsuarioOut, UsuarioInDB

usuarios = APIRouter(prefix="/api/v1/usuarios", tags=["sistema"])


def get_usuario(database: Session, usuario_id: int) -> Usuario:
    """Consultar un usuario por su ID"""
    usuario = database.query(Usuario).get(usuario_id)
    if usuario is None:
        raise MyNotExistsError("No existe ese usuario")
    if usuario.estatus != "A":
        raise MyIsDeletedError("No es activo ese usuario, está eliminado")
    return usuario


@usuarios.get("/{usuario_id}", response_model=OneUsuarioOut)
async def detalle_usuario(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    usuario_id: int,
):
    """Detalle de un usuario a partir de su e-mail"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        usuario = get_usuario(database, usuario_id)
    except MyAnyError as error:
        return OneUsuarioOut(success=False, message=str(error))
    return OneUsuarioOut.model_validate(usuario)
