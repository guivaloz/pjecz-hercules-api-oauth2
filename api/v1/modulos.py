"""
Modulos, API v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from lib.authentications import get_current_user
from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from lib.fastapi_pagination_custom_page import CustomPage
from models.modulo import Modulo
from models.permiso import Permiso
from schemas.modulo import ModuloOut, OneModuloOut
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
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
    modulo_id: int,
):
    """Detalle de un modulo a partir de su ID"""
    if current_user.permissions.get("MODULOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        modulo = get_modulo(database, modulo_id)
    except MyAnyError as error:
        return OneModuloOut(success=False, message=str(error), errors=[str(error)], data=None)
    return OneModuloOut(success=True, message="Detalle de un modulo", errors=[], data=ModuloOut.model_validate(modulo))


@modulos.get("", response_model=CustomPage[ModuloOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de modulos"""
    if current_user.permissions.get("MODULOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    query = database.query(Modulo).filter(Modulo.estatus == "A").order_by(Modulo.nombre)
    return paginate(query)
