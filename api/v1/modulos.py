"""
Modulos v1
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from lib.database import Session, get_db
from lib.exceptions import MyAnyError, MyIsDeletedError, MyNotExistsError
from models.modulo import Modulo
from schemas.modulo import OneModuloOut

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
    database: Annotated[Session, Depends(get_db)],
    modulo_id: int,
):
    """Detalle de un módulo a partir de su ID"""
    try:
        modulo = get_modulo(database, modulo_id)
    except MyAnyError as error:
        return OneModuloOut(success=False, message=str(error))
    return OneModuloOut.model_validate(modulo)
