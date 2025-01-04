"""
Modulos v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from models.modulo import Modulo
from models.permiso import Permiso
from schemas.modulo import OneModuloOut
from schemas.usuario import UsuarioInDB

modulos = APIRouter(prefix="/api/v1/modulos", tags=["sistema"])


def get_modulo(database: Session, modulo_id: int) -> Modulo:
    """Consultar un módulo por su ID"""
    modulo = database.query(Modulo).get(modulo_id)
    if modulo is None:
        raise MyNotExistsError("No existe ese modulo")
    if modulo.estatus != "A":
        raise MyIsDeletedError("No es activo ese modulo, está eliminado")
    return modulo


@modulos.get("/{modulo_id}", response_model=OneModuloOut)
async def detalle_modulo(
    modulo_id: int,
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Detalle de un módulo a partir de su ID"""
    if current_user.permissions.get("MODULOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        modulo = get_modulo(database, modulo_id)
    except MyAnyError as error:
        return OneModuloOut(success=False, message=str(error))
    return OneModuloOut.model_validate(modulo)
