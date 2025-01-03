"""
Usuarios v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError, MyNotValidParamError
from lib.safe_string import safe_email
from models.usuario import Usuario
from schemas.usuario import OneUsuarioOut

usuarios = APIRouter(prefix="/api/v1/usuarios", tags=["sistema"])


def get_usuario(database: Session, usuario_id: int) -> Usuario:
    """Consultar un usuario por su ID"""
    usuario = database.query(Usuario).get(usuario_id)
    if usuario is None:
        raise MyNotExistsError("No existe ese usuario")
    if usuario.estatus != "A":
        raise MyIsDeletedError("No es activo ese usuario, está eliminado")
    return usuario


def get_usuario_with_email(database: Session, usuario_email: str) -> Usuario:
    """Consultar un usuario por su email"""
    try:
        email = safe_email(usuario_email)
    except ValueError as error:
        raise MyNotValidParamError("El email no es válido") from error
    usuario = database.query(Usuario).filter_by(email=email).first()
    if usuario is None:
        raise MyNotExistsError("No existe ese usuario")
    if usuario.estatus != "A":
        raise MyIsDeletedError("No es activo ese usuario, está eliminado")
    return usuario


@usuarios.get("/{email}", response_model=OneUsuarioOut)
async def detalle_usuario(
    database: Annotated[Session, Depends(get_db)],
    email: str,
):
    """Detalle de un usuario a partir de su e-mail"""
    try:
        usuario = get_usuario_with_email(database, email)
    except MyAnyError as error:
        return OneUsuarioOut(success=False, message=str(error))
    return OneUsuarioOut.model_validate(usuario)
